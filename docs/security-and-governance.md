# Proposed security and governance

These are reference-design requirements, **not confirmed customer controls**. The system assists charging review; it does not recommend charges or decide legal matters. Azure Government placement alone is not proof of compliance or fairness.

## Identity is not authorization

**Users:** baseline assumes an approved Government Entra tenant and a tenant-specific authority at `login.microsoftonline.us` [S3](sources.md#s3---national-cloud-user-authentication). An interactive authorization-code flow with PKCE is a proposed option; the customer flow is unknown. Validate signature, issuer, tenant, audience, expiry, and required permissions. Apply organization-approved MFA/session/device policies where supported and confirmed. A valid token is insufficient without case- and action-level authorization.

Register the API/client in the appropriate cloud. Do not assume commercial identities can transparently access Government resources. If federation, guests, or cross-cloud identity are required, document the tenant relationship and supported flow separately.

**Services:** API and worker use distinct managed identities, scoped to required data-plane actions. A worker credential authorizes processing, not a user to read a case. Retain initiating user/case context for audit, but re-check current authorization for approval/download. Do not pass a user's bearer token through the queue or make workers depend on long-lived delegated tokens.

Entra token authentication to Document Intelligence requires a custom endpoint, a suitable role, and sovereign audience configuration [S4](sources.md#s4---document-intelligence-authentication), [S5](sources.md#s5---document-intelligence-sovereign-audience). Confirm the built-in role's complete permissions; `Cognitive Services User` is documented but should not be described as an extraction-only custom role. If narrower supported permissions are needed, evaluate a custom role.

If managed identity cannot satisfy a verified service integration, an approved service principal/certificate or API key is a documented exception, not an inferred historical choice. Store required secrets in Key Vault, restrict retrieval to the specific host identity, rotate/revoke, and monitor use. Never put keys in examples, URLs, queues, repository files, or logs. Disable local key authentication where supported after token-authentication verification.

## Proposed access matrix

| Actor | Originals and extraction/candidate text | Derivatives | Control/audit |
| --- | --- | --- | --- |
| Submitter | Upload approved source; no implied read-back | Status and approved output only if separately case-authorized | Own case-safe status |
| Charging reviewer | Denied by default | Approved, assigned-case versions only | Minimal provenance display, no removed text |
| Redaction specialist | Case-scoped access with justification | Candidate review and approval of exact version | Review evidence; no general audit administration |
| API identity | Scoped upload/read actions needed to mediate authorized requests | Scoped candidate/approved reads and approved-state enforcement | Conditional job/approval writes and audit emission |
| Worker identity | Read eligible originals and restricted intermediates | Write candidates; cannot approve release | Scoped stage transitions and validation evidence |
| Operations support | No content by default | No content by default | Safe metrics/error categories; privileged escalation separately approved |
| Audit/retention administrators | Only justified legal/administrative functions | Same principle | Separation of duties, protected records and holds |

Storage RBAC alone generally does not implement per-case authorization. The API enforces it on every request; scoped service roles do not give callers direct storage access. Separate read, write, approval, retention, and management duties. Avoid subscription-wide Owner/Contributor for processing identities. Scope storage data roles to containers/tables where supported; management access is not interchangeable with data-plane access.

Candidate files stay in a quarantined derivative container. The API publishes only when a ledger approval references the exact validated hash/version. Never grant charging reviewers read access to the whole derivative account. Do not disclose restricted manifest text in an approved derivative's embedded metadata.

## Private connectivity and trust boundaries

Use private office-to-API routing, TLS, private endpoints for extraction/storage/queue/vault, and explicit public-network denial where supported. Government DNS zones differ from commercial values [S8](sources.md#s8---government-private-dns). Private endpoint creation does not disable public access, validate tokens, or filter cases.

Link private DNS zones to the worker/API VNet. Configure approved office DNS conditional forwarding/resolution and test both positive and negative paths. Verify service hostname, TLS certificate, private IP resolution, endpoint approval, routing, and public-network denial. Entra authority and other necessary dependencies need controlled egress; not everything becomes private.

Use byte submission to Document Intelligence. If a future design uses URLs, evaluate service-side storage reachability, identity and firewall rules separately; a worker's private endpoint does not grant the extraction service a private path [S7](sources.md#s7---private-access-to-document-intelligence). Do not copy commercial Studio IP allowlists to Government.

Restrict administrative ingress, use approved privileged access paths, and prohibit exposing VM management ports publicly. Patch and isolate parsing/rendering processes; treat PDFs as untrusted active input. Limit CPU, memory, runtime, file-system access, and outbound network access during parsing. No external scripts, links, or plugins are executed from documents.

## Encryption, keys, and temporary data

Require approved TLS for all hops and encryption at rest for storage, queue, disks, backups, and temporary workspaces. Document Intelligence describes encrypted temporary same-region storage [S10](sources.md#s10---document-intelligence-data-handling); validate selected-cloud applicability and contract. Do not equate that statement with zero retention.

Use platform-managed keys unless legal/security owners require supported customer-managed keys. CMK coverage differs by service/tier/cloud and must be checked; key rotation, backup/recovery, access separation, and revocation impact are operational responsibilities. Key revocation can stop processing and retrieval.

Temporary OCR, snippets, coordinates, candidate manifests, reviewer screenshots, and failed outputs can reveal the removed information. Classify them like originals, encrypt disks/scratch space, restrict access, and remove them under an explicit retention policy. Hashes and opaque IDs may still be linkable; avoid public disclosure.

## Audit without sensitive logging

Record subject/service identity, opaque case/document/job IDs, source/derivative hashes, version lineage, action, stage, timestamp, authorization outcome, review/approval, and reason codes. Protect detailed provenance separately from operational logs. Audit original reads, derivative downloads, rejected access, policy changes, replay, holds, deletion, and key/role changes.

Do not log document text, candidate snippets, tokens, SAS URLs, credentials, request bodies, or full SDK responses. Use explicit allowlisted telemetry fields. Disable content-bearing debug tracing and sanitize exception paths; crash dumps and support bundles require the same controls. Restrict audit read/delete permissions and use approved tamper-evident storage/export where verified. Define what happens if audit emission fails: hold release until durable audit recording succeeds, while alerting operators.

## Retention and legal process

Legal/evidence owners specify schedules separately for original records, service temporary data, extracted text, candidates, approved derivatives, audit, backups, and dead-letter references. No durations are invented here.

Document Intelligence general documentation says inputs/results are deleted 24 hours after completion and describes an earlier-delete API [S10](sources.md#s10---document-intelligence-data-handling). Earlier deletion is **not a baseline guarantee** for the unselected Government API. Preserve necessary app-owned results before service expiry; enforce app retention independently.

Honor legal holds before deletion. Coordinate object versions, snapshots, replicas, backups, review exports, and service copies; a deleted current Blob is not proof all copies are gone. Verify supported immutable storage features before choosing them, and do not assert compliance with a named legal framework without an approved assessment.

The original evidentiary record must remain intact in an approved system. Hashes, timestamps, and derivative lineage do **not** replace chain-of-custody procedures, evidence authentication, admissibility decisions, or authorized source transfer records. If the proposed original account is only a processing copy, the source evidence system remains authoritative and its custody process continues unchanged.

## Legal/domain decisions and residual risk

Domain owners approve redaction categories, proxy treatment, legally material exceptions, reviewer access, notice/labeling, escalation, and retention. Removing a descriptor can impair identity matching or understanding; leaving a proxy can expose race-identifying context. Record that tradeoff rather than calling either choice universally correct.

Residual exposure can arise from OCR errors, images, handwritten notes, multilingual references, repeated context, attachments, reviewer prior knowledge, or output defects. A reduction in visible references is not proof that decisions are unbiased. Charging outcomes and broader fairness questions require separate legal, ethical, and empirical review; they are not claims made by this pipeline.
