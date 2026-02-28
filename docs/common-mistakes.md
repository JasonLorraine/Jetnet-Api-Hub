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

### `"SUCCESS: NO RESULTS FOUND"` is a normal response

Several endpoints return `responsestatus` values like `"SUCCESS: NO RESULTS FOUND [PHONE NUMBERS]"` when a query matches zero records. This is **not an error** — it is a valid business state. Use a prefix check, not strict equality:

```python
# Wrong — breaks on "SUCCESS: NO RESULTS FOUND [...]"
if result["responsestatus"] != "SUCCESS":
    raise ValueError("Request failed")

# Correct — treats any SUCCESS prefix as OK
if not result.get("responsestatus", "").upper().startswith("SUCCESS"):
    raise ValueError(f"JETNET error: {result['responsestatus']}")
```

```javascript
// Wrong
if (data.responsestatus !== "SUCCESS") throw new Error("Failed");

// Correct
if (!(data.responsestatus || "").toUpperCase().startsWith("SUCCESS")) {
  throw new Error(`JETNET error: ${data.responsestatus}`);
}
```

### Null arrays — guard before iterating

Fields like `phonenumbers`, `relatedcompanies`, and `companycertifications` return `null` (not `[]`) when empty. Any code calling `.map()` or `.forEach()` without a guard will crash:

```python
# Wrong — TypeError if phonenumbers is None
for p in result["phonenumbers"]:
    print(p)

# Correct
for p in result.get("phonenumbers") or []:
    print(p)
```

```javascript
// Wrong — Cannot read properties of null
data.phonenumbers.map(p => p.number);

// Correct
(data.phonenumbers ?? []).map(p => p.number);
```

### `isoperator` is a `"Y"` / `"N"` string

In relationship data, `isoperator` is a string, not a boolean:

```python
# Wrong — always truthy because "N" is a non-empty string
if record["isoperator"]:

# Correct
if record["isoperator"] == "Y":
```

## URL Shape Variations

### Mixed URL patterns across endpoints

JETNET endpoints use three different URL patterns. Trying to build all paths with a single template will break:

```
# Pattern 1: POST body + token only
POST /api/Contact/getContactList/{apiToken}

# Pattern 2: Resource ID + token
GET /api/Contact/getContact/{contactId}/{apiToken}

# Pattern 3: Token + pagination in path
POST /api/Aircraft/getHistoryListPaged/{apiToken}/{pageSize}/{page}
```

Build your URL helper to accept optional `id`, `pageSize`, and `page` parameters rather than assuming one shape fits all.

## Response key changes between paged and non-paged variants

The non-paged and paged versions of the same search endpoint use **different response keys**:

| Endpoint (non-paged) | Response key | Endpoint (paged) | Response key |
|----------------------|-------------|------------------|-------------|
| `getContactList` | `contacts` | `getContactListPaged` | `contactlist` |
| `getCompanyList` | `companies` | `getCompanyListPaged` | `companylist` |

Non-paged endpoints also return `currentpage: 0` and `maxpages: 0` — do **not** interpret these as paging metadata.

```python
# Wrong — assumes same key for both variants
data = response.json()
records = data["contacts"]  # works for non-paged, breaks for paged

# Correct — use the right key per variant
if is_paged:
    records = data["contactlist"]
else:
    records = data["contacts"]
```

## N+1 and Fan-Out Risks

### Company → Contacts returns ID arrays, not full objects

`getContacts` (`/api/Company/getContacts/{companyId}/{apiToken}`) returns contact IDs as a plain array — not hydrated contact objects:

```json
{ "contacts": [523097, 282591, 198443] }
```

To get full contact data, you must call `getContact` or `getIdentification` for **each** ID. This creates an N+1 fan-out problem. Mitigate with concurrency limits:

```python
import asyncio

sem = asyncio.Semaphore(5)

async def fetch_contact(session, contact_id):
    async with sem:
        return await session.get(f".../getContact/{contact_id}/{token}")

tasks = [fetch_contact(session, cid) for cid in contact_ids]
contacts = await asyncio.gather(*tasks)
```

```javascript
// Limit concurrency to 5 at a time
const pLimit = (await import("p-limit")).default;
const limit = pLimit(5);

const contacts = await Promise.all(
  contactIds.map(id => limit(() => fetchContact(id)))
);
```

### `ownerpercent` can be null even when relationship exists

Do not assume `ownerpercent` or `fractionexpiresdate` are always populated on ownership/fractional relationships. Always provide a fallback:

```python
pct = record.get("ownerpercent") or "0.00"
```

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
