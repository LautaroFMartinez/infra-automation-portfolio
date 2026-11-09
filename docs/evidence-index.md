# Evidence index

Use this page to choose the smallest useful starting point and see what can be verified without access to a client system.

## Runnable proofs

Each proof has a short command, a bounded result and a longer case page explaining its production boundary.

- **[Linux/Docker audit](../cases/linux-docker-audit/README.md)** — run `bash cases/linux-docker-audit/audit.sh` on the target host. It reports listening sockets, filesystem usage and visible containers without changing system state; the handoff should attach the command output to each finding.
- **[Backup verification](../cases/backup-verification/README.md)** — run the documented temporary-directory example. It prints the archive checksum, member count and `archive_read=OK`; a mismatch exits non-zero without extracting the archive.
- **[Monitoring health check](../cases/monitoring-stack/README.md)** — run `(cd cases/monitoring-stack && python -m unittest -v test_healthcheck)`. The tracked tests prove both a successful endpoint and a non-zero result for an HTTP error.
- **[n8n/API payload validation](../cases/n8n-api-automation/README.md)** — run `(cd cases/n8n-api-automation && python validate_payload.py mock_payload.json)`. The result reports `Payload valid` and the explicit `human-review` route without credentials or an external API.
- **[E-commerce webhook lab](../cases/ecommerce-webhook-lab/README.md)** — run `(cd cases/ecommerce-webhook-lab && python -m unittest -v)`. The tests cover signatures, deduplication, idempotent processing, transient retries and two-page reconciliation with synthetic data.

## Confirmed operational summaries

- **[Production operations](../cases/production-operations/README.md)** — anonymized summaries of monitoring-agent migration, CI/CD dependency removal, temporary capacity scaling and a RabbitMQ incident. The page states which outcomes are approximate, ongoing or intentionally not claimed.

## Boundaries

These materials are proof layers, not production access or client testimonials. The examples use synthetic or sanitized data, and the public checks avoid credentials and external provider calls. A real engagement still requires discovery, authorization, backups, rollback criteria and provider-specific validation.

## Repository-wide validation

From the repository root:

```bash
bash scripts/check_portfolio.sh
```

The check compiles tracked Python, runs the case tests, exercises backup verification, validates JSON/SVG/Markdown/HTML assets, checks shell and Compose syntax, rejects common secret-file patterns and reports `Portfolio checks: OK` on success.
