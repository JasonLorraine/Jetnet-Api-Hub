# JETNET Lite: Tail Number Research Portal

A reference architecture for building a lightweight JETNET lookup tool. Enter a tail number, get a complete dashboard: aircraft profile, owner/operator, company details, contacts, flight activity, and transaction history.

This is not a demo -- it's a blueprint for an internal research console that mirrors the core pages of JETNET Connect in a streamlined, single-input interface.

---

## What It Does

One input (tail number) triggers a 7-step API call sequence that produces a complete intelligence profile:

```
User enters: N650GD
                ↓
┌─────────────────────────────────────────────┐
│  Aircraft Profile                           │
│  Make | Model | Serial | Year | Lifecycle   │
├─────────────────────────────────────────────┤
│  Owner & Operator                           │
│  Company Name | Relationship | Location     │
├─────────────────────────────────────────────┤
│  Company Profile                            │
│  Address | Website | Business Type | Fleet  │
├─────────────────────────────────────────────┤
│  Decision-Maker Contacts                    │
│  Name | Title | Email | Phone               │
├─────────────────────────────────────────────┤
│  Flight Activity (Last 12 Months)           │
│  Date | Origin | Destination                │
├─────────────────────────────────────────────┤
│  Transaction History                        │
│  Date | Type | Buyer | Seller               │
└─────────────────────────────────────────────┘
```

---

## Application Structure

```
jetnet-lite/
├── app.py                     # Flask/FastAPI entry point
├── jetnet_client.py           # Auth, token refresh, request wrapper
├── services/
│   ├── aircraft_service.py    # Tail resolve + aircraft profile
│   ├── relationship_service.py
│   ├── flight_service.py
│   ├── history_service.py
│   ├── contact_service.py
│   └── company_service.py
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   └── partials/
│       ├── aircraft_card.html
│       ├── relationships.html
│       ├── flights.html
│       ├── transactions.html
│       ├── contacts.html
│       └── company.html
└── requirements.txt
```

The service layer pattern keeps each API domain isolated. The client handles auth, token refresh, and error normalization (see [session helpers](../src/jetnet/session.py)).

---

## API Call Sequence

All 7 steps in order. Steps 3-7 can be parallelized after Step 1 resolves the `aircraftid`.

### Step 1: Resolve Tail Number → `aircraftid`

```
GET /api/Aircraft/getRegNumber/{regnbr}/{apiToken}
```

Returns the `aircraftid` -- the master join key for all subsequent calls.

**Response key:** `aircraftresult` (single object, not an array). This uses a **flat schema** with `companyrelation` (not `relationtype`).

> **Why not `getAircraftList`?** `getRegNumber` is a simple GET that returns one aircraft by exact registration. `getAircraftList` is a POST with filters -- heavier and unnecessary for a single tail lookup. See [Aircraft](aircraft.md).

### Step 2: Aircraft Profile

```
GET /api/Aircraft/getAircraft/{aircraftid}/{apiToken}
```

Returns the full aircraft record: make, model, serial number, year manufactured, lifecycle status, specifications.

**Response key:** `aircraft` -- a composite object with nested sub-records (identification, airframe, engine, avionics, etc.).

### Step 3: Owner/Operator Relationships

```
POST /api/Aircraft/getRelationships/{apiToken}
Body: { "aclist": [aircraftid] }
```

Returns company relationships: owner, operator, manager, trustee, fractional owner.

**Response key:** `relationships` -- array of objects with `companyid`, `companyname`, `relationtype`, `isoperator` ("Y"/"N" string).

Store the `companyid` values -- you need them for Steps 6 and 7.

### Step 4: Flight Activity

```
POST /api/Aircraft/getFlightDataPaged/{apiToken}/{pagesize}/{pagenumber}
Body: {
  "aircraftid": aircraftid,
  "startdate": "03/01/2025",
  "enddate": "02/28/2026"
}
```

Returns per-flight records: departure/arrival airports, dates, duration.

**Response key:** `flightdata`

> **Date format:** Must be `MM/DD/YYYY` with leading zeros. `3/1/2025` will fail. See [Common Mistakes](common-mistakes.md).

### Step 5: Transaction History

```
POST /api/Aircraft/getHistoryListPaged/{apiToken}/{pagesize}/{pagenumber}
Body: {
  "aircraftid": aircraftid,
  "transtype": ["None"],
  "startdate": "01/01/2015",
  "enddate": "02/28/2026"
}
```

Returns ownership transactions: sales, deliveries, registrations, leases.

**Response key:** `history`

> **Critical:** `transtype` must be `["None"]` to get all transaction types. An empty array `[]` may return nothing. See [Common Mistakes](common-mistakes.md).

> **Use `getHistoryListPaged`**, not `getHistoryList`. The non-paged version can timeout on aircraft with long histories. See [History](history.md).

### Step 6: Contacts

```
POST /api/Contact/getContactList/{apiToken}
Body: { "companyid": companyid }
```

Call this for each `companyid` from Step 3 to get decision-maker contacts.

**Response key:** `contacts`

> **Gotcha:** `getContactList` → response key `contacts`. `getContactListPaged` → response key `contactlist`. Different endpoints, different keys. See [Contacts](contacts.md).

### Step 7: Company Profile

```
POST /api/Company/getCompanyList/{apiToken}
Body: { "complist": [companyid] }
```

Returns company details: name, address, website, business type, fleet size, operator flag.

**Response key:** `companies`

> **Gotcha:** `getCompanyList` → response key `companies`. `getCompanyListPaged` → response key `companylist`. See [Companies](companies.md).

---

## Error Handling

Every call must check for these conditions:

| Condition | How to Detect | Action |
|-----------|--------------|--------|
| HTTP 200 but API error | `responsestatus` starts with `"ERROR"` or `"INVALID"` | Show error, don't parse data |
| Expired token | `responsestatus` contains `"INVALID SECURITY TOKEN"` | Re-authenticate, retry once |
| No aircraft found | Empty response from `getRegNumber` | Show "tail not found" message |
| Missing `companyid` | `companyrelationships` is empty | Skip Steps 6 and 7 gracefully |
| Date format rejected | API returns error | Validate `MM/DD/YYYY` with leading zeros before sending |

The session helpers (`src/jetnet/session.py` / `session.ts`) handle token refresh and error normalization automatically. See [Authentication](authentication.md) and [Response Handling](response-handling.md).

---

## Performance

Total API calls per lookup: 6-7 (depending on number of related companies).

### Parallelization

After Step 1 resolves the `aircraftid`, Steps 2-5 can run in parallel:

```python
import asyncio

aircraft, relationships, flights, history = await asyncio.gather(
    get_aircraft(aircraftid),
    get_relationships(aircraftid),
    get_flights(aircraftid, start, end),
    get_history(aircraftid, start, end),
)
```

Steps 6 and 7 depend on `companyid` from Step 3, so they run after relationships resolve.

### Caching

These responses change infrequently and are safe to cache:

| Data | Cache Duration | Why |
|------|---------------|-----|
| Aircraft profile | 24 hours | Specs rarely change |
| Company profile | 24 hours | Address/fleet size updates are infrequent |
| Transaction history | 1 hour | New transactions are low-frequency |
| Flight activity | 15 minutes | Flights update more frequently |
| Relationships | 1 hour | Ownership changes are event-driven |

---

## Deployment

```bash
pip install flask requests
export JETNET_EMAIL="your_email@example.com"
export JETNET_PASSWORD="your_password"
python app.py
```

Use HTTPS only. Never expose `apiToken` to the browser -- keep it server-side.

---

## What This Becomes

At its core, this is an internal JETNET research console:

- **Aircraft page** -- specs, lifecycle, status
- **Company page** -- owner/operator profile, fleet size
- **Contact page** -- decision-makers with titles and contact info
- **Flight activity** -- where the aircraft has been
- **Market history** -- every transaction on record

All from a single tail number input.

### Extensions

Once the base is working, you can add:

- Market trends tab (`getModelMarketTrends`)
- Model comparison (`getModelPerformanceSpecs`)
- Export to CSV/PDF
- CRM push (Salesforce, HubSpot)
- AI summary panel (feed the dashboard data to an LLM)
- Activity heatmap (aggregate flight data by airport)

---

## Related Docs

- [Data Model](data-model.md) -- How Aircraft, Company, and Contact entities connect
- [Authentication](authentication.md) -- Login flow, token refresh, dual-token pattern
- [Common Mistakes](common-mistakes.md) -- Every known gotcha
- [Response Shapes](response-shapes.md) -- Normalized UI contracts (AircraftCard, CompanyCard)
- [Aircraft](aircraft.md) -- Full aircraft endpoint reference
- [Companies](companies.md) -- Company endpoint reference
- [Contacts](contacts.md) -- Contact endpoint reference
- [Flight Data](flight-data.md) -- Flight activity endpoints
- [History](history.md) -- Transaction history endpoints
- [Pagination](pagination.md) -- Paging patterns for large datasets
