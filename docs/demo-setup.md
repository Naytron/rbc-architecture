# Low-cost demo setup (commercial Azure analog)

**This is a personal learning demo in commercial Azure, not Azure Government, and not a reproduction of the customer engagement.** The rest of this repository proposes a Government reference architecture. Azure Government subscriptions require special eligibility (U.S. government agencies, contractors, or qualifying entities) [S1](sources.md#s1---government-development-and-availability), so most individuals cannot provision one for an interview demo. This guide deliberately substitutes commercial Azure endpoints and simplifies several production controls to keep cost near zero and setup under an hour. Every simplification is labeled below so you can explain the gap between "what I built as a demo" and "what the proposed Government architecture requires."

If you are later asked "does this run in Government?", the honest answer is: the demo validates the **pipeline logic** (extract, detect, redact, validate, hold-for-review), not Government identity, networking, or SKU availability. Those remain gated per [Azure Government verification](azure-government-verification.md).

## What this demo proves and what it does not

| Proves | Does not prove |
| --- | --- |
| The four-stage separation (extraction, detection, rendering/validation, human review) works end to end on a real Document Intelligence call. | Azure Government endpoint, identity authority, or DNS compatibility. |
| Permanent content removal (not a drawn box) using a real PDF library, with an independent validation pass. | Production-scale throughput, concurrency, or failure-injection testing. |
| A human-review gate that blocks automatic release of unapproved derivatives. | That detection logic (simple keyword rules here) is adequate for real case documents. |
| Managed, auditable Azure resource provisioning via CLI. | Private networking, Key Vault-backed secrets, or multi-account isolation (ADR-003 uses three storage accounts; this demo uses one, with three containers, to cut cost). |

## Cost overview

Every resource below is pay-as-you-go with a cost close to zero for a handful of test documents, but **none is contractually free forever** — verify current pricing in the Azure Portal calculator before you create resources, and tear everything down when you finish practicing.

| Resource | Demo tier | Why |
| --- | --- | --- |
| Resource group | n/a | Free; lets you delete everything in one command. |
| Storage account | Standard LRS, Blob + Queue | Cheapest redundancy tier; pennies for a few test documents. |
| Document Intelligence | `S0` (pay-as-you-go), or `F0` (free tier) if available on your subscription | `S0` bills per page analyzed. Community reports describe an `F0` tier limited to about 2 pages per document and roughly 500 pages per month, but this was **not** confirmed in the official pricing documentation fetched for this repository — check the Portal's own pricing tier picker for your subscription before relying on `F0` limits. |
| Compute | Your laptop (local Python script), no Function App or VM | Removes compute hosting cost and lets you run the pipeline interactively while you talk through it. |
| Key Vault | Not created | No long-lived secret is needed; the demo authenticates with your own `az login` session (see identity note below). |
| Service Bus | Not created | The proposed architecture uses Service Bus Premium for private-endpoint queueing [S9](sources.md#s9---service-bus-private-networking); this demo uses the Storage Queue that ships with the storage account, since a single-operator demo does not need Premium messaging. |

Expect well under $5 total if you delete resources promptly after practicing. Nothing here should be left running unattended.

## Deliberate simplifications versus the proposed Government architecture

State these out loud in the interview if asked "did you actually deploy the full design" — the answer is no, and here is exactly what differs and why:

| Proposed Government architecture | This demo | Why the demo differs |
| --- | --- | --- |
| Separate original / derivative / control storage accounts (ADR-003) | One storage account, three containers (`originals`, `quarantine`, `approved`) | Three accounts triples minimum storage cost and setup steps for a demo with no real access-control requirement. |
| Service Bus Premium with private endpoints (ADR-002) | Storage Queue, public endpoint | Premium tier has an hourly cost regardless of use; a demo queue does not need private networking. |
| API and worker on Government VMs (ADR-004) | A local Python CLI script you run yourself | Removes VM hosting/patching cost and avoids standing up a network boundary for a single-operator demo. |
| User authentication separate from service identity (security doc) | You authenticate as yourself via `az login`; the script uses your own Entra token for both "submission" and "processing" | A one-person demo has no second identity to separate. State plainly that production requires this separation and show where a managed identity would replace your user token. |
| Private endpoints, VNet, Government DNS zones | Public service endpoints over TLS, commercial cloud | Private endpoints add cost (and are a Government-specific verification gate) that is unnecessary to demonstrate pipeline logic. |
| Verified GA Document Intelligence API/region/SKU combination (Government gate) | Latest GA commercial API version, your nearest commercial region | Commercial Azure has broader, more documented regional availability; this sidesteps the unverified Government combination entirely. |
| Versioned, domain-owner-approved detection taxonomy (architecture doc) | A small hardcoded keyword list, explicitly illustrative | Building a real taxonomy requires legal/domain ownership this demo does not have. |

## Prerequisites

- An Azure subscription (commercial, e.g. a free trial or pay-as-you-go) and the Azure CLI (`az`) signed in: `az login`.
- Python 3.10+.
- A terminal. No IDE or cloud shell is required.

## Step 1 — Resource group and variables

```bash
export RG=rg-rbc-demo
export LOCATION=eastus
export STORAGE=strbcdemo$RANDOM
export DOCINTEL=rbc-demo-docintel-$RANDOM

az group create --name "$RG" --location "$LOCATION"
```

Pick any commercial region near you; this demo makes no Government region claim.

## Step 2 — Storage account and containers

```bash
az storage account create \
  --name "$STORAGE" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --kind StorageV2

for c in originals quarantine approved; do
  az storage container create \
    --account-name "$STORAGE" \
    --name "$c" \
    --auth-mode login
done
```

`originals` holds the synthetic test document, `quarantine` holds rendered candidates awaiting human approval, `approved` holds released derivatives — a scaled-down version of the proposed original/derivative separation (ADR-003).

## Step 3 — Document Intelligence resource

A **custom subdomain is required** for Entra ID (token-based) authentication; the default regional endpoint does not support it [S4](sources.md#s4---document-intelligence-authentication). This mirrors the same requirement called out for Government in this repository, so practicing it here is directly transferable.

```bash
az cognitiveservices account create \
  --name "$DOCINTEL" \
  --resource-group "$RG" \
  --kind FormRecognizer \
  --sku S0 \
  --location "$LOCATION" \
  --custom-domain "$DOCINTEL" \
  --yes
```

If your subscription offers an `F0` free tier for this resource kind, you can substitute `--sku F0`, but confirm the current page/month limits in the Portal first — see the cost table above.

## Step 4 — Grant yourself data-plane roles (no stored keys)

The demo authenticates with your own signed-in identity instead of an API key, which is the pattern the proposed architecture also prefers for service-to-service calls [S4](sources.md#s4---document-intelligence-authentication).

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

az role assignment create \
  --assignee "$USER_OBJECT_ID" \
  --role "Cognitive Services User" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$DOCINTEL"

az role assignment create \
  --assignee "$USER_OBJECT_ID" \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/$STORAGE"
```

Role assignments can take a few minutes to propagate. In the proposed Government architecture, a worker's **managed identity** would hold these same two roles instead of a human user — point this out explicitly if asked, since it is the clearest "demo versus production" identity gap.

## Step 5 — Install the demo scripts

```bash
cd demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

See [`demo/README.md`](../demo/README.md) for what each script does. All demo code is intentionally small, synchronous, and single-document — it demonstrates the four proposed stages (extraction, detection, rendering/validation, human review), not the proposed asynchronous queue/worker topology (ADR-002).

## Step 6 — Generate a synthetic test document

```bash
python3 generate_sample_pdf.py --out sample.pdf
```

This writes a one-page PDF containing the same synthetic sentence used in [`examples/synthetic-input.md`](../examples/synthetic-input.md): a fictional person and a fictional location. No real case material exists anywhere in this repository or demo.

## Step 7 — Upload the original and run the pipeline

```bash
az storage blob upload \
  --account-name "$STORAGE" \
  --container-name originals \
  --name sample.pdf \
  --file sample.pdf \
  --auth-mode login

python3 pipeline.py \
  --storage-account "$STORAGE" \
  --docintel-endpoint "https://$DOCINTEL.cognitiveservices.azure.com" \
  --blob-name sample.pdf
```

`pipeline.py` performs, as separately named functions mirroring ADR-001:

1. **Extract** — calls Document Intelligence Layout (commercial GA endpoint) and stores page/word/polygon output.
2. **Detect** — applies a small, explicitly illustrative keyword list against the extracted text to find candidate spans. This is a stand-in for the versioned, domain-owned taxonomy the real architecture requires — say so if asked.
3. **Render and validate** — uses a PDF library to permanently remove the matched text (not draw a box over it), strip document metadata, and re-extract text from the output to confirm the target string no longer appears.
4. **Hold** — writes the candidate derivative and a JSON manifest to the `quarantine` container; nothing is released automatically.

## Step 8 — Run the human-review step

```bash
python3 review_cli.py \
  --storage-account "$STORAGE" \
  --list
```

This lists pending quarantined candidates with their manifest (what was detected, what was removed). Approve one to simulate the specialist-approval gate from the [human-review workflow](architecture.md#human-review-and-exceptions):

```bash
python3 review_cli.py \
  --storage-account "$STORAGE" \
  --approve sample.pdf
```

Approving copies the exact validated blob from `quarantine` to `approved` and appends an approval record to the manifest. Nothing reaches `approved` without this explicit step — the same "no silent release" principle as the proposed architecture, just without a second human role to separate reviewer-from-specialist.

## Step 9 — Inspect the result

Download the approved derivative and confirm visually and by text search that the detected phrase is gone, while unrelated context remains:

```bash
az storage blob download \
  --account-name "$STORAGE" \
  --container-name approved \
  --name sample.pdf \
  --file approved.pdf \
  --auth-mode login
```

## Step 10 — Tear down (do this every time you stop practicing)

```bash
az group delete --name "$RG" --yes --no-wait
```

Deleting the resource group removes the storage account, containers, and Document Intelligence resource together. Confirm deletion completed in the Portal or with `az group exists --name "$RG"` before considering the demo "off."

## If you are asked to extend this toward the proposed architecture

Be ready to describe, without claiming you built it, how you would evolve this demo:

- Replace the local script's polling loop with a **durable queue message and a worker process** (Storage Queue first, Service Bus Premium once private endpoints are required) — ADR-002.
- Move the worker to a **managed identity** (Function App, VM, or container) instead of your own `az login` session — closes the identity gap called out in Step 4.
- Split `originals`/`quarantine`/`approved` into **separate storage accounts** once more than one person needs different access levels — ADR-003.
- Replace the keyword list with a **versioned, domain-owned taxonomy**, and evaluate it with the measures in [evaluation and operations](evaluation-and-operations.md) before trusting it beyond a demo.
- Re-run the full [Government readiness gates](azure-government-verification.md) before assuming any of this transfers to an Azure Government tenant — commercial availability is not evidence of Government parity.
