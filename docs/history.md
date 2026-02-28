# JETNET Aircraft History Endpoints

## Conceptual Model

History endpoints return **transaction events**, not aircraft state. Each record represents a discrete ownership or leasing event -- a sale, lease, transfer, or relationship change.

```
Aircraft Timeline = Ordered Set of Transactions

2019-03  Full Sale — Company A → Company B
2021-07  Lease — Company B → Company C
2024-01  Full Sale — Company C → Company D
```

This is fundamentally different from other endpoint types:

| Endpoint Type | What It Returns | Use Case |
|---------------|----------------|----------|
| Aircraft / Bulk Export | Current state | "Who owns this now?" |
| Snapshot | State at a historical date | "Who owned this in 2016?" |
| History | Change events over time | "When was this sold? To whom?" |
| Flight Data | Operational activity | "How many hours did it fly?" |

---

## Endpoints

### Aircraft History

```
POST /api/Aircraft/getHistoryListPaged/{apiToken}/{pagesize}/{page}
```

Returns transaction records filtered by aircraft attributes, model, company, and transaction type.

### Company History

```
POST /api/Company/getCompanyHistoryPaged/{apiToken}/{pagesize}/{page}
```

Returns transaction history for a specific company. Use when the question is "What aircraft has this company bought/sold?" rather than "What happened to this aircraft?"

---

## Request Structure

```json
{
  "aircraftid": 0,
  "airframetype": "None",
  "maketype": "None",
  "make": "",
  "modelid": 0,
  "modlist": [1194],
  "aclist": [],
  "companyid": 0,
  "isnewaircraft": "No",
  "isinternaltrans": "No",
  "allrelationships": true,
  "transtype": ["FullSale", "Lease"],
  "startdate": "08/22/2025",
  "enddate": "02/18/2026"
}
```

### Filter Parameters

**Aircraft identification:**

| Field | Purpose |
|-------|---------|
| `aircraftid` | Single aircraft lookup (0 = no filter) |
| `make` | Manufacturer filter (case-insensitive) |
| `modelid` | Single model ID |
| `modlist` | Array of model IDs for multi-model queries |
| `aclist` | Array of aircraft IDs |
| `airframetype` | `"FixedWing"`, `"Rotorcraft"`, `"None"` |
| `maketype` | `"BusinessJet"`, `"Turboprop"`, `"None"` |

**Transaction filters:**

| Field | Purpose | Values |
|-------|---------|--------|
| `transtype` | Transaction categories | `["None"]` (all), `["FullSale"]`, `["Lease"]`, `["InternalSale"]`, `["Management"]`, `["Insurance"]`, `["Repossession"]`, `["Registration"]` |
| `isnewaircraft` | Include factory-new deliveries | `"Yes"`, `"No"`, `"Ignore"` |
| `isinternaltrans` | Include intra-company transfers | `"Yes"`, `"No"`, `"Ignore"` |
| `allrelationships` | Return all parties (Seller, Purchaser, Brokers) | `true` / `false` |

**Company / relationship:**

| Field | Purpose |
|-------|---------|
| `companyid` | History tied to a specific company (0 = no filter) |
| `allrelationships` | Include all ownership/operator relationships |

**Date range:**

| Field | Purpose |
|-------|---------|
| `startdate` | Beginning of history window (`MM/DD/YYYY`) |
| `enddate` | End of history window (`MM/DD/YYYY`) |

Date filtering is critical for performance. Always provide a bounded date range.

---

## Response Structure

Response key: **`history`** (array)

```json
{
  "responseid": "556111434",
  "responsestatus": "SUCCESS: PAGE [ 1 of 428 ]",
  "count": 38,
  "currentpage": 1,
  "maxpages": 428,
  "history": [
    {
      "aircraftid": 246204,
      "transid": 31305852,
      "modelid": 1194,
      "make": "CITATION",
      "model": "CJ3+",
      "sernbr": "525B-0739",
      "regnbr": "F-HVLE",
      "yearmfr": 2024,
      "yeardlv": 2025,
      "maketype": "BusinessJet",
      "weightclass": "Light",
      "categorysize": "Light Jet",
      "transtype": "Full Sale - Retail to Unidentified",
      "transdate": "2025-08-25T00:00:00",
      "actiondate": "2025-09-04T15:09:33",
      "translastactiondate": "2025-09-04T15:09:33",
      "description": "Sold from AMW Aero to Awaiting Documentation",
      "internaltrans": false,
      "newac": "preowned",
      "transretail": true,
      "soldprice": null,
      "askingprice": null,
      "listdate": "2025-04-10T00:00:00",
      "purchasedate": "2025-01-16T00:00:00",
      "usage": "Charter",
      "forsale": true,
      "marketstatus": "For Sale",
      "lifecycle": "InOperation",
      "basecountry": "France",
      "basecontinent": "Europe",
      "estaftt": 76,
      "estcycles": 17,
      "companyrelationships": [...]
    }
  ]
}
```

### Key Response Fields

| Field | Meaning |
|-------|---------|
| `transid` | Unique transaction identifier |
| `transtype` | Descriptive transaction string (not the request category) |
| `transdate` | Actual transaction date (ISO) |
| `actiondate` | When JETNET last updated this record (ISO) |
| `translastactiondate` | Last action timestamp on this transaction |
| `description` | Human-readable transaction summary |
| `soldprice` / `askingprice` | Often `null` -- many deals are confidential |
| `transretail` | `true` = arm's length retail transaction (use for comparable sales) |
| `internaltrans` | `false` = not an intra-company transfer |
| `newac` | `"preowned"` or `"new"` |
| `listdate` | When aircraft was listed for sale |
| `purchasedate` | When it entered current owner's fleet |
| `pageurl` | Deep link to JETNET Evolution web detail page |

**Important:** `transtype` values in the **request** are categories (`"FullSale"`), but values in the **response** are descriptive strings (`"Full Sale - Retail to Retail"`, `"Full Sale - Retail to Leasing Company"`, etc.). See [Enum Reference](enum-reference.md) for known values.

### Company Relationships (Nested Schema)

History uses the **nested relationship schema** -- same as `getRelationships`. Each entry contains `company: {}` and `contact: {}` sub-objects with a `relationtype` field.

```json
{
  "companyid": 422540,
  "name": "AMW Aero",
  "relationtype": "Seller",
  "company": {
    "companyid": 422540,
    "name": "AMW Aero",
    "address1": "11 Route d Archigny",
    "city": "Sainte-Radegonde",
    "country": "France",
    "email": "Sales02@acimetechnology.fr"
  },
  "contact": {
    "contactid": 606048,
    "firstname": "Herve",
    "lastname": "Mouly",
    "title": "Manager",
    "email": "herve@amwaero.com"
  }
}
```

History-specific `relationtype` values: `"Seller"`, `"Purchaser"`, `"Operator"`, `"Seller's Broker"`, `"Purchaser's Broker"`.

See [Response Handling](response-handling.md) for the full nested vs flat schema comparison.

---

## History Records Are Event Pointers

History records include aircraft summary fields (make, model, tail, serial) but they are primarily **transaction records**. For full current aircraft state, enrich with other endpoints:

| Need | Endpoint |
|------|----------|
| Current ownership / operator details | `getRelationships` |
| Full aircraft detail | `getAircraftList` or `getRegNumber` |
| Company detail | `getCompany` |
| Flight activity | `getFlightDataPaged` |

### Enrichment Pattern

```python
history = get_all_pages(bearer, token, history_path, history_body)

for record in sorted(history, key=lambda r: r["transdate"]):
    aircraft_id = record["aircraftid"]
    
    relationships = api_post(
        f"/api/Aircraft/getRelationships/{token}",
        {"aclist": [aircraft_id], "modlist": []}
    )
```

---

## Use Cases

### Ownership Timeline

Query a single aircraft's full transaction history to build a chronological ownership chain:

```json
{
  "aircraftid": 125375,
  "transtype": ["None"],
  "startdate": "01/01/2010",
  "enddate": "02/28/2026",
  "allrelationships": true,
  "isinternaltrans": "Ignore",
  "isnewaircraft": "Ignore"
}
```

Sort results by `transdate ASC` to produce a timeline.

### Comparable Sales Analysis

Find all retail pre-owned sales for a model in a date window:

```json
{
  "modlist": [1194],
  "transtype": ["FullSale"],
  "isnewaircraft": "No",
  "isinternaltrans": "No",
  "allrelationships": true,
  "startdate": "01/01/2025",
  "enddate": "02/28/2026"
}
```

Filter results where `transretail: true` for arm's length transactions.

### Leasing Intelligence

Track lease activity for a model segment:

```json
{
  "modlist": [278, 288, 663],
  "transtype": ["Lease"],
  "startdate": "01/01/2025",
  "enddate": "02/28/2026",
  "allrelationships": true
}
```

### Change Detection Alerts

Poll periodically with a narrow date window to detect new transactions:

```json
{
  "modlist": [278],
  "transtype": ["None"],
  "startdate": "02/27/2026",
  "enddate": "02/28/2026",
  "allrelationships": true
}
```

---

## Performance Notes

- Always provide `startdate` / `enddate` to bound the query
- Use `modelid`, `modlist`, or `companyid` to limit scope
- High-activity models (e.g., King Air, Citation CJ series) produce dense result sets
- `maxpages: 0` / `currentpage: 0` means all results fit in one response -- not an error. See [Pagination](pagination.md) for the `max(maxpages, 1)` pattern.

---

## See Also

- [Response Handling](response-handling.md) -- nested relationship schema details
- [Enum Reference](enum-reference.md) -- `transtype` request categories and response values
- [Pagination](pagination.md) -- paged loop patterns and `maxpages: 0` quirk
- [Snapshots](snapshots.md) -- historical fleet state at a specific date
- [Flight Data](flight-data.md) -- operational activity (complementary to transaction history)
- [Common Mistakes](common-mistakes.md) -- known gotchas
