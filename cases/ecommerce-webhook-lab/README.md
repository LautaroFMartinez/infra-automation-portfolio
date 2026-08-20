# E-commerce webhook reliability lab

A small, dependency-free laboratory for the part of e-commerce integrations that is usually underestimated: receiving provider events safely, deduplicating them, processing them outside the HTTP request, retrying transient failures and reconciling remote state.

This is a **synthetic demonstration**, not a connection to Mercado Libre, Tiendanube, Shopify, Stripe, PayPal or Revolut. It contains no credentials, customer data or real webhook payloads.

## What it demonstrates

```text
provider webhook
      ↓
signature validation + event ID
      ↓
SQLite raw-event inbox with unique deduplication key
      ↓
separate processing step
      ↓
idempotent normalized order upsert
      ↓
retry/dead-letter status
      ↓
explicit reconciliation against a paginated-style fixture
```

Implemented safeguards:

- HMAC signature validation before parsing/processing.
- Stable `(provider, event_id)` deduplication.
- Raw payload hash for auditability without logging payloads.
- Fast receiver: ingestion and persistence are separate from processing.
- Idempotent order upsert by `(provider, external_id)`.
- Transient failure → retry state; malformed payload → failed state.
- Reconciliation reports remote items and local items missing remotely.
- SQLite WAL mode and a small health endpoint.

## Run locally

Requires Python 3.11+ and no external packages.

```bash
cd cases/ecommerce-webhook-lab
python -m unittest -v
python app.py --db /tmp/ecommerce-webhook-lab.sqlite3
```

In another terminal, create a signed synthetic event:

```bash
BODY='{"id":"order-1001","status":"paid","amount":"125.00","currency":"USD"}'
SIGNATURE=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac 'demo-secret' -r | cut -d' ' -f1)
curl -i http://127.0.0.1:8789/webhooks/stripe \
  -H 'Content-Type: application/json' \
  -H 'X-Event-ID: evt-demo-1001' \
  -H 'X-Event-Type: order.created' \
  -H "X-Webhook-Signature: $SIGNATURE" \
  --data "$BODY"

# Send the same event again: it is acknowledged but not inserted twice.
curl -s http://127.0.0.1:8789/webhooks/stripe \
  -H 'Content-Type: application/json' \
  -H 'X-Event-ID: evt-demo-1001' \
  -H 'X-Event-Type: order.created' \
  -H "X-Webhook-Signature: $SIGNATURE" \
  --data "$BODY"

# Process the persisted inbox separately.
curl -s -X POST http://127.0.0.1:8789/admin/process
curl -s http://127.0.0.1:8789/health
```

The lab intentionally uses the same HMAC shape for every provider only to demonstrate the pattern. Real integrations must implement each provider's exact signature, header, timestamp tolerance and event semantics.

## Reconciliation example

```bash
curl -s -X POST http://127.0.0.1:8789/admin/reconcile \
  -H 'Content-Type: application/json' \
  --data '{"provider":"shopify","orders":[{"id":"order-1001","status":"paid"},{"id":"order-1002","status":"shipped"}]}'
```

A real adapter would fetch all pages from the provider using its cursor/offset rules, collect each page at the adapter boundary and then call the same reconciliation boundary. The unit tests include a two-page synthetic example.

## Docker Compose

```bash
cd cases/ecommerce-webhook-lab
WEBHOOK_SECRET='replace-me-locally' docker compose up --build
```

The example binds to loopback by default. Do not expose it publicly without HTTPS, provider-specific signature verification, authentication for administrative endpoints and a durable queue/worker.

## Production boundary

This lab is deliberately small. A production implementation still needs:

- provider-specific adapters and signature verification;
- a durable queue or outbox and worker supervision;
- retry backoff with jitter and maximum attempts;
- dead-letter storage and safe replay authorization;
- tenant isolation and encrypted credentials;
- provider-specific API versioning and rate-limit handling;
- metrics, alerting and retention rules;
- contract tests against sandbox/dev stores;
- explicit handling for refunds, cancellations, payment state and fulfillment;
- authentication and authorization on admin/reconciliation endpoints.

The point of the case is to make those boundaries visible instead of pretending that a single `POST` completes an integration.
