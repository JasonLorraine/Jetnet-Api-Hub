# JETNET Flight Data Integration

## Endpoints Covered

* `getFlightData` / `getFlightDataPaged` -- granular per-flight records
* `getFlights` (Aircraft Flight Summary) -- aggregated monthly utilization

---

## Two Endpoints, Two Roles

| Endpoint | Role | Data Level |
|----------|------|------------|
| **getFlightData** | Detailed, per-flight operational records | Transactional telemetry |
| **getFlights** | Aggregated monthly utilization statistics | Pre-aggregated cache |

```
getFlightData  → detailed events
        ↓ aggregation
getFlights     → monthly summaries
```

| Question | Correct Endpoint |
|----------|-----------------|
| Where did aircraft fly? | getFlightData |
| How active is aircraft monthly? | getFlights |
| Build utilization trend? | getFlights |
| Detect new travel patterns? | getFlightData |
| Estimate emissions? | getFlightData |

---

## 1. getFlightData (Detail)

### `POST /api/Aircraft/getFlightDataPaged/{apiToken}/{pagesize}/{page}`

Returns granular flight-level records for aircraft matching filters. This is the primary activity dataset and should be treated as the authoritative operational feed.

### Request Body

```json
{
  "aircraftid": 0,
  "airframetype": "None",
  "sernbr": "",
  "regnbr": "",
  "maketype": "None",
  "modelid": 0,
  "make": "",
  "origin": "",
  "destination": "",
  "startdate": "02/19/2026",
  "enddate": "02/20/2026",
  "aclist": [],
  "modlist": [1194],
  "exactMatchReg": true
}
```

### Key Filters

| Field | Behavior |
|-------|----------|
| `startdate / enddate` | **Required** for scalable queries. Use `MM/DD/YYYY` with leading zeros. |
| `modlist` | Most efficient filter (model-based retrieval). Use AMODID values from `references/model-id-table.json`. |
| `aclist` | Target specific aircraft IDs. Empty `[]` = no filter. |
| `origin / destination` | Airport filtering (ICAO codes). |
| `regnbr` | Tail-specific lookup. |
| `exactMatchReg` | Set `true` to prevent fuzzy matching. |

### Response Fields

| Field | Meaning |
|-------|---------|
| `flightid` | Unique flight record ID |
| `flightdate` | Flight occurrence date |
| `origin_time` | Departure timing |
| `flighttime` | Minutes flown |
| `distance` | Flight distance |
| `estfuelburn` | Estimated fuel usage |
| `fuelburnrate` | Consumption rate |
| `estCO2emissions` | Environmental impact metric |
| `callsign` | Operational identifier |
| `origin` / `destination` | Route endpoints (ICAO codes) |

The response key is `flightdata` (array).

### Engineering Notes

- Model filtering (`modlist`) dramatically reduces payload size.
- Date range must be constrained -- large queries without filters may exceed backend limits.
- Response includes aircraft metadata + operational context (no extra joins required).
- Flight data already includes sustainability metrics (fuel burn, CO2) -- no external calculation needed.

---

## 2. getFlights (Monthly Summary)

### `GET /api/Aircraft/getFlights/{aircraftId}/{apiToken}`

Returns aggregated monthly utilization totals for a single aircraft. This is **not** flight-level detail -- it is summarized analytics per month.

### Response Example

```json
{
  "flights": [
    {
      "flightyear": 2025,
      "flightmonth": 2,
      "flights": 103,
      "flighthours": 240
    }
  ]
}
```

### Response Fields

| Field | Meaning |
|-------|---------|
| `flightyear` | Calendar year |
| `flightmonth` | Month (1-12) |
| `flights` | Number of flights in month |
| `flighthours` | Total hours flown in month |

This endpoint functions as a pre-aggregated utilization cache. It avoids needing to compute totals from raw flight records.

---

## 3. Ingestion Strategy

### Recommended Approach

```
FOR each model (modlist)
   FOR each day/week (date window)
      call getFlightDataPaged
```

- Batch by model, not fleet-wide pulls.
- Partition by date window (daily or weekly ingestion).
- Use `getFlights` periodically to snapshot monthly totals without re-processing raw records.

### Data Model

```
Aircraft
 └── AircraftFlight
        ├── flight_id
        ├── date
        ├── origin
        ├── destination
        ├── duration
        ├── distance
        ├── fuel_burn
        └── co2_estimate

AircraftMonthlyUsage (from getFlights)
        ├── year
        ├── month
        ├── flight_count
        └── hours_flown
```

---

## 4. CRM & Analytics Signals

### Derived Signals from Flight Data

| Signal | Derived From |
|--------|-------------|
| Aircraft becoming active | Flight count increase (getFlights trend) |
| Charter behavior | High route diversity (getFlightData origins/destinations) |
| Ownership transition risk | Activity drop (getFlights trend) |
| Sustainability scoring | CO2 + fuel burn (getFlightData estCO2emissions) |
| FBO lead generation | Origin/destination patterns (getFlightData) |
| Utilization benchmarking | Monthly hours vs fleet average (getFlights) |

### Architecture

1. **Discovery Layer** -- Use aircraft endpoints to identify target fleet
2. **Activity Intelligence** -- Pull `getFlightData` in date-windowed batches, store normalized flight records
3. **Utilization Snapshot** -- Periodically call `getFlights`, store as `AircraftMonthlyUsage` for CRM scoring
4. **Derived Signals** -- Compute trends, detect behavioral changes, score leads

---

## 5. Key Takeaways

1. `getFlightData` is the core intelligence endpoint -- detailed, per-flight, includes route + emissions.
2. `getFlights` is an aggregation accelerator -- monthly totals without processing raw records.
3. Always use `modlist` or `aclist` filters. Never pull unfiltered fleet-wide data.
4. Always constrain date ranges. Daily or weekly windows are recommended.
5. These endpoints together enable behavioral aviation analytics: activity scoring, travel pattern detection, sustainability tracking, and CRM automation.
