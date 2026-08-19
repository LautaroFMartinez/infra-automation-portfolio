# Production operations case studies

These cases are anonymized summaries of real TEC/SIC operational work. They are intentionally written without internal ticket keys, hostnames, IPs, domains, customer names or proprietary identifiers.

## Monitoring-agent migration at scale

### Context

A fleet of production Linux servers was running an agent version approaching end of support. The fleet included messaging, DRM, licensing and backend services, and each host needed to land in the correct group and monitoring template after migration.

### Challenge

A manual replacement could leave hosts unregistered, attached to the wrong metadata or without the expected visibility during a change window.

### Approach

I designed and executed a repeatable runbook that included:

- Pre-change backup of the existing agent configuration.
- Host-by-host inventory of group, templates and metadata.
- A Bash helper to calculate the expected host name from the infrastructure convention.
- Agent package replacement and proxy reconfiguration.
- Validation of autoregistration, group/template assignment and agent logs.
- A rollback procedure for hosts that did not register as expected.

### Outcome

The migration was executed in controlled batches using the same checklist and validation steps across multiple change windows. The runbook reduced manual decisions and made the migration repeatable.

**Technologies:** Linux, Zabbix, Bash, monitoring proxies, Jira change management.

---

## Removing a legacy CI/CD deployment jump host

### Context

Several production deployment pipelines used a legacy SSH jump host as an intermediate step before reaching their runner or target environment.

### Challenge

The host had become a single point of failure and a piece of infrastructure that needed to be retired without leaving hidden pipeline dependencies behind.

### Approach

I mapped the affected jobs, migrated them to run directly from the runner, and validated that no production pipeline still depended on the legacy hop. The retirement was staged:

1. Decouple the known jobs.
2. Shut down the host in a controlled manner.
3. Observe pipeline behavior during a rollback window.
4. Remove the component only after the dependency check remained clean.

### Outcome

The deployment chain no longer depended on the legacy jump host, reducing operational debt and eliminating a single point of failure without a recorded production deployment outage.

**Technologies:** CI/CD, SSH, deployment runners, legacy infrastructure retirement.

---

## Temporary capacity scaling for a high-traffic load test

### Context

A UAT environment needed to run a representative stress test before a high-traffic event. Its standard capacity was not sufficient to model the expected load.

### Challenge

The environment needed additional capacity for the test window, but leaving it oversized afterward would create unnecessary infrastructure cost.

### Approach

I coordinated the temporary vertical scaling of the search/indexing layer and a distributed column-oriented database before the test window. After the stress test, I coordinated the verified scale-down back to the baseline size.

### Outcome

The performance test ran against a capacity level closer to the expected event conditions, while the environment returned to its normal footprint after the window.

**Technologies:** distributed search/indexing, distributed database, cloud capacity planning, change management.

---

## Disk saturation in a production messaging cluster

### Context

Consumers depending on an AMQP messaging cluster stopped processing messages after one cluster node ran out of disk space.

### Investigation and recovery

I identified the affected node, diagnosed the disk saturation and freed enough space to restore the cluster and its dependent workers. A related preventive change reduced log retention and enabled compression in UAT before promotion to production.

The ticket does not establish whether the disk usage was exclusively logs or also persisted queue data, nor does it document message loss or an exact recovery time. Those details are intentionally not claimed here.

**Technologies:** AMQP messaging, Linux, logrotate, infrastructure monitoring.

---

## Challenging a risky process-management fix

### Context

A monitoring alert reported an unusual accumulation of processes on a production Linux middleware server. A proposed fix was to add `wait $!` to a script that intentionally launched work asynchronously.

### Technical assessment

I identified that a blocking `wait` could change the intended asynchronous behavior rather than fix the underlying process/session problem. I proposed investigating inherited SSH/PTY file descriptors and considered a safer separation using `setsid` plus explicit descriptor redirection.

The final root cause and whether the proposal was implemented are not documented in the source material, so this case is presented as a diagnostic review and risk prevention example, not as a claim of a completed production fix.

**Technologies:** Linux process management, SSH/PTY sessions, Bash, `setsid`, root-cause analysis.
