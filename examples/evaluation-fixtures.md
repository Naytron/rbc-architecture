# Synthetic evaluation fixtures - proposed tests

These are test designs, **not executed test results**. Generate actual synthetic PDFs/images locally when an implementation and approved renderer exist. Domain owners adjudicate expected content policy before scoring.

| Synthetic scenario | Expected handling |
| --- | --- |
| "The report describes Person A as Black." | Candidate for explicit-reference removal under the illustrative policy; preserve span/page mappings. |
| "The person wore a black coat." | Do not blindly redact a color word as a race reference; domain-approved context rule. |
| "No race descriptor was recorded." | Test policy interpretation/negation; do not infer a demographic attribute. |
| "Person A waited near Fictional Square." | Possible contextual proxy discussion, not automatic race inference or universal removal. |
| Reference split over two lines or pages | Map all relevant regions; ambiguous boundary becomes a held case. |
| Scanned text with OCR error "B1ack" | End-to-end miss evaluation and specialist escalation; detector-only scoring is insufficient. |
| Rotated/cropped scan with a descriptor | Check transforms and pixel removal; reject unmapped/partial coverage. |
| Photograph or handwritten annotation | Human/domain policy path if automated extraction/detection is insufficient. |
| Visible removal but hidden OCR still contains the term | Integrity failure; reject and hold, regardless of detector score. |
| Metadata/XMP, attachment, bookmark or old PDF revision contains the term | Sanitization/integrity failure; reject and hold. |
| Correct removal damages a materially necessary description | Specialist/domain adjudication; no automatic legal-materiality decision. |
| Malformed/encrypted PDF, oversized input or active content | Explicit reject/quarantine/approved manual route; no success-shaped fallback. |
| Identical job delivered twice after worker crash | Resume guarded state, no duplicate approval/publication; external extraction may repeat. |
| Candidate changes after approval screen opens | Reject stale approval; approval must bind exact version/hash and validation evidence. |
| Valid token for a different case | Deny job/artifact access without disclosing document existence/content. |
