# Market Trends & Time-Series Analytics

The JETNET API exposes multiple endpoints that, when combined, form a complete longitudinal dataset for aviation market intelligence. This guide explains how to layer them into time-series analytics.

---

## Data Layers

| Layer | Endpoint | What It Provides |
|-------|----------|-----------------|
| **Market** | `getModelMarketTrends` | Monthly pricing, inventory, days-on-market per model |
| **State** | `getCondensedSnapshot` | Fleet ownership/operator state at a historical date |
| **Causal** | `getEventListPaged` | Discrete lifecycle changes explaining why state changed |
| **Activity** | `getFlightData` / `getFlights` | Flight hours, routes, utilization |
| **Transaction** | `getHistoryListPaged` | Sales, leases, ownership transfers |
| **Current** | `getCondensedOwnerOperators` | Current ownership/operator relationships |

Unified by: **model ID**, **aircraft ID**, and **date**.

---

## 1. Model Market Trends (Core Time Series)

`POST /api/Model/getModelMarketTrends/{apiToken}`

The strongest native time-series endpoint. Returns monthly snapshots at model-level granularity with historical depth spanning multiple years.

### Request

```json
{
  "modlist": [278, 288, 663],
  "displayRange": 12,
  "startdate": "01/01/2024",
  "airframetype": "None",
  "maketype": "None",
  "productcode": ["None"],
  "modelid": 0,
  "make": ""
}
```

- `modlist` -- array of model IDs to track
- `displayRange` -- number of months of data to return
- `startdate` -- beginning of the trend window (`MM/DD/YYYY`)

### Response Key: `modelMarketTrends`

One record per model per month:

```json
{
  "modelid": 278,
  "make": "GULFSTREAM",
  "model": "G550",
  "trend_year": 2024,
  "trend_month": 6,
  "trend_snapshot_date": "2024-06-30T00:00:00",
  "aircraft_for_sale_count": 28,
  "in_operation_count": 553,
  "end_user_count": 15,
  "dealer_owned_count": 5,
  "domestic_count": 18,
  "international_count": 10,
  "avg_asking_price": 18500000,
  "high_asking_price": 24900000,
  "low_asking_price": 12500000,
  "make_offer_count": 8,
  "avg_daysonmarket": 185,
  "avg_year": 2012,
  "avg_airframe_time": 6200,
  "avg_engine_time": 5800,
  "avail_new_onmarket_count": 0
}
```

### Derived Metrics

| Metric | Formula |
|--------|---------|
| **Supply Pressure** | `aircraft_for_sale_count / in_operation_count` |
| **Liquidity Score** | Inverse of `avg_daysonmarket` trend slope |
| **Price Trend Index** | MoM change in `avg_asking_price` |
| **Market Heat** | Supply Pressure inverted -- low supply + high utilization = hot market |
| **Inventory Velocity** | Rate of change in `aircraft_for_sale_count` |

---

## 2. Fleet Snapshot Trends (Historical State)

`POST /api/Aircraft/getCondensedSnapshot/{apiToken}`

Query the same filters across multiple `snapshotdate` values to build fleet composition curves over time. See [Snapshots](snapshots.md) for full endpoint documentation.

### Time-Series Construction

```python
dates = ["12/31/2018", "12/31/2019", "12/31/2020", "12/31/2021",
         "12/31/2022", "12/31/2023", "12/31/2024"]

for date in dates:
    body["snapshotdate"] = date
    result = api_post(f"/api/Aircraft/getCondensedSnapshot/{token}", body)
    store_snapshot(date, result["count"], result["snapshotowneroperators"])
```

### Derived Metrics

| Metric | What It Shows |
|--------|--------------|
| Net fleet change by region | Geographic migration trends |
| Ownership turnover rate | Market liquidity signal |
| Manufacturer market penetration | Competitive landscape |
| Active vs inactive fleet ratio | Lifecycle health |

Snapshots are the **baseline state layer** that contextualizes market trend movements.

---

## 3. Flight Activity Trends

`POST /api/Aircraft/getFlightDataPaged/{apiToken}/{pagesize}/{page}` (per-flight)
`GET /api/Aircraft/getFlights/{aircraftId}/{apiToken}` (monthly summary)

See [Flight Data](flight-data.md) for full endpoint documentation.

### Trend Metrics

| Metric | Source |
|--------|--------|
| Flight hours trend | Monthly `flighthours` from `getFlights` |
| Utilization per model | Aggregate `flighthours / fleet_count` |
| Route patterns | Origin/destination from `getFlightData` |
| Fuel/emissions trends | `estfuelburn` / `estCO2emissions` from `getFlightData` |

### Correlation Signals

| Pattern | Signal |
|---------|--------|
| Rising utilization + declining inventory | Tightening market |
| Falling utilization + growing inventory | Market softening |
| Stable utilization + rising prices | Demand-driven pricing |

---

## 4. Transaction Trends

`POST /api/Aircraft/getHistoryListPaged/{apiToken}/{pagesize}/{page}`

See [History](history.md) for full endpoint documentation.

### Trend Metrics

| Metric | How To Compute |
|--------|---------------|
| Transaction volume | Count of history records per month |
| Buyer vs seller cycles | Ratio of `FullSale` vs `Lease` transactions over time |
| Turnover velocity | Time between `purchasedate` and next `transdate` for same aircraft |
| Regional acquisition waves | Group by `basecountry` / `basecontinent` over time |

Filter with `transretail: true` for arm's length transactions when building comparable sales trends.

---

## 5. Owner/Operator Movement Trends

`POST /api/Aircraft/getCondensedOwnerOperators/{apiToken}`

Returns current ownership/operator relationships. When captured periodically, enables:

| Metric | What It Shows |
|--------|--------------|
| Operator fleet expansion/contraction | Growth signals |
| Corporate fleet migration | Market movement |
| Charter vs private ownership shifts | Segment trends |
| New entrant detection | Companies appearing for the first time |

Response key: `aircraftowneroperators`

---

## Composite Indicators

By combining data across layers, build higher-value analytics:

### Market Momentum Index

```
(Monthly Transaction Volume + Flight Utilization Change) / Inventory Growth
```

High momentum = active, tightening market. Low or negative = cooling.

### Supply Pressure Index

```
Aircraft For Sale / In Operation Fleet
```

From `getModelMarketTrends`. Track monthly for supply curve direction.

### Utilization vs Pricing Correlation

Plot `avg_airframe_time` trends against `avg_asking_price` from market trends. Divergence signals mispricing.

---

## Architecture

```
┌─────────────────────────────────────────┐
│            Unified Trend Store          │
│  (Model ID + Aircraft ID + Date)        │
├──────────┬──────────┬──────────┬────────┤
│  Market  │  State   │ Activity │ Deals  │
│  Trends  │ Snapshot │  Flight  │ History│
├──────────┼──────────┼──────────┼────────┤
│ Monthly  │ Point-in │  Daily / │ Event  │
│ pricing  │ time     │  Monthly │ based  │
│ & supply │ fleet    │  hours   │ sales  │
└──────┬───┴────┬─────┴────┬─────┴───┬────┘
       │        │          │         │
   getModel  getCond   getFlight  getHistory
   Market    ensed     Data/      ListPaged
   Trends    Snapshot  Flights
```

### Data Collection Schedule

| Layer | Endpoint | Frequency |
|-------|----------|-----------|
| Market | `getModelMarketTrends` | Monthly (data updates monthly) |
| State | `getCondensedSnapshot` | Quarterly or on-demand |
| Causal | `getEventListPaged` | Daily or hourly for alerts |
| Activity | `getFlights` | Monthly per aircraft |
| Transactions | `getHistoryListPaged` | Weekly or daily for alerts |
| Current | `getCondensedOwnerOperators` | Daily or weekly for CRM sync |

---

## See Also

- [Events](events.md) -- discrete lifecycle changes (the causal layer)
- [Snapshots](snapshots.md) -- historical fleet state endpoint details
- [History](history.md) -- transaction history endpoint details
- [Flight Data](flight-data.md) -- flight activity endpoint details
- [Bulk Export](bulk-export.md) -- full aircraft data replication
- [Response Handling](response-handling.md) -- schema differences across endpoints
