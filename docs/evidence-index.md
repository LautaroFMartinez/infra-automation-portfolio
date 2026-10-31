# Evidence index

Use this page to choose the smallest useful starting point and see what can be verified without access to a client system.

## Runnable proofs

- **[Linux/Docker audit](../cases/linux-docker-audit/README.md)** — read-only shell audit for listening sockets, filesystem usage and visible containers. Run `bash cases/linux-docker-audit/audit.sh` on the target host; it does not change system state.
- **[Backup verification](../cases/backup-verification/README.md)** — creates a synthetic archive, checks its SHA-256 and reads every regular-file payload without extracting it. Run the documented temporary-directory example.
- **[Monitoring health check](../cases/monitoring-stack/README.md)** — exercises successful and failed HTTP health responses through the tracked Python tests.
- **[n8n/API payload validation](../cases/n8n-api-automation/README.md)** — validates a mock intake and makes the human-review route explicit. Run `python validate_payload.py mock_payload.json` from that case directory.
- **[E-commerce webhook lab](../cases/ecommerce-webhook-lab/README.md)** — tests signature validation, event deduplication, idempotent processing, transient retries and paginated reconciliation with synthetic data. Run `python -m unittest -v` from that case directory.

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
