# Proposed architecture diagrams

All four diagrams depict a **proposed reference architecture**, not a recovered customer deployment. Each is embedded in [architecture.md](../docs/architecture.md) and supplied as a standalone source:

| Source | Diagram |
| --- | --- |
| [system-context.mmd](system-context.mmd) | System context and trust boundaries |
| [processing-sequence.mmd](processing-sequence.mmd) | End-to-end processing sequence |
| [human-review.mmd](human-review.mmd) | Human review and exception workflow |
| [government-topology.mmd](government-topology.mmd) | Proposed Government deployment topology |

## Local SVG rendering

No SVG exports were generated. No local Mermaid CLI/browser renderer was available in this environment. Syntax parsing was performed separately; it does not validate visual layout.

On a workstation with Node.js and a compatible local headless browser, select an approved version of `@mermaid-js/mermaid-cli`, install it locally, and record the version used. Then, from the repository root:

```sh
mmdc -i diagrams/system-context.mmd -o diagrams/system-context.svg
mmdc -i diagrams/processing-sequence.mmd -o diagrams/processing-sequence.svg
mmdc -i diagrams/human-review.mmd -o diagrams/human-review.svg
mmdc -i diagrams/government-topology.mmd -o diagrams/government-topology.svg
```

Renderer exit status validates Mermaid parsing; inspect every export for clipped labels, unreadable text, and misleading boundaries. Keep embedded sources synchronized with standalone sources. Local rendering is preferred; do not send sensitive future diagrams to public rendering services.

## Validation status

`python3 scripts/check_docs.py` checks local Markdown targets/heading anchors, JSON parsing and illustrative span consistency, fenced-block balance, and exact correspondence between embedded and standalone Mermaid. It does **not** parse Mermaid grammar, validate product availability, render SVG, or prove PDF redaction integrity.

All four standalone sources passed local `mermaid.parse` using **Mermaid 11.17.2** on **2026-10-03**, with a temporary isolated Node.js/jsdom environment. The consistency check confirms that embedded copies match those parsed sources. These parser dependencies are not repository or application dependencies.

SVG rendering and visual inspection remain pending on a renderer-equipped workstation. External product links are source references, not a promise that their contents remain unchanged. Refresh the dated Government verification register when preparing an implementation.
