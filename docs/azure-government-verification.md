# Azure Government verification and readiness gates

**Proposed deployment only.** This is a documentation review, not a subscription inspection or connectivity test. No Azure access, credentials, provisioning, or deployment was performed. Reviewed **2026-10-03**.

## What the official evidence establishes

| Capability | Verified documentation | Unverified detail and conservative alternative |
| --- | --- | --- |
| Document Intelligence in Government | Government endpoint suffix and Studio are documented [S2](sources.md#s2---government-endpoint-mappings), [S11](sources.md#s11---government-studio). | Exact region/model/API/add-on/SKU capacity is unverified. Select only a confirmed GA extraction combination later; if none meets requirements, use approved manual extraction/redaction, not a commercial-cloud endpoint. |
| User identity | Government Entra authority and separate app registration documented [S3](sources.md#s3---national-cloud-user-authentication). | Customer directory/federation is unknown. Baseline assumes an approved Government tenant; cross-cloud access requires separate assessment. |
| Service authentication to extraction | Keys and Entra token credentials, custom subdomain, and role documented [S4](sources.md#s4---document-intelligence-authentication); Government audience documented [S5](sources.md#s5---document-intelligence-sovereign-audience). | End-to-end managed-identity/RBAC operation with chosen SDK/API/region is untested. If approved and necessary, use a narrowly distributed, rotated service key in Key Vault; it cannot substitute for user authorization. |
| Document Intelligence private access | General service private-endpoint configuration [S7](sources.md#s7---private-access-to-document-intelligence); Government account DNS zone [S8](sources.md#s8---government-private-dns). | Exact resource/SKU configuration and DNS reachability are untested. Hold automated processing if required private access is unavailable; do not silently enable public access. |
| Blob/Table storage | Government endpoints and private DNS mappings [S2](sources.md#s2---government-endpoint-mappings), [S8](sources.md#s8---government-private-dns). | Selected replication, immutability, CMK, private endpoint, and API features require confirmation. Use an approved supported replication/retention configuration; preserve originals in the approved evidence system if a requirement cannot be met. |
| Service Bus | Government endpoint/DNS mapping [S2](sources.md#s2---government-endpoint-mappings), [S8](sources.md#s8---government-private-dns); private endpoints require Premium [S9](sources.md#s9---service-bus-private-networking). | Regional Premium availability/capacity is unverified. If unavailable, assess Storage Queue with application-managed poison handling, leases, and deduplication; no implicit feature equivalence. Otherwise hold automation. |
| API and worker compute | VM-based topology is proposed to avoid adding an API gateway/serverless hosting dependency. Government cloud differences apply [S1](sources.md#s1---government-development-and-availability). | VM SKU/image, managed identity, patching, zones, outbound access, and capacity are unverified. Choose a confirmed supported VM/image; no zone-resiliency claim. |
| Key Vault and telemetry | Government endpoint and private DNS mappings [S2](sources.md#s2---government-endpoint-mappings), [S8](sources.md#s8---government-private-dns). | Selected Key Vault features and Azure Monitor Private Link ingestion/query paths are untested. Use approved in-cloud protected audit/metrics storage if telemetry features are absent; retain auditability. Hold processing if required secret protection is unavailable. |
| Optional language model/NER service | No optional hosted detection service is selected. | Government model, PII taxonomy, language coverage, private access, and preview status are **unverified**. Baseline uses local rules and human adjudication; no dependency on Language, OpenAI, or Foundry agents. |

An endpoint or DNS listing is stronger evidence than assuming parity, but weaker than verifying a complete deployable combination. The interactive [regional catalog](sources.md#s13---official-regional-catalog) did not expose its matrix in the retrieved content. This repository makes **no exact regional GA availability claim**.

## Cloud configuration map

Values below are documented Government mappings, not live resource addresses. Obtain exact resource URLs from approved resource configuration later; do not form URLs by replacing `.com` with `.us`.

| Purpose | Government value or pattern | Source |
| --- | --- | --- |
| Portal | `https://portal.azure.us` | [S3](sources.md#s3---national-cloud-user-authentication) |
| User/service-principal authority | `https://login.microsoftonline.us/{approved-tenant}` | [S3](sources.md#s3---national-cloud-user-authentication) |
| Resource management | `https://management.usgovcloudapi.net` | [S2](sources.md#s2---government-endpoint-mappings) |
| Extraction custom endpoint | `https://{resource}.cognitiveservices.azure.us` | [S2](sources.md#s2---government-endpoint-mappings), [S4](sources.md#s4---document-intelligence-authentication) |
| Extraction token audience | Select the SDK's documented `AzureGovernment` audience, independent of authority | [S5](sources.md#s5---document-intelligence-sovereign-audience) |
| Blob | `https://{account}.blob.core.usgovcloudapi.net` | [S2](sources.md#s2---government-endpoint-mappings) |
| Table control ledger | `https://{account}.table.core.usgovcloudapi.net` | [S2](sources.md#s2---government-endpoint-mappings) |
| Service Bus namespace | `{namespace}.servicebus.usgovcloudapi.net` | [S2](sources.md#s2---government-endpoint-mappings) |
| Key Vault | `https://{vault}.vault.usgovcloudapi.net` | [S2](sources.md#s2---government-endpoint-mappings) |

User API token audience is the registered application identifier, **not** the Document Intelligence or management audience. Managed identity uses the host identity endpoint; do not redirect that endpoint to the Entra login URL. Configure sovereign audience/resource options for each data-plane client, and avoid public-cloud SDK defaults.

Private DNS zones [S8](sources.md#s8---government-private-dns):

- Extraction: `privatelink.cognitiveservices.azure.us`.
- Blob: `privatelink.blob.core.usgovcloudapi.net`.
- Table: `privatelink.table.core.usgovcloudapi.net`.
- Service Bus: `privatelink.servicebus.usgovcloudapi.net`.
- Key Vault: `privatelink.vaultcore.usgovcloudapi.net`.
- Monitor: use the complete Government zone set from S8 if Azure Monitor Private Link is selected; a single Monitor zone is insufficient.

Private endpoints do not create private Entra login endpoints. Permit approved identity and management dependencies through controlled egress. Resolve standard service hostnames to private addresses inside the VNet and from authorized office networks; do not call raw private IPs.

## Before any future implementation is approved

Platform owners would record target tenant/cloud, region, resource kind, SKU, capacity, GA/preview status, API/model IDs, SDK version and audience, RBAC roles, endpoint URLs, DNS zones, and evidence date. They would then test on synthetic documents:

1. Tenant-specific sign-in, issuer/audience checks, denied case access, and denied original access.
2. Managed-identity extraction and result polling through the custom endpoint; negative tests without roles.
3. Private DNS resolution, endpoint approval, public-network denial, and office-to-VNet routing.
4. Binary extraction upload, chosen model response shape/geometry, input limits, and recovery after timeouts.
5. Queue delivery/recovery, ledger concurrency, storage access, service result retention, and operational telemetry.

Version candidates from general documentation are v4.0 `2024-11-30` and v3.1 `2023-07-31` [S12](sources.md#s12---api-support-status), not a version commitment. Pin a confirmed supported GA combination and regression-test upgrades. Preview capabilities are excluded from the baseline; if later considered, explicitly document preview status, approval, and a non-preview/manual fallback.
