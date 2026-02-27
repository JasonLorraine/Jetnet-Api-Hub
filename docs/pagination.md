# Pagination

## When to Use Paged Endpoints

Use `Paged` endpoint variants for history, flight data, events, bulk export, company lists, and contact lists. Non-paged versions time out on large datasets.

| Endpoint | Paged Variant |
|----------|--------------|
| `getHistoryList` | `getHistoryListPaged` |
| `getFlightData` | `getFlightDataPaged` |
| `getEventList` | `getEventListPaged` |
| `getBulkAircraftExport` | Always paged |
| `getCompanyList` | `getCompanyListPaged` |
| `getContactList` | `getContactListPaged` |
| `getCondensedOwnerOperators` | `getCondensedOwnerOperatorsPaged` |

## URL Pattern

```
POST .../getHistoryListPaged/{apiToken}/{pagesize}/{page}
```

- `{pagesize}` — number of records per page (typically `100`)
- `{page}` — **1-based** (first page = `1`, not `0`)

## Response Fields

| Field | Meaning |
|-------|---------|
| `maxpages` | Total number of pages available |
| `count` | Records on **this page** (not total records) |
| `currentpage` | The page you requested |
| `responsestatus` | Status string like `"SUCCESS: PAGE [ 1 of 428 ]"` |

Use `maxpages` for loop control — do not parse the `responsestatus` string.

## LIST_KEYS

Paged responses contain the data array under one of these keys:

```
history, flightdata, events, aircraft, aircraftowneroperators,
companylist, contactlist, relationships, aircraftcompfractionalrefs
```

## Pagination Loop — Python

```python
LIST_KEYS = {
    "history", "flightdata", "events", "aircraft",
    "aircraftowneroperators", "companylist", "contactlist",
    "relationships", "aircraftcompfractionalrefs"
}

def get_all_pages(bearer, token, paged_path, body, pagesize=100):
    results, page = [], 1
    while True:
        data = api("POST", f"{paged_path}/{pagesize}/{page}", bearer, token, body)
        for key in LIST_KEYS:
            if key in data and isinstance(data[key], list):
                results.extend(data[key])
                break
        if page >= data.get("maxpages", 1):
            break
        page += 1
    return results
```

## Pagination Loop — JavaScript

```javascript
const LIST_KEYS = new Set([
  "history", "flightdata", "events", "aircraft",
  "aircraftowneroperators", "companylist", "contactlist",
  "relationships", "aircraftcompfractionalrefs"
]);

async function getAllPages(bearerToken, apiToken, pagedPath, body, pagesize = 100) {
  const results = [];
  let page = 1;
  while (true) {
    const data = await api("POST", `${pagedPath}/${pagesize}/${page}`, bearerToken, apiToken, body);
    for (const key of LIST_KEYS) {
      if (Array.isArray(data[key])) {
        results.push(...data[key]);
        break;
      }
    }
    if (page >= (data.maxpages || 1)) break;
    page++;
  }
  return results;
}
```

## getBulkAircraftExport — maxpages:0 Quirk

`getBulkAircraftExport` returns `maxpages: 0` and `currentpage: 0` when **all results fit in a single response**. If your loop checks `page >= maxpages` before processing, you will exit immediately and miss all records.

**Fix:** Use `Math.max(maxpages, 1)` (or `max(maxpages, 1)` in Python) in your loop condition:

```python
def get_bulk_export(bearer, token, body, pagesize=100):
    results, page = [], 1
    while True:
        data = api("POST",
                   f"/api/Aircraft/getBulkAircraftExport/{token}/{pagesize}/{page}",
                   bearer, token, body)
        results.extend(data.get("aircraft", []))
        if page >= max(data.get("maxpages", 1), 1):
            break
        page += 1
    return results
```

```javascript
async function getBulkExport(bearerToken, apiToken, body, pagesize = 100) {
  const results = [];
  let page = 1;
  while (true) {
    const data = await api("POST",
      `/api/Aircraft/getBulkAircraftExport/${apiToken}/${pagesize}/${page}`,
      bearerToken, apiToken, body);
    results.push(...(data.aircraft || []));
    if (page >= Math.max(data.maxpages || 1, 1)) break;
    page++;
  }
  return results;
}
```
