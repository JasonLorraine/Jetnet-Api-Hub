# JETNET API Documentation & Examples

The complete developer guide for working with the JETNET API (Jetnet Connect) -- the aviation industry's most comprehensive aircraft intelligence database. Cradle-to-grave data on every business jet, turboprop, helicopter, and airliner: specifications, ownership, transactions, flight activity, valuations, and more.

**Base URL:** `https://customer.jetnetconnect.com`
**Swagger:** `https://customer.jetnetconnect.com/swagger/index.html`

> **New here?** Go to **[START_HERE.md](START_HERE.md)** -- pick your path and get running in minutes.
> Demo UI | Bulk Data | CRM Enrichment | **AI Agent / Code Agent**
>
> **AI / LLM?** Ingest [`llms.txt`](llms.txt) (concise) or [`llms-full.txt`](llms-full.txt) (complete) for your context window.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Run on Replit](#run-on-replit)
- [Token Validation Strategy](#token-validation-strategy)
- [Repository Structure](#repository-structure)
- [The Golden Path](#the-golden-path)
- [Documentation](#documentation)
- [Templates](#templates)
- [Prompts (AI-Native)](#prompts-ai-native)
- [Code Examples](#code-examples)
- [Quick Reference Snippets](#quick-reference-snippets)
- [Helper Scripts](#helper-scripts)
- [References](#references)
- [Common Mistakes](#common-mistakes)

---

## Quick Start

### 1. Set your credentials

Store your JETNET credentials as environment variables:

```bash
export JETNET_EMAIL="your_email@example.com"
export JETNET_PASSWORD="your_password"
```

### 2. Authenticate

> **Guardrail: `emailAddress` casing.** The field is `emailAddress` with a capital **A**. Using `emailaddress`, `email`, or `email_address` will fail silently.

**Python**

```python
import requests, os

BASE = "https://customer.jetnetconnect.com"

r = requests.post(f"{BASE}/api/Admin/APILogin", json={
    "emailAddress": os.environ["JETNET_EMAIL"],   # capital A -- not emailaddress
    "password": os.environ["JETNET_PASSWORD"]
})
r.raise_for_status()
data = r.json()

bearer = data["bearerToken"]   # goes in Authorization header
token  = data["apiToken"]      # goes in URL path -- never in headers or body
print(f"Authenticated. Token: {token[:8]}...")
```

**JavaScript**

```javascript
const BASE  = "https://customer.jetnetconnect.com";
const EMAIL = process.env.JETNET_EMAIL;
const PASS  = process.env.JETNET_PASSWORD;

const r = await fetch(`${BASE}/api/Admin/APILogin`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ emailAddress: EMAIL, password: PASS })  // capital A
});
const data = await r.json();

const bearer = data.bearerToken;  // goes in Authorization header
const token  = data.apiToken;     // goes in URL path -- never in headers or body
console.log(`Authenticated. Token: ${token.slice(0, 8)}...`);
```

> **Guardrail: Token placement.** `bearerToken` goes in the `Authorization: Bearer {bearerToken}` header. `apiToken` goes in the URL path (e.g. `/getRegNumber/N1KE/{apiToken}`). Do not swap them.

### 3. Look up an aircraft by tail number

> **Guardrail: HTTP 200 does not mean success.** Always check `responsestatus` in the JSON body before using the data.

```python
headers = {"Authorization": f"Bearer {bearer}"}
r = requests.get(f"{BASE}/api/Aircraft/getRegNumber/N650GD/{token}", headers=headers)
result = r.json()

# Always check responsestatus -- HTTP 200 does not mean success
status = result.get("responsestatus", "")
if "ERROR" in status.upper():
    raise ValueError(f"JETNET error: {status}")

aircraft = result["aircraftresult"]
print(f"{aircraft['regnbr']} | {aircraft['make']} {aircraft['model']} | SN: {aircraft['serialnbr']}")
```

> **Guardrail: Date format.** All date fields require `MM/DD/YYYY` with leading zeros. Use `"01/01/2024"` not `"1/1/2024"`. Month comes first (not day).

That's it. You're connected.

For production apps, use the session helpers instead of managing tokens manually:
- **Python:** [`src/jetnet/session.py`](src/jetnet/session.py)
- **TypeScript:** [`src/jetnet/session.ts`](src/jetnet/session.ts)

## Run on Replit

### Option A -- Python (recommended)

1. **Create a Repl** -- Go to Replit, click **Create Repl**, choose **Python**, and import this repo (or paste the GitHub URL).
2. **Add credentials** -- Open **Tools > Secrets** (padlock icon) and add:
   - `JETNET_EMAIL` = your login email
   - `JETNET_PASSWORD` = your password
3. **Install dependencies** -- In the Shell: `pip install -r requirements.txt`
4. **Run a demo** -- `python examples/python/02_tail_lookup.py N650GD`

### Option B -- Node.js

1. **Create a Repl** -- Choose **Node.js** and import this repo.
2. **Add credentials** -- Same as above: `JETNET_EMAIL` and `JETNET_PASSWORD` in **Secrets**.
3. **Install dependencies** -- In the Shell: `npm install`
4. **Run a demo** -- `node examples/javascript/02_tail_lookup.js N650GD`

### Troubleshooting (Replit)

| Issue | Fix |
|-------|-----|
| Missing env vars | Set `JETNET_EMAIL` and `JETNET_PASSWORD` in **Secrets**, then restart the Repl |
| Auth/token errors | Tokens expire after 60 min; the examples re-login automatically. Re-run the command. |
| Module not found | Run `pip install -r requirements.txt` (Python) or `npm install` (Node) |
| Wrong working directory | Run commands from the repo root (where `examples/` lives) |

## Token Validation Strategy

Tokens expire after 60 minutes. We validate via `/getAccountInfo` and auto re-login once.

```python
from src.jetnet.session import login, ensure_session, jetnet_request

session = login("you@example.com", "password", "https://customer.jetnetconnect.com")

session = ensure_session(session)

result = jetnet_request("GET", "/api/Aircraft/getRegNumber/N1KE/{apiToken}", session)
```

The session helpers handle everything: proactive refresh at 50 minutes, validation via `/getAccountInfo`, and one automatic retry on `INVALID SECURITY TOKEN`.

To observe the actual TTL for your tenant:

```bash
python scripts/token_probe.py
# Output: "Observed token TTL: 57m 12s"
```

---

## Repository Structure

```
jetnet-api-docs/
│
├── README.md                           ← You are here
├── START_HERE.md                       ← Choose your path (new here? start here)
├── llms.txt                           ← AI/LLM concise reference (single file)
├── llms-full.txt                      ← AI/LLM complete reference (all docs)
│
├── src/jetnet/                         ← Session helpers (auto-refresh, validation)
│   ├── session.py                      ← Python session module
│   └── session.ts                      ← TypeScript session module
│
├── docs/                               ← Core documentation
│   ├── authentication.md               ← Login, tokens, refresh, retry
│   ├── pagination.md                   ← Paged endpoints, loop patterns
│   ├── response-handling.md            ← Response structure, schema differences
│   ├── response-shapes.md             ← Normalized UI contracts (AircraftCard, etc.)
│   ├── id-system.md                    ← aircraftid vs regnbr vs modelid
│   ├── bulk-export.md                 ← Bulk export: snapshot/delta, change detection
│   ├── history.md                     ← Transaction history & ownership timeline
│   ├── snapshots.md                   ← Historical fleet state at a point in time
│   ├── flight-data.md                 ← Flight activity & monthly utilization
│   ├── common-mistakes.md              ← Every gotcha and how to fix it
│   └── enum-reference.md              ← Valid values for every enum field
│
├── templates/                          ← One-click starter apps
│   ├── nextjs-tail-lookup/            ← Next.js tail lookup UI
│   └── python-fastapi-golden-path/    ← FastAPI backend (Golden Path)
│
├── prompts/                            ← AI prompts (paste into Cursor/Copilot)
│   ├── 01_golden_path_tail_lookup_app.md
│   ├── 02_fbo_airport_activity_leads.md
│   ├── 03_fleet_watchlist_alerts.md
│   └── 04_bulk_export_pipeline.md
│
├── evals/                             ← AI eval test cases
│   └── evals.json
│
├── examples/                           ← Complete runnable examples
│   ├── python/                         ← Python examples (requests + Flask)
│   │   ├── 01_authentication.py ... 08_golden_path_server.py
│   ├── javascript/                     ← JavaScript examples (fetch + Express)
│   │   ├── 01_authentication.js ... 08_golden_path_server.js
│   └── responses/                     ← Known-good JSON response examples (16 files)
│       ├── tail-lookup.json, relationships-single.json, bulk-export-paged.json, ...
│
├── snippets/                           ← Copy-paste quick reference
│   ├── fleet.md                        ← Fleet search snippets
│   ├── ownership.md                    ← Ownership & relationships
│   ├── usage.md                        ← Flight activity & utilization
│   ├── specifications.md              ← Specs, engine, maintenance data
│   └── valuation.md                   ← Market trends & pricing
│
├── scripts/                            ← Production-ready helper utilities
│   ├── paginate.py                     ← Generic pagination helper
│   ├── validate_payload.py            ← Payload validator (catches mistakes)
│   ├── token_probe.py                 ← Measure actual token TTL
│   └── model_search.py               ← Search model IDs by make/model/ICAO
│
└── references/                         ← Complete reference material
    ├── model-ids.md                   ← Model ID lookup (872 models, grouped by type)
    ├── model-id-table.json            ← Machine-readable model reference (872 entries)
    ├── model-id-table.csv             ← Same data in CSV for spreadsheets
    ├── endpoints.md                    ← Every endpoint with parameters
    ├── vertical-playbooks.md          ← Industry-specific workflows
    └── buildkit.md                    ← App builder guide (Node + Python)
```

---

## The Golden Path

The most common workflow: look up an aircraft by tail number and build a complete profile.

```
1. getRegNumber/{reg}/{apiToken}           → GET  → aircraftid
2. getPictures/{aircraftid}/{apiToken}     → GET  → pictures[]
   getRelationships/{apiToken}             → POST → relationships[]
   getFlightDataPaged/{apiToken}/100/1     → POST → flightdata[]   (parallel)
3. getHistoryListPaged/{apiToken}/100/1    → POST → history[]      (lazy)
   getEventListPaged/{apiToken}/100/1      → POST → events[]       (lazy)
```

**Why this order:** `aircraftid` is the join key for everything. You cannot call pictures, relationships, or flight endpoints without it. Steps 2 runs in parallel for speed. Step 3 loads on demand to keep the initial response fast.

See the full working implementation:
- **Python:** [`examples/python/08_golden_path_server.py`](examples/python/08_golden_path_server.py)
- **JavaScript:** [`examples/javascript/08_golden_path_server.js`](examples/javascript/08_golden_path_server.js)
- **App builder guide:** [`references/buildkit.md`](references/buildkit.md)

---

## Documentation

| Guide | What you'll learn |
|-------|-------------------|
| [Authentication](docs/authentication.md) | Login, token handling, refresh strategy, retry pattern |
| [Pagination](docs/pagination.md) | Paged endpoints, loop patterns, maxpages quirks |
| [Response Handling](docs/response-handling.md) | Response structure, schema differences by endpoint |
| [Response Shapes](docs/response-shapes.md) | Normalized UI contracts: AircraftCard, CompanyCard, GoldenPathResult |
| [Bulk Export](docs/bulk-export.md) | Snapshot vs delta mode, graph-based change detection, integration pattern |
| [History](docs/history.md) | Transaction events: ownership timeline, comparable sales, leasing intelligence |
| [Snapshots](docs/snapshots.md) | Historical fleet state at a point in time (`getCondensedSnapshot`) |
| [Flight Data](docs/flight-data.md) | Flight activity + monthly utilization: getFlightData vs getFlights |
| [ID System](docs/id-system.md) | `aircraftid` vs `regnbr` vs `modelid` vs `companyid` |
| [Common Mistakes](docs/common-mistakes.md) | Every known gotcha with explanations and fixes |
| [Enum Reference](docs/enum-reference.md) | Valid values for `airframetype`, `maketype`, `transtype`, etc. |

---

## Templates

Starter apps that run out of the box. Copy `.env.example` to `.env`, add your credentials, and go.

| Template | Stack | What it does |
|----------|-------|-------------|
| [nextjs-tail-lookup](templates/nextjs-tail-lookup/) | Next.js (App Router) | Tail number input → aircraft card + owner/operator |
| [python-fastapi-golden-path](templates/python-fastapi-golden-path/) | FastAPI + requests | `/lookup?tail=N12345` → normalized GoldenPathResult |

Both templates use session helpers with `/getAccountInfo` health checks and auto token refresh.

---

## Prompts (AI-Native)

Copy-paste these into Cursor, Copilot, or ChatGPT to generate working apps that follow JETNET best practices.

| Prompt | Use case |
|--------|----------|
| [01 Golden Path Tail Lookup](prompts/01_golden_path_tail_lookup_app.md) | Build a tail lookup app with aircraft card + owner/operator |
| [02 FBO Airport Activity Leads](prompts/02_fbo_airport_activity_leads.md) | Airport-based flight activity for FBO lead generation |
| [03 Fleet Watchlist Alerts](prompts/03_fleet_watchlist_alerts.md) | Monitor a fleet by model, alert on ownership changes |
| [04 Bulk Export Pipeline](prompts/04_bulk_export_pipeline.md) | Paginated bulk export with incremental sync |

Each prompt includes the exact API call sequence, error handling rules, and references the session helpers. See [`prompts/README.md`](prompts/README.md) for how to use them.

---

## Code Examples

### Python

| Example | Description |
|---------|-------------|
| [01_authentication.py](examples/python/01_authentication.py) | Login and get tokens |
| [02_tail_lookup.py](examples/python/02_tail_lookup.py) | Look up aircraft by tail number |
| [03_fleet_search.py](examples/python/03_fleet_search.py) | Search for-sale inventory by model |
| [04_ownership.py](examples/python/04_ownership.py) | Get owner/operator relationships |
| [05_flight_activity.py](examples/python/05_flight_activity.py) | Query flight data with pagination |
| [06_valuation.py](examples/python/06_valuation.py) | Market trends and pricing context |
| [07_bulk_export.py](examples/python/07_bulk_export.py) | Bulk aircraft export with pagination |
| [08_golden_path_server.py](examples/python/08_golden_path_server.py) | Full Flask server (Golden Path) |

### JavaScript

| Example | Description |
|---------|-------------|
| [01_authentication.js](examples/javascript/01_authentication.js) | Login and get tokens |
| [02_tail_lookup.js](examples/javascript/02_tail_lookup.js) | Look up aircraft by tail number |
| [03_fleet_search.js](examples/javascript/03_fleet_search.js) | Search for-sale inventory by model |
| [04_ownership.js](examples/javascript/04_ownership.js) | Get owner/operator relationships |
| [05_flight_activity.js](examples/javascript/05_flight_activity.js) | Query flight data with pagination |
| [06_valuation.js](examples/javascript/06_valuation.js) | Market trends and pricing context |
| [07_bulk_export.js](examples/javascript/07_bulk_export.js) | Bulk aircraft export with pagination |
| [08_golden_path_server.js](examples/javascript/08_golden_path_server.js) | Full Express server (Golden Path) |

---

## Quick Reference Snippets

Copy-paste-ready code for the most common tasks:

| Snippet | Use case |
|---------|----------|
| [Fleet](snippets/fleet.md) | Search aircraft by model, find for-sale inventory, fleet by geography |
| [Ownership](snippets/ownership.md) | Owner/operator lookup, ownership history, bulk relationships |
| [Usage](snippets/usage.md) | Flight activity, utilization analysis, airport traffic |
| [Specifications](snippets/specifications.md) | Performance specs, engine data, maintenance, avionics |
| [Valuation](snippets/valuation.md) | Market trends, comparable sales, price history |

---

## Session Helpers

Production-ready session modules that handle login, token refresh, and validation automatically:

| Module | Language | Features |
|--------|----------|----------|
| [`src/jetnet/session.py`](src/jetnet/session.py) | Python | `login()`, `ensure_session()`, `jetnet_request()`, `normalize_error()` |
| [`src/jetnet/session.ts`](src/jetnet/session.ts) | TypeScript | `login()`, `ensureSession()`, `jetnetRequest()`, `normalizeError()` |

Both modules validate tokens via `/api/Admin/getAccountInfo`, proactively refresh at 50 minutes, and auto re-login once on `INVALID SECURITY TOKEN`.

---

## Helper Scripts

### [`scripts/paginate.py`](scripts/paginate.py)

Generic pagination helper that fetches all pages from any JETNET paged endpoint.

```python
from scripts.paginate import paginate_all

all_history = paginate_all(
    bearer=bearer,
    token=token,
    base_path="/api/Aircraft/getHistoryListPaged",
    body={
        "modlist": [145],
        "startdate": "01/01/2024",
        "enddate": "12/31/2024",
        "transtype": ["None"],
        "allrelationships": False,
        "airframetype": "None",
        "maketype": "None",
        "isnewaircraft": "Ignore",
        "aclist": []
    },
    pagesize=100
)
print(f"Total records: {len(all_history)}")
```

### [`scripts/validate_payload.py`](scripts/validate_payload.py)

Validates request payloads before sending -- catches the most common mistakes.

```python
from scripts.validate_payload import validate

errors = validate("getHistoryListPaged", {
    "modlist": [145],
    "startdate": "1/1/2024",    # will flag: missing leading zeros
    "transtype": [],            # will flag: use ["None"] not []
})
for e in errors:
    print(f"  ERROR: {e}")
```

### [`scripts/model_search.py`](scripts/model_search.py)

Search the JETNET model-ID reference table. Find the `AMODID` values to use in `modlist`.

```bash
python scripts/model_search.py "G550"
#   AMODID=278  GULFSTREAM G550  ICAO=GLF5  Business Jet  fleet=622

python scripts/model_search.py "citation"
#   37 models found, with ready-to-use modlist array

python scripts/model_search.py
# Interactive mode -- type, see results, repeat
```

### [`scripts/token_probe.py`](scripts/token_probe.py)

Measures the practical token TTL for your account by polling `/getAccountInfo` until failure.

```bash
python scripts/token_probe.py
# Output: "Observed token TTL: 57m 12s"
# Results saved to .cache/token_probe.json
```

---

## References

| Reference | Description |
|-----------|-------------|
| [Model ID Lookup](references/model-ids.md) | 872 aircraft models with AMODID values for `modlist` -- grouped by type |
| [Model ID Table (JSON)](references/model-id-table.json) | Machine-readable model reference for scripts and apps |
| [Model ID Table (CSV)](references/model-id-table.csv) | Same data in CSV for Excel/spreadsheet users |
| [Full Endpoint Reference](references/endpoints.md) | Every endpoint with all parameters |
| [Vertical Playbooks](references/vertical-playbooks.md) | Industry workflows (brokerage, OEM, FBO, MRO, finance, charter) |
| [Build Kit](references/buildkit.md) | App builder guide with full Node.js + Python examples |

---

## Common Mistakes

The biggest time-savers, all in one place:

| Mistake | Fix |
|---------|-----|
| `emailaddress` in login | Use `emailAddress` (capital A) |
| `apiToken` in headers/body | `apiToken` goes in the **URL path only** |
| Empty `transtype: []` | Use `["None"]` to get all transaction types |
| Dates without leading zeros | Use `"01/01/2024"` not `"1/1/2024"` |
| HTTP 200 = success | Always check `responsestatus` for `"ERROR"` |
| Using `regnbr` as database key | Use `aircraftid` -- tail numbers can change |
| `forsale` as boolean | It's a string: `"true"` / `"false"` in requests |
| `companyrelation` vs `relationtype` | Different endpoints use different field names |

Full list with detailed explanations: [Common Mistakes Guide](docs/common-mistakes.md)

---

## Two-Tier Model

JETNET endpoints fall into two tiers:

**Tier A -- Interactive / Real-time**
Tail lookup, owner/operator, pictures, quick flight summary, CRM enrichment.
One aircraft at a time. Low volume. User is waiting.

**Tier B -- Bulk / Data Engineering**
Nightly sync, history exports, analytics pipelines, large event windows.
Always paged. Run async. Never drive a live UI off these.

If building an app or a script for a salesperson: **Tier A.**
If building bulk exports, nightly refreshes, or history across thousands of aircraft: **Tier B.**

---

## Authentication Quick Reference

```
POST /api/Admin/APILogin
Body: { "emailAddress": "...", "password": "..." }

Response: { "bearerToken": "...", "apiToken": "..." }

Every subsequent call:
  Header:  Authorization: Bearer {bearerToken}
  URL:     .../{apiToken}/...
```

Tokens expire after 60 minutes. For pipelines, refresh proactively after 50 minutes.
On `INVALID SECURITY TOKEN`: re-login and retry once. Never loop.

---

## Contributing

Contributions are welcome. Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
