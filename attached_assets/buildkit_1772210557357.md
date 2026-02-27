# JETNET Build Kit -- App Builder Reference

For authentication, pagination, response shapes, and endpoint details, see `SKILL.md`.
This document is for builders shipping an app, iPhone MVP, or Replit integration.

---

## The App You Are Building

A lightweight aircraft intelligence app:
- **Input:** registration number (tail)
- **Output:** aircraft profile
  - Overview (identity, base, quick context)
  - Pictures
  - Relationships (owner, operator, manager)
  - Flight activity signal
  - History and Events (lazy load on demand)

---

## Core Workflow: Enter Tail, Profile Loads

### What happens after the user presses Enter

1. Backend ensures auth tokens exist (login if needed)
2. Backend resolves `regnbr` to `aircraftid` -- synchronous, must succeed before anything else
3. Backend returns Overview immediately (first paint -- make it feel fast)
4. Backend fans out in parallel:
   - Pictures
   - Relationships
   - Flights (short window)
5. History and Events load only when the user opens those tabs (lazy -- they can be heavy)

### Why this order

`aircraftid` is the join key for everything else. You cannot call pictures,
relationships, or flight endpoints without it. First paint makes the app feel
responsive. Lazy loading history/events prevents a slow initial experience.

---

## Canonical Endpoint Set

| Step | Method | Path |
|------|--------|------|
| Auth | POST | `/api/Admin/APILogin` |
| Tail lookup | GET | `/api/Aircraft/getRegNumber/{reg}/{apiToken}` |
| Pictures | GET | `/api/Aircraft/getPictures/{aircraftid}/{apiToken}` |
| Relationships | POST | `/api/Aircraft/getRelationships/{apiToken}` |
| Flight activity | POST | `/api/Aircraft/getFlightDataPaged/{apiToken}/{pagesize}/{page}` |
| History | POST | `/api/Aircraft/getHistoryListPaged/{apiToken}/{pagesize}/{page}` |
| Events | POST | `/api/Aircraft/getEventListPaged/{apiToken}/{pagesize}/{page}` |
| Event enums (optional) | GET | `/api/Utility/getEventTypes/{apiToken}` |

---

## Copy-Paste Payload Templates

### Login

```json
{
  "emailAddress": "Email@domain.com",
  "password": "Pa$$w0rd"
}
```

Store server-side: `bearerToken` and `apiToken` (also called `securityToken` in some docs -- same field).

Every request after login:
- Header: `Authorization: Bearer <bearerToken>`
- Path includes `/{apiToken}`

---

### Tail lookup

```
GET /api/Aircraft/getRegNumber/N123AB/{apiToken}
```

Returns `aircraftresult` containing `aircraftid`, `make`, `model`, `serialnbr`,
`regnbr`, `yearmfr`, `baseicao`, `baseairport`, and identity fields you can render immediately.

---

### Pictures

```
GET /api/Aircraft/getPictures/{aircraftid}/{apiToken}
```

Returns `pictures[]` with `description`, `imagedate`, and `pictureurl`.
Treat `pictureurl` as expiring (pre-signed S3) -- display immediately, do not
cache the URL for more than an hour.

---

### Relationships -- Two Patterns

**Single aircraft (Golden Path, Tier A):**
```json
{
  "aircraftid": 211461,
  "aclist": [],
  "modlist": [],
  "actiondate": "",
  "showHistoricalAcRefs": false
}
```

**Bulk fleet (Tier B -- pass a list of aircraft IDs):**
```json
{
  "aclist": [7103, 8542, 11200, 15033, 22981],
  "modlist": [],
  "actiondate": "",
  "showHistoricalAcRefs": false
}
```

Both return the same `relationships` array. Each entry has `aircraftid`, `regnbr`,
`name` (company name), `relationtype` (`"Owner"`, `"Operator"`, etc.),
`relationseqno`, and a nested `company` object.

Use single aircraft for the Golden Path app flow. Use bulk when you already have a
fleet of `aircraftid` values and want all their ownership in one call.

---

### Flight Activity (paged)

```
POST /api/Aircraft/getFlightDataPaged/{apiToken}/100/1
```

```json
{
  "aircraftid": 211461,
  "startdate": "COMPUTE_6_MONTHS_AGO",
  "enddate": "COMPUTE_TODAY",
  "origin": "",
  "destination": "",
  "aclist": [],
  "modlist": [],
  "exactMatchReg": true
}
```

Compute `startdate` and `enddate` dynamically at runtime -- do not hardcode dates.
Use a 6-month window for the initial app view. Use `maxpages` to paginate if needed.

---

### History (paged, lazy load)

```
POST /api/Aircraft/getHistoryListPaged/{apiToken}/100/1
```

```json
{
  "aircraftid": 211461,
  "startdate": "01/01/2020",
  "enddate": "COMPUTE_TODAY",
  "allrelationships": true,
  "aclist": [],
  "modlist": [],
  "transtype": ["None"],
  "isnewaircraft": "Ignore"
}
```

Load this only when the user clicks the History tab.

---

### Events (paged, lazy load)

```
POST /api/Aircraft/getEventListPaged/{apiToken}/100/1
```

```json
{
  "aircraftid": 211461,
  "evtype": [],
  "evcategory": [],
  "startdate": "COMPUTE_12_MONTHS_AGO",
  "enddate": "COMPUTE_TODAY",
  "aclist": [],
  "modlist": []
}
```

Important: enum values in `evtype` and `evcategory` are strict. If you send
unrecognized values, the API returns an error inside `responsestatus` even when
HTTP is 200. Use `getEventTypes` and `getEventCategories` to populate dropdowns safely.

---

## Normalized Response Contract

Do not pass raw JETNET responses directly to a mobile UI or frontend. Normalize to
a stable shape your client can depend on:

```json
{
  "aircraft": {
    "id": 211461,
    "reg": "N123AB",
    "make": "GULFSTREAM",
    "model": "G650",
    "year": 2018
  },
  "base": {
    "icao": "KTEB",
    "airport": "Teterboro"
  },
  "photos": [
    { "description": "Exterior", "date": "2022-08-11", "url": "https://..." }
  ],
  "relationships": [
    { "type": "Owner", "company": "Example Owner LLC", "companyId": 350427 },
    { "type": "Operator", "company": "Example Operator Inc.", "companyId": 456 }
  ],
  "flights": [
    { "date": "2026-02-10", "origin": "KTEB", "dest": "KPBI", "minutes": 165 }
  ],
  "history": [],
  "events": []
}
```

This shape is easy to plug into React, Swift, Flutter, or any CRM system.

---

## Workflow Timing Table

| Phase | Trigger | API calls | Notes |
|-------|---------|-----------|-------|
| Auth | First call or token expired | `APILogin` | Store both tokens server-side |
| Lookup | User presses Enter | `getRegNumber` | Resolve `aircraftid` -- required first |
| First paint | Immediately after lookup | None | Render aircraft identity from lookup result |
| Fan-out async | After first paint | `getPictures`, `getRelationships`, `getFlightDataPaged` | Run in parallel |
| Lazy load | User opens History or Events tab | `getHistoryListPaged`, `getEventListPaged` | On demand only |
| Enum preload | App startup (optional) | `getEventTypes`, `getEventCategories` | Populate filter dropdowns safely |

---

## Node.js Example (Replit-Friendly)

Minimal Express server. Includes login, token cache, retry once on auth failure,
and the full Golden Path profile endpoint.

```js
import express from "express";

const app = express();
app.use(express.json());

const BASE  = process.env.JETNET_BASE_URL || "https://customer.jetnetconnect.com";
const EMAIL = process.env.JETNET_EMAIL    || "Email@domain.com";
const PASS  = process.env.JETNET_PASSWORD || "Pa$$w0rd";

let bearerToken = null;
let apiToken    = null;

async function login() {
  const r = await fetch(`${BASE}/api/Admin/APILogin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emailAddress: EMAIL, password: PASS })
  });
  const j = await r.json();
  // apiToken is also called securityToken in some environments -- check both
  bearerToken = j.bearerToken;
  apiToken    = j.apiToken || j.securityToken;
  if (!bearerToken || !apiToken) throw new Error("Login succeeded but tokens not found.");
}

function isJetnetError(json) {
  return json?.responsestatus && String(json.responsestatus).toUpperCase().includes("ERROR");
}

async function jetnetFetch(path, opts = {}, didRetry = false) {
  if (!bearerToken || !apiToken) await login();

  const url = `${BASE}${path}`.replace("{apiToken}", apiToken);
  const r = await fetch(url, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${bearerToken}`,
      ...(opts.headers || {})
    }
  });

  const text = await r.text();
  let j;
  try { j = JSON.parse(text); } catch { j = { raw: text }; }

  if (!r.ok || isJetnetError(j)) {
    const msg = isJetnetError(j) ? j.responsestatus : `HTTP ${r.status}: ${text}`;
    if (!didRetry && (String(msg).toUpperCase().includes("INVALID SECURITY TOKEN") || r.status === 401)) {
      await login();
      return jetnetFetch(path, opts, true);
    }
    throw new Error(msg);
  }

  return j;
}

function daysAgo(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return `${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")}/${d.getFullYear()}`;
}

function today() { return daysAgo(0); }

app.get("/profile/:reg", async (req, res) => {
  try {
    const reg = req.params.reg.toUpperCase();

    // Step 1: resolve tail to aircraftid
    const lookup = await jetnetFetch(
      `/api/Aircraft/getRegNumber/${reg}/{apiToken}`,
      { method: "GET" }
    );
    const ac = lookup.aircraftresult;
    if (!ac?.aircraftid) return res.status(404).json({ ok: false, error: "Aircraft not found." });

    const id = ac.aircraftid;

    // Step 2: fan out in parallel
    const [pics, rels, flights] = await Promise.all([
      jetnetFetch(`/api/Aircraft/getPictures/${id}/{apiToken}`, { method: "GET" }),
      jetnetFetch(`/api/Aircraft/getRelationships/{apiToken}`, {
        method: "POST",
        body: JSON.stringify({ aircraftid: id, aclist: [], modlist: [], actiondate: "", showHistoricalAcRefs: false })
      }),
      jetnetFetch(`/api/Aircraft/getFlightDataPaged/{apiToken}/100/1`, {
        method: "POST",
        body: JSON.stringify({
          aircraftid: id,
          startdate: daysAgo(180),
          enddate: today(),
          origin: "", destination: "",
          aclist: [], modlist: [],
          exactMatchReg: true
        })
      })
    ]);

    // Step 3: normalize for frontend
    res.json({
      ok: true,
      data: {
        aircraft: { id, reg: ac.regnbr, make: ac.make, model: ac.model, year: ac.yearmfr || ac.yeardlv || null },
        base: { icao: ac.baseicao || null, airport: ac.baseairport || null },
        photos: (pics.pictures || []).map(p => ({ description: p.description, date: p.imagedate, url: p.pictureurl })),
        relationships: (rels.relationships || []).map(r => ({ type: r.relationtype, company: r.name, companyId: r.companyid })),
        flights: (flights.flightdata || []).slice(0, 20)
      }
    });
  } catch (e) {
    res.status(500).json({ ok: false, error: String(e.message || e) });
  }
});

app.listen(3000, () => console.log("JETNET Light running on :3000"));
```

---

## Python Example (Flask)

Same flow. Clean wrapper with retry.

```python
import os, requests
from datetime import datetime, timedelta
from flask import Flask, jsonify

BASE  = os.getenv("JETNET_BASE_URL", "https://customer.jetnetconnect.com")
EMAIL = os.getenv("JETNET_EMAIL",    "Email@domain.com")
PASS  = os.getenv("JETNET_PASSWORD", "Pa$$w0rd")

bearer = None
token  = None

def login():
    global bearer, token
    r = requests.post(f"{BASE}/api/Admin/APILogin", json={"emailAddress": EMAIL, "password": PASS})
    r.raise_for_status()
    j = r.json()
    bearer = j.get("bearerToken")
    token  = j.get("apiToken") or j.get("securityToken")
    if not bearer or not token:
        raise RuntimeError("Login succeeded but tokens not found.")

def is_error(j):
    return isinstance(j, dict) and "ERROR" in str(j.get("responsestatus", "")).upper()

def jetnet(method, path, body=None, did_retry=False):
    global bearer, token
    if not bearer or not token:
        login()
    url = f"{BASE}{path}".replace("{apiToken}", token)
    headers = {"Authorization": f"Bearer {bearer}"}
    r = requests.request(method, url, headers=headers, json=body)
    try:
        j = r.json()
    except Exception:
        j = {"raw": r.text}
    if r.status_code >= 400 or is_error(j):
        msg = j.get("responsestatus") if is_error(j) else r.text
        if not did_retry and ("INVALID SECURITY TOKEN" in str(msg).upper() or r.status_code == 401):
            login()
            return jetnet(method, path, body, did_retry=True)
        raise RuntimeError(msg)
    return j

def fmt_date(d): return d.strftime("%m/%d/%Y")
def days_ago(n): return fmt_date(datetime.now() - timedelta(days=n))
def today():     return fmt_date(datetime.now())

app = Flask(__name__)

@app.get("/profile/<reg>")
def profile(reg):
    reg = reg.upper()
    lookup = jetnet("GET", f"/api/Aircraft/getRegNumber/{reg}/{{apiToken}}")
    ac = lookup.get("aircraftresult") or {}
    aircraft_id = ac.get("aircraftid")
    if not aircraft_id:
        return jsonify({"ok": False, "error": "Aircraft not found"}), 404

    pics    = jetnet("GET", f"/api/Aircraft/getPictures/{aircraft_id}/{{apiToken}}")
    rels    = jetnet("POST", "/api/Aircraft/getRelationships/{apiToken}", {
        "aircraftid": aircraft_id, "aclist": [], "modlist": [],
        "actiondate": "", "showHistoricalAcRefs": False
    })
    flights = jetnet("POST", "/api/Aircraft/getFlightDataPaged/{apiToken}/100/1", {
        "aircraftid": aircraft_id,
        "startdate": days_ago(180), "enddate": today(),
        "origin": "", "destination": "",
        "aclist": [], "modlist": [], "exactMatchReg": True
    })

    return jsonify({
        "ok": True,
        "data": {
            "aircraft": {"id": aircraft_id, "reg": ac.get("regnbr"), "make": ac.get("make"), "model": ac.get("model"), "year": ac.get("yearmfr") or ac.get("yeardlv")},
            "base": {"icao": ac.get("baseicao"), "airport": ac.get("baseairport")},
            "photos": [{"description": p.get("description"), "date": p.get("imagedate"), "url": p.get("pictureurl")} for p in (pics.get("pictures") or [])],
            "relationships": [{"type": r.get("relationtype"), "company": r.get("name"), "companyId": r.get("companyid")} for r in (rels.get("relationships") or [])],
            "flights": (flights.get("flightdata") or [])[:20]
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
```

---

## Caching Recommendations

| Data | TTL | Reason |
|------|-----|--------|
| `bearerToken` + `apiToken` | Until error | Re-auth only on `INVALID SECURITY TOKEN` |
| `tail -> aircraftid` mapping | 24 hours | Registration numbers rarely change |
| Pictures | 1 hour | `pictureurl` is a pre-signed S3 URL that expires |
| Dossier (owner/operator/base) | 7 days | Changes infrequently unless using `actiondate` sync |
| Flight activity | 4-6 hours | Updates as flights complete |
| History / Events | 24 hours | Changes on transactions only |

---

## AI Agent Checklist

An AI agent can build the app from this document if it follows this checklist:

- [ ] Implements `APILogin` and stores both `bearerToken` and `apiToken` server-side
- [ ] Adds `Authorization: Bearer` header to every request
- [ ] Inserts `apiToken` into URL path (not headers or body)
- [ ] Checks both HTTP status and `responsestatus` for `"ERROR"`
- [ ] Retries once on `INVALID SECURITY TOKEN`, does not retry indefinitely
- [ ] Uses `getRegNumber` first to get `aircraftid` before any other call
- [ ] Loads pictures, relationships, and flights in parallel after first paint
- [ ] Uses paged endpoints for flights, history, and events
- [ ] Normalizes output to a stable shape before sending to frontend
- [ ] Treats `pictureurl` as expiring -- does not cache the URL
- [ ] Never sends credentials or tokens to the mobile client
- [ ] Computes date strings dynamically -- never hardcodes them

For production readiness, also add: caching layer, rate limiting, structured logs.
For an MVP or demo, the checklist above is enough to ship.
