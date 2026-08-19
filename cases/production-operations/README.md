# Production operations case studies

These cases are anonymized summaries of real TEC/SIC operational work. They are intentionally written without internal ticket keys, hostnames, IPs, domains, customer names or proprietary identifiers.

## Monitoring-agent migration at scale

### Context

A fleet of production Linux servers was running an agent version approaching end of support. The migration covered messaging, DRM, licensing and backend services, and each host needed to land in the correct group and monitoring template after the change.

### Challenge

A manual replacement could leave hosts unregistered, attached to the wrong metadata or without monitoring visibility during the migration window.

### Approach

I designed and executed a repeatable runbook that included:

- Pre-change backup of the existing agent configuration.
- Host-by-host inventory of group, templates and metadata.
- A Bash helper to calculate the expected host name from the infrastructure convention.
- Agent package replacement and proxy reconfiguration.
- Validation of autoregistration, group/template assignment and agent logs.
- A rollback procedure for hosts that did not register as expected.

### Outcome

I migrated approximately **50 hosts** across controlled batches and multiple change windows. No rollback was required, and no host lost monitoring visibility for more than approximately **two minutes** during the migration.

**Technologies:** Linux, Zabbix, Bash, monitoring proxies, Jira change management.

---

## Removing a legacy CI/CD deployment jump host

### Context

Several production deployment jobs used a legacy SSH jump host as an intermediate step before reaching their runner or target environment.

### Challenge

The host had become a single point of failure and a piece of infrastructure that needed to be retired without leaving hidden pipeline dependencies behind.

### Approach

I mapped the affected jobs, migrated them to run directly from the runner, and validated that the known production jobs no longer depended on the legacy hop. The retirement was staged:

1. Decouple the affected jobs.
2. Shut down the host in a controlled manner.
3. Observe pipeline behavior during a rollback window.
4. Remove the component only after the dependency check remained clean.

### Current outcome

Approximately **15–20 jobs** have been migrated so far. The work is still in progress, so the final retirement of the legacy host is intentionally not claimed here.

**Technologies:** CI/CD, SSH, deployment runners, legacy infrastructure retirement.

---

## Temporary capacity scaling for a high-traffic load test

### Context

A UAT environment needed to run a representative stress test before a high-traffic event. Its standard capacity was not sufficient to model the expected load.

### Challenge

The environment needed additional capacity for the test window, but leaving it oversized afterward would create unnecessary infrastructure cost.

### Approach

I coordinated the temporary vertical scaling of the search/indexing layer and a distributed column-oriented database. Capacity was increased to **twice the baseline** for the test window and then returned to the normal footprint afterward.

The stress test measured the relevant operational signals, including:

- CPU consumption.
- Memory consumption.
- Latency.
- Error rate.
- Throughput.
- Cache behavior.
- Overall service behavior under load.

### Outcome

The stress test passed without issues. The temporary scaling provided a representative capacity profile for the expected event while avoiding permanent overprovisioning after the test window.

**Technologies:** distributed search/indexing, distributed database, cloud capacity planning, performance testing, change management.

---

## Disk and memory pressure in a production RabbitMQ cluster

### Context

Consumers connected to a production RabbitMQ cluster were processing messages too slowly. The backlog increased and the affected node accumulated resource pressure.

### Incident

The backlog contributed to message loss and created a risk that the machine would exhaust its available resources. Resolution also depended on another team, which extended the time needed to close the incident.

### Response

I investigated the affected RabbitMQ component, coordinated the recovery and stopped the affected component before the machine reached a more severe resource-exhaustion condition. The exact component that was stopped and the precise recovery time are intentionally left for confirmation rather than inferred from the ticket summary.

### Prevention

The related log-rotation change was promoted successfully to production, reducing the risk of log growth contributing to a recurrence.

**Technologies:** RabbitMQ/AMQP, Linux, consumers, resource monitoring, logrotate, incident coordination.

---

## Publication notes

- These cases describe real operational work but remain intentionally anonymized.
- The CI/CD case is ongoing and does not claim final host retirement.
- The RabbitMQ case does not claim an exact recovery time or identify which component was stopped.
- No customer names, internal identifiers, hostnames, IPs, domains or proprietary configuration are included.
