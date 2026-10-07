# Azure Government Document Processing for Race-Blind Charging Review

**Documentation-first interview case study.** This repository helps explain a real customer engagement and defend a **proposed** reference architecture in a Senior Azure AI Solutions Architect / Engineer interview. It is not a production implementation, deployment package, or assertion that all proposed components existed in the customer solution.

Here, "race-blind" describes the customer's goal of reducing reviewers' exposure to race-identifying information in police reports and supporting documents during **charging review**. It does not mean that redaction eliminates bias, proves fairness, or makes every document race-neutral.

## What I personally contributed

While working at Microsoft, I helped a large district attorney's office with:

- Authentication design into Azure Government.
- API-based document ingestion and processing using Azure Document Intelligence.
- The redaction workflow and resulting output.

These are the confirmed contributions. This repository does not assert code ownership, a specific identity flow, production operation, or measured customer outcomes.

## Facts versus proposed decisions versus memory questions

| Classification | What belongs here |
| --- | --- |
| **Confirmed engagement facts** | The customer context, goal, and three contributions above. |
| **Proposed reference architecture** | All component selections, API contracts, security controls, evaluation methods, diagrams, and architecture decisions in this repository. |
| **Historical details to recover** | Exact identity flow, source repository, Document Intelligence model/API version, detection technology, output format, deployment maturity, measured outcomes, and responsibility boundaries. See [open questions](docs/open-questions.md). |

The system assists document preparation and charging review. It **does not recommend charges, determine guilt, make legal decisions, or automate sentencing**. Authorized people retain legal judgment. Legal and domain owners must approve what can be removed without impairing evidentiary meaning or obligations.

## Architecture summary

**Proposed:** approved source -> authorized ingestion API -> protected original -> asynchronous queue -> Document Intelligence text/layout extraction -> separate sensitive-reference detection -> separate permanent-redaction renderer -> integrity validation -> human approval -> separately authorized derivative delivery.

Document Intelligence is the extraction component, **not the entire redaction solution**. Text offsets and page geometry connect detection to rendering; an extraction failure or ambiguous reference becomes an exception, not a silently released document. Originals remain separately protected.

The minimal reference topology uses an API and worker on Azure Government VMs, Blob/Table storage, Service Bus Premium, Document Intelligence, and restricted operational telemetry. Key Vault is included when secrets or customer-managed keys are required. These are proposals; exact region, SKU, API, identity, and networking compatibility must pass the [Government readiness gates](docs/azure-government-verification.md).

## Navigation

| Artifact | Use |
| --- | --- |
| [Architecture](docs/architecture.md) | Components, data flows, trust boundaries, detection alternatives, PDF handling |
| [Security and governance](docs/security-and-governance.md) | Identity, access, networking, retention, evidence governance |
| [Evaluation and operations](docs/evaluation-and-operations.md) | Proposed measures, release gates, failure recovery, production responsibilities |
| [Azure Government verification](docs/azure-government-verification.md) | Current official evidence, endpoint mappings, unverified combinations and alternatives |
| [Architecture decisions](docs/decision-records/README.md) | Small set of proposed decisions and tradeoffs |
| [Executive summary](docs/executive-summary.md) | Non-technical 30s/2min story and executive-level anticipated questions |
| [Interview guide](docs/interview-guide.md) | 90-second story, whiteboard route, answer outlines |
| [Architecture explainer](docs/architecture-explainer.md) | Decision-by-decision rationale and likely follow-up questions, for live Q&A |
| [Low-cost demo setup](docs/demo-setup.md) | Steps to build a working analog in your own commercial Azure subscription |
| [Open questions](docs/open-questions.md) | Historical details to answer from memory |
| [Source register](docs/sources.md) | Official sources attached to consequential product claims |
| [Diagrams](diagrams/README.md) | Four standalone Mermaid sources and local rendering instructions |
| [Synthetic examples](examples/README.md) | Illustrative input, derivative text, and restricted provenance manifest |
| [Demo scripts](demo/README.md) | Runnable illustrative pipeline for the low-cost demo (not production code) |

## Reading and maintenance

Start with the interview guide, then architecture and the Government verification register. All examples are invented; none contains customer material. No Azure credentials or resources are needed to read or maintain this repository.

Official documentation was reviewed on **2026-10-03**. Documented cloud support is not a guarantee of every feature in every Government region. Unverified combinations are explicitly gated; previews are not baseline dependencies. See [validation notes](diagrams/README.md#validation-status) for Mermaid rendering limits.
