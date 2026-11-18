# Monitoring and alerting

## Problem
Small deployments often discover outages only after a user reports them.

## Demonstration

- Collect host and container metrics.
- Track CPU, memory, disk space, I/O and service health.
- Add custom checks for backups and storage health.
- Route actionable alerts to a notification channel.
- Preserve enough logs to investigate restarts and failures.

## Success criteria

The owner can see what is running, receive a useful alert and follow documented next steps.

## Run the health-check proof

The tracked helper uses only Python's standard library and returns a non-zero exit code when the endpoint is unhealthy:

```bash
cd cases/monitoring-stack
python -m unittest -v test_healthcheck
```

The tests start a local synthetic HTTP server and verify both sides of the contract: a `204` response produces `health=OK` and exit code `0`, while a `503` response produces `health=FAIL` and exit code `1`. To check a real endpoint directly:

```bash
python healthcheck.py https://example.internal/health
```

Use the exit code as the input to the scheduler or alerting system; keep authentication, timeout policy and notification routing outside this small probe.

## Scope control

Dashboards are not a substitute for an incident plan. The first stage focuses on visibility and actionable alerts, not a large observability platform.
