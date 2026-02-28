# JETNET Aircraft Endpoints

## Conceptual Model

Aircraft endpoints cover the full lifecycle of a single aircraft record. JETNET models an aircraft as a **composite document** -- a root record (`getAircraft`) composed of independent sub-records that can be fetched individually or bundled together.

```
                    ┌──────────────┐
                    │  getAircraft │  (full composite)
                    └──────┬───────┘
                           │
    ┌──────────┬───────────┼───────────┬──────────┐
    │          │           │           │          │
┌───┴───┐ ┌───┴───┐ ┌─────┴─────┐ ┌──┴───┐ ┌───┴────┐
│ Ident │ │Engine │ │ Avionics  │ │ Pics │ │Company │
│       │ │       │ │ Features  │ │      │ │  Rels  │
│Status │ │  APU  │ │ AddlEquip │ │Lease │ │        │
│Airfrm │ │       │ │ Int / Ext │ │      │ │        │
│ Maint │ │       │ │           │ │      │ │        │
└───────┘ └───────┘ └───────────┘ └──────┘ └────────┘
```

You have three access patterns:

| Pattern | When to Use | Endpoint |
|---------|-------------|----------|
| Full record | Need everything for one aircraft | `getAircraft` |
| Sub-record | Need one section (e.g., engines only) | `getEngine`, `getAirframe`, etc. |
| Quick lookup | Start from tail number or hex code | `getRegNumber`, `getHexNumber` |

---

## Endpoints

| # | Endpoint | Method | Path | Response Key |
|---|----------|--------|------|-------------|
| 1 | getAircraft | GET | `/api/Aircraft/getAircraft/{id}/{apiToken}` | `aircraft` |
| 2 | getIdentification | GET | `/api/Aircraft/getIdentification/{id}/{apiToken}` | `identification` |
| 3 | getStatus | GET | `/api/Aircraft/getStatus/{id}/{apiToken}` | `status` |
| 4 | getAirframe | GET | `/api/Aircraft/getAirframe/{id}/{apiToken}` | `airframe` |
| 5 | getEngine | GET | `/api/Aircraft/getEngine/{id}/{apiToken}` | `engine` |
| 6 | getApu | GET | `/api/Aircraft/getApu/{id}/{apiToken}` | `apu` |
| 7 | getAvionics | GET | `/api/Aircraft/getAvionics/{id}/{apiToken}` | `avionics` |
| 8 | getFeatures | GET | `/api/Aircraft/getFeatures/{id}/{apiToken}` | `features` |
| 9 | getAdditionalEquipment | GET | `/api/Aircraft/getAdditionalEquipment/{id}/{apiToken}` | `additionalequipment` |
| 10 | getInterior | GET | `/api/Aircraft/getInterior/{id}/{apiToken}` | `interior` |
| 11 | getExterior | GET | `/api/Aircraft/getExterior/{id}/{apiToken}` | `exterior` |
| 12 | getMaintenance | GET | `/api/Aircraft/getMaintenance/{id}/{apiToken}` | `maintenance` |
| 13 | getLeases | GET | `/api/Aircraft/getLeases/{id}/{apiToken}` | `leases` |
| 14 | getPictures | GET | `/api/Aircraft/getPictures/{id}/{apiToken}` | `pictures` |
| 15 | getCompanyrelationships | GET | `/api/Aircraft/getCompanyrelationships/{id}/{apiToken}` | `companyrelationships` |
| 16 | getFlights | GET | `/api/Aircraft/getFlights/{id}/{apiToken}` | `flightsummary` |
| 17 | getRegNumber | GET | `/api/Aircraft/getRegNumber/{reg}/{apiToken}` | `aircraftresult` |
| 18 | getHexNumber | GET | `/api/Aircraft/getHexNumber/{hex}/{apiToken}` | `aircraft` |
| 19 | getAircraftList | POST | `/api/Aircraft/getAircraftList/{apiToken}` | `aircraft` |
| 20 | getRelationships | POST | `/api/Aircraft/getRelationships/{apiToken}` | `relationships` |
| 21 | getAllAircraftObjects | POST | `/api/Aircraft/getAllAircraftObjects/{apiToken}/{pagesize}/{page}` | `allaircraftobjects` |

Endpoints with dedicated docs (not duplicated here):

| Endpoint | See |
|----------|-----|
| getHistoryListPaged | [docs/history.md](history.md) |
| getEventListPaged | [docs/events.md](events.md) |
| getFlightDataPaged / getFlights | [docs/flight-data.md](flight-data.md) |
| getBulkAircraftExportPaged | [docs/bulk-export.md](bulk-export.md) |
| getCondensedOwnerOperatorsPaged | [docs/trends.md](trends.md) |
| getCondensedSnapshot | [docs/snapshots.md](snapshots.md) |
| getAcCompanyFractionalReportPaged | [docs/response-handling.md](response-handling.md) |
| getAcSellerPurchaserReportPaged | [references/endpoints.md](../references/endpoints.md) |

---

## 1. getAircraft (Full Record)

```
GET /api/Aircraft/getAircraft/{id}/{apiToken}
```

Returns the complete aircraft record for a single `aircraftid`. This is the bundled composite -- it includes identification, status, airframe, engines, avionics, features, interior, exterior, maintenance, leases, pictures, and company relationships as nested objects.

### Response Structure

```json
{
  "responsestatus": "SUCCESS",
  "aircraft": {
    "identification": {
      "aircraftid": 12345,
      "modelid": 278,
      "make": "Gulfstream Aerospace",
      "model": "G550",
      "sernbr": "5432",
      "regnbr": "N550GD",
      "yearmfr": 2014,
      "yeardlv": 2015,
      "actiondate": "2025-01-15T00:00:00",
      "pageurl": "..."
    },
    "airframe": { ... },
    "engine": { ... },
    "apu": { ... },
    "avionics": [ ... ],
    "features": [ ... ],
    "additionalequipment": [ ... ],
    "interior": { ... },
    "exterior": { ... },
    "maintenance": { ... },
    "leases": [ ... ],
    "pictures": [ ... ],
    "companyrelationships": [ ... ],
    "status": { ... }
  }
}
```

### When to Use

Use `getAircraft` when you need the full profile for a single aircraft. For targeted data (e.g., just engines or just maintenance), use the individual sub-record endpoints instead -- they return faster and consume less bandwidth.

---

## 2. getIdentification

```
GET /api/Aircraft/getIdentification/{id}/{apiToken}
```

Returns the identification header for an aircraft: make, model, registration, serial number, year manufactured, year delivered, and metadata.

### Response Key

`identification`

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `aircraftid` | integer | Primary key |
| `modelid` | integer | Model ID (AMODID) for `modlist` filters |
| `make` | string | Manufacturer name |
| `model` | string | Model designation |
| `sernbr` | string | Manufacturer serial number |
| `regnbr` | string | Registration / tail number |
| `yearmfr` | integer | Year manufactured |
| `yeardlv` | integer | Year delivered |
| `actiondate` | string (ISO) | Last data update |
| `pageurl` | string | JETNET web page URL |

---

## 3. getStatus

```
GET /api/Aircraft/getStatus/{id}/{apiToken}
```

Returns lifecycle and market status indicators: whether the aircraft is in operation, for sale, in storage, retired, etc.

### Response Key

`status`

---

## 4. getAirframe

```
GET /api/Aircraft/getAirframe/{id}/{apiToken}
```

Returns airframe time and landing metrics.

### Response Key

`airframe`

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `aftt` | number | Airframe total time (hours) |
| `landings` | number | Total landings |
| `timesasofdate` | string (ISO) | Date when times were last reported |
| `estaftt` | number | Estimated airframe total time |

---

## 5. getEngine

```
GET /api/Aircraft/getEngine/{id}/{apiToken}
```

Returns engine details including maintenance program enrollment and per-engine times.

### Response Key

`engine`

### Response Structure

The `engine` object contains top-level fields plus an `engines` array for per-engine data:

```json
{
  "responsestatus": "SUCCESS",
  "engine": {
    "maintenanceprogram": "MSP Gold",
    "model": "BR725",
    "enginenoiserating": "Stage 4",
    "engines": [
      {
        "sequencenumber": 1,
        "serialnumber": "E-12345",
        "timesincenew": 4500,
        "tbo": 8000
      },
      {
        "sequencenumber": 2,
        "serialnumber": "E-12346",
        "timesincenew": 4500,
        "tbo": 8000
      }
    ]
  }
}
```

### Gotcha

The response has two levels: the outer `engine` object (model-level data) and the inner `engines` array (per-engine data). Don't confuse `data["engine"]` with `data["engine"]["engines"]`.

---

## 6. getApu

```
GET /api/Aircraft/getApu/{id}/{apiToken}
```

Returns APU (Auxiliary Power Unit) details when available.

### Response Key

`apu` (object or `null`)

### Null Handling

Many aircraft have no APU data. When no APU exists:

```json
{
  "responsestatus": "SUCCESS: NO RESULTS FOUND [APU]",
  "apu": null
}
```

Always check for `null` before accessing APU fields. Also note that `responsestatus` starts with `"SUCCESS"` even when no data is found -- use `.startsWith("SUCCESS")`, not strict equality.

---

## 7. getAvionics

```
GET /api/Aircraft/getAvionics/{id}/{apiToken}
```

Returns installed avionics packages.

### Response Key

`avionics` (array) + `count`

### Response Structure

```json
{
  "responsestatus": "SUCCESS",
  "count": 3,
  "avionics": [
    { "name": "Collins Pro Line 21", "description": "Integrated avionics suite" },
    { "name": "HUD/EVS", "description": "Head-up display with enhanced vision" }
  ]
}
```

---

## 8. getFeatures

```
GET /api/Aircraft/getFeatures/{id}/{apiToken}
```

Returns aircraft feature list (cabin options, systems, modifications).

### Response Key

`features` (array) + `count`

---

## 9. getAdditionalEquipment

```
GET /api/Aircraft/getAdditionalEquipment/{id}/{apiToken}
```

Returns additional installed equipment, often free-text descriptions.

### Response Key

`additionalequipment` (array) + `count`

### Response Structure

```json
{
  "responsestatus": "SUCCESS",
  "count": 2,
  "additionalequipment": [
    { "name": "WiFi", "description": "Gogo AVANCE L5 broadband with global coverage" },
    { "name": "Satcom", "description": "Honeywell JetWave Ka-band satellite" }
  ]
}
```

---

## 10. getInterior

```
GET /api/Aircraft/getInterior/{id}/{apiToken}
```

Returns interior configuration, cabin layout, and refurbishment notes.

### Response Key

`interior`

---

## 11. getExterior

```
GET /api/Aircraft/getExterior/{id}/{apiToken}
```

Returns paint scheme, exterior configuration, and repaint history.

### Response Key

`exterior`

---

## 12. getMaintenance

```
GET /api/Aircraft/getMaintenance/{id}/{apiToken}
```

Returns maintenance status, program enrollment, and coverage notes.

### Response Key

`maintenance`

---

## 13. getLeases

```
GET /api/Aircraft/getLeases/{id}/{apiToken}
```

Returns lease information when available.

### Response Key

`leases` (array or `null`)

When no lease data exists, `leases` is `null` (not an empty array).

---

## 14. getPictures

```
GET /api/Aircraft/getPictures/{id}/{apiToken}
```

Returns image metadata and URLs for aircraft photos.

### Response Key

`pictures` (array) + `count`

---

## 15. getCompanyrelationships

```
GET /api/Aircraft/getCompanyrelationships/{id}/{apiToken}
```

Returns company relationship rows tied to a specific aircraft: owner, operator, manager, trustee, etc.

### Response Key

`companyrelationships` (array) + `count`

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `companyid` | integer | Company ID |
| `name` | string | Company name |
| `relationtype` | string | Relationship type (Owner, Operator, Manager, Trustee, etc.) |
| `relationseqno` | integer | Sequence number for ordering |
| `contactid` | integer | Associated contact ID |
| `ownerpercent` | number | Ownership percentage (for fractional) |
| `fractionexpiresdate` | string | Fractional share expiration |
| `isoperator` | string | `"Y"` or `"N"` -- **string, not boolean** |

### Gotcha: `isoperator` Is a String

```python
# WRONG
if rel["isoperator"]:  # always truthy -- "N" is truthy in Python

# CORRECT
if rel["isoperator"] == "Y":
```

### Difference from `getRelationships`

`getCompanyrelationships` is a **GET** endpoint for a single aircraft by ID. `getRelationships` is a **POST** endpoint for batch queries across multiple aircraft. They return different response structures:

| Endpoint | Method | Response Key | Use Case |
|----------|--------|-------------|----------|
| `getCompanyrelationships` | GET | `companyrelationships` | Single aircraft, flat records |
| `getRelationships` | POST | `relationships` | Batch query, nested company/contact objects |

---

## 16. getFlights (Flight Summary)

```
GET /api/Aircraft/getFlights/{id}/{apiToken}
```

Returns aggregated monthly flight utilization for an aircraft. For per-flight detail records, use `getFlightDataPaged` instead.

### Response Key

`flightsummary`

See [docs/flight-data.md](flight-data.md) for full documentation including the distinction between `getFlights` (summary) and `getFlightDataPaged` (detail).

---

## 17. getRegNumber (Tail Lookup)

```
GET /api/Aircraft/getRegNumber/{reg}/{apiToken}
```

Quick lookup by registration / tail number. This is the **entry point** for the Golden Path workflow.

### Response Key

`aircraftresult` (object)

### Response Structure

Returns a flat object with essential aircraft fields plus inline company relationships:

```json
{
  "responsestatus": "SUCCESS",
  "aircraftresult": {
    "aircraftid": 12345,
    "make": "Gulfstream Aerospace",
    "model": "G550",
    "modelid": 278,
    "sernbr": "5432",
    "regnbr": "N550GD",
    "yearmfr": 2014,
    "yeardlv": 2015,
    "forsale": "N",
    "marketstatus": "",
    "asking": 0,
    "companyrelationships": [
      {
        "companyid": 4425,
        "companyname": "Acme Aviation LLC",
        "companyrelation": "Owner",
        "contactid": 343,
        "contactfirstname": "William",
        "contactlastname": "Butler"
      }
    ]
  }
}
```

### Schema Note

`getRegNumber` uses a **flat schema** with `companyrelation` (not `relationtype`). This differs from `getRelationships` which uses a **nested schema** with `relationtype`. See [docs/response-handling.md](response-handling.md) for the full schema comparison.

---

## 18. getHexNumber (Hex Code Lookup)

```
GET /api/Aircraft/getHexNumber/{hex}/{apiToken}
```

Quick lookup by Mode S / ICAO hex code (e.g., `A12345`).

### Response Key

`aircraft` (object with essential fields)

---

## 19. getAircraftList (Fleet Search)

```
POST /api/Aircraft/getAircraftList/{apiToken}
```

Returns aircraft matching filters: model, lifecycle, for-sale status, geography, etc.

### Request Body (`AcListOptions`)

| Field | Type | Description |
|-------|------|-------------|
| `modlist` | array of int | Model IDs to filter |
| `forsale` | string | `"true"`, `"false"`, or `""` (all) |
| `lifecycle` | string | `InOperation`, `Retired`, `InStorage`, etc. |
| `basecountry` | string | Country filter |
| `basecountrylist` | array | Multiple countries |
| `basestate` | array | US state abbreviations |
| `make` | string | Make filter |
| `makelist` | array | Multiple makes |
| `aclist` | array of int | Specific aircraft IDs |
| `companyid` | integer | Filter by company |
| `actiondate` | string | Changed-since date (MM/DD/YYYY) |
| `enddate` | string | Changed-before date (MM/DD/YYYY) |
| `aircraftchanges` | string | `"true"` for delta mode |
| `sernbr` | string | Serial number filter |
| `regnbr` | string | Registration filter |
| `regnbrlist` | array | Multiple registration numbers |
| `exactMatchReg` | boolean | Exact match on registration |
| `showHistoricalAcRefs` | boolean | Include historical relationships |

### Response Key

`aircraft` (array) + `count`

### Response Fields

Each aircraft object includes: `aircraftid`, `make`, `model`, `modelid`, `icao`, `sernbr`, `regnbr`, `yearmfr`, `yeardlv`, `forsale`, `marketstatus`, `asking`, `pageurl`.

### Gotcha: No Paged Variant

Unlike most list endpoints, `getAircraftList` does **not** have a paged version. Use filters (`modlist`, geographic params, `forsale`) to control result size. For large datasets, use `getBulkAircraftExportPaged` instead.

### Example

```python
body = {
    "modlist": [278],
    "forsale": "true",
    "lifecycle": "InOperation",
    "basecountrylist": ["United States"],
    "aclist": [],
    "airframetype": "None",
    "maketype": "None"
}
resp = session.post(f"{BASE}/api/Aircraft/getAircraftList/{token}", json=body)
aircraft = resp.json().get("aircraft", [])
```

```javascript
const body = {
  modlist: [278],
  forsale: "true",
  lifecycle: "InOperation",
  basecountrylist: ["United States"],
  aclist: [],
  airframetype: "None",
  maketype: "None"
};
const resp = await fetch(`${BASE}/api/Aircraft/getAircraftList/${TOKEN}`, {
  method: "POST",
  headers: { "Content-Type": "application/json", Authorization: `Bearer ${BEARER}` },
  body: JSON.stringify(body)
});
const { aircraft } = await resp.json();
```

---

## 20. getRelationships (Batch)

```
POST /api/Aircraft/getRelationships/{apiToken}
```

Returns relationship records (owner, operator, manager, trustee, etc.) for aircraft matching filter criteria. Used for batch queries across multiple aircraft.

### Request Body

| Field | Type | Description |
|-------|------|-------------|
| `aircraftid` | integer | Single aircraft ID |
| `aclist` | array of int | List of aircraft IDs |
| `modlist` | array of int | Model IDs |
| `actiondate` | string | Changed-since date (MM/DD/YYYY) |
| `showHistoricalAcRefs` | boolean | Include historical relationships |

### Response Key

`relationships` (array) + `count`

### Nested Schema

Each relationship record uses the nested schema with `company: {}` and `contact: {}` sub-objects:

```json
{
  "relationships": [
    {
      "aircraftid": 12345,
      "relationtype": "Owner",
      "company": {
        "companyid": 4425,
        "name": "Acme Aviation LLC",
        "city": "Dallas",
        "state": "Texas",
        "country": "United States"
      },
      "contact": {
        "contactid": 343,
        "firstname": "William",
        "lastname": "Butler",
        "title": "President"
      }
    }
  ]
}
```

### Best Practice

Always include `aclist` with the aircraft IDs you want, even if you also set `aircraftid`:

```python
body = {
    "aircraftid": 12345,
    "aclist": [12345],
    "modlist": [],
    "actiondate": "",
    "showHistoricalAcRefs": False
}
```

---

## 21. getAllAircraftObjects (Bulk Detail)

```
POST /api/Aircraft/getAllAircraftObjects/{apiToken}/{pagesize}/{page}
```

Paged retrieval of full aircraft object records. Requires an aircraft ID list -- sending an empty list returns an error.

### Request Body

| Field | Type | Description |
|-------|------|-------------|
| `aclist` | array of int | **Required** -- aircraft IDs to retrieve |
| `airframetype` | string | Airframe type filter |
| `maketype` | string | Make type filter |
| `sernbr` | string | Serial number filter |
| `regnbr` | string | Registration filter |
| `regnbrlist` | array | Registration number list |
| `modelid` | integer | Model ID filter |
| `make` | string | Make filter |

### Response Key

`allaircraftobjects` (array)

### Error: Missing ID List

```json
{
  "responsestatus": "ERROR: Aircraft ID List cannot be null or empty."
}
```

---

## Common Patterns

### Sub-Record Fan-Out

When you need specific sections for an aircraft, call the individual sub-record endpoints instead of `getAircraft`. This is especially useful when you only need one or two sections:

```python
aircraft_id = 12345

engine_data = session.get(f"{BASE}/api/Aircraft/getEngine/{aircraft_id}/{token}").json()
airframe_data = session.get(f"{BASE}/api/Aircraft/getAirframe/{aircraft_id}/{token}").json()

engines = engine_data.get("engine", {})
airframe = airframe_data.get("airframe", {})

print(f"AFTT: {airframe.get('aftt')} hours")
print(f"Engine program: {engines.get('maintenanceprogram')}")
```

```javascript
const [engineResp, airframeResp] = await Promise.all([
  fetch(`${BASE}/api/Aircraft/getEngine/${aircraftId}/${TOKEN}`),
  fetch(`${BASE}/api/Aircraft/getAirframe/${aircraftId}/${TOKEN}`)
]);

const { engine } = await engineResp.json();
const { airframe } = await airframeResp.json();

console.log(`AFTT: ${airframe?.aftt} hours`);
console.log(`Engine program: ${engine?.maintenanceprogram}`);
```

### Tail-to-Profile (Golden Path)

The most common workflow starts with a tail number and builds a complete profile:

```
1. getRegNumber/{tail}/{apiToken}         → aircraftid, basic info
2. getRelationships/{apiToken}            → owner, operator, manager
   getPictures/{aircraftid}/{apiToken}    → photos (parallel with step 2)
3. getHistoryListPaged/{apiToken}/100/1   → transaction history (lazy)
```

See the [Golden Path](../START_HERE.md) documentation for the full walkthrough.

### Null Array Handling

Several sub-record endpoints return `null` instead of `[]` when no data exists. Always use defensive access:

```python
avionics = resp.get("avionics") or []
leases = resp.get("leases") or []
pictures = resp.get("pictures") or []
```

```javascript
const avionics = data.avionics ?? [];
const leases = data.leases ?? [];
const pictures = data.pictures ?? [];
```

---

## Response Key Quick Reference

| Endpoint | Response Key | Type | Notes |
|----------|-------------|------|-------|
| getAircraft | `aircraft` | Object | Composite with nested sub-records |
| getIdentification | `identification` | Object | |
| getStatus | `status` | Object | |
| getAirframe | `airframe` | Object | `aftt`, `landings`, `timesasofdate` |
| getEngine | `engine` | Object | Contains `engines[]` sub-array |
| getApu | `apu` | Object or null | Check responsestatus for "NO RESULTS FOUND" |
| getAvionics | `avionics` | Array | + `count` |
| getFeatures | `features` | Array | + `count` |
| getAdditionalEquipment | `additionalequipment` | Array | + `count` |
| getInterior | `interior` | Object | |
| getExterior | `exterior` | Object | |
| getMaintenance | `maintenance` | Object | |
| getLeases | `leases` | Array or null | null when no leases |
| getPictures | `pictures` | Array | + `count` |
| getCompanyrelationships | `companyrelationships` | Array | + `count`; `isoperator` is string |
| getFlights | `flightsummary` | Object/Array | See flight-data.md |
| getRegNumber | `aircraftresult` | Object | Flat schema with `companyrelation` |
| getHexNumber | `aircraft` | Object | Essential fields |
| getAircraftList | `aircraft` | Array | No paged variant |
| getRelationships | `relationships` | Array | Nested schema with `relationtype` |
| getAllAircraftObjects | `allaircraftobjects` | Array | Requires aclist |
