"""Minimal human-review gate for the low-cost demo.

ILLUSTRATIVE ONLY. This is a stand-in for the proposed human-review and
exception workflow (docs/architecture.md#human-review-and-exceptions). It
has no role separation (one person both "submits" and "approves" in this
demo), no audit-grade storage, and no legal authority. It exists only to
demonstrate the principle that nothing moves from quarantine to approved
without an explicit step.
"""

import argparse
import json
from datetime import datetime, timezone

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


def list_pending(blob_service: BlobServiceClient, quarantine_container: str) -> None:
    container = blob_service.get_container_client(quarantine_container)
    manifests = [b.name for b in container.list_blobs() if b.name.endswith(".manifest.json")]
    if not manifests:
        print("No pending candidates in quarantine.")
        return
    for name in manifests:
        data = container.download_blob(name).readall()
        manifest = json.loads(data)
        print(f"--- {manifest['source_blob']} ---")
        print(f"  status: {manifest['status']}")
        print(f"  candidates detected: {len(manifest['candidates'])}")
        for c in manifest["candidates"]:
            print(f"    page {c['page_number']}: '{c['matched_text']}' ({c['rule']})")
        print(f"  validation passed: {manifest['validation']['passed']}")


def approve(blob_service: BlobServiceClient, quarantine_container: str, approved_container: str, blob_name: str) -> None:
    quarantine = blob_service.get_container_client(quarantine_container)
    approved = blob_service.get_container_client(approved_container)

    manifest_name = f"{blob_name}.manifest.json"
    manifest = json.loads(quarantine.download_blob(manifest_name).readall())

    if not manifest["validation"]["passed"]:
        print("REFUSING to approve: independent validation did not pass. Resolve and re-run the pipeline first.")
        return

    pdf_bytes = quarantine.download_blob(blob_name).readall()
    approved.upload_blob(blob_name, pdf_bytes, overwrite=True)

    manifest["status"] = "approved"
    manifest["approved_at"] = datetime.now(timezone.utc).isoformat()
    manifest["approval_note"] = "Approved via demo review_cli.py — single-operator demo, not a real reviewer role."
    approved.upload_blob(manifest_name, json.dumps(manifest, indent=2), overwrite=True)

    print(f"Approved '{blob_name}'. Copied to '{approved_container}'. No automatic release occurred before this step.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage-account", required=True)
    parser.add_argument("--quarantine-container", default="quarantine")
    parser.add_argument("--approved-container", default="approved")
    parser.add_argument("--list", action="store_true", help="List pending candidates")
    parser.add_argument("--approve", metavar="BLOB_NAME", help="Approve and release a candidate by blob name")
    args = parser.parse_args()

    credential = DefaultAzureCredential()
    blob_service = BlobServiceClient(
        account_url=f"https://{args.storage_account}.blob.core.windows.net",
        credential=credential,
    )

    if args.list:
        list_pending(blob_service, args.quarantine_container)
    elif args.approve:
        approve(blob_service, args.quarantine_container, args.approved_container, args.approve)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
