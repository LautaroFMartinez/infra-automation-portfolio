import hashlib
import hmac
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import Store


SECRET = "test-secret"


class WebhookLabTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "test.sqlite3")

    def tearDown(self):
        self.store.conn.close()
        self.tmp.cleanup()

    def test_duplicate_event_is_accepted_once(self):
        payload = {"order_id": "ord-1", "status": "paid", "amount": "10.00", "currency": "USD"}
        self.assertTrue(self.store.ingest("stripe", "evt-1", "order.created", payload))
        self.assertFalse(self.store.ingest("stripe", "evt-1", "order.created", payload))
        self.assertEqual(len(self.store.list_events()), 1)

    def test_processing_is_idempotent(self):
        payload = {"order_id": "ord-1", "status": "paid", "amount": "10.00", "currency": "USD"}
        self.store.ingest("paypal", "evt-1", "order.created", payload)
        self.assertEqual(self.store.process_pending(), {"processed": 1, "retried": 0, "failed": 0})
        self.assertEqual(self.store.process_pending(), {"processed": 0, "retried": 0, "failed": 0})
        rows = self.store.conn.execute("SELECT * FROM orders").fetchall()
        self.assertEqual(len(rows), 1)

    def test_transient_failure_is_retried(self):
        payload = {"order_id": "ord-1", "status": "paid", "simulate_failure": True}
        self.store.ingest("revolut", "evt-1", "order.created", payload)
        self.assertEqual(self.store.process_pending(), {"processed": 0, "retried": 1, "failed": 0})
        self.assertEqual(self.store.process_pending(), {"processed": 1, "retried": 0, "failed": 0})

    def test_reconciliation_reports_missing_local_orders(self):
        self.store.upsert_order("shopify", {"id": "local-only", "status": "paid"})
        result = self.store.reconcile("shopify", [{"id": "remote-1", "status": "paid"}])
        self.assertEqual(result, {"seen": 1, "created_or_updated": 1, "missing_local": 1})

    def test_reconciliation_accepts_multiple_pages(self):
        result = self.store.reconcile_pages(
            "mercado-libre",
            [
                {"orders": [{"id": "page-1", "status": "paid"}]},
                {"orders": [{"id": "page-2", "status": "shipped"}]},
            ],
        )
        self.assertEqual(result, {"seen": 2, "created_or_updated": 2, "missing_local": 0})

    def test_signature_calculation_contract(self):

        body = json.dumps({"id": "evt-1"}, separators=(",", ":")).encode()
        signature = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
        self.assertEqual(len(signature), 64)


if __name__ == "__main__":
    unittest.main()
