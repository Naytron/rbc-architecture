# Official source register

Reviewed **2026-10-03** using official Microsoft documentation. These sources establish product behavior, not historical customer implementation or measured effectiveness. General Azure documentation is labeled as such; it is not evidence of complete Government feature parity.

## S1 - Government development and availability

[Azure Government developer guide](https://learn.microsoft.com/azure/azure-government/documentation-government-developer-guide)

Establishes a separate cloud instance, possible feature/configuration differences, and the official regional availability lookup. Supports the readiness gates rather than an assumption of parity.

## S2 - Government endpoint mappings

[Compare Azure Government and global Azure](https://learn.microsoft.com/azure/azure-government/compare-azure-government-global-azure)

Lists Government endpoint suffixes including Document Intelligence (`cognitiveservices.azure.us`), storage, Service Bus, Key Vault, and management. Endpoint listings do not certify a chosen region/SKU/API combination.

## S3 - National-cloud user authentication

[Microsoft identity platform national clouds](https://learn.microsoft.com/entra/identity-platform/authentication-national-cloud)

Establishes Government authority `https://login.microsoftonline.us`, Government portal, cloud-specific app registration, and distinct cloud instances. Does not establish the customer's federation or tenant topology.

## S4 - Document Intelligence authentication

[Document Intelligence SDK v4.0 overview](https://learn.microsoft.com/azure/ai-services/document-intelligence/versioning/sdk-overview-v4-0?view=doc-intel-4.0.0)

Documents API-key and Entra token credentials, managed-identity recommendation, `Cognitive Services User`, and the need for a custom subdomain for Entra authentication (regional endpoints do not support it). This is general service guidance; target-cloud compatibility remains a gate.

## S5 - Document Intelligence sovereign audience

[KnownDocumentIntelligenceAudience enum](https://learn.microsoft.com/javascript/api/@azure-rest/ai-document-intelligence/knowndocumentintelligenceaudience?view=azure-node-latest)

Documents the `AzureGovernment` audience option for sovereign-cloud token authentication. Default public-cloud audience is not sufficient. The proposal does not select a programming language or SDK version.

## S6 - Extraction and page geometry

[Document Intelligence layout model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0)

Documents text, structure, spans, pages, polygons, page size, angle, and coordinate units. Capability details vary by API/model/input type. Does not provide a permanent PDF-redaction solution.

## S7 - Private access to Document Intelligence

[Configure secure access with managed identities and virtual networks](https://learn.microsoft.com/azure/ai-services/document-intelligence/authentication/managed-identities-secured-access?view=doc-intel-4.0.0)

Documents client private endpoints and service identity for storage access. The examples are general Azure examples, including commercial Studio IP addresses; do not copy those addresses into a Government design. Service-side storage retrieval is not automatically routed through a client's VNet.

## S8 - Government private DNS

[Azure Private Endpoint private DNS zone values - Government](https://learn.microsoft.com/azure/private-link/private-endpoint-dns#government)

Government-specific DNS mappings for Cognitive Services, storage Blob/Table, Service Bus, Key Vault, and Azure Monitor. Correct DNS and endpoint approval are necessary but do not alone disable public access or grant authorization.

## S9 - Service Bus private networking

[Service Bus private endpoints](https://learn.microsoft.com/azure/service-bus-messaging/private-link-service)

Documents Premium-tier requirement for private endpoints and the need to configure public-network access separately. General feature guidance plus Government DNS evidence does not confirm regional Premium capacity.

## S10 - Document Intelligence data handling

[Data, privacy, and security for Document Intelligence](https://learn.microsoft.com/azure/foundry/responsible-ai/document-intelligence/data-privacy-security)

Documents same-region processing and temporary encrypted service storage; describes deletion of submitted input/results 24 hours after completion and an earlier-delete API. Confirm applicability to the selected Government API and contract before relying on early deletion. App-owned copies and backups have independent retention.

## S11 - Government Studio

[Document Intelligence FAQ](https://learn.microsoft.com/azure/ai-services/document-intelligence/faq?view=doc-intel-4.0.0)

Documents Government Studio at `https://formrecognizer.appliedai.azure.us/studio`. A Studio URL does not establish model/API availability or private browser access.

## S12 - API support status

[Document Intelligence overview](https://learn.microsoft.com/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0)

General documentation identifies v4.0 (`2024-11-30`) as GA/current and v3.1 (`2023-07-31`) as GA/previous. This is **not** confirmation that either combination is available in a selected Government region.

## S13 - Official regional catalog

[Azure products by region](https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/)

The page was consulted, but the retrieved content did not expose the interactive regional service matrix. Exact regional availability, SKU capacity, and preview status could not be confirmed from that result. Record them as unverified, not as available or unavailable.

## S14 - Document Intelligence Python SDK usage

[azure-ai-documentintelligence readme](https://learn.microsoft.com/python/api/overview/azure/ai-documentintelligence-readme?view=azure-python)

Documents the `DocumentIntelligenceClient` constructor, `begin_analyze_document("prebuilt-layout", body=f)` for local-file submission, `DefaultAzureCredential` usage (noting regional endpoints do not support it), and `page.width`/`page.height`/`page.unit`/`line.polygon`/`word.polygon` result fields. `demo/pipeline.py` follows this documented pattern; it has not been executed against a live Document Intelligence resource in this repository (see `demo/README.md`).

## S15 - PyMuPDF redaction and document scrubbing

[PyMuPDF `Page.apply_redactions()`](https://pymupdf.readthedocs.io/en/latest/page.html#Page.apply_redactions) and [`Document.scrub()`](https://pymupdf.readthedocs.io/en/latest/document.html#Document.scrub)

Documents that `apply_redactions()` removes the underlying content within a redaction annotation's rectangle (not a visual-only overlay) and that `scrub()` can remove metadata, attachments, embedded files, JavaScript, and hidden text. `demo/pipeline.py` uses both and was tested locally end-to-end (see `demo/README.md`). This is one possible implementation choice among several compared in `docs/architecture.md`, not a claim that PyMuPDF was the customer's tool.

## Evidence boundaries

Permanent PDF redaction, legal governance, API design, role separation, retry behavior, and evaluation gates here are **proposed requirements**, not claims about capabilities supplied by Document Intelligence. A selected PDF library would need its own documentation, license review, adversarial validation, and operational support evidence.
