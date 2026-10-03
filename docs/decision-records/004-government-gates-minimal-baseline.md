# ADR-004: Government compatibility gates and minimal baseline

**Status:** Proposed for interview reference architecture.

## Context

Government endpoints and feature configurations differ from commercial Azure [S1](../sources.md#s1---government-development-and-availability). The exact region/API/SKU combination has not been verified. Adding optional hosted AI or managed-hosting dependencies expands the verification surface.

## Decision

Propose VM-hosted API/worker, Blob/Table, Service Bus Premium, Document Intelligence, protected monitoring, and Key Vault only when needed. Pin a verified GA extraction combination later. Use Government authority/audience/DNS; keep local rules and human review as detection baseline. No preview, LLM, search index, gateway, or Kubernetes requirement.

## Alternatives

Managed hosting can reduce patching responsibilities if all required Government networking/identity features are confirmed. Hosted NER/contextual models may assist detection after evaluation and availability review. A commercial-cloud fallback is rejected; an approved manual workflow is safer than violating the selected cloud boundary.

## Consequences

VM patching/availability remain customer responsibilities. Service availability must be documented, not assumed. No deployment should proceed until the [readiness gates](../azure-government-verification.md) are satisfied. This decision does not establish what the customer deployed historically.
