#!/usr/bin/env python3
"""Sanitized e-commerce webhook reliability lab.

The implementation intentionally uses only the Python standard library so the
case is easy to inspect and run without provider credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DB_PATH = os.environ.get("LAB_DB", "lab.sqlite3")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "demo-secret")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class Store:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self.conn:
            self.conn.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT,
                    received_at TEXT NOT NULL,
                    processed_at TEXT,
                    next_attempt_at TEXT,
                    UNIQUE(provider, event_id)
                );
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    amount TEXT,
                    currency TEXT,
                    updated_at TEXT NOT NULL,
                    UNIQUE(provider, external_id)
                );
                CREATE TABLE IF NOT EXISTS reconciliation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    seen_count INTEGER NOT NULL,
                    created_or_updated_count INTEGER NOT NULL,
                    missing_local_count INTEGER NOT NULL,
                    ran_at TEXT NOT NULL
                );
                """
            )

    def health(self) -> dict[str, Any]:
        with self.lock:
            events = self.conn.execute(
                "SELECT status, COUNT(*) AS count FROM events GROUP BY status"
            ).fetchall()
            return {
                "ok": True,
                "database": "ok",
                "events": {row["status"]: row["count"] for row in events},
            }

    def ingest(self, provider: str, event_id: str, event_type: str, payload: dict[str, Any]) -> bool:
        raw = canonical_json(payload)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        with self.lock, self.conn:
            try:
                self.conn.execute(
                    """INSERT INTO events
                    (provider, event_id, event_type, payload, payload_sha256, received_at)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (provider, event_id, event_type, raw, digest, now()),
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def pending_events(self, limit: int = 50) -> list[sqlite3.Row]:
        with self.lock:
            return self.conn.execute(
                """SELECT * FROM events
                WHERE status IN ('pending', 'retry')
                ORDER BY id LIMIT ?""",
                (limit,),
            ).fetchall()

    def process_pending(self, limit: int = 50) -> dict[str, Any]:
        processed = retried = failed = 0
        for event in self.pending_events(limit):
            payload = json.loads(event["payload"])
            try:
                if payload.get("simulate_failure") and event["attempts"] == 0:
                    raise RuntimeError("simulated transient destination failure")
                if event["event_type"] in {"order.created", "order.updated", "orders/updated"}:
                    self.upsert_order(event["provider"], payload)
                with self.lock, self.conn:
                    self.conn.execute(
                        """UPDATE events SET status='processed', attempts=attempts+1,
                        processed_at=?, last_error=NULL WHERE id=?""",
                        (now(), event["id"]),
                    )
                processed += 1
            except RuntimeError as exc:
                with self.lock, self.conn:
                    self.conn.execute(
                        """UPDATE events SET status='retry', attempts=attempts+1,
                        last_error=?, next_attempt_at=? WHERE id=?""",
                        (str(exc), now(), event["id"]),
                    )
                retried += 1
            except (KeyError, TypeError, ValueError) as exc:
                with self.lock, self.conn:
                    self.conn.execute(
                        """UPDATE events SET status='failed', attempts=attempts+1,
                        last_error=? WHERE id=?""",
                        (f"invalid payload: {exc}", event["id"]),
                    )
                failed += 1
        return {"processed": processed, "retried": retried, "failed": failed}

    def upsert_order(self, provider: str, payload: dict[str, Any]) -> None:
        external_id = str(payload["order_id"] if "order_id" in payload else payload["id"])
        status = str(payload.get("status", "unknown"))
        amount = str(payload.get("amount", ""))
        currency = str(payload.get("currency", ""))
        with self.lock, self.conn:
            self.conn.execute(
                """INSERT INTO orders(provider, external_id, status, amount, currency, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(provider, external_id) DO UPDATE SET
                  status=excluded.status, amount=excluded.amount,
                  currency=excluded.currency, updated_at=excluded.updated_at""",
                (provider, external_id, status, amount, currency, now()),
            )

    def reconcile(self, provider: str, remote_orders: list[dict[str, Any]]) -> dict[str, int]:
        remote_ids = {str(item["order_id"] if "order_id" in item else item["id"]) for item in remote_orders}
        for order in remote_orders:
            self.upsert_order(provider, order)
        with self.lock:
            local_ids = {
                str(row["external_id"])
                for row in self.conn.execute(
                    "SELECT external_id FROM orders WHERE provider=?", (provider,)
                ).fetchall()
            }
            missing = len(local_ids - remote_ids)
            self.conn.execute(
                """INSERT INTO reconciliation_runs
                (provider, seen_count, created_or_updated_count, missing_local_count, ran_at)
                VALUES (?, ?, ?, ?, ?)""",
                (provider, len(remote_ids), len(remote_orders), missing, now()),
            )
        return {"seen": len(remote_ids), "created_or_updated": len(remote_orders), "missing_local": missing}

    def reconcile_pages(self, provider: str, pages: list[dict[str, Any]]) -> dict[str, int]:
        """Flatten provider pages at the adapter boundary, then reconcile once."""
        orders: list[dict[str, Any]] = []
        for page in pages:
            orders.extend(page.get("orders", []))
        return self.reconcile(provider, orders)

    def list_events(self) -> list[dict[str, Any]]:
        with self.lock:
            return [dict(row) for row in self.conn.execute("SELECT * FROM events ORDER BY id").fetchall()]


class Handler(BaseHTTPRequestHandler):
    store: Store

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, sort_keys=True).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._send(200, self.store.health())
        elif path == "/events":
            self._send(200, {"events": self.store.list_events()})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/admin/process":
            self._send(200, self.store.process_pending())
            return
        if path == "/admin/reconcile":
            try:
                body = json.loads(self._body())
                result = self.store.reconcile(body["provider"], body["orders"])
                self._send(200, result)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                self._send(400, {"error": f"invalid_reconciliation: {exc}"})
            return
        if not path.startswith("/webhooks/"):
            self._send(404, {"error": "not_found"})
            return

        provider = path.removeprefix("/webhooks/")
        event_id = self.headers.get("X-Event-ID")
        signature = self.headers.get("X-Webhook-Signature", "")
        raw = self._body()
        expected = hmac.new(WEBHOOK_SECRET.encode(), raw, hashlib.sha256).hexdigest()
        if not event_id:
            self._send(400, {"error": "missing_event_id"})
            return
        if not hmac.compare_digest(signature, expected):
            self._send(401, {"error": "invalid_signature"})
            return
        try:
            payload = json.loads(raw)
            event_type = self.headers.get("X-Event-Type", payload.get("type", "unknown"))
            inserted = self.store.ingest(provider, event_id, event_type, payload)
        except (json.JSONDecodeError, TypeError) as exc:
            self._send(400, {"error": f"invalid_json: {exc}"})
            return
        self._send(200, {"accepted": True, "duplicate": not inserted})

    def log_message(self, fmt: str, *args: Any) -> None:
        # Keep the demo output useful without logging payloads or signatures.
        print(f"{self.address_string()} - {fmt % args}")


def serve(host: str, port: int, db: str) -> None:
    store = Store(db)
    handler = type("LabHandler", (Handler,), {"store": store})
    server = ThreadingHTTPServer((host, port), handler)
    print(f"listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        store.conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("serve", nargs="?", default="serve")
    parser.add_argument("--host", default=os.environ.get("LAB_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("LAB_PORT", "8789")))
    parser.add_argument("--db", default=DB_PATH)
    args = parser.parse_args()
    serve(args.host, args.port, args.db)


if __name__ == "__main__":
    main()
