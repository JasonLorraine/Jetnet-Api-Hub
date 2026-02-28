# Airports

The Airports endpoint provides standardized airport reference data used across flight operations, basing analysis, and geographic market intelligence. Unlike transactional datasets (flights, events, history), airports represent **static infrastructure entities** that enable consistent geographic normalization and spatial aggregation.

This dataset functions as a **dimension table** within analytics pipelines -- the spatial index that ties together flights, events, snapshots, and market trends.

---

## Endpoint

### `POST /api/Utility/getAirportList/{apiToken}`

Returns airport records matching the provided filters. All parameters are optional and can be combined.

### Request Body

```json
{
  "name": "",
  "city": "",
  "state": [],
  "statename": [],
  "country": "",
  "iata": "",
  "icao": "",
  "faaid": ""
}
```

### Request Parameters

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Airport name filter |
| `city` | string | City filter |
| `state` | array[string] | State/province abbreviations |
| `statename` | array[string] | Full state names |
| `country` | string | Country filter |
| `iata` | string | IATA airport code (e.g., `"SLK"`) |
| `icao` | string | ICAO airport identifier (e.g., `"KSLK"`) |
| `faaid` | string | FAA identifier (U.S. airports) |

### Response Fields

| Field | Description |
|-------|-------------|
| `airportid` | Unique JETNET airport identifier |
| `name` | Airport name |
| `city` | Associated city |
| `state` | State or region |
| `country` | Country |
| `iata` | IATA code |
| `icao` | ICAO code |
| `faaid` | FAA identifier (where applicable) |

### Example: Lookup by ICAO

```python
resp = session.post(
    f"{BASE}/api/Utility/getAirportList/{token}",
    json={"icao": "KTEB"}
)
airports = resp.json()  # array of matching airport records
```

### Example: Filter by State

```python
resp = session.post(
    f"{BASE}/api/Utility/getAirportList/{token}",
    json={"state": ["NY", "NJ"]}
)
airports = resp.json()
```

---

## Role as a Dimension Table

Airports serve as the geographic backbone for nearly every other dataset in the JETNET API. The relationship model:

```
Airports (Dimension)
    ↓
Flights (Fact)      -- origin / destination fields join to ICAO/IATA
Events (Fact)       -- location context for lifecycle changes
Snapshots (Fact)    -- base airport for ownership state
Market Trends (Fact) -- regional aggregation layer
```

Key join fields across datasets:

| Dataset | Join Field | Airport Key |
|---------|-----------|-------------|
| Flight Data (`getFlightData`) | `origin` / `destination` | ICAO code |
| Aircraft base location | `basecode` | Airport identifier |
| Condensed Snapshots | Base fields | Airport identifier |

---

## Analytical Applications

### 1. Traffic Analysis

Join airport data with `getFlightData` to produce:

- Traffic volume by airport
- Origin/destination heatmaps
- Route density analysis
- Regional utilization trends

### 2. Basing Distribution

Combined with snapshots (`getCondensedSnapshot`) and ownership data:

- Aircraft basing distribution by airport/region
- Fleet geographic migration over time
- Operator regional concentration

### 3. Geographic Migration

Track how fleet basing shifts across time windows by comparing snapshot data against the airport dimension:

- Quarter-over-quarter base changes
- Country-level fleet growth
- Emerging operational hubs

### 4. Event Correlation

Paired with aircraft events (`getEventListPaged`):

- Base change tracking
- Operational relocations
- Market entry/exit signals by region

### 5. Market & Trend Modeling

Supports aggregation for:

- Activity by metropolitan region
- Country-level fleet growth
- Airport ecosystem analysis

---

## Time-Series Opportunities

Although airports themselves are static, they enable derived time-series when joined with temporal datasets:

| Derived Series | Source |
|---------------|--------|
| Monthly operations per airport | `getFlightData` grouped by origin/destination |
| Aircraft counts by airport over time | `getCondensedSnapshot` with base fields |
| Event density by region | `getEventListPaged` grouped by location |
| Fleet migration timelines | Sequential snapshots compared against airport dimension |

Airports function as the **spatial index** for all temporal datasets.

---

## Caching Recommendation

Airport data changes very infrequently. Recommended approach:

- **Cache locally** after initial fetch
- **Refresh schedule**: weekly or monthly is sufficient
- **Normalization**: use ICAO codes as the canonical join key across datasets (most consistent identifier)
- Maintain a local airport dimension table for analytics joins

---

## Best Practices

1. **Normalize geographic references** against ICAO codes when possible -- they are the most globally consistent identifier.
2. **Maintain airport dimension keys** in your data warehouse for consistent analytics joins.
3. **Use airports to avoid free-text geographic fragmentation** -- raw city/state strings in other datasets can be inconsistent.
4. **Cache aggressively** -- this is a low-volatility reference dataset.
5. **Filter narrowly** when querying -- use specific `icao`, `iata`, or `state` parameters rather than pulling the entire list repeatedly.

---

## See Also

- [Flight Data](flight-data.md) -- per-flight records with origin/destination airport codes
- [Snapshots](snapshots.md) -- historical fleet state with base location fields
- [Events](events.md) -- lifecycle changes that may include location context
- [Trends](trends.md) -- market analytics that can be aggregated by region
- [Utility Endpoints](utility-endpoints.md) -- other reference/dimension endpoints
