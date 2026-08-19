# Technical Infrastructure & Automation Portfolio

Small, verifiable examples of Linux, Docker, backups, monitoring and workflow automation.

## What this demonstrates

- Diagnosing infrastructure from evidence instead of guesswork.
- Deploying Docker services with safer defaults.
- Verifying that backups can actually be decrypted and listed.
- Monitoring containers, disk health and service availability.
- Building small n8n/API workflows with validation and human review.
- Making the workflow observable and recoverable: [architecture diagram](docs/automation-architecture.svg).

The repository also includes a lightweight GitHub Actions check that compiles the Python examples, validates JSON, checks shell syntax and rejects common secret-file patterns.

These are sanitized demonstrations and laboratory work. They are not presented as client testimonials or production credentials.

## Cases

- [Linux and Docker audit](cases/linux-docker-audit/README.md)
- [Backup verification](cases/backup-verification/README.md)
- [Monitoring and alerting](cases/monitoring-stack/README.md)
- [n8n and API automation](cases/n8n-api-automation/README.md)

## Delivery principles

- Scope a small first stage.
- Back up state before risky changes.
- Keep secrets out of repositories.
- Add logs, health checks and rollback notes.
- Verify the result with reproducible evidence.
