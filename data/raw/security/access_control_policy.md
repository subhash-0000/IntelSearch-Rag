# Access Control Policy

All production systems must enforce least privilege and short-lived credentials.

## Joiner process
New engineers are provisioned read-only access by default.
Elevated production permissions require manager approval and security review.

## Break-glass access
Emergency break-glass access is allowed only for active incidents.
Access expires automatically after 60 minutes and is fully audited.
A follow-up security review is required within one business day.

## Offboarding
User accounts must be disabled within 30 minutes of termination notice.
Credential rotation for shared service accounts must occur within 24 hours.
