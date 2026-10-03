# Historical details to recover from memory

These questions are not answers or implied historical facts. If memory is uncertain, say so in the interview and use the proposed design to explain how you would address the issue today. Do not include customer names, real documents, credentials, or sensitive identifiers in answers.

| Topic | Questions to answer | If still unknown |
| --- | --- | --- |
| My role and ownership | What did I personally design, configure, review, or demonstrate? Which responsibilities belonged to customer engineers, partners, or other Microsoft staff? | Use only the three confirmed contributions; do not claim implementation ownership. |
| Engagement stage | Was this discovery, a prototype, pilot, or production? What was delivered or demonstrated? Who operated it afterward? | Say deployment maturity is not established; no production-operation claim. |
| User identity | Which tenant/cloud hosted identities? What sign-in/federation/guest flow was used? What did my authentication-design contribution cover? | Do not present the proposed PKCE/Government-tenant flow as historical. |
| Service identity | Were calls made with keys, service principals, or managed identities? What permissions and token audiences were used? | Explain present-day options separately. |
| Source and ingestion | What approved source repository or upload path existed? What API boundary, file types, size limits, validation, and asynchronous behavior were used? | Keep source product and exact API contract unknown. |
| Extraction | What model, API version, cloud region, resource kind, and SDK were used? Were page coordinates available and how were they consumed? | Confirm only API-based processing using Document Intelligence. |
| Detection | Who/what identified references? Rules, people, NER, another product, or a combination? How were indirect proxies and legal exceptions defined? | Do not credit Document Intelligence with the entire redaction solution. |
| Output | Was output PDF, text, image, or another format? How was underlying content handled? What did I contribute to the workflow/output? | PDF permanent-redaction design remains a proposal. |
| Human workflow | Who reviewed candidates? Were originals available to charging reviewers? What happened when extraction/detection failed? | Do not claim a historical approval or exception process. |
| Security/governance | What networking, logging, retention, evidence custody, and artifact permissions actually existed? | Describe proposed controls, not implemented controls. |
| Evaluation | Was an annotated dataset used? Which misses/over-redactions were observed? Who approved risk? Were latency or workload measured? | No accuracy, savings, outcome, or fairness claims. |
| Results and lessons | What can I substantiate as an observed result or stakeholder decision without sensitive detail? What tradeoff did I directly discuss? | State the customer goal and confirmed contribution, not an invented success story. |

## Safe memory-recovery template

For each recovered point, privately record: remembered fact, personal action, evidence/confidence, ownership boundary, and what remains uncertain. Add a historical claim to this repository only when it is accurate and safe to disclose. Current documentation can validate a present-day architecture, but cannot prove what the customer used then.
