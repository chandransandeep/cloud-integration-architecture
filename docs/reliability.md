# Reliability and security

## Failure scenarios

| Failure | Expected production behaviour | Local PoC status |
| --- | --- | --- |
| Crash before DB commit | Roll back order and event | SQLite transaction modeled |
| Crash after DB commit | Event remains pending | Outbox table modeled |
| Duplicate order submission | Return existing order | Order ID check modeled |
| Duplicate event delivery | Do not duplicate fulfilment | Consumer deduplication modeled |
| Broker outage | Retry with backoff, alert on queue age | Not implemented |
| Poison message | Quarantine in DLQ, support replay | Not implemented |
| Multi-worker concurrency | Use transactional claims/locks | Not implemented |
| Lost database | Restore encrypted backups within RTO/RPO | Not implemented |

## Security baseline for production

Authenticated clients, input size limits, TLS, managed identities, encrypted data stores, secret rotation, request rate limits, restrictive outbound networking, PII redaction, audit logs and retention limits are required. The simple PoC deliberately does not pretend to implement these.

## Delivery semantics caveat

Marking an outbox row delivered after handling it is a **single-process illustration only**. In a real system, broker acknowledgment and consumer commit can occur separately, so delivery should be modeled as at least once with idempotent consumers and a replay/reconciliation mechanism.
