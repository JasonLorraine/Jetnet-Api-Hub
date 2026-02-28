# JETNET Company Endpoints

## Conceptual Model

Company endpoints let you search, retrieve, and expand company profiles. A "company" in JETNET is any legal entity with a relationship to aircraft: owners, operators, manufacturers, lessors, brokers, FBOs, and fractional providers all share the same `companyid` namespace.

Companies sit at the center of a relationship graph:

```
                    ┌─────────────┐
                    │  Contacts   │
                    │ (contactid) │
                    └──────┬──────┘
                           │
┌──────────────┐    ┌──────┴──────┐    ┌──────────────┐
│   Aircraft   │────│   Company   │────│   Related    │
│ (aircraftid) │    │ (companyid) │    │  Companies   │
└──────────────┘    └──────┬──────┘    └──────────────┘
                           │
                    ┌──────┴──────┐
                    │   History   │
                    │  (transid)  │
                    └─────────────┘
```

---

## Endpoints

| # | Endpoint | Method | Path | Returns |
|---|----------|--------|------|---------|
| 1 | getCompany | GET | `/api/Company/getCompany/{id}/{apiToken}` | Full company record (nested objects) |
| 2 | getIdentification | GET | `/api/Company/getIdentification/{id}/{apiToken}` | Lightweight identification record |
| 3 | getContacts | GET | `/api/Company/getContacts/{id}/{apiToken}` | Contact ID array (not full objects) |
| 4 | getPhonenumbers | GET | `/api/Company/getPhonenumbers/{id}/{apiToken}` | Phone number list |
| 5 | getRelatedcompanies | GET | `/api/Company/getRelatedcompanies/{id}/{apiToken}` | Affiliated / parent / child companies |
| 6 | getAircraftrelationships | GET | `/api/Company/getAircraftrelationships/{id}/{apiToken}` | Aircraft tied to this company |
| 7 | getCompanyCertifications | GET | `/api/Company/getCompanyCertifications/{id}/{apiToken}` | Regulatory certifications |
| 8 | getCompanyHistory | POST | `/api/Company/getCompanyHistory/{apiToken}` | Transaction history (bulk) |
| 9 | getCompanyList / Paged | POST | `/api/Company/getCompanyListPaged/{apiToken}/{pagesize}/{page}` | Company search with pagination |

---

## 1. getCompany (Full Record)

```
GET /api/Company/getCompany/{id}/{apiToken}
```

Returns the complete company object with nested sub-structures: identification, phone numbers, contacts, aircraft relationships, certifications, and related companies.

### Response Structure

```json
{
  "responsestatus": "SUCCESS",
  "company": {
    "identification": {
      "companyid": 4425,
      "parentcompanyid": 0,
      "name": "Acme Aviation LLC",
      "altname": "",
      "address1": "123 Main St",
      "city": "Dallas",
      "state": "Texas",
      "postcode": "75201",
      "country": "United States",
      "email": "info@acmeaviation.com",
      "website": "www.acmeaviation.com",
      "actiondate": "2025-01-15T00:00:00"
    },
    "phonenumbers": [...],
    "contacts": [...],
    "aircraftrelationships": [...],
    "relatedcompanies": null,
    "companycertifications": null
  }
}
```

### When to Use

Use this when you need the full company profile in a single call. For lightweight validation or display previews, prefer `getIdentification`.

---

## 2. getIdentification (Lightweight)

```
GET /api/Company/getIdentification/{id}/{apiToken}
```

Returns identification fields only. Useful for quick validation, UI previews, and confirming a `companyid` exists before making heavier calls.

### Response Key

`companyIdentification`

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `companyid` | integer | Primary key |
| `parentcompanyid` | integer | Parent company (0 = standalone) |
| `name` | string | Legal company name |
| `altname` | string | Alternate / DBA name |
| `address1` | string | Street address |
| `city` | string | City |
| `state` | string | State / province |
| `postcode` | string | Postal code |
| `country` | string | Country |
| `email` | string | Primary email |
| `website` | string | Company website |
| `actiondate` | string (ISO) | Last update timestamp |

---

## 3. getContacts (Contact IDs Only)

```
GET /api/Company/getContacts/{id}/{apiToken}
```

Returns an array of `contactid` integers associated with this company.

### Critical Behavior

This endpoint returns **ID arrays, not full contact objects**. You must call `Contact/getContact/{contactid}/{apiToken}` or `Contact/getIdentification/{contactid}/{apiToken}` for each ID to hydrate full contact records.

### Fan-Out Warning

A company with 20 contacts requires 20 follow-up calls. Limit concurrency and consider whether you truly need all contacts or just the primary ones from `getAircraftrelationships`.

```python
contact_ids = resp.get("contacts") or []
for cid in contact_ids[:10]:
    contact = session.get(f"/api/Contact/getIdentification/{cid}/{token}")
```

```javascript
const contactIds = data.contacts ?? [];
const results = [];
for (const cid of contactIds.slice(0, 10)) {
  results.push(await fetch(`${BASE}/api/Contact/getIdentification/${cid}/${TOKEN}`));
}
```

---

## 4. getPhonenumbers

```
GET /api/Company/getPhonenumbers/{id}/{apiToken}
```

### Response Structure

```json
{
  "responsestatus": "SUCCESS",
  "count": 2,
  "phonenumbers": [
    { "type": "Office", "number": "214-555-0100" },
    { "type": "Fax", "number": "214-555-0101" }
  ]
}
```

### Null Array Warning

When no phone numbers exist, the response is:

```json
{
  "responsestatus": "SUCCESS: NO RESULTS FOUND [PHONE NUMBERS]",
  "count": 0,
  "phonenumbers": null
}
```

Always guard before iterating:

```python
phones = resp.get("phonenumbers") or []
```

```javascript
const phones = data.phonenumbers ?? [];
```

---

## 5. getRelatedcompanies

```
GET /api/Company/getRelatedcompanies/{id}/{apiToken}
```

Returns affiliated, parent, and subsidiary companies.

### Response Key

`relatedcompanies` (array or `null`)

### Typical Empty Response

```json
{
  "responsestatus": "SUCCESS: NO RESULTS FOUND [RELATED COMPANIES]",
  "count": 0,
  "relatedcompanies": null
}
```

### When to Use

- Corporate family / hierarchy mapping
- Affiliate graph expansion
- Due diligence and relationship intelligence
- Understanding if an "operator" is a subsidiary of the named owner

---

## 6. getAircraftrelationships

```
GET /api/Company/getAircraftrelationships/{id}/{apiToken}
```

Returns all aircraft tied to this company and the nature of each relationship.

### Response Key

`aircraftrelationships` (array)

### Response Structure

```json
{
  "responsestatus": "SUCCESS",
  "count": 3,
  "aircraftrelationships": [
    {
      "aircraftid": 211461,
      "relationtype": "Owner",
      "relationseqno": 1,
      "contactid": 524808,
      "ownerpercent": null,
      "fractionexpiresdate": null,
      "isoperator": "N",
      "businesstype": "End User"
    }
  ]
}
```

### Key Fields

| Field | Type | Notes |
|-------|------|-------|
| `aircraftid` | integer | Join key to Aircraft endpoints |
| `relationtype` | string | `"Owner"`, `"Operator"`, `"Additional Company/Contact"` |
| `relationseqno` | integer | Sequence number within this relation type |
| `contactid` | integer | Bridge to Contact endpoints |
| `ownerpercent` | number or null | Fractional ownership percentage (can be null) |
| `fractionexpiresdate` | string or null | Fractional share expiration |
| `isoperator` | string | `"Y"` or `"N"` (string, not boolean) |
| `businesstype` | string | `"End User"`, `"Dealer Broker"`, `"Charter Company"`, etc. |

### Gotchas

- `isoperator` is a `"Y"`/`"N"` **string**, not a boolean. Do not cast directly to boolean.
- `ownerpercent` and `fractionexpiresdate` can be `null` even when a relationship exists.
- `contactid` provides a direct bridge to Contact endpoints without needing `getContacts`.

---

## 7. getCompanyCertifications

```
GET /api/Company/getCompanyCertifications/{id}/{apiToken}
```

### Response Key

`companycertifications` (array or `null`)

### Typical Empty Response

```json
{
  "responsestatus": "SUCCESS: NO RESULTS FOUND [CERTIFICATIONS]",
  "count": 0,
  "companycertifications": null
}
```

This endpoint frequently returns empty results. Use for compliance, audits, or operator qualification workflows.

---

## 8. getCompanyHistory

```
POST /api/Company/getCompanyHistory/{apiToken}
POST /api/Company/getCompanyHistoryPaged/{apiToken}/{pagesize}/{page}
```

Returns transaction history for one or more companies. Use when the question is "What aircraft has this company bought or sold?" rather than "What happened to this specific aircraft?"

### Request Body (`CompHistoryOptions`)

```json
{
  "companyid": 0,
  "complist": [2346, 12389],
  "aircraftid": 0,
  "aclist": [],
  "transtype": ["FullSale"],
  "relationship": [],
  "startdate": "01/01/2024",
  "enddate": "12/31/2025",
  "lastactionstartdate": "",
  "lastactionenddate": "",
  "isinternaltrans": "No",
  "isoperator": "Ignore"
}
```

| Field | Type | Purpose |
|-------|------|---------|
| `companyid` | integer | Single company filter (0 = no filter) |
| `complist` | array | Multiple company IDs for bulk queries |
| `aircraftid` | integer | Single aircraft filter (0 = no filter) |
| `aclist` | array | Multiple aircraft IDs |
| `transtype` | array | `["None"]` (all), `["FullSale"]`, `["Lease"]`, etc. |
| `relationship` | array | Filter by relationship type |
| `startdate` / `enddate` | string | Date range (`MM/DD/YYYY`) |
| `lastactionstartdate` / `lastactionenddate` | string | Filter by JETNET record update date |
| `isinternaltrans` | string | `"Yes"`, `"No"`, `"Ignore"` |
| `isoperator` | string | `"Yes"`, `"No"`, `"Ignore"` |

### Response Key

`history` (array) — same structure as Aircraft history. See [History](history.md) for full field reference.

---

## 9. getCompanyList / getCompanyListPaged (Search)

```
POST /api/Company/getCompanyList/{apiToken}
POST /api/Company/getCompanyListPaged/{apiToken}/{pagesize}/{page}
```

Search for companies by name, location, business type, aircraft association, and more.

### Request Body (`CompListOptions`)

```json
{
  "name": "NetJets",
  "country": "United States",
  "city": "",
  "state": ["NY", "NJ"],
  "statename": [],
  "bustype": ["Charter Company", "Fixed Base Operator"],
  "airframetype": "None",
  "maketype": "None",
  "modelid": [],
  "make": [],
  "relationship": [],
  "isoperator": "",
  "actiondate": "",
  "companychanges": "",
  "website": "",
  "complist": [],
  "aircraftid": []
}
```

| Field | Type | Purpose |
|-------|------|---------|
| `name` | string | Company name search (partial match) |
| `country` | string | Country filter |
| `city` | string | City filter |
| `state` | array | State/province codes |
| `statename` | array | Full state names |
| `bustype` | array | Business type filter (see values below) |
| `airframetype` | enum | `"FixedWing"`, `"Rotary"`, `"None"` |
| `maketype` | enum | `"BusinessJet"`, `"Turboprop"`, `"None"` |
| `modelid` | array | Filter by aircraft model IDs |
| `make` | array | Filter by manufacturer |
| `relationship` | array | Filter by relationship type |
| `isoperator` | string | `"Y"` = operators only, `"N"` = non-operators, `""` = all |
| `actiondate` | string | Records updated since this date (`MM/DD/YYYY`) |
| `companychanges` | string | Change detection filter |
| `website` | string | Website search |
| `complist` | array | Specific company IDs to retrieve |
| `aircraftid` | array | Companies associated with these aircraft |

### Common `bustype` Values

`"End User"`, `"Charter Company"`, `"Fixed Base Operator"`, `"Dealer Broker"`, `"Management Company"`, `"Fractional Company"`, `"Manufacturer"`, `"Maintenance Facility"`

### Response Structure

```json
{
  "responsestatus": "SUCCESS: PAGE [ 1 of 5 ]",
  "count": 47,
  "currentpage": 1,
  "maxpages": 5,
  "companylist": [
    {
      "companyid": 4425,
      "name": "Acme Aviation LLC",
      "city": "Dallas",
      "state": "Texas",
      "country": "United States",
      "bustype": "Charter Company",
      "pageurl": "https://www.jetnetevolution.com/..."
    }
  ]
}
```

### Response Key

Non-paged (`getCompanyList`): `companies` (array)
Paged (`getCompanyListPaged`): `companylist` (array)

The response key **changes** between paged and non-paged variants. Non-paged also returns `currentpage: 0, maxpages: 0` — do not interpret these as paging metadata.

Always use the paged variant (`getCompanyListPaged`) for automated pipelines and production workflows.

---

## Recommended Workflow

```
Search → Validate → Expand → Link to Aircraft/Contacts
```

1. **`getCompanyListPaged`** — find companies matching your criteria, get `companyid` values
2. **`getIdentification`** — lightweight confirm + display fields
3. **`getCompany`** — full profile when needed
4. **`getPhonenumbers`** — communications enrichment
5. **`getRelatedcompanies`** — expand corporate family graph
6. **`getAircraftrelationships`** — link aircraft and roles (includes `contactid` for bridging)
7. **`getContacts`** — get all contact IDs, then hydrate individually
8. **`getCompanyHistory`** — pull transaction change log

### Workflow Example (Python)

```python
companies = get_all_pages(bearer, token,
    f"/api/Company/getCompanyListPaged/{token}",
    {"bustype": ["Charter Company"], "state": ["TX"]},
    response_key="companies"
)

for comp in companies:
    cid = comp["companyid"]

    rels = session.get(
        f"{BASE}/api/Company/getAircraftrelationships/{cid}/{token}",
        headers={"Authorization": f"Bearer {bearer}"}
    ).json()

    aircraft_links = rels.get("aircraftrelationships") or []
    for link in aircraft_links:
        print(f"  Aircraft {link['aircraftid']} — {link['relationtype']}")
```

---

## Key Behaviors and Gotchas

### "SUCCESS: NO RESULTS FOUND" Is Normal

Several Company sub-endpoints return this status when no data exists. It is a valid business state, not an error. Use a prefix check:

```python
status = resp.get("responsestatus", "")
if status.upper().startswith("SUCCESS"):
    pass
elif "ERROR" in status.upper():
    raise ValueError(f"JETNET error: {status}")
```

```javascript
const status = data.responsestatus || "";
if (status.toUpperCase().startsWith("SUCCESS")) {
  // ok — may or may not contain data
} else if (status.toUpperCase().includes("ERROR")) {
  throw new Error(`JETNET error: ${status}`);
}
```

### Null Arrays

`phonenumbers`, `relatedcompanies`, `companycertifications`, and `contacts` can be `null` instead of `[]`. Always guard before calling `.map()`, `.forEach()`, or iterating:

```javascript
const phones = data.phonenumbers ?? [];
const related = data.relatedcompanies ?? [];
```

### `isoperator` Is a String

The `isoperator` field in aircraft relationships is `"Y"` or `"N"` (string), not a boolean. Direct boolean casting will treat both as truthy.

### `ownerpercent` Can Be Null

Even when a valid ownership relationship exists, `ownerpercent` may be `null`. Do not assume it is always populated for Owner relationships.

### Fan-Out / N+1 Risk

`getContacts` returns only an array of `contactid` integers. Hydrating each contact requires a separate API call. Batch your requests, limit concurrency, and consider whether `getAircraftrelationships` (which includes `contactid`) already provides the contacts you need.

---

## See Also

- [Contacts](contacts.md) — Contact endpoint details and hydration patterns
- [History](history.md) — Transaction history (Aircraft and Company)
- [Response Handling](response-handling.md) — Nested vs flat relationship schemas
- [ID System](id-system.md) — `companyid`, `contactid`, `aircraftid` join keys
- [Pagination](pagination.md) — Paged loop patterns and `maxpages: 0` quirk
- [Common Mistakes](common-mistakes.md) — Known gotchas including null arrays and string booleans
