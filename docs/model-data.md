# Model Data Endpoints

The JETNET API provides four Model endpoints that return manufacturer-level reference data for aircraft types. These endpoints are keyed by `modelid` (the numeric AMODID) and cover market trends, operating costs, performance specifications, and intelligence summaries.

`getModelMarketTrends` is documented separately in [Market Trends](trends.md). This guide covers the remaining three endpoints.

---

## Endpoints Overview

| Endpoint | Response Key | What It Returns |
|----------|-------------|-----------------|
| `getModelOperationCosts` | `modeloperationcosts` | Annual operating cost breakdown per model |
| `getModelPerformanceSpecs` | `modelperformancespecs` | Physical dimensions, range, speed, cabin specs |
| `getModelIntelligence` | *(see below)* | Aggregated model intelligence summary |
| `getModelMarketTrends` | `modelMarketTrends` | Monthly pricing, inventory, days-on-market ([docs](trends.md)) |

All Model endpoints are `POST` requests with the token in the URL path.

---

## 1. getModelOperationCosts

`POST /api/Model/getModelOperationCosts/{apiToken}`

Returns annual operating cost estimates broken down by cost category for one or more models.

### Request Body (`ModelPerformanceOptions`)

```json
{
  "modlist": [278, 288],
  "airframetype": "None",
  "maketype": "None",
  "make": "",
  "annualhours": 400,
  "fuelprice": 6
}
```

| Field | Type | Description |
|-------|------|-------------|
| `modlist` | array | Model IDs to query (required for useful results) |
| `airframetype` | string | Airframe filter (`"None"` for all) |
| `maketype` | string | Make type filter (`"None"` for all) |
| `make` | string | Manufacturer name filter (empty string for all) |
| `annualhours` | integer | Assumed annual flight hours for cost projection (0 for defaults) |
| `fuelprice` | integer | Fuel price per gallon for cost projection (0 for defaults) |

### Response

```json
{
  "responseid": "123456789",
  "responsestatus": "SUCCESS",
  "count": 2,
  "modeloperationcosts": [
    {
      "modelid": 278,
      "airframetype": "FixedWing",
      "maketype": "BusinessJet",
      "make": "GULFSTREAM",
      "model": "G550",
      "fuel_gal_cost": 6.00,
      "fuel_additive_cost": 0.05,
      "fuel_burn_rate": 280,
      ...
    }
  ]
}
```

**Response key**: `modeloperationcosts` (all lowercase).

### Key Fields

| Field | Description |
|-------|-------------|
| `modelid` | Numeric model identifier |
| `make` / `model` | Manufacturer and model name |
| `fuel_gal_cost` | Fuel cost per gallon used in calculation |
| `fuel_additive_cost` | Fuel additive cost per gallon |
| `fuel_burn_rate` | Gallons per hour burn rate |

Additional cost fields cover crew, maintenance, insurance, hangar, and other variable and fixed operating expenses. The exact fields returned depend on the model and data availability.

---

## 2. getModelPerformanceSpecs

`POST /api/Model/getModelPerformanceSpecs/{apiToken}`

Returns physical dimensions, range, speed, payload, and cabin specifications for one or more models.

### Request Body (`ModelPerformanceOptions`)

```json
{
  "modlist": [145, 634],
  "airframetype": "None",
  "maketype": "None",
  "make": "",
  "annualhours": 0,
  "fuelprice": 0
}
```

Uses the same `ModelPerformanceOptions` schema as `getModelOperationCosts`. Set `annualhours` and `fuelprice` to `0` when only performance data is needed.

### Response

```json
{
  "responseid": "123456789",
  "responsestatus": "SUCCESS",
  "count": 2,
  "modelperformancespecs": [
    {
      "modelid": 145,
      "airframetype": "FixedWing",
      "maketype": "BusinessJet",
      "make": "CESSNA",
      "model": "CITATION X",
      "fuselage_length": 73.3,
      "fuselage_height": 5.7,
      "fuselage_wing_span": 63.6,
      ...
    }
  ]
}
```

**Response key**: `modelperformancespecs` (all lowercase).

### Key Fields

| Field | Description |
|-------|-------------|
| `modelid` | Numeric model identifier |
| `make` / `model` | Manufacturer and model name |
| `fuselage_length` | Overall fuselage length |
| `fuselage_height` | Fuselage height |
| `fuselage_wing_span` | Wingspan |

Additional fields cover cabin dimensions (length, width, height), range, max speed, cruise speed, max altitude, max passengers, baggage volume, and engine specifications. Field availability varies by model.

---

## 3. getModelIntelligence

`POST /api/Model/getModelIntelligence/{apiToken}`

Returns an aggregated intelligence summary for the requested models. This endpoint combines fleet population, market positioning, and classification metadata.

### Request Body

```json
{
  "modlist": [278],
  "airframetype": "None",
  "maketype": "None",
  "make": ""
}
```

### Notes

- The request body must be valid JSON. Malformed bodies (e.g., unmatched brackets) return a `400` validation error.
- Consult the API documentation or test in Postman for the exact response structure, as field availability depends on the model and subscription tier.

---

## Common Patterns

### Shared Request Schema

`getModelOperationCosts` and `getModelPerformanceSpecs` share the same `ModelPerformanceOptions` request body. You can query both endpoints with the same payload to get a complete cost-plus-performance picture for a set of models.

### Response Key Casing

| Endpoint | Response Key |
|----------|-------------|
| `getModelOperationCosts` | `modeloperationcosts` (lowercase) |
| `getModelPerformanceSpecs` | `modelperformancespecs` (lowercase) |
| `getModelMarketTrends` | `modelMarketTrends` (camelCase with capital M) |

The inconsistent casing between `modelMarketTrends` and the other two endpoints is a known API quirk. Always use the exact key shown above when extracting data from responses.

### Model ID Lookup

All Model endpoints require `modlist` (an array of numeric model IDs). To find the right IDs:

- Use the [Model ID Reference](../references/model-ids.md) table
- Run `python scripts/model_search.py "G550"` to search by name
- Call `POST /api/Utility/getAircraftModelList/{apiToken}` at runtime

An empty `modlist: []` returns all models (potentially very large result sets).

---

## Use Cases

### Operating Cost Benchmarks

Compare annual operating costs across competing models to support fleet planning or acquisition decisions.

```python
body = {
    "modlist": [278, 288, 663],
    "airframetype": "None",
    "maketype": "None",
    "make": "",
    "annualhours": 400,
    "fuelprice": 6
}
costs = api_post(f"/api/Model/getModelOperationCosts/{token}", body)
for item in costs["modeloperationcosts"]:
    print(f"{item['make']} {item['model']}: fuel burn {item['fuel_burn_rate']} gal/hr")
```

### Performance Comparisons

Evaluate range, speed, and cabin size across models for mission-fit analysis.

```python
body = {
    "modlist": [145, 634],
    "airframetype": "None",
    "maketype": "None",
    "make": "",
    "annualhours": 0,
    "fuelprice": 0
}
specs = api_post(f"/api/Model/getModelPerformanceSpecs/{token}", body)
for item in specs["modelperformancespecs"]:
    print(f"{item['make']} {item['model']}: length {item['fuselage_length']}")
```

### Valuation Support

Combine `getModelOperationCosts` with `getModelMarketTrends` ([docs](trends.md)) to contextualize asking prices against operating economics. High operating costs relative to market value can signal depreciation pressure; low costs relative to peers can indicate value opportunities.

### Full Model Profile

Query all three endpoints with the same `modlist` to build a complete model profile:

1. **Performance** (`getModelPerformanceSpecs`) -- what the aircraft can do
2. **Costs** (`getModelOperationCosts`) -- what it costs to operate
3. **Market** (`getModelMarketTrends`) -- what the market is doing

---

## See Also

- [Market Trends](trends.md) -- `getModelMarketTrends` time-series documentation
- [Model ID Reference](../references/model-ids.md) -- complete model ID lookup table
- [Enum Reference](enum-reference.md) -- `eAirFrameTypes`, `eMakeTypes` values
- [Response Handling](response-handling.md) -- general response structure guidance
- [Utility Endpoints](utility-endpoints.md) -- `getAircraftModelList` for runtime model lookup
