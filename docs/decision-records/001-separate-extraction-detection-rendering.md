# ADR-001: Separate extraction, detection, rendering, and validation

**Status:** Proposed for interview reference architecture.

## Context

Document Intelligence provides text/layout and provenance [S6](../sources.md#s6---extraction-and-page-geometry). Extraction success neither identifies all race-related references nor removes underlying PDF content. Detection policy and legal exceptions evolve independently of OCR and rendering.

## Decision

Use separate logical stages with versioned contracts: extraction -> sensitive-reference candidates -> permanent-redaction rendering -> independent output validation. Preserve canonical span/page mappings. Start with approved rules/dictionaries plus specialist adjudication; evaluate other detectors without claiming a historical customer technology.

## Alternatives

An end-to-end black-box "redaction AI" hides failure attribution and coordinate provenance. Manual-only redaction has lower integration complexity and remains an exception/fallback, but increases specialist workload. Optional NER/contextual models may broaden detection only after domain evaluation and Government verification.

## Consequences

More contracts and fixtures, but independent testing of OCR, policy, geometry, and integrity. Every stage can explicitly fail/hold. Model upgrades cannot silently change release policy. No claim that exposure reduction proves fairness.

See [architecture](../architecture.md) and [evaluation](../evaluation-and-operations.md).
