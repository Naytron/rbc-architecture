"""Low-cost demo pipeline: extract, detect, render/validate, hold-for-review.

ILLUSTRATIVE ONLY. This script is a personal, single-document, synchronous
demo for an interview conversation. It is not production code and not the
customer's historical implementation. See docs/demo-setup.md for the full
setup walkthrough and an explicit list of what this demo simplifies away
from the proposed Government reference architecture (ADR-001 through
ADR-004 in docs/decision-records/).

Stages, kept as separate functions to mirror ADR-001 (separate extraction,
detection, rendering, and validation):

  1. extract_layout()      -> calls Document Intelligence prebuilt-layout
  2. detect_candidates()   -> illustrative keyword matching over extracted words
  3. render_and_validate() -> permanent redaction + metadata scrub + re-check
  4. quarantine_result()   -> uploads candidate + manifest; nothing is released

Authentication uses DefaultAzureCredential (your `az login` session), not an
API key. In the proposed architecture a worker's managed identity would hold
the same two roles instead of a human user — see docs/demo-setup.md Step 4.
"""

import argparse
import hashlib
import io
import json
from datetime import datetime, timezone

import pymupdf as fitz
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Explicitly illustrative. A real deployment requires a versioned,
# domain-owned taxonomy approved by legal/domain owners (see
# docs/architecture.md#separate-detection-stage). Do not treat this list as
# adequate detection for real documents.
ILLUSTRATIVE_TERMS = [
    "black",
    "white",
    "hispanic",
    "asian",
    "native american",
]


def extract_layout(client: DocumentIntelligenceClient, pdf_bytes: bytes) -> dict:
    """Stage 1: extraction. Returns a plain-dict summary of pages/words."""
    poller = client.begin_analyze_document("prebuilt-layout", body=io.BytesIO(pdf_bytes))
    result = poller.result()

    pages = []
    for page in result.pages:
        words = [
            {
                "content": w.content,
                "polygon": list(w.polygon) if w.polygon else [],
                "confidence": w.confidence,
            }
            for w in (page.words or [])
        ]
        pages.append(
            {
                "page_number": page.page_number,
                "unit": page.unit,
                "width": page.width,
                "height": page.height,
                "words": words,
            }
        )
    return {
        "model_id": "prebuilt-layout",
        "api_version": getattr(result, "api_version", "unknown"),
        "pages": pages,
    }


def detect_candidates(extraction: dict) -> list:
    """Stage 2: detection. Illustrative single/two-word keyword matching only."""
    candidates = []
    for page in extraction["pages"]:
        words = page["words"]
        for idx, word in enumerate(words):
            content_lower = word["content"].lower().strip(".,;:")
            if content_lower in ILLUSTRATIVE_TERMS:
                candidates.append(
                    {
                        "page_number": page["page_number"],
                        "unit": page["unit"],
                        "matched_text": word["content"],
                        "polygons": [word["polygon"]],
                        "rule": "illustrative-keyword-list",
                    }
                )
            # Two-word phrase check (e.g. "Native American").
            if idx + 1 < len(words):
                pair = f"{content_lower} {words[idx + 1]['content'].lower().strip('.,;:')}"
                if pair in ILLUSTRATIVE_TERMS:
                    candidates.append(
                        {
                            "page_number": page["page_number"],
                            "unit": page["unit"],
                            "matched_text": f"{word['content']} {words[idx + 1]['content']}",
                            "polygons": [word["polygon"], words[idx + 1]["polygon"]],
                            "rule": "illustrative-keyword-list",
                        }
                    )
    return candidates


def _polygon_to_rect(polygon: list, unit: str) -> fitz.Rect:
    """Convert a Document Intelligence polygon to a PyMuPDF point-space rect.

    Document Intelligence reports polygons in the page's own unit (commonly
    "inch" for born-digital PDFs). PyMuPDF page coordinates are in points
    (1/72 inch). If a future document reports a different unit, this
    conversion must be revisited — it is not validated for every input type.
    """
    xs = polygon[0::2]
    ys = polygon[1::2]
    scale = 72.0 if unit == "inch" else 1.0
    return fitz.Rect(min(xs) * scale, min(ys) * scale, max(xs) * scale, max(ys) * scale)


def render_and_validate(pdf_bytes: bytes, candidates: list) -> tuple:
    """Stage 3: permanent redaction, metadata scrub, and independent re-check.

    Returns (redacted_pdf_bytes, validation_report). Uses PyMuPDF's redaction
    annotations, which remove the underlying text/image content within the
    rectangle (not a visual overlay) when apply_redactions() is called.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for candidate in candidates:
        page = doc[candidate["page_number"] - 1]
        for polygon in candidate["polygons"]:
            if not polygon:
                continue
            rect = _polygon_to_rect(polygon, candidate["unit"])
            page.add_redact_annot(rect, fill=(0, 0, 0))

    for page in doc:
        page.apply_redactions()

    # Strip metadata, embedded files, and JavaScript — not just visible text.
    doc.set_metadata({})
    try:
        doc.scrub(
            attached_files=True,
            embedded_files=True,
            hidden_text=True,
            javascript=True,
            metadata=True,
        )
    except AttributeError:
        # Older PyMuPDF versions may not expose scrub(); metadata is still cleared above.
        pass

    # Save as a fresh file, not an incremental save, so stripped objects do
    # not survive in the file's cross-reference history.
    out_buffer = io.BytesIO()
    doc.save(out_buffer, garbage=4, deflate=True, clean=True)
    redacted_bytes = out_buffer.getvalue()
    doc.close()

    # Independent validation pass: re-open the saved output and confirm the
    # matched text no longer appears anywhere in extractable text.
    check_doc = fitz.open(stream=redacted_bytes, filetype="pdf")
    full_text = "\n".join(p.get_text() for p in check_doc).lower()
    check_doc.close()

    failures = [c["matched_text"] for c in candidates if c["matched_text"].lower() in full_text]
    validation_report = {
        "checked_terms": [c["matched_text"] for c in candidates],
        "failures": failures,
        "passed": len(failures) == 0,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    return redacted_bytes, validation_report


def build_manifest(blob_name: str, source_bytes: bytes, extraction: dict, candidates: list, validation_report: dict) -> dict:
    return {
        "source_blob": blob_name,
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "model_id": extraction["model_id"],
        "api_version": extraction["api_version"],
        "page_count": len(extraction["pages"]),
        "candidates": candidates,
        "validation": validation_report,
        "status": "quarantined" if validation_report["passed"] else "held-validation-failed",
        "note": "ILLUSTRATIVE DEMO MANIFEST. Detection uses a hardcoded keyword list, not a domain-owned taxonomy.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage-account", required=True)
    parser.add_argument("--docintel-endpoint", required=True, help="e.g. https://<resource>.cognitiveservices.azure.com")
    parser.add_argument("--blob-name", required=True)
    parser.add_argument("--originals-container", default="originals")
    parser.add_argument("--quarantine-container", default="quarantine")
    args = parser.parse_args()

    credential = DefaultAzureCredential()

    blob_service = BlobServiceClient(
        account_url=f"https://{args.storage_account}.blob.core.windows.net",
        credential=credential,
    )
    source_client = blob_service.get_blob_client(args.originals_container, args.blob_name)
    pdf_bytes = source_client.download_blob().readall()
    print(f"Downloaded original: {args.blob_name} ({len(pdf_bytes)} bytes)")

    di_client = DocumentIntelligenceClient(endpoint=args.docintel_endpoint, credential=credential)
    extraction = extract_layout(di_client, pdf_bytes)
    print(f"Extracted {len(extraction['pages'])} page(s).")

    candidates = detect_candidates(extraction)
    print(f"Detected {len(candidates)} illustrative candidate(s).")

    redacted_bytes, validation_report = render_and_validate(pdf_bytes, candidates)
    print(f"Validation passed: {validation_report['passed']}")

    manifest = build_manifest(args.blob_name, pdf_bytes, extraction, candidates, validation_report)

    quarantine_container = blob_service.get_container_client(args.quarantine_container)
    quarantine_container.upload_blob(args.blob_name, redacted_bytes, overwrite=True)
    quarantine_container.upload_blob(
        f"{args.blob_name}.manifest.json",
        json.dumps(manifest, indent=2),
        overwrite=True,
    )
    print(f"Uploaded candidate derivative and manifest to '{args.quarantine_container}'. Awaiting human review.")


if __name__ == "__main__":
    main()
