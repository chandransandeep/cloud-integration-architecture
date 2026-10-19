# ADR-0001: Transactional outbox for order events

## Status
Accepted for the fictional integration reference.

## Context
Persisting an order and separately publishing an event can fail halfway, leaving downstream fulfilment unaware of a successful order.

## Decision
Write both order and outbox message in one transaction. Relay pending messages asynchronously. Require consumer idempotency by event identifier.

## Alternatives
- Direct publish after insert: simple but leaves a crash window.
- Two-phase distributed transactions: high complexity and limited portability.
- Transactional outbox: chosen to retain a durable delivery obligation.

## Consequences
Possible duplicate delivery and temporary processing delay. Requires monitoring, relay ownership, replay and event schema/version governance.

## Verification
Unit tests cover atomic outbox creation, duplicate order handling and consumer replay. Broker failure and multi-worker concurrency remain planned future tests.
