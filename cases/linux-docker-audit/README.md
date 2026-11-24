# Linux and Docker audit

## Problem
A small team runs services on Linux and Docker but does not have a clear view of exposure, health, storage risk or recovery steps.

## First-stage deliverable

- Inventory services and listening ports.
- Review SSH, firewall and container boundaries.
- Check disk pressure, logs and restart behavior.
- Identify backup and monitoring gaps.
- Produce a prioritized report with quick wins and out-of-scope items.

## Evidence

The audit is non-destructive. Findings should include the command or observation that supports each recommendation.

## Run the read-only snapshot

From the repository root, run the helper on the host being assessed:

```bash
bash cases/linux-docker-audit/audit.sh
```

It prints a UTC timestamp and hostname, the first listening sockets reported by `ss`, root filesystem usage from `df`, and the visible Docker containers from `docker ps`. Missing commands or insufficient Docker permissions are reported in the output instead of being treated as a successful inventory. Save the output with the handoff, then redact hostnames, addresses and service names before sharing it publicly.

The helper does not change firewall rules, containers, packages or files. It is an inventory snapshot, not a vulnerability scan or a replacement for reviewing SSH, firewall, Docker and backup configuration.

## Scope control

This case does not promise a full migration, 24/7 operations or changes without a backup and rollback plan.
