# Synthetic illustrative examples

**All content is invented. No customer documents, identifiers, outcomes, or processing results are included.** These files are hand-authored illustrations, not Document Intelligence responses or outputs of a functioning redaction pipeline.

| File | Meaning |
| --- | --- |
| [synthetic-input.md](synthetic-input.md) | Invented narrative and the exact canonical text used by the manifest |
| [illustrative-output.md](illustrative-output.md) | Hand-authored text derivative showing one proposed removal |
| [illustrative-manifest.json](illustrative-manifest.json) | Example restricted provenance/candidate shape, with invented coordinates and placeholders |
| [evaluation-fixtures.md](evaluation-fixtures.md) | Synthetic test scenarios and expected review/integrity behavior |

For this example only, a fictional policy removes an explicit race reference and retains a fictional location as event context. This is **not a universal legal redaction rule**. No race is inferred from the location. Real domain owners would decide proxy treatment and materially necessary exceptions.

The manifest has one zero-based Unicode-code-point span over its exact `canonicalText`. Coordinates are invented in inches and have not been mapped to a real PDF. Hashes/API/model/renderer IDs are intentionally placeholders, not fake evidence.

The output is Markdown text, **not a sanitized PDF**, and cannot demonstrate permanent PDF redaction. Required PDF tests are in [architecture](../docs/architecture.md#separate-rendering-and-output-integrity-stage). In a real system the manifest's removed text and original provenance would be restricted; only approved derivative-safe metadata would accompany delivery.
