# Response Shapes

Normalized UI contracts for building frontends, mobile apps, and CRM integrations on top of JETNET data. Never pass raw JETNET responses directly to a client — map them to these stable shapes first.

---

## AircraftCard

The core aircraft identity object. Every UI that shows an aircraft should render this shape.

| Field | Type | Description |
|-------|------|-------------|
| `aircraftId` | integer | JETNET internal aircraft ID — the universal join key |
| `regNbr` | string | Registration / tail number (e.g. `"N123AB"`) |
| `serialNbr` | string | Manufacturer serial number |
| `make` | string | Aircraft make (e.g. `"GULFSTREAM"`) |
| `model` | string | Aircraft model (e.g. `"G650"`) |
| `year` | integer \| null | Year manufactured (`yearmfr`) or year delivered (`yeardlv`) — use whichever is present |
| `ownerCompanyId` | integer \| null | Company ID of the current owner (if resolved) |
| `operatorCompanyId` | integer \| null | Company ID of the current operator (if resolved) |

```json
{
  "aircraftId": 211461,
  "regNbr": "N123AB",
  "serialNbr": "6302",
  "make": "GULFSTREAM",
  "model": "G650",
  "year": 2018,
  "ownerCompanyId": 4425,
  "operatorCompanyId": 5678
}
```

---

## CompanyCard

Represents an owner, operator, or any company related to an aircraft.

| Field | Type | Description |
|-------|------|-------------|
| `companyId` | integer | JETNET company ID |
| `companyName` | string | Legal or display name |
| `segment` | string \| null | Business segment (e.g. `"Corporate"`, `"Charter"`) |
| `location` | string \| null | City/state/country summary |
| `primaryPhone` | string \| null | Main phone number |

```json
{
  "companyId": 4425,
  "companyName": "Acme Aviation LLC",
  "segment": "Corporate",
  "location": "Teterboro, NJ, US",
  "primaryPhone": "+1-201-555-0100"
}
```

---

## GoldenPathResult

The full response for the "enter a tail number, get a profile" workflow. This is the shape your `/lookup` or `/profile` endpoint should return.

| Field | Type | Description |
|-------|------|-------------|
| `aircraft` | AircraftCard | Core aircraft identity (always present) |
| `owner` | CompanyCard \| null | Current owner, if resolved |
| `operator` | CompanyCard \| null | Current operator, if resolved |
| `utilization` | object \| null | Flight activity summary for a recent window |
| `_debug` | object | Raw endpoint responses for troubleshooting (strip in production) |

```json
{
  "aircraft": {
    "aircraftId": 211461,
    "regNbr": "N123AB",
    "serialNbr": "6302",
    "make": "GULFSTREAM",
    "model": "G650",
    "year": 2018,
    "ownerCompanyId": 4425,
    "operatorCompanyId": 5678
  },
  "owner": {
    "companyId": 4425,
    "companyName": "Acme Aviation LLC",
    "segment": "Corporate",
    "location": "Teterboro, NJ, US",
    "primaryPhone": "+1-201-555-0100"
  },
  "operator": {
    "companyId": 5678,
    "companyName": "Flight Ops Inc",
    "segment": "Management",
    "location": "White Plains, NY, US",
    "primaryPhone": "+1-914-555-0200"
  },
  "utilization": {
    "periodDays": 180,
    "totalFlights": 47,
    "totalHours": 132.5,
    "topOrigin": "KTEB",
    "topDestination": "KPBI"
  },
  "_debug": {
    "endpoints": [
      "getRegNumber",
      "getRelationships",
      "getFlightDataPaged"
    ],
    "rawResponsestatuses": [
      "SUCCESS",
      "SUCCESS",
      "SUCCESS: PAGE [ 1 of 1 ]"
    ]
  }
}
```

---

## Error

Normalized error shape. Every error response your backend emits should follow this contract so the frontend has a single error-handling path.

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Machine-readable error code (e.g. `"AIRCRAFT_NOT_FOUND"`, `"AUTH_FAILED"`, `"JETNET_ERROR"`) |
| `message` | string | Human-readable description |
| `endpoint` | string \| null | The JETNET endpoint that failed (for debugging) |
| `rawResponsestatus` | string \| null | The raw `responsestatus` value from JETNET, if available |

```json
{
  "code": "JETNET_ERROR",
  "message": "JETNET returned an error on tail lookup",
  "endpoint": "/api/Aircraft/getRegNumber/NXXXXX/{apiToken}",
  "rawResponsestatus": "ERROR: INVALID SECURITY TOKEN"
}
```

---

## Mapping Examples

### 1. `getRegNumber` → AircraftCard

The tail lookup endpoint returns an `aircraftresult` object with flat fields. Map it to an `AircraftCard`:

```python
raw = jetnet("GET", f"/api/Aircraft/getRegNumber/{reg}/{{apiToken}}")
ac = raw["aircraftresult"]

aircraft_card = {
    "aircraftId":        ac["aircraftid"],
    "regNbr":            ac["regnbr"],
    "serialNbr":         ac.get("serialnbr", ""),
    "make":              ac["make"],
    "model":             ac["model"],
    "year":              ac.get("yearmfr") or ac.get("yeardlv"),
    "ownerCompanyId":    None,   # not available from this endpoint
    "operatorCompanyId": None,   # not available from this endpoint
}
```

> **Note:** `getRegNumber` does not return owner/operator company IDs directly. You must call `getRelationships` or inspect the `companyrelationships` array (if present) to fill those in.

### 2. `getRelationships` → CompanyCard (owner + operator)

The relationships endpoint returns a `relationships` array with nested `company` objects. Extract owner and operator:

```python
raw = jetnet("POST", "/api/Aircraft/getRelationships/{apiToken}", {
    "aircraftid": aircraft_id,
    "aclist": [], "modlist": [],
    "actiondate": "", "showHistoricalAcRefs": False
})

owner = None
operator = None

for rel in raw.get("relationships", []):
    card = {
        "companyId":    rel.get("companyid") or rel.get("company", {}).get("companyid"),
        "companyName":  rel.get("name") or rel.get("company", {}).get("name"),
        "segment":      None,          # not returned by this endpoint
        "location":     None,          # not returned by this endpoint
        "primaryPhone": None,          # not returned by this endpoint
    }
    if rel.get("relationtype") == "Owner" and rel.get("relationseqno") == 1:
        owner = card
    elif rel.get("relationtype") == "Operator" and rel.get("relationseqno") == 1:
        operator = card
```

> To fill in `segment`, `location`, and `primaryPhone`, make a follow-up call to `GET /api/Company/getCompany/{companyId}/{apiToken}`.

### 3. `getBulkAircraftExport` → AircraftCard (with owner/operator pre-filled)

The bulk export uses flat role-prefixed fields (`owr*`, `opr*`). You can build both `AircraftCard` and `CompanyCard` objects from a single row:

```python
raw = jetnet("POST", "/api/Aircraft/getBulkAircraftExportPaged/{apiToken}/100/1", {
    "make": "GULFSTREAM", "aclist": [], "modlist": []
})

for row in raw.get("aircraft", []):
    aircraft_card = {
        "aircraftId":        row["aircraftid"],
        "regNbr":            row["regnbr"],
        "serialNbr":         row.get("sernbr", ""),
        "make":              row["make"],
        "model":             row["model"],
        "year":              row.get("yearmfr") or row.get("yeardlv"),
        "ownerCompanyId":    row.get("owrcompanyid"),
        "operatorCompanyId": row.get("oprcompanyid"),
    }

    owner_card = {
        "companyId":    row.get("owrcompanyid"),
        "companyName":  row.get("owrcompanyname"),
        "segment":      None,
        "location":     None,
        "primaryPhone": None,
    } if row.get("owrcompanyid") else None

    operator_card = {
        "companyId":    row.get("oprcompanyid"),
        "companyName":  row.get("oprcompanyname"),
        "segment":      None,
        "location":     None,
        "primaryPhone": None,
    } if row.get("oprcompanyid") else None
```

---

## Where People Go Wrong

### 1. Treating HTTP 200 as success

JETNET returns HTTP 200 for most responses — including errors. You **must** check the `responsestatus` field in every response body:

```python
result = r.json()
status = result.get("responsestatus", "")
if "ERROR" in status.upper():
    raise ValueError(f"JETNET error: {status}")
```

If you skip this check, your app will silently render empty data or crash downstream when fields are missing.

### 2. Assuming the same schema across endpoints

The `companyrelationships` structure differs by endpoint — this is the single biggest source of mapping bugs:

| Endpoint | Schema Style | Relation Field | How to get company name |
|----------|-------------|----------------|------------------------|
| `getRegNumber` | Flat | `companyrelation` | `companyname` (top-level) |
| `getRelationships` | Nested | `relationtype` | `company.name` (nested object) |
| `getBulkAircraftExport` | Role-prefixed | Field prefix (`owr*`, `opr*`) | `owrcompanyname`, `oprcompanyname` |

If you copy mapping code from one endpoint and use it on another, fields will be `undefined` / `None`. Always check which endpoint you are mapping from.

### 3. Confusing owner vs. operator

Many aircraft have both an **owner** (the legal title holder) and an **operator** (the company that flies it). These are often different entities. When `relationseqno` > 1, there may be multiple owners or operators — always filter for `relationseqno == 1` to get the primary.

### 4. Forgetting to enrich CompanyCard fields

The `getRelationships` and `getBulkAircraftExport` endpoints return company ID and name but not segment, location, or phone. If your UI needs those fields, you need a follow-up call to `GET /api/Company/getCompany/{companyId}/{apiToken}` or `GET /api/Company/getIdentification/{companyId}/{apiToken}`.

### 5. Hardcoding date strings

Flight activity and history endpoints require `startdate` and `enddate` in `MM/DD/YYYY` format. Compute these dynamically at runtime:

```python
from datetime import datetime, timedelta
start = (datetime.now() - timedelta(days=180)).strftime("%m/%d/%Y")
end = datetime.now().strftime("%m/%d/%Y")
```

Never hardcode dates like `"01/01/2024"` — your queries will silently return stale or empty data as time passes.

### 6. Swapping bearer token and API token

- `bearerToken` goes in the **Authorization header**: `Authorization: Bearer {bearerToken}`
- `apiToken` goes in the **URL path**: `/api/Aircraft/getRegNumber/N123AB/{apiToken}`

If you swap them, you will get `INVALID SECURITY TOKEN` errors even though you just logged in successfully.
