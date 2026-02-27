# Common Mistakes

## Authentication

### `emailAddress` has a capital A

The login field is `emailAddress` — not `email`, `emailaddress`, or `email_address`. This is the single most common auth mistake.

```json
// Wrong
{ "email": "user@example.com", "password": "..." }
{ "emailaddress": "user@example.com", "password": "..." }

// Correct
{ "emailAddress": "user@example.com", "password": "..." }
```

### `apiToken` goes in the URL path only

The `apiToken` is placed in the URL path — never in headers or the JSON body.

```
// Wrong
Authorization: Bearer {bearerToken} {apiToken}
{ "apiToken": "abc123", ... }

// Correct
GET /api/Aircraft/getRegNumber/N123AB/{apiToken}
Authorization: Bearer {bearerToken}
```

## Response Handling

### HTTP 200 does not mean success

JETNET returns HTTP 200 for most responses, including errors. Always check `responsestatus`:

```python
result = r.json()
if "ERROR" in result.get("responsestatus", "").upper():
    raise ValueError(f"JETNET error: {result['responsestatus']}")
```

### `companyrelation` vs `relationtype`

Different endpoints use different field names for the relationship type. Using the wrong field returns nothing:

| Endpoint | Field Name |
|----------|-----------|
| `getRegNumber` | `companyrelation` |
| `getHistoryList` / `getRelationships` | `relationtype` |
| `getBulkAircraftExport` | Field prefix (`owr*`, `opr*`, `chp*`) |
| `getAcCompanyFractionalReportPaged` | `relation` |

See [Response Handling](response-handling.md) for the full schema comparison.

## Filters and Payloads

### Empty `aclist: []` means no filter, not empty results

Sending `"aclist": []` does not return zero results — it removes the aircraft filter entirely, returning all matching records. Be intentional:

```json
// Returns ALL aircraft (no filter)
{ "aclist": [], "modlist": [] }

// Returns only these specific aircraft
{ "aclist": [128228, 242781], "modlist": [] }
```

### `transtype: ["None"]` not `[]` for all history types

To get all transaction types in history queries, send `["None"]` — not an empty array:

```json
// Wrong — may not return all types
{ "transtype": [] }

// Correct — returns all transaction types
{ "transtype": ["None"] }
```

## Date Formatting

### Use `MM/DD/YYYY` with leading zeros

JETNET requires `MM/DD/YYYY` format with leading zeros:

```json
// Wrong
{ "startdate": "1/1/2024" }

// Correct
{ "startdate": "01/01/2024" }
```

### `getBulkAircraftExport` accepts datetime strings

The `actiondate` and `enddate` fields accept full datetime strings for hourly polling windows:

```json
{ "actiondate": "02/26/2026 10:00:00", "enddate": "02/26/2026 11:00:00" }
```

## String Booleans

### `forsale` in responses is a string

In most endpoints, `forsale` is `"true"` or `"false"` (strings), not JSON booleans:

```python
# Wrong
if record["forsale"]:  # Always truthy because it's a non-empty string

# Correct
if record["forsale"] == "true":
```

### `getBulkAircraftExport` uses `"Y"` / `"N"` for forsale

The bulk export endpoint uses a different convention:

```python
# In getBulkAircraftExport
if record["forsale"] == "Y":
```

### `datepurchased` format differs in bulk export

In `getBulkAircraftExport`, `datepurchased` is `YYYYMMDD` format (not `MM/DD/YYYY`).

## Endpoint-Specific Issues

### `getAircraftList` has no paged variant

Unlike most list endpoints, `getAircraftList` does not have a paged version. Use filters (`modlist`, geographic params, `forsale`) to control result size.

### `getEventList` enum values are strict

Sending unrecognized enum values to `getEventList` produces an `ERROR` in `responsestatus` despite HTTP 200. Use `getEventTypes` and `getEventCategories` to get valid values first.

### `getBulkAircraftExport` returns `maxpages: 0` for single-page results

When all results fit in one call, the response has `maxpages: 0` and `currentpage: 0`. Use `max(maxpages, 1)` in your loop or you will exit immediately and miss all records:

```python
if page >= max(data.get("maxpages", 1), 1):
    break
```

### `getAcCompanyFractionalReportPaged` response key

The response key is `aircraftcompfractionalrefs`. Each row is one relationship per aircraft:

- `fractionPercentOwned: "100.00"` = actual owner
- `fractionPercentOwned: "0.00"` = operator/manager on same aircraft
- The `relationship` filter is an array: `["Fractional Owner"]`

## Field Name Gotchas

### `getRegNumber` flat companyrelationships

The flat schema uses `companyrelation` and prefixed fields (`companyname`, `contactfirstname`). For FBO ramp contact lookup, filter on `contacttitle` for Chief Pilot, Director of Aviation, Scheduler, or Dispatcher.

### `getBulkAircraftExport` flat prefixed schema

Role-prefixed fields: `owr*` = owner, `opr*` = operator, `chp*` = chief pilot, `excbrk1*`/`excbrk2*` = brokers, `addl1-3*` = additional. This is not the same schema as `getRegNumber` or `getRelationships`.
