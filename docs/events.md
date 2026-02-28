# JETNET Aircraft Events

## Conceptual Model

Events are **discrete, timestamped records of real-world changes** to aircraft -- ownership transfers, for-sale listings, accidents, maintenance milestones, and lifecycle transitions. They represent the **atomic causal layer** of the JETNET dataset.

Where other endpoints describe *what* the market looks like (snapshots), *how* it's trending (market trends), or *what activity occurred* (flights), events explain **why things changed**.

```
EVENTS  →  SNAPSHOTS  →  TRENDS
(raw)      (state)       (analytics)
```

| Layer | Endpoint | Time Meaning |
|-------|----------|-------------|
| Atomic Events | `getEventListPaged` | Individual real-world changes |
| Snapshot | `getCondensedSnapshot` | Market state at a point in time |
| Aggregated Trends | `getModelMarketTrends` | Derived market metrics over time |
| Transaction History | `getHistoryListPaged` | Ownership/leasing transactions |
| Flight Activity | `getFlightDataPaged` | Operational movements |

Events are the **ground truth** that snapshots and trends are built from.

---

## Endpoint

```
POST /api/Aircraft/getEventListPaged/{apiToken}/{pagesize}/{page}
```

Returns aircraft event records filtered by event category, event type, date range, model, and aircraft list.

---

## Request Structure

```json
{
  "evcategory": ["transaction"],
  "evtype": ["Off Market Due To Sale"],
  "startdate": "01/25/2026",
  "enddate": "02/02/2026",
  "aclist": [],
  "modlist": [],
  "aircraftid": 0,
  "modelid": 0,
  "make": ""
}
```

### Parameters

| Field | Purpose | Notes |
|-------|---------|-------|
| `evcategory` | Event category filter | Array of strings. Use `[]` for all categories. |
| `evtype` | Event type filter | Array of strings. Use `[]` for all types. |
| `startdate` | Start of event window | `MM/DD/YYYY` with leading zeros |
| `enddate` | End of event window | `MM/DD/YYYY` with leading zeros |
| `aclist` | Aircraft ID filter | Array of aircraft IDs. `[]` = no filter. |
| `modlist` | Model ID filter | Array of model IDs. `[]` = no filter. |
| `aircraftid` | Single aircraft lookup | `0` = no filter |
| `modelid` | Single model filter | `0` = no filter |
| `make` | Manufacturer filter | Case-insensitive. `""` = no filter. |

### Enum Values Are Strict

`evcategory` and `evtype` values must match exactly. Sending unrecognized values returns an error inside `responsestatus` even when HTTP status is 200.

To get valid enum values, call the utility endpoints first:

```
GET  /api/Utility/getEventCategories/{apiToken}
POST /api/Utility/getEventTypes/{apiToken}  body: { "eventcategory": "transaction" }
```

**Safe default:** Use `[]` for both `evcategory` and `evtype` to return all event types without guessing enum strings.

---

## Response Structure

Response key: **`events`** (array)

```json
{
  "responseid": "340652808",
  "responsestatus": "SUCCESS",
  "count": 961,
  "currentpage": 0,
  "maxpages": 0,
  "events": [
    {
      "aircraftid": 232064,
      "make": "ROBINSON",
      "model": "R44 RAVEN II",
      "sernbr": "14343",
      "regnbr": "VH-NSX",
      "yearmfr": 2019,
      "yeardlv": 2019,
      "date": "2025-04-14T05:48:33",
      "subject": "New Owner",
      "description": "AirX, Inc."
    }
  ]
}
```

### Response Fields

| Field | Meaning |
|-------|---------|
| `aircraftid` | Aircraft reference ID |
| `make` / `model` | Manufacturer and model |
| `sernbr` | Serial number |
| `regnbr` | Registration / tail number |
| `yearmfr` / `yeardlv` | Year manufactured / delivered |
| `date` | Event timestamp (ISO format) |
| `subject` | Event subject / headline |
| `description` | Event detail |

---

## Events as the Causal Layer

Events explain the **why** behind changes visible in other datasets:

| Observation in Trends/Snapshots | Events Explanation |
|---------------------------------|-------------------|
| Inventory spike for a model | Cluster of for-sale listing events |
| Price drop in market trends | Dealer acquisition events increasing supply |
| Operator count change in snapshots | Ownership transfer events |
| Fleet size decline | Retirement or export events |

---

## Use Cases

### Lifecycle Timeline per Aircraft

Query all events for a single aircraft to reconstruct its full lifecycle:

```json
{
  "aircraftid": 232064,
  "evcategory": [],
  "evtype": [],
  "startdate": "01/01/2010",
  "enddate": "02/28/2026"
}
```

Sort by `date ASC` to produce a timeline:

```
Delivery → Operator Change → Lease → For Sale → Sale → New Owner → Export
```

### Market Velocity Measurement

Count events per model per month to measure transaction frequency:

```json
{
  "modlist": [278, 288, 663],
  "evcategory": ["transaction"],
  "evtype": [],
  "startdate": "01/01/2025",
  "enddate": "02/28/2026"
}
```

High event density = active trading. Low density = sticky ownership.

### Pre-Listing Detection

Look for patterns that predict aircraft entering the market:

```
Operator change → Maintenance event → For-sale listing
```

Query broad event categories and filter for sequences that precede listings.

### Ownership Churn Index

```
Owner change events per model / in-operation fleet count = churn rate
```

Combine with `getModelMarketTrends` (for fleet count) to compute. High churn indicates an unstable or liquidating market segment.

### Event-Driven Alerts

Poll events on a schedule (hourly or daily) with a narrow date window to detect new activity:

```json
{
  "modlist": [278],
  "evcategory": [],
  "evtype": [],
  "startdate": "02/27/2026",
  "enddate": "02/28/2026"
}
```

---

## Derived Metrics

| Metric | How To Compute |
|--------|---------------|
| **Events per Aircraft (90-day rolling)** | Count events per `aircraftid` in trailing 90-day window |
| **Transfer-to-Listing Conversion Rate** | Ownership transfer events followed by for-sale listing / total transfers |
| **Operator Change Frequency** | Operator change events per model per year |
| **Average Time Between Events** | Mean gap between consecutive events per aircraft |
| **Regional Movement Index** | Registration change events grouped by country |

---

## Events in the Analytics Stack

Events complete the four-layer analytics architecture:

```
┌──────────────────────────────────────┐
│          Analytics Output            │
│  Dashboards, Alerts, Predictions     │
├──────────┬──────────┬───────┬────────┤
│  Market  │  State   │ Causal│Activity│
│  Trends  │ Snapshot │ Events│ Flight │
├──────────┼──────────┼───────┼────────┤
│ Monthly  │ Point-in │Atomic │ Daily/ │
│ pricing  │ time     │changes│ Monthly│
│ & supply │ fleet    │       │ hours  │
└──────┬───┴────┬─────┴───┬───┴───┬────┘
       │        │         │       │
   getModel  getCond   getEvent getFlight
   Market    ensed     ListPaged Data/
   Trends    Snapshot           Flights
```

---

## Performance Notes

- Always provide `startdate` / `enddate` to bound the query
- Use `modlist` or `aclist` to limit scope -- broad event queries can return thousands of records
- Use `[]` for `evcategory` and `evtype` when unsure of valid enum values
- `maxpages: 0` / `currentpage: 0` means results fit in one response -- same quirk as other paged endpoints

---

## See Also

- [Trends](trends.md) -- market analytics that events help explain
- [Snapshots](snapshots.md) -- fleet state that events help contextualize
- [History](history.md) -- transaction records (complementary to events)
- [Flight Data](flight-data.md) -- operational activity
- [Pagination](pagination.md) -- paged loop patterns
- [Common Mistakes](common-mistakes.md) -- known gotchas including enum strictness
