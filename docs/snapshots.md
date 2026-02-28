# JETNET Aircraft Snapshot Endpoint

## Conceptual Model

The snapshot endpoint provides a **frozen view of aircraft ownership and operator state at a specific historical date**. Unlike history endpoints (which return transaction events) or live queries (which return current state), snapshots answer:

> "Who owned or operated this aircraft on May 1, 2016?"

Think of it as a database time machine for fleet composition.

```
Aircraft Timeline
------------------------------
2014  Owner A
2016  Owner B
2019  Owner C

Snapshot(2016) → Owner B
History        → [A→B→C transitions]
Current        → Owner C
```

| Endpoint Type | Returns | Analogy |
|---------------|---------|---------|
| Aircraft / Bulk Export | Current state | "NOW" |
| Snapshot | State at a historical date | "THEN" |
| History | Change events over time | "WHAT CHANGED" |
| Flight Data | Operational activity | "WHAT HAPPENED" |

---

## Endpoint

```
POST /api/Aircraft/getCondensedSnapshot/{apiToken}
```

Returns condensed aircraft ownership/operator records as they existed on the requested `snapshotdate`.

**Important:** This endpoint is **non-paged**. It returns the full dataset in a single response, which can be multi-MB for broad queries.

---

## Request Structure

```json
{
  "airframetype": "None",
  "maketype": "None",
  "sernbr": "",
  "regnbr": "",
  "modelid": 0,
  "make": "",
  "lifecycle": "None",
  "basecountry": "Mexico",
  "snapshotdate": "05/01/2016",
  "yearmfr": 0,
  "yeardlv": 0,
  "aclist": [],
  "modlist": [],
  "exactMatchReg": false
}
```

### Parameters

**Temporal control (required):**

| Field | Purpose | Format |
|-------|---------|--------|
| `snapshotdate` | Historical reference date | `MM/DD/YYYY` |

This is the defining parameter. Everything returned reflects the fleet as it existed on this date.

**Aircraft filters:**

| Field | Purpose |
|-------|---------|
| `make` | Manufacturer filter (case-insensitive) |
| `modelid` | Single model ID (0 = no filter) |
| `modlist` | Array of model IDs |
| `aclist` | Array of aircraft IDs |
| `sernbr` | Serial number filter |
| `regnbr` | Registration / tail number filter |
| `exactMatchReg` | `true` for exact match, `false` for partial |
| `airframetype` | `"FixedWing"`, `"Rotorcraft"`, `"None"` |
| `maketype` | `"BusinessJet"`, `"Turboprop"`, `"Piston"`, `"None"` |

**Operational filters:**

| Field | Purpose |
|-------|---------|
| `lifecycle` | Aircraft operational state (`"InOperation"`, `"None"`) |
| `basecountry` | Country where aircraft was based |
| `basestate` | State/region filter (array) |
| `yearmfr` | Manufacturing year (0 = no filter) |
| `yeardlv` | Delivery year (0 = no filter) |

---

## Response Structure

Response key: **`snapshotowneroperators`** (array)

```json
{
  "responseid": "...",
  "responsestatus": "SUCCESS",
  "count": 2651,
  "snapshotowneroperators": [
    {
      "snapshotdate": "5/2016",
      "acid": 610,
      "airframetype": "FixedWing",
      "maketype": "Piston",
      "make": "BARON",
      "model": "58"
    }
  ]
}
```

Each record represents an aircraft + ownership/operator relationship as it existed at the snapshot date.

---

## Performance and Payload Size

Snapshot responses can be large:
- A country-level query (e.g., all aircraft based in Mexico) can return thousands of records and multi-MB payloads
- There is **no pagination** -- the full dataset comes in one response

**Always filter** to keep payloads manageable:

| Filter | Effect |
|--------|--------|
| `modlist` | Scope to specific models -- most effective |
| `basecountry` | Limit to a single country |
| `maketype` | Limit to a category (BusinessJet, Turboprop) |
| `lifecycle` | Exclude scrapped/stored aircraft |
| `aclist` | Query specific aircraft only |

Avoid unrestricted global snapshot pulls. A query with no filters against a broad `snapshotdate` produces very large payloads.

---

## Use Cases

### Historical Fleet Composition

"How many G550s were based in the US in 2018?"

```json
{
  "modlist": [278],
  "basecountry": "United States",
  "snapshotdate": "12/31/2018",
  "lifecycle": "InOperation"
}
```

Count the results to get fleet size at that date.

### "Who Owned This in Year X?"

```json
{
  "aclist": [125375],
  "snapshotdate": "06/15/2020"
}
```

### Market Comparison Across Years

Run the same filtered query with different `snapshotdate` values to compare fleet composition over time:

```python
years = ["12/31/2018", "12/31/2020", "12/31/2022", "12/31/2024"]
fleet_sizes = {}

for date in years:
    body = {
        "modlist": [278],
        "basecountry": "United States",
        "snapshotdate": date,
        "lifecycle": "InOperation",
        "airframetype": "None",
        "maketype": "None",
        "make": "",
        "modelid": 0,
        "sernbr": "",
        "regnbr": "",
        "yearmfr": 0,
        "yeardlv": 0,
        "aclist": [],
        "exactMatchReg": False
    }
    result = api_post(f"/api/Aircraft/getCondensedSnapshot/{token}", body)
    fleet_sizes[date] = result["count"]
```

### Country Fleet Growth Analysis

Compare aircraft counts by country across snapshot dates to identify growing or shrinking markets.

---

## Engineering Recommendations

**Caching:** Snapshot data is historical and immutable -- cache aggressively. A snapshot for `05/01/2016` will always return the same data.

**Pre-aggregation:** For dashboards or recurring analytics, pre-aggregate common snapshot dates into summary tables rather than calling the API repeatedly.

**Backend summarization:** Avoid feeding raw multi-MB snapshot payloads directly into conversational AI or LLM prompts. Summarize or aggregate on your backend first.

```
Application
  ↓
Backend Service
  ↓
JETNET Snapshot API
  ↓
Normalize → Cache → Summarize
  ↓
Dashboard / LLM Response
```

---

## See Also

- [History](history.md) -- transaction change events (complementary to snapshots)
- [Flight Data](flight-data.md) -- operational activity
- [Bulk Export](bulk-export.md) -- current state with full relationship graphs
- [Enum Reference](enum-reference.md) -- valid values for `airframetype`, `maketype`, `lifecycle`
- [Response Handling](response-handling.md) -- schema differences across endpoints
