# ADR-002: Durable asynchronous jobs and idempotency

**Status:** Proposed for interview reference architecture.

## Context

Extraction is long-running, documents vary in size, and remote submission may succeed even when a response is lost. Upload requests should not wait for analysis, rendering, and human approval.

## Decision

Persist original and job state before returning acceptance. Dispatch via a ledger/outbox reconciler. Use Service Bus Premium with opaque references, stage checkpoints, leases/conditional updates, bounded retries, and explicit held/failed states. Application idempotency is scoped to case/source/profile; approval references an exact artifact hash/version.

Service Bus private endpoints require Premium [S9](../sources.md#s9---service-bus-private-networking); Government region/capacity remain gated.

## Alternatives

Synchronous requests simplify a prototype but couple availability and latency to processing. Storage Queue is a conservative candidate if Premium is unavailable, but needs explicit poison handling and a revised lease/recovery design. Queue deduplication alone cannot supply end-to-end exactly-once execution.

## Consequences

Control-state reconciliation and replay runbooks are necessary. Delivery is at least once; extraction can repeat after uncertain submission. Prevent duplicate publication rather than promising no duplicate external calls. Reprocess only with authorization and retained lineage.

See [operations](../evaluation-and-operations.md).
