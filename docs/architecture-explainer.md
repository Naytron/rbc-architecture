# Architecture explainer: decisions, rationale, and likely follow-ups

This document is the "defend the design" companion to [`docs/interview-guide.md`](interview-guide.md). The interview guide gives you a story and a Q&A table; this document goes one level deeper into **why each major decision was made, what was rejected, and the sharpest follow-up question an interviewer is likely to ask about it.** It synthesizes [`docs/architecture.md`](architecture.md) and the four [decision records](decision-records/) — it does not introduce new technical claims beyond what those documents already establish.

As with the rest of this repository: every decision below is a **proposed reference-architecture choice**, not a description of what the customer actually built. see [`README.md`](../README.md#facts-versus-proposed-decisions-versus-memory-questions) for the boundary between confirmed facts and proposal.

## How to use this document in an interview

Read a decision's **"Why"** and **"Rejected alternatives"** before the interview so you can state the tradeoff in one or two sentences without reading notes. Keep the **"Sharpest follow-up"** in mind — if you can answer that one well, you can usually handle variations of it. If you are asked something this document does not cover, it is more credible to say "I'd want to verify that" than to improvise a new technical claim.

---

## Decision 1 — Four separate stages instead of one "redaction AI" ([ADR-001](decision-records/001-separate-extraction-detection-rendering.md))

**Why:** Document Intelligence gives you text, layout, and coordinate provenance [S6](sources.md#s6---extraction-and-page-geometry) — it does not decide what is sensitive, and it does not remove anything from a PDF. Those are two more decisions, each with its own failure mode: detection can miss a reference or over-match; rendering can fail to actually strip content even when detection was correct. Collapsing all of this into one black-box step would make failures impossible to attribute and impossible to test independently.

**Rejected alternatives:** A single end-to-end "AI redacts the document" service looks simpler on a slide but hides exactly the failure you most need to see (did OCR miss a word, or did detection miss a known word, or did rendering fail to remove it?). Manual-only redaction remains a valid fallback/exception path, not a replacement for automation — it has lower integration complexity but higher specialist workload.

**Sharpest follow-up:** *"Doesn't adding stages just add complexity and latency?"* Answer: it adds contracts and fixtures, not necessarily wall-clock time, and it lets you hold a document at the exact stage that failed instead of either releasing it wrongly or discarding good extraction work. The demo's `pipeline.py` keeps these as four literal named functions (`extract_layout`, `detect_candidates`, `render_and_validate`, quarantine upload) specifically so this separation is concrete, not just conceptual.

## Decision 2 — Detection is rules/dictionaries plus human review, not an LLM ([ADR-001](decision-records/001-separate-extraction-detection-rendering.md), [architecture.md](architecture.md))

**Why:** A versioned, explainable rule or dictionary can be unit-tested, reviewed by a domain owner, and reasoned about when it misses something. A contextual/LLM-based detector could broaden coverage (e.g., catching paraphrased or indirect references) but introduces availability, grounding, and prompt-injection surface that must be evaluated before it is trusted on legally consequential documents — and it is not what this repository claims the customer used.

**Rejected alternatives:** Pure keyword matching alone is the known-weakest option (this repository's own demo uses it, labeled explicitly as illustrative, precisely to show its limits). An LLM-first approach was not rejected outright — it is positioned as a later, evaluated option, not a baseline, because it raises the evaluation and governance bar significantly for a system touching charging review.

**Sharpest follow-up:** *"Would you ever use an LLM here?"* Answer: possibly, after evaluation — but not as the baseline, and never as the sole decision-maker. It would still feed the same "candidate" contract that any other detector feeds, so swapping detectors does not change the rest of the pipeline.

## Decision 3 — Explicit identifiers vs. indirect proxies are treated as different problems (architecture.md)

**Why:** "Black," "Hispanic," and similar explicit terms are tractable for a dictionary. Indirect proxies — a neighborhood name, a nickname, a culturally coded phrase — are not reliably catchable by the same technique and require separate domain review to even define scope. Conflating the two in one requirement risks either under-promising (dictionary "solves" the explicit case and nothing else is attempted) or over-promising (claiming the system handles "all bias" when it only catches explicit terms).

**Rejected alternatives:** Treating all sensitive references as one undifferentiated detection problem was rejected because it invites exactly the over-claiming this repository is trying to avoid — redacting explicit race terms does not redact every proxy for race, and saying otherwise would misrepresent what the design does.

**Sharpest follow-up:** *"Does removing race references eliminate bias in charging review?"* Answer: no — explicitly reject this framing. The system reduces exposure to explicit identifiers; proxies, prior knowledge, and other bias sources are a separate, larger problem that this design does not claim to solve.

## Decision 4 — PDF redaction means permanent content removal, not a drawn box ([architecture.md](architecture.md), [S15](sources.md#s15---pymupdf-redaction-and-document-scrubbing))

**Why:** A black rectangle drawn over text in a PDF viewer does not remove the underlying text object — copy-paste or a different viewer can still expose it. A real redaction step must remove the content object itself, then also address metadata, hidden/invisible text layers, embedded files, and JavaScript that could retain or regenerate sensitive content, and then independently re-extract the output to confirm the matched text is actually gone.

**Rejected alternatives:** Visual-only masking (image overlay or black box annotation without content removal) was rejected as insufficient for any document that might be copied, re-OCR'd, or opened in a different tool. Converting every page to a flattened image before redacting is a theoretically safer but heavier alternative, discussed in architecture.md as a tradeoff (loses selectable text/accessibility) rather than adopted outright.

**Sharpest follow-up:** *"How do you know the redaction actually worked?"* Answer: an independent validation pass — re-open the rendered output and confirm the matched text no longer appears in extractable text — not just trusting that the removal step ran without error. The demo's `render_and_validate()` does exactly this and reports pass/fail in a manifest; see [`demo/pipeline.py`](../demo/pipeline.py).

## Decision 5 — Originals, derivatives, and human release are three separate trust zones ([ADR-003](decision-records/003-originals-derivatives-human-release.md))

**Why:** A charging reviewer should never inherit original-document access rights just because a derivative failed or was unavailable — that would silently defeat the entire purpose of the system. Keeping protected originals, quarantined candidate derivatives, and approved/released derivatives as separate access-controlled zones means a failure in one zone cannot leak into another.

**Rejected alternatives:** One storage account with scoped containers (which is what the low-cost demo actually uses, see [`docs/demo-setup.md`](demo-setup.md)) reduces resource count but weakens operational isolation between the three zones — acceptable for a single-operator demo, explicitly rejected for production. Automatic release without human approval was rejected because it requires its own risk-based evidence this design does not yet have.

**Sharpest follow-up:** *"What happens if the redacted version isn't ready — does the reviewer see the original?"* Answer: no — that document is held/exception-routed, not silently substituted. This is the core design invariant, and it is worth stating plainly because it is the question most likely to expose a hand-wavy design.

## Decision 6 — Durable asynchronous processing with idempotency, not request/response ([ADR-002](decision-records/002-durable-asynchronous-processing.md))

**Why:** Extraction is long-running and document size varies; a synchronous request couples client availability to processing time and risks lost work if a connection drops mid-analysis. Persisting job state before returning "accepted," then dispatching through a durable queue with checkpoints and bounded retries, means a dropped connection does not silently lose a document.

**Rejected alternatives:** A fully synchronous design was rejected for anything beyond a one-document demo. Promising "exactly-once" processing was explicitly rejected as a false guarantee — the design targets at-least-once delivery with idempotent, version-bound approval instead, because queue deduplication alone cannot supply true exactly-once execution across an external API call.

**Sharpest follow-up:** *"Can a document get processed twice?"* Answer: possibly, at the extraction-call level (if submission status was uncertain), but duplicate *publication/release* is prevented by scoping idempotency to case/source/profile and binding approval to an exact artifact hash/version — so a repeat extraction cannot cause a repeat release.

## Decision 7 — Service Bus Premium in the proposal, Storage Queue in the demo ([ADR-002](decision-records/002-durable-asynchronous-processing.md), [demo-setup.md](demo-setup.md))

**Why:** Service Bus private endpoints require the Premium tier [S9](sources.md#s9---service-bus-private-networking), and the proposed architecture assumes private connectivity is required for a system handling charging-review documents. The low-cost demo substitutes the Storage Queue that ships for free with the storage account, because a single-operator demo with no private-networking requirement does not need Premium's cost or features.

**Rejected alternatives:** Using Storage Queue in production was not rejected outright — it is named in ADR-002 as "a conservative candidate if Premium is unavailable," but it needs its own poison-message handling and lease/recovery design that has not been specified here.

**Sharpest follow-up:** *"Why not just use Storage Queue everywhere and save the cost?"* Answer: it's a legitimate option if private endpoints aren't required and you build the poison/lease handling yourself — the demo does exactly this to save cost, explicitly labeled as a simplification, not a universal recommendation.

## Decision 8 — User case authorization is separate from worker service identity (security-and-governance.md, [S4](sources.md#s4---document-intelligence-authentication))

**Why:** A charging reviewer's permission to view a specific case's approved derivatives is a different authorization question from whether a backend worker process is allowed to call Document Intelligence or write to a storage container. Conflating them (e.g., giving the worker a human's broad permissions, or giving a reviewer direct access to backend service credentials) breaks least privilege in both directions.

**Rejected alternatives:** Using one shared identity for both humans and services was rejected for production. The low-cost demo deliberately does this anyway (your own `az login` identity plays both roles) because a one-person demo has no second identity to separate — this is called out explicitly in [`demo/README.md`](../demo/README.md) as a simplification, not a recommendation.

**Sharpest follow-up:** *"Why does the demo use your own identity for everything, if that's wrong for production?"* Answer: because the demo's purpose is proving the pipeline logic works, not proving identity separation — and pretending otherwise would be dishonest about what was actually built. A managed identity would replace the user identity for the worker role in any multi-user deployment.

## Decision 9 — Azure Government compatibility is a gate you check, not an assumption ([ADR-004](decision-records/004-government-gates-minimal-baseline.md), [azure-government-verification.md](azure-government-verification.md))

**Why:** Azure Government is a separate cloud instance from commercial Azure with its own authority, endpoints, and — in some cases — different feature/region/SKU availability [S1](sources.md#s1---government-development-and-availability). Assuming commercial feature parity in a Government design is a common and risky mistake. The proposed architecture therefore keeps a minimal baseline (VM-hosted API/worker, Blob/Table, Service Bus Premium, Document Intelligence, Key Vault only if needed) and defers anything not yet verified (specific region/API/SKU combination) to an explicit readiness-gate document rather than assuming it will "just work."

**Rejected alternatives:** Adding optional dependencies (managed hosting platforms, hosted NER models, search indexes, gateways, Kubernetes) was rejected for the baseline because each one expands the Government-verification surface without being necessary to prove the core design. A commercial-cloud fallback when a Government service or feature is unavailable was explicitly rejected — crossing the cloud boundary defeats the reason for choosing Government in the first place; an approved manual process is the safer fallback.

**Sharpest follow-up:** *"Why not use [commercial-only feature X] since it would be so much easier?"* Answer: because the design does not assume commercial Azure feature parity in Government, and introducing a dependency that turns out to be commercial-only would either block deployment or silently break the chosen cloud boundary. This is exactly why the low-cost demo runs in commercial Azure and says so loudly — it validates pipeline logic, not Government compatibility.

---

## If asked "which of these did the customer actually build?"

None of the above decisions are claimed as historical fact. The confirmed engagement facts are limited to three areas — see [`README.md`](../README.md) and [`docs/open-questions.md`](open-questions.md) for the exact boundary. Everything above is this repository's proposed reference architecture, presented as a defendable design with explicit tradeoffs, not a reconstruction of what was deployed.
