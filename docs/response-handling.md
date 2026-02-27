# Response Handling

## HTTP 200 Does Not Mean Success

JETNET returns HTTP 200 for most responses, including errors. You must always check the `responsestatus` field in the JSON body:

```python
result = r.json()
if "ERROR" in result.get("responsestatus", "").upper():
    raise ValueError(f"JETNET error: {result['responsestatus']}")
```

```javascript
const data = await res.json();
if ((data.responsestatus || "").toUpperCase().includes("ERROR")) {
  throw new Error(`JETNET error: ${data.responsestatus}`);
}
```

## responsestatus Values

| Status Pattern | Meaning |
|---------------|---------|
| `"SUCCESS"` | Request succeeded (non-paged) |
| `"SUCCESS: PAGE [ 1 of 428 ]"` | Paged request succeeded |
| `"ERROR: INVALID SECURITY TOKEN"` | Token expired — re-login and retry once |
| `"ERROR: ..."` | Any other error — do not retry, surface the message |

## companyrelationships Schema Differences

The `companyrelationships` structure **differs by endpoint**. This is the single biggest source of bugs when working across multiple JETNET endpoints.

| Endpoint | Schema | Relation Field | Relation Values |
|----------|--------|---------------|----------------|
| `getRegNumber` | **Flat** — prefixed fields (`companyname`, `contactfirstname`) | `companyrelation` | `"Owner"`, `"Operator"`, `"Chief Pilot"` |
| `getAircraftList` | Not present | — | — |
| `getHistoryList` / `getRelationships` | **Nested** — `company: {}`, `contact: {}` sub-objects | `relationtype` | `"Owner"`, `"Operator"`, `"Seller"`, `"Purchaser"`, `"Seller's Broker"` |
| `getBulkAircraftExport` | **Flat prefixed by role** — `owr*`, `opr*`, `chp*`, `excbrk1*`, `addl1*` | Field prefix | Owner=`owr*`, Operator=`opr*`, Chief Pilot=`chp*` |
| `getAcCompanyFractionalReportPaged` | **Flat** — top-level `comp*` and `contact*` fields | `relation` | `"Owner"`, `"Flight Department"`, `"Certificate Holder"` |

### getRegNumber (Flat Schema)

Fields are prefixed at the top level of each relationship object:

```json
{
  "companyrelation": "Owner",
  "companyname": "Acme Aviation LLC",
  "companyid": 4425,
  "contactfirstname": "John",
  "contactlastname": "Doe",
  "contacttitle": "Director of Aviation"
}
```

### getHistoryList / getRelationships (Nested Schema)

Each relationship contains nested `company` and `contact` objects:

```json
{
  "relationtype": "Owner",
  "relationseqno": 1,
  "company": {
    "companyid": 4425,
    "name": "Acme Aviation LLC",
    "address": "123 Main St"
  },
  "contact": {
    "contactid": 747133,
    "firstname": "John",
    "lastname": "Doe"
  }
}
```

### getBulkAircraftExport (Flat Prefixed by Role)

Each role uses a different field prefix:

```json
{
  "owrcompanyname": "Acme Aviation LLC",
  "owrcompanyid": 4425,
  "oprcompanyname": "Flight Ops Inc",
  "oprcompanyid": 5678,
  "chpfirstname": "Mike",
  "chplastname": "Smith"
}
```

| Prefix | Role |
|--------|------|
| `owr*` | Owner |
| `opr*` | Operator |
| `chp*` | Chief Pilot |
| `excbrk1*` / `excbrk2*` | Exclusive Brokers |
| `addl1*` / `addl2*` / `addl3*` | Additional relationships |

### getAcCompanyFractionalReportPaged (Flat)

```json
{
  "relation": "Fractional Owner",
  "companyname": "NetJets Sales Inc",
  "companyid": 12345,
  "fractionPercentOwned": "100.00"
}
```

- `fractionPercentOwned: "100.00"` = actual owner
- `fractionPercentOwned: "0.00"` = operator/manager on same aircraft

## Key Response Keys by Endpoint

| Endpoint | Response Key | Type |
|----------|-------------|------|
| `getRegNumber` | `aircraftresult` | Object |
| `getAircraftList` | `aircraft` | Array |
| `getHistoryListPaged` | `history` | Array |
| `getFlightDataPaged` | `flightdata` | Array |
| `getEventListPaged` | `events` | Array |
| `getRelationships` | `relationships` | Array |
| `getBulkAircraftExport` | `aircraft` | Array |
| `getCondensedOwnerOperators` | `aircraftowneroperators` | Array |
| `getPictures` | `pictures` | Array |
