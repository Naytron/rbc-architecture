# Executive summary (for interview use)

This is the short, non-technical version of this repository — written to be **spoken from memory**, not read aloud. Use [`docs/interview-guide.md`](interview-guide.md) for the technical whiteboard walkthrough and [`docs/architecture-explainer.md`](architecture-explainer.md) for decision-by-decision technical rationale. This document is the layer above both: what you'd say to a hiring manager or non-technical panel member before going deep.

As with the rest of this repository, keep the three categories separate when you speak: **what I actually did**, **what I'm proposing now**, and **what I don't know**. See [`README.md`](../README.md#facts-versus-proposed-decisions-versus-memory-questions) for the full boundary.

## 30-second version

> "At Microsoft, I worked with a large district attorney's office that wanted to reduce reviewers' unconscious bias risk when deciding charges — specifically, their exposure to race-identifying details in police reports. I contributed three things: the Azure Government authentication design, the API-based document ingestion using Azure Document Intelligence, and the redaction workflow that produced the reviewer-facing output.
>
> Since then I've built out a full reference architecture showing how I'd design and defend this today — covering secure ingestion, extraction, detection, redaction, human review, and governance in Azure Government — plus a working low-cost demo to prove the pipeline logic actually holds up."

## 2-minute version (if asked for more)

> "The customer's goal was narrow and important: charging reviewers shouldn't see a defendant's race in the narrative text before they decide what to charge — because that's a known bias vector. This isn't sentencing automation and it doesn't decide guilt; it's an assistive step before a human makes a legal decision.
>
> My piece was getting documents in securely — Azure Government has its own identity and endpoint model, different from commercial Azure — then extracting text and layout with Document Intelligence, and handling the redaction step that produced the output reviewers actually saw.
>
> What I've done since is take that experience and build a complete, defendable reference architecture: separating extraction from detection from redaction (so failures are traceable), keeping protected originals separate from redacted derivatives, requiring human review before release, and mapping it to Azure Government's actual constraints rather than assuming commercial Azure feature parity. I also stood up a low-cost version in my own subscription to validate the core logic end-to-end."

## Anticipated executive-level questions

| Question | Answer |
| --- | --- |
| What business problem did this solve? | Reduced a known bias input (race-identifying narrative text) from the charging-review process, without automating or replacing the human legal decision. |
| Did this eliminate bias? | No — and I'm careful not to claim that. It removes one explicit input; indirect proxies (neighborhood, name, etc.) are a separate, harder problem not solved here. |
| What exactly did you build vs. design after the fact? | I'm explicit about the line: confirmed work was auth design, ingestion/processing via Document Intelligence, and the redaction workflow/output. The deeper architecture, security model, and demo are my proposed design for the role — not a claim about what the customer historically built. |
| Was it successful? What were the metrics? | No measured outcomes are established from that engagement, and I don't invent numbers. I do propose how I'd *measure* success going forward — missed redactions, over-redaction, review workload, latency. |
| Why Azure Government instead of commercial Azure? | The customer required it for data residency/compliance. It has a separate identity authority, endpoints, and sometimes different feature availability — which is exactly why I don't assume commercial parity anywhere in the design. |
| Why not just use an LLM to do all of this? | Rules/dictionaries plus human review are explainable and testable from day one; an LLM could broaden detection later but adds evaluation, availability, and governance overhead that's not justified as the starting point for something feeding legal decisions. |
| What's the biggest risk in this design? | Silent failure — a document getting released without being properly redacted. That's why the architecture forces a hold-and-review state instead of ever falling back to showing the original. |
| Why should we care about this for this role? | It shows I can work inside a highly regulated cloud, translate a vague customer intent ("reduce bias exposure") into a concrete, defensible technical design, and be disciplined about separating fact from proposal — which matters a lot in sensitive-domain AI work. |

## Where to go deeper

- Technical whiteboard walkthrough and a longer Q&A table: [`docs/interview-guide.md`](interview-guide.md)
- Decision-by-decision rationale and rejected alternatives: [`docs/architecture-explainer.md`](architecture-explainer.md)
- Full architecture, data flows, and trust boundaries: [`docs/architecture.md`](architecture.md)
- Run it yourself in a low-cost commercial Azure subscription: [`docs/demo-setup.md`](demo-setup.md)
