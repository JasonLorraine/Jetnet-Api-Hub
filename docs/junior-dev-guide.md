# Junior Developer Guide

Everything a new developer needs to start building with the JETNET API. This guide cuts through the 40+ endpoints and shows you only what matters for your first integration.

---

## The 4 Endpoints That Matter First

You don't need to learn 40 endpoints. Start with these 4:

| # | Endpoint | What It Does |
|---|----------|-------------|
| 1 | `POST /api/Admin/APILogin` | Get your tokens |
| 2 | `GET /api/Aircraft/getRegNumber/{reg}/{apiToken}` | Look up a tail number |
| 3 | `GET /api/Aircraft/getAircraft/{id}/{apiToken}` | Get full aircraft record |
| 4 | `POST /api/Aircraft/getRelationships/{apiToken}` | Get owner/operator |

That's it. Everything else is optional until you need it.

---

## Step 1: Authenticate (2 minutes)

```python
import requests

BASE = "https://customer.jetnetconnect.com"

resp = requests.post(f"{BASE}/api/Admin/APILogin", json={
    "emailAddress": "your_email@example.com",
    "password": "your_password"
})

data = resp.json()
bearer = data["bearerToken"]
api_token = data["apiToken"]
```

**Three things to remember:**
- `emailAddress` has a capital **A** -- `emailaddress` fails silently
- You get two tokens: `bearerToken` goes in the `Authorization` header, `apiToken` goes in the URL path
- Tokens expire after 60 minutes -- refresh at 50 minutes

```javascript
const BASE = "https://customer.jetnetconnect.com";

const resp = await fetch(`${BASE}/api/Admin/APILogin`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    emailAddress: "your_email@example.com",
    password: "your_password"
  })
});

const { bearerToken, apiToken } = await resp.json();
```

> **Don't build your own auth logic.** Copy [`src/jetnet/session.py`](../src/jetnet/session.py) (Python) or [`src/jetnet/session.ts`](../src/jetnet/session.ts) (TypeScript) into your project. They handle login, token refresh, retry on expired tokens, and error normalization automatically.

---

## Step 2: Look Up a Tail Number

```python
headers = { "Authorization": f"Bearer {bearer}" }

resp = requests.get(
    f"{BASE}/api/Aircraft/getRegNumber/N650GD/{api_token}",
    headers=headers
)

data = resp.json()

# IMPORTANT: Always check responsestatus first
if not data.get("responsestatus", "").startswith("SUCCESS"):
    print(f"Error: {data.get('responsestatus')}")
else:
    aircraft = data["aircraftresult"]
    aircraft_id = aircraft["aircraftid"]
    print(f"Found: {aircraft['make']} {aircraft['model']} (ID: {aircraft_id})")
```

```javascript
const resp = await fetch(
  `${BASE}/api/Aircraft/getRegNumber/N650GD/${apiToken}`,
  { headers: { Authorization: `Bearer ${bearerToken}` } }
);

const data = await resp.json();

if (!data.responsestatus?.startsWith("SUCCESS")) {
  console.error("Error:", data.responsestatus);
} else {
  const aircraft = data.aircraftresult;
  console.log(`Found: ${aircraft.make} ${aircraft.model} (ID: ${aircraft.aircraftid})`);
}
```

---

## Step 3: Get the Full Aircraft Record

```python
resp = requests.get(
    f"{BASE}/api/Aircraft/getAircraft/{aircraft_id}/{api_token}",
    headers=headers
)
data = resp.json()
if not data.get("responsestatus", "").startswith("SUCCESS"):
    print(f"Error: {data.get('responsestatus')}")
else:
    full = data["aircraft"]
    print(f"{full['make']} {full['model']} — SN: {full['sernbr']}, Year: {full['yearmfr']}")
```

---

## Step 4: Get Owner/Operator

```python
resp = requests.post(
    f"{BASE}/api/Aircraft/getRelationships/{api_token}",
    headers=headers,
    json={ "aclist": [aircraft_id] }
)
data = resp.json()
if not data.get("responsestatus", "").startswith("SUCCESS"):
    print(f"Error: {data.get('responsestatus')}")
else:
    for rel in data["relationships"]:
        print(f"{rel['companyname']} — {rel['relationtype']}")
```

---

## You're Done

Those 4 calls give you: aircraft identity, full specs, and owner/operator relationships. Everything else in the API builds on this foundation.

**Next steps when you're ready:**
- Flight activity → [Flight Data](flight-data.md)
- Transaction history → [History](history.md)
- Contacts at the owner company → [Contacts](contacts.md)
- Search for aircraft by model → [Aircraft](aircraft.md) (`getAircraftList`)
- Build a full lookup tool → [JETNET Lite](jetnet-lite.md)

---

## The 5 Things That Will Bite You

These are the errors every new developer hits. Memorize them now and save hours of debugging.

### 1. HTTP 200 Does Not Mean Success

The JETNET API always returns HTTP 200, even on errors. You must check `responsestatus`:

```python
data = resp.json()
if data.get("responsestatus", "").startswith("ERROR"):
    raise Exception(f"API error: {data['responsestatus']}")
```

### 2. Dates Must Be `MM/DD/YYYY` with Leading Zeros

```
✅ "01/01/2024"
❌ "1/1/2024"
❌ "2024-01-01"
```

```python
from datetime import date

def format_date(d):
    return d.strftime("%m/%d/%Y")
```

```javascript
function formatDate(d) {
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${mm}/${dd}/${d.getFullYear()}`;
}
```

### 3. `transtype` Must Be `["None"]`, Not `[]`

When querying transaction history and you want all types:

```
✅ "transtype": ["None"]
❌ "transtype": []
```

An empty array may return nothing.

### 4. `forsale` Is a String, Not a Boolean

```
✅ "forsale": "true"
❌ "forsale": true
```

### 5. Token Refresh — Don't Wait for Failure

Tokens expire after 60 minutes. Don't wait for `INVALID SECURITY TOKEN` -- refresh proactively at 50 minutes:

```python
import time

login_time = time.time()

def ensure_valid():
    if time.time() - login_time > 3000:  # 50 minutes
        login()  # Re-authenticate
```

Or just use the session helpers -- they do this automatically.

---

## Error Decoder

When something goes wrong, find your error here:

| `responsestatus` Value | Meaning | Fix |
|----------------------|---------|-----|
| `ERROR: INVALID SECURITY TOKEN` | Token expired | Re-authenticate and retry |
| `ERROR: INVALID CATEGORY` | Enum value wrong | Check exact casing in [Enum Reference](enum-reference.md) |
| `ERROR: VALIDATION` | Bad field format | Check date format, field types |
| `SUCCESS - NO RECORDS FOUND` | Query is valid but no results | Broaden your filters |
| *(empty or missing)* | Field name wrong | Check `emailAddress` casing, field names |

---

## Minimal Request Bodies

The API has many optional fields. Here's the minimum you need for the most common calls:

### getFlightDataPaged — Minimum

```json
{
  "aircraftid": 12345,
  "startdate": "01/01/2025",
  "enddate": "02/28/2026"
}
```

### getHistoryListPaged — Minimum

```json
{
  "aircraftid": 12345,
  "transtype": ["None"],
  "startdate": "01/01/2024",
  "enddate": "12/31/2024"
}
```

### getAircraftList — Minimum (G650s for sale)

```json
{
  "modlist": [278],
  "forsale": "true",
  "lifecycle": "InOperation"
}
```

### getRelationships — Minimum

```json
{
  "aclist": [12345]
}
```

### getContactList — Minimum

```json
{
  "companyid": 67890
}
```

### getCompanyList — Minimum

```json
{
  "complist": [67890]
}
```

Everything else in these request bodies is optional. Add filters only when you need to narrow results.

---

## How Endpoints Connect

```
Tail Number (e.g., N650GD)
        │
        ▼
   getRegNumber ──────► aircraftid (the master join key)
        │
        ├──► getAircraft ────────► specs, lifecycle, serial
        │
        ├──► getRelationships ──► companyid + relationship type
        │         │
        │         ├──► getCompanyList ──► company profile
        │         │
        │         └──► getContactList ──► decision-makers
        │
        ├──► getFlightDataPaged ► flight activity
        │
        └──► getHistoryListPaged ► transaction history
```

Everything starts with `aircraftid`. Get that first, then branch out to whatever data you need.

For the full entity model, see [Data Model](data-model.md).

---

## Session Helpers — Use Them

Don't build your own auth/retry logic. The repo includes production-ready session helpers:

| File | Language | What It Handles |
|------|----------|----------------|
| [`src/jetnet/session.py`](../src/jetnet/session.py) | Python | Login, token refresh at 50 min, auto-retry on expired token, `responsestatus` checking, error normalization |
| [`src/jetnet/session.ts`](../src/jetnet/session.ts) | TypeScript | Same features, async/await pattern |

Copy one into your project. Call `ensure_session()` before every request and it handles everything.

---

## Related Docs

- [START_HERE.md](../START_HERE.md) — Pick your path (demo, bulk data, CRM, AI agent, MCP)
- [Common Mistakes](common-mistakes.md) — Full list of every known gotcha (30+ entries)
- [Authentication](authentication.md) — Deep dive on the dual-token pattern
- [Enum Reference](enum-reference.md) — Valid values for every enum field
- [Data Model](data-model.md) — How Aircraft, Company, and Contact entities connect
- [JETNET Lite](jetnet-lite.md) — Full reference architecture for a lookup tool
- [Aircraft](aircraft.md) — All 21 aircraft endpoints
