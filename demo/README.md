# Demo scripts — illustrative only

**These scripts are a personal, single-operator learning demo in commercial Azure.** They are not production code, not the customer's historical implementation, and not the complete proposed Government architecture. See [`docs/demo-setup.md`](../docs/demo-setup.md) for the full setup walkthrough, cost notes, and an explicit list of what this demo simplifies away from the proposed architecture (private networking, Service Bus Premium, separate storage accounts, managed identity, a real detection taxonomy).

All sample text is synthetic, matching [`examples/synthetic-input.md`](../examples/synthetic-input.md). No real case material exists here.

## Files

| File | Purpose |
| --- | --- |
| `generate_sample_pdf.py` | Writes a one-page synthetic PDF for testing — no scanner or real document needed. |
| `pipeline.py` | Runs extraction (Document Intelligence Layout), detection (illustrative keyword rules), and rendering/validation (permanent redaction + re-extraction check) for one document. Uploads the candidate derivative and a manifest to the `quarantine` container. |
| `review_cli.py` | Lists quarantined candidates and their manifests, and moves an approved candidate to the `approved` container — a minimal stand-in for the proposed human-review gate. |
| `requirements.txt` | Python dependencies: `azure-ai-documentintelligence`, `azure-identity`, `azure-storage-blob`, `azure-storage-queue`, `pymupdf`. |

## Why a local script instead of a deployed service

The proposed architecture uses a durable queue and an always-on worker (ADR-002) so that extraction, detection, and rendering happen asynchronously and survive restarts. For a one-document interview demo, a synchronous local script is cheaper, faster to set up, and easier to narrate line by line — but it does not demonstrate retries, leasing, or concurrent processing. Say so if asked; do not imply this script is the production design.

## Authentication

Scripts use `azure.identity.DefaultAzureCredential`, which picks up your `az login` session. No API key or secret is stored anywhere in this repository. In the proposed architecture, a worker process would instead use a **managed identity** with the same two roles (`Cognitive Services User`, `Storage Blob Data Contributor`) — using your own user identity here is a deliberate demo simplification, not a security recommendation for a multi-user system.

## What the detection step actually does (and does not)

`pipeline.py` matches a short, hardcoded, explicitly illustrative keyword list (see `ILLUSTRATIVE_TERMS` in the file) against extracted text. This stands in for the versioned, domain-owned taxonomy described in [Separate detection stage](../docs/architecture.md#separate-detection-stage). It is intentionally simple so the demo is honest about what it proves: that detection can be a distinct, testable stage with its own inputs and outputs — not that keyword matching is an adequate real-world detector. Do not extend this list with real sensitive terms or real document text.

## What has and has not been tested

The `detect_candidates()`, `render_and_validate()`, and `build_manifest()` functions in `pipeline.py` were exercised locally end-to-end (word-box input, redaction, metadata/attachment scrub, and the re-extraction validation check all ran successfully against a generated sample PDF) using PyMuPDF's own word extraction as a stand-in for Document Intelligence output. The call to the live Document Intelligence service (`extract_layout()`) and the Blob Storage upload/download calls have **not** been exercised against a real Azure resource in this repository — they follow the official SDK's documented call signatures (see `docs/sources.md`), but you are the first one to run them against a live resource when you follow `docs/demo-setup.md`.
