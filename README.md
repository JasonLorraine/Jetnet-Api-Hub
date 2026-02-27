# JETNET API Documentation & Examples

The complete developer guide for working with the JETNET API (Jetnet Connect) -- the aviation industry's most comprehensive aircraft intelligence database. Cradle-to-grave data on every business jet, turboprop, helicopter, and airliner: specifications, ownership, transactions, flight activity, valuations, and more.

**Base URL:** `https://customer.jetnetconnect.com`
**Swagger:** `https://customer.jetnetconnect.com/swagger/index.html`

---

## Table of Contents

- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [The Golden Path](#the-golden-path)
- [Documentation](#documentation)
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

**Python**

```python
import requests, os

BASE = "https://customer.jetnetconnect.com"

r = requests.post(f"{BASE}/api/Admin/APILogin", json={
    "emailAddress": os.environ["JETNET_EMAIL"],   # capital A in emailAddress
    "password": os.environ["JETNET_PASSWORD"]
})
r.raise_for_status()
data = r.json()

bearer = data["bearerToken"]
token  = data["apiToken"]
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
  body: JSON.stringify({ emailAddress: EMAIL, password: PASS })
});
const data = await r.json();

const bearer = data.bearerToken;
const token  = data.apiToken;
console.log(`Authenticated. Token: ${token.slice(0, 8)}...`);
```

### 3. Look up an aircraft by tail number

```python
headers = {"Authorization": f"Bearer {bearer}"}
r = requests.get(f"{BASE}/api/Aircraft/getRegNumber/N650GD/{token}", headers=headers)
aircraft = r.json()["aircraftresult"]

print(f"{aircraft['regnbr']} | {aircraft['make']} {aircraft['model']} | SN: {aircraft['serialnbr']}")
```

That's it. You're connected.

---

## Repository Structure

```
jetnet-api-docs/
│
├── README.md                           ← You are here
│
├── docs/                               ← Core documentation
│   ├── authentication.md               ← Login, tokens, refresh, retry
│   ├── pagination.md                   ← Paged endpoints, loop patterns
│   ├── response-handling.md            ← Response structure, schema differences
│   ├── id-system.md                    ← aircraftid vs regnbr vs modelid
│   ├── common-mistakes.md              ← Every gotcha and how to fix it
│   └── enum-reference.md              ← Valid values for every enum field
│
├── examples/                           ← Complete runnable examples
│   ├── python/                         ← Python examples (requests + Flask)
│   │   ├── 01_authentication.py
│   │   ├── 02_tail_lookup.py
│   │   ├── 03_fleet_search.py
│   │   ├── 04_ownership.py
│   │   ├── 05_flight_activity.py
│   │   ├── 06_valuation.py
│   │   ├── 07_bulk_export.py
│   │   └── 08_golden_path_server.py
│   └── javascript/                     ← JavaScript examples (fetch + Express)
│       ├── 01_authentication.js
│       ├── 02_tail_lookup.js
│       ├── 03_fleet_search.js
│       ├── 04_ownership.js
│       ├── 05_flight_activity.js
│       ├── 06_valuation.js
│       ├── 07_bulk_export.js
│       └── 08_golden_path_server.js
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
│   └── validate_payload.py            ← Payload validator (catches mistakes)
│
└── references/                         ← Complete reference material
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
| [ID System](docs/id-system.md) | `aircraftid` vs `regnbr` vs `modelid` vs `companyid` |
| [Common Mistakes](docs/common-mistakes.md) | Every known gotcha with explanations and fixes |
| [Enum Reference](docs/enum-reference.md) | Valid values for `airframetype`, `maketype`, `transtype`, etc. |

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

---

## References

| Reference | Description |
|-----------|-------------|
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
