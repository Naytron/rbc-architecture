# ADR-003: Protected originals, separated derivatives, human release

**Status:** Proposed for interview reference architecture.

## Context

Originals can contain evidence and sensitive references. Derivatives can still leak through hidden content, proxies, or incorrect removals. A charging reviewer should not inherit original-access rights merely because a derivative fails.

## Decision

Use separate original, derivative, and control storage accounts. Keep candidates quarantined. Require independent integrity validation and specialist approval of each exact version before case-authorized delivery. Restrict text-bearing provenance; preserve original evidentiary records under approved policy.

## Alternatives

One account with scoped containers reduces resources but weakens operational isolation. Automatic release could reduce workload but requires a separate risk-based decision and evidence. Automatically falling back to originals defeats the exposure goal and is rejected.

## Consequences

Specialists need privileged access and time; approval backlog is operationally meaningful. Hashes/version lineage support traceability but do not replace legal chain of custody. Human approval does not guarantee no missed references or fairness.

See [security/governance](../security-and-governance.md) and [evaluation](../evaluation-and-operations.md).
