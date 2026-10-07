# Interview guide

Use the first-person statements below only within the confirmed contribution boundary. Architecture answers are deliberately future/proposal language.

## 90-second story

> While working at Microsoft, I helped a large district attorney's office with an Azure Government document-processing engagement. The goal was to reduce charging reviewers' exposure to race-identifying information in police reports and supporting documents.
>
> My confirmed contributions were authentication design into Azure Government, API-based document ingestion and processing using Azure Document Intelligence, and the redaction workflow and resulting output. I would not claim the exact identity flow, detection technology, output format, production maturity, or measured outcomes without recovering those details.
>
> For a reference architecture today, I would separate four concerns: authorized ingestion, text and layout extraction, sensitive-reference detection, and permanent redaction with output validation. Document Intelligence handles extraction; it is not the entire redaction solution.
>
> I would process documents asynchronously, preserve originals separately, use page and coordinate provenance to map removals, and hold uncertain or failed documents for authorized human review. Charging reviewers would receive only approved derivatives through case-level authorization.
>
> The key design tension is reducing exposure without removing legally important context. I would have domain owners approve the policy and evaluate missed references, over-redaction, output integrity, and review workload. This assists charging review; it does not recommend charges, determine guilt, automate sentencing, or prove that bias has been eliminated.

## Whiteboard walkthrough

Use this when asked to "walk me through the architecture" at a whiteboard. It mirrors the four diagrams in [`diagrams/`](../diagrams/README.md) exactly, so what you sketch live stays consistent with what's checked into the repository.

### Sketch 1 — System context (~60 seconds)

1. Draw a **big dashed box** on the right, label it **"Azure Government — PROPOSED."** Say: *"Everything in this box is a proposal, not a claim about what was historically built."*
2. Draw a **smaller box** on the left labeled **"Office."** Inside it, just write four labels (no detail yet): *Source documents, Document steward, Charging reviewer, Redaction specialist.*
3. Draw one box inside the Gov boundary: **"Ingestion / Review API."** Arrow from *Steward* -> API. Say: *"Nothing enters except through this API, authenticated against Government Entra."*
4. Draw a small box above the API: **"Government Entra ID,"** dotted arrow into API. Say: *"Separate identity authority from commercial Azure — different login endpoint, different tokens."*
5. From the API, draw two arrows down into: **"Protected Originals"** and **"Pipeline (Extract -> Detect -> Render -> Validate)."** Arrow from Originals into Pipeline too.
6. From Pipeline, one arrow labeled **"candidate only"** -> **"Approved Derivatives."** Say out loud: *"Nothing here is automatic — 'candidate' means not yet released."*
7. Arrow from Derivatives back to API. Then draw *Reviewer* -> API labeled **"case-scoped access,"** and *Specialist* -> API labeled **"privileged review."**
8. Last box, off to the side: **"Restricted Audit."** Dotted arrows in from API and Pipeline, labeled **"content-free signals."** Say: *"Audit logs what happened, never the sensitive content itself."*

### Sketch 2 — Zoom into the Pipeline box (~45 seconds)

Erase/circle the Pipeline box and redraw it bigger as four boxes in a row:

**Extract -> Detect -> Render/Validate -> Hold or Publish**

- Under **Extract**: *"Document Intelligence — text, layout, coordinates. Not redaction itself."*
- Under **Detect**: *"Separate stage — rules/dictionary today, evaluated models later. Finds candidate spans."*
- Under **Render/Validate**: *"Permanently removes content, strips metadata, then re-checks the output — not a drawn box."*
- Draw a **diamond** after this labeled *"Passed?"* -> No goes to a **"Hold / Exception"** box; Yes goes to a **"Human approves?"** diamond -> No loops back to Hold; Yes -> **"Publish to reviewer."**
- Say: *"Three ways to fail safe: bad extraction, failed validation, or no human sign-off — all three hold the document instead of releasing it."*

### Sketch 3 — Processing sequence (optional, only if asked "how does this actually run")

Draw a simple left-to-right timeline: **User -> API (202 Accepted) -> Queue -> Worker -> Document Intelligence -> back to Worker -> Store.**
Say: *"The API returns immediately — it doesn't wait for analysis. Everything after that is asynchronous with retries, so a dropped connection never loses a document."*

### The one sentence to say while drawing nothing

*"Three boundaries matter more than any box: identity, where originals live versus derivatives, and the human gate before release — everything else is detail."*

### Condensed order (if short on time)

1. **Draw the boundary:** office/source -> Government API -> original/derivative stores. State that the source product and historical topology are unknown. Write "PROPOSED" above the design.
2. **Separate identity and permission:** Government authority/custom audience; user case authorization versus worker service identity. Show original access as a distinct privilege.
3. **Draw asynchronous work:** API acceptance -> durable ledger/outbox -> queue -> worker. Explain at-least-once delivery, checkpoints, bounded retries, and held/failed states.
4. **Split the AI/redaction stages:** extraction -> candidates -> rendering -> independent integrity checks. Add page/span/polygon provenance; a black rectangle alone is insufficient.
5. **Draw the human gate:** specialists resolve ambiguity, approve exact versions, or hold. Charging reviewers get approved derivatives, not automatic fallback to originals.
6. **Close with defendability:** Government readiness gates, retention/legal custody, category-specific evaluation and operational failure handling. No customer metrics are claimed.

Use the [four diagrams](../diagrams/README.md) rather than drawing every Azure service icon. Explain a minimal design first; do not introduce an LLM or gateway merely to showcase technology.

## Likely questions and answer outlines

| Question | Answer outline |
| --- | --- |
| What did you personally contribute? | "Authentication design into Azure Government, API-based ingestion and Document Intelligence processing, and the redaction workflow/output." Do not add code ownership, production responsibility, or measured savings. |
| Was this actually deployed? | "Deployment maturity is not established in this case-study record." Recover memory before making a stronger claim. |
| Which model/API/detector did the customer use? | "Those historical details are not established. In this proposal I would verify a supported Government GA extraction model, and evaluate detection separately." |
| Why Azure Government instead of commercial Azure? | Confirm the engagement used Government; do not invent the customer's regulatory rationale. For the proposal, discuss approved cloud/residency requirements and different authority/endpoints/feature availability. |
| How does Document Intelligence redact a PDF? | It supplies text/layout extraction, not the complete renderer. Detect approved spans, map coordinates, permanently remove content, sanitize ancillary data, and independently validate. |
| Would you use an LLM? | Not in the baseline. Rules plus specialist review are auditable; contextual models require availability, privacy, grounding, prompt-injection controls, evaluation, and approval. They cannot decide legal materiality. |
| Does removing race eliminate bias? | No. Proxies and prior knowledge remain; over-redaction can harm interpretation. Evaluate exposure reduction and document utility separately from broader fairness questions. |
| Why managed identity? | Reduce stored credentials for services. It does not authorize an end user or establish cloud parity. Verify custom endpoint, sovereign audience, data-plane roles, and actual integration. |
| Is a private endpoint enough? | No. Need routing, Government DNS, public-access denial, TLS, identity, case authorization, and necessary controlled egress. |
| What if OCR misses a reference? | End-to-end evaluation includes OCR omissions. Missing/unmapped pages and poor quality hold the document; specialists/manual processing handle it. Never release on an empty detection list alone. |
| Why not make it synchronous? | Variable document size and service polling favor durable asynchronous jobs. A 202 is acceptance, not success. Bounded retry and recovery prevent lost work. |
| Can you guarantee exactly once? | No. Use idempotency, ledger leases, deterministic artifacts, and version-bound approval to prevent duplicate release. External analysis may repeat after uncertain submission. |
| How do you preserve evidence? | Keep the original separately and immutable under approved policy; record derivative lineage. Legal chain of custody is a separate organizational process, not solved by a hash alone. |
| What metrics prove success? | Proposed miss/over-redaction, OCR/layout, integrity, workload, latency/failure measures. No measurements here. Domain owners approve risk-based thresholds; none proves fairness. |
| What happens when a service is unavailable in Government? | Do not route to commercial Azure. Select a verified supported alternative with explicit tradeoffs, or hold and use an approved manual process. No preview dependency in baseline. |
| How would you operate this? | Discuss queue/review backlog, safe telemetry, replay authorization, patching, restore, retention/legal holds, incident quarantine, and readiness gates. These are proposed, not personal production-operation claims. |

## Language that preserves credibility

| Avoid | Use instead |
| --- | --- |
| "We eliminated bias." | "The customer wanted to reduce exposure to race-identifying information." |
| "I built and operated this entire production platform." | "My confirmed contributions were these three areas; broader ownership and maturity are not established." |
| "Document Intelligence handled redaction." | "Document Intelligence supported extraction; detection and rendering are distinct concerns." |
| "Our accuracy was 99%." | "No measured result is established; I would evaluate category-specific misses and over-redaction." |
| "The system decided charges." | "It prepared review documents; authorized people retained legal judgment." |
| "All Azure features work in Government." | "I verify the chosen region, API, identity, networking and SKU combination." |
