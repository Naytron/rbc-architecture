# Proposed evaluation and operations

No customer measurements or outcomes are available. Everything here is an evaluation/operations proposal. **No universal acceptance thresholds are asserted.**

## Evaluation corpus and ground truth

Start with synthetic documents like the [examples](../examples/README.md). Build a held-out synthetic benchmark with explicit references, ambiguous proxies, misspellings, negation, multilingual text, handwriting-like scans, rotated/cropped pages, tables, stamps, photos, attachments, searchable PDFs, and deliberately malicious hidden content. Synthetic performance does not establish performance on real police reports.

For a future authorized engagement, representative evidence would require legal/privacy approval, secure annotation, defined use/retention, and no uploads to unapproved tools. This repository contains no such evidence. Use independent domain annotators with adjudication of disagreement; preserve policy rationale, not inferred demographic labels. Split by document family/source template to reduce leakage, and keep a holdout untouched during rule tuning.

Annotate canonical spans/page regions, categories, required removals, approved keep decisions, ambiguous cases, and critical content that must survive. Evaluate detection conditional on correct extraction **and** end-to-end on input pages; otherwise OCR misses disappear from the detector's denominator.

## Measures

| Dimension | Proposed measurement | Important caveat |
| --- | --- | --- |
| Missed sensitive references | False negatives / ground-truth required-removal references, by category; documents with any critical miss / evaluated documents | Report counts, denominators, adjudication uncertainty, and confidence intervals. Include missed images/pages, not just extracted text. |
| Over-redaction | Incorrect removals / all removals, plus document-level counts of materially damaged meaning | Precision alone misses the legal severity of removing a crucial fact. Measure specialist reversals and category-specific harm. |
| OCR/layout quality | Character/word error rates, missing-page rate, region coverage/overlap, rotation/crop mapping errors | Stratify scans versus native PDFs, language, handwriting, and template; inspect regions even when text is correct. |
| Output redaction integrity | Leakage events from independent text/object/metadata/image checks; page completeness and accessibility checks | Test hidden OCR, XMP, attachments, old revisions, layers, and copy/search. Detector success does not imply renderer success. |
| Human-review workload | Specialist active minutes/document and page, queue age, percentage escalated, correction/re-render rate, disagreement rate | Distinguish active work from waiting; baseline manual workload must be measured, not assumed. |
| Latency | Acceptance-to-candidate and acceptance-to-approval p50/p95/p99; stage times and queue delay | Segment page count/input type; approval includes human waiting. Do not advertise an invented SLA. |
| Processing failures | Failed/held jobs per accepted document; retry count, terminal error rate, recovery time, duplicate release count | Retries are not new documents. Separate infrastructure failure, unsupported input, quality hold, and integrity failure. |

Compare rules-only and any optional detector against the same held-out corpus and policy. Inspect repeated misses and high-severity false removals, not just average scores. Evaluate throughput under realistic concurrency/size and service throttling. Retain dataset/policy/model/API/renderer versions so comparisons are reproducible.

## Risk-based approval, not invented thresholds

Legal/domain owners define category-specific severity and tolerance; security owners define integrity/access conditions; operations owners define capacity/recovery objectives. They approve dataset coverage, metric definitions, thresholds, confidence requirements, escalation rules, and residual risks **before** evaluating release candidates.

As a proposed release invariant, any detected output-integrity failure, incomplete page set, invalid coordinate map, unresolved required removal, or missing approval blocks that artifact. "No failures observed" in a sample is not proof of zero future risk. Low-frequency categories need enough observations to justify an estimate, or stay mandatory-human-review/manual.

Initial release requires specialist approval of every derivative. Automated release, if ever desired, is a separate decision with explicit evidence and approval. No metric here establishes legal fairness or charging-outcome improvement.

## Durable state and retry policy

Proposed job states:

`accepted -> queued -> extracting -> detecting -> rendering -> validating -> awaiting_review -> approved`

`held`, `failed`, and `cancelled` are explicit alternatives, never aliases for approved. Review corrections create a new candidate version; only an approval bound to its hash can release it. A validated candidate is not automatically approved.

Use Table conditional updates/ETags and stage leases. Queue messages carry a job ID and expected processing profile, not text or signed access URLs. Guard each transition and make checkpoints repeatable. Complete queue delivery after durable stage/job updates; reconcile pending-dispatch entries and reclaim expired leases.

For throttling and transient failures, honor service retry guidance, use bounded exponential backoff with jitter, and cap elapsed time/attempts based on approved operational requirements. Do not endlessly retry invalid/encrypted inputs, forbidden access, unsupported models, or mapping/integrity failures. Authentication failures alert operations; content issues go to specialists.

Persist the extraction operation reference before proceeding; resume polling instead of resubmitting when possible. A timeout after submission but before saving the operation reference can cause duplicate analysis; do not claim exactly-once execution. Track uncertain submission, reconcile where possible, and bound duplicate cost. Stage success and artifact writes use deterministic references/hash checks.

Dead-letter/poison handling records a safe reason and references to restricted artifacts, not their content. Specialists/operators triage according to role. Replay requires authorization, reason, repaired cause, and a new attempt/profile where applicable; it never overwrites approved history.

## Production runbooks and ownership

| Trigger | Proposed response and owner |
| --- | --- |
| Queue age/throttling rises | Operations checks concurrency, page sizes, capacity and service status; bound workers and preserve accepted work. No silent model/cloud switch. |
| Extraction/mapping quality deteriorates | Domain and engineering owners hold affected document classes, compare against fixtures, and use approved manual processing. |
| Integrity leak or wrong-case delivery | Suspend affected delivery path, quarantine/revoke artifact access, preserve audit, notify security/legal owners, assess prior recipients and versions. A downloaded copy cannot be remotely recalled by assumption. |
| Worker crash or lease expiry | Operations reclaims leases and resumes durable stages; deduplication prevents extra publication, not necessarily extra extraction. |
| Identity/DNS/private endpoint failure | Platform owner checks issuer/audience/roles, resolution, route and endpoint approval; do not bypass with public endpoints or shared keys. |
| Audit or approval-store outage | Hold publication; preserve candidate and recoverable state, alert operators, reconcile before release. |
| Service result expires | Engineering verifies stored result availability; re-analysis is authorized and audited if necessary. |
| Retention/hold conflict | Evidence/legal owner resolves it; operations does not delete on an assumed schedule. |

Dashboards include content-free job counts/stage times, failure categories, queue/dead-letter age, lease expiry, review backlog, publication failures, denied access, disk pressure, and audit gaps. Alert thresholds and SLOs are approved later; none are customer results.

## Reliability and change management

Define RTO/RPO, source re-ingestion rules, storage redundancy, backup/restore, and disaster-recovery region with evidence/legal owners. Verify Government region/SKU availability, data residency, quotas, and failover permissions before proposing a multi-region service. The diagram is single-region and makes no zone/HA guarantee. A production design must address VM process supervision, restart, host failure, patching, backup, capacity, and approved redundancy or accept documented downtime.

Pin extraction API/model, detector policy, renderer library, and validator versions. Use synthetic regression suites for Unicode offsets, page geometry, adversarial PDFs, authorization, duplicate dispatch, crash recovery, and artifact approval races. Test updates in isolated staging; retain prior profiles for reproducibility, not automatic insecure rollback. Changes to redaction policy require legal/domain approval; changes to identity/networking require security review.

Restore tests include legal holds, original hashes, job ledger, provenance, and approved artifacts. Incident recovery never recreates approvals from candidate filenames. Reconcile approved ledger hashes to files before delivery.

## Interview evidence discipline

Say "I would measure..." for this section. Do not turn the illustrative examples into measured accuracy, workload savings, production throughput, or improved fairness. Recover actual evaluation/deployment history through the [open questions](open-questions.md).
