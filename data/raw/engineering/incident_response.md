# Incident Response Playbook

## Severity Definition
- SEV-1: Platform outage, data integrity risk, or broad customer impact.
- SEV-2: Degraded core workflows with workaround.
- SEV-3: Limited impact bug.

## Escalation Path
1. On-call engineer acknowledges pager alert within 5 minutes.
2. Incident Commander (IC) is assigned immediately for SEV-1 and SEV-2.
3. IC opens a bridge channel and publishes status updates every 15 minutes.
4. Platform Lead and Security Lead are paged for any SEV-1.
5. Executive escalation starts after 30 minutes of unresolved SEV-1.

## Postmortem
- Publish postmortem in 48 hours.
- Include timeline, root cause, contributing factors, and action items with owners.
