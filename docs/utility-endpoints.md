# Utility & Reference Endpoints

## Conceptual Model

The Utility endpoints provide **foundational reference data** -- the controlled vocabularies, classification taxonomies, and enumeration values that every other JETNET endpoint depends on. They are the metadata backbone of the API.

Think of them as **dimension tables** in a data warehouse: they define the valid values for `lifecycle`, `airframetype`, `maketype`, `modelid`, `categorysize`, event categories, and more. Without them, you cannot reliably filter, join, or interpret data from Aircraft, Company, Contact, Model, or Flight endpoints.

```
Utility Layer (Cached Reference Data)
│
├── Lifecycle Status    ← lifecycle filter values
├── Airframe Types      ← FixedWing / Rotary
├── Make List           ← manufacturer taxonomy
├── Model List          ← modelid foreign key + classification
├── JNIQ Sizes          ← category size taxonomy
├── Event Categories    ← event domain groupings
├── Event Types         ← specific event signals per category
├── Weight Classes      ← aircraft weight classification
├── Make Types          ← propulsion/category classification
├── Business Types      ← company business type taxonomy
├── Relationship Types  ← aircraft-company relationship taxonomy
├── History Trans Types ← transaction type enumeration
├── Country List        ← country reference
├── State List          ← state/province reference per country
└── Product Codes       ← account entitlement codes
        ↓
  Used by every operational endpoint
        ↓
  Snapshots / Trends / Events / Flights / Aircraft / Companies / Contacts
```

---

## Aircraft Lifecycle Status

```
GET /api/Utility/getAircraftLifecycleStatus/{apiToken}
```

Returns the authoritative list of aircraft lifecycle states used as filter values across the API.

### Response

Response key: **`lifecyclestatus`** (array of strings)

```json
{
  "lifecyclestatus": [
    "InProduction",
    "NewWithManufacturer",
    "InOperation",
    "Retired",
    "InStorage"
  ]
}
```

### Usage

- Populate `lifecycle` filter in `getAircraftList`, `getCondensedSnapshot`, `getBulkAircraftExport`
- Partition fleets into active vs inactive populations
- Drive UI dropdown filters

---

## Aircraft Make List

```
POST /api/Utility/getAircraftMakeList/{apiToken}
```

Returns all aircraft manufacturers (OEM makes) recognized by JETNET.

### Request Body

```json
{
  "airframetype": "None",
  "maketype": "None"
}
```

| Field | Purpose | Notes |
|-------|---------|-------|
| `airframetype` | Filter by airframe | `"None"` = all |
| `maketype` | Filter by propulsion | `"None"` = all |

### Response

Each record includes:

| Field | Description |
|-------|-------------|
| `make` | Canonical make name (ALL CAPS) |
| `manufacturer` | Display manufacturer name |

```json
{
  "make": "GULFSTREAM",
  "manufacturer": "Gulfstream Aerospace"
}
```

### Usage

- Top-level taxonomy for aircraft classification
- Validate `make` parameter before passing to search endpoints
- Build cascading selectors: Make → Model
- Map to internal canonical manufacturer IDs

---

## Aircraft Model List

```
POST /api/Utility/getAircraftModelList/{apiToken}
```

Returns the complete aircraft model catalog. This is one of the **most critical reference datasets** -- `modelid` is the canonical foreign key used by Trends, Snapshots, Events, and search endpoints.

### Request Body

```json
{
  "airframetype": "None",
  "maketype": "None",
  "make": ""
}
```

| Field | Purpose | Notes |
|-------|---------|-------|
| `airframetype` | Filter by airframe | `"None"` = all |
| `maketype` | Filter by propulsion | `"None"` = all |
| `make` | Filter by manufacturer | `""` = all |

### Response

Key fields per record:

| Field | Description |
|-------|-------------|
| `modelid` | Canonical model ID (integer) -- the primary foreign key |
| `airframetype` | `FixedWing` or `Rotary` |
| `maketype` | Propulsion category (`BusinessJet`, `Turboprop`, etc.) |
| `make` | Manufacturer name (ALL CAPS) |
| `model` | Model designation |
| `manufacturer` | Display manufacturer name |
| `weightclass` | Weight classification |
| `categorysize` | JNIQ category size code |

### Usage

- Resolve `modelid` for use in `getModelMarketTrends`, `getCondensedSnapshot`, `getAircraftList`, `getEventListPaged`
- Fleet segmentation by `weightclass` or `categorysize`
- Model-level dashboards and comparisons
- Cross-reference with `references/model-id-table.json` for quick lookups

---

## Airframe JNIQ Sizes

```
GET /api/Utility/getAirframeJniqSizes/{apiToken}
```

Returns JETNET's standardized aircraft category sizing taxonomy.

### Response

```json
{
  "catcode": "ABJ",
  "description": "Airline Business Jet",
  "trbdescription": "Class X Jets"
}
```

| Field | Description |
|-------|-------------|
| `catcode` | Category code (matches `categorysize` in model records) |
| `description` | Human-readable category name |
| `trbdescription` | Alternative classification label |

### Usage

- Market segmentation and trend rollups
- Fleet class comparisons (Light Jet vs Mid vs Heavy)
- Visualization grouping
- Maps to `categorysize` field in Model List and Trends responses

---

## Airframe Types

```
GET /api/Utility/getAirframeTypes/{apiToken}
```

Returns the highest-level aircraft structural classification.

### Response

Response key: **`airframetypes`** (array of strings)

```json
{
  "airframetypes": ["FixedWing", "Rotary"]
}
```

### Usage

- Primary partition dimension for helicopter vs fixed-wing filtering
- Feeds `airframetype` parameter across all search and filter endpoints
- Treat as a static enum -- these values never change

---

## Make Type List

```
POST /api/Utility/getMakeTypeList/{apiToken}
```

Returns aircraft propulsion/category classifications.

### Request Body

```json
{
  "airframetype": "None"
}
```

### Response

Returns make type values: `BusinessJet`, `Turboprop`, `Piston`, `JetAirliner`, `Turbine`

### Usage

- Feeds `maketype` parameter across search endpoints
- Segments fleet by propulsion type

---

## Weight Class Types

```
GET /api/Utility/getWeightClassTypes/{apiToken}
```

Returns aircraft weight classifications used for regulatory and market segmentation.

### Usage

- Maps to `weightclass` field in model records
- Weight-based fleet analytics

---

## Event Categories

```
GET /api/Utility/getEventCategories/{apiToken}
```

Returns all valid event category strings for use with `getEventListPaged`.

### Known Categories

| Category | Covers |
|----------|--------|
| Aircraft Information | Base changes, airframe hours, registration, specs |
| Company / Contact | Ownership, operator, contact updates |
| Financial Documents | Financial record changes |
| Market Status | For-sale listings, off-market, status transitions |
| Transaction | Sales, leases, ownership transfers |

### Usage

- Populate `evcategory` filter array in event queries
- Values must match exactly -- use this endpoint to discover valid strings rather than guessing

See [Events](events.md) for full event query documentation.

---

## Event Types

```
POST /api/Utility/getEventTypes/{apiToken}
```

Returns valid event type strings within a specific event category.

### Request Body

```json
{
  "eventcategory": "Transaction"
}
```

### Usage

- Populate `evtype` filter array in event queries
- Must call once per category to discover all valid type strings
- Values are strict -- unrecognized values cause errors inside `responsestatus`

See [Events](events.md) for full event query documentation.

---

## Company Business Types

```
GET /api/Utility/getCompanyBusinessTypes/{apiToken}
```

Returns valid business type classifications for companies.

### Usage

- Feeds `bustype` filter in `getCompanyList` and `getCompanyListPaged`
- Classify companies by industry role (FBO, MRO, Broker, Charter, etc.)

---

## Aircraft Company Relationship Types

```
GET /api/Utility/getAircraftCompanyRelationships/{apiToken}
```

Returns valid relationship type values between aircraft and companies.

### Usage

- Feeds `relationship` filter in company and aircraft search endpoints
- Understand the nature of aircraft-company links (Owner, Operator, Manager, etc.)

---

## Aircraft History Transaction Types

```
GET /api/Utility/getAircraftHistoryTransTypes/{apiToken}
```

Returns valid transaction type values for history queries.

### Usage

- Feeds `transtype` filter in `getHistoryList` / `getHistoryListPaged`
- See [Enum Reference](../docs/enum-reference.md) for request vs response `transtype` differences

---

## Country List

```
GET /api/Utility/getCountryList/{apiToken}
```

Returns all countries in the JETNET database.

### Usage

- Feeds `basecountry` / `basecountrylist` / `country` filters
- Geographic segmentation and reporting

---

## State List

```
POST /api/Utility/getStateList/{apiToken}
```

Returns states/provinces for a given country.

### Request Body

```json
{
  "country": "United States"
}
```

### Usage

- Feeds `basestate` / `state` / `statename` filters
- Regional fleet analysis

---

## Product Codes

```
GET /api/Utility/getProductCodes/{apiToken}
```

Returns product codes available to your account.

### Usage

- Check entitlements before calling endpoints that require specific product codes
- Feeds `productcode` filter in `getModelMarketTrends`

---

## Account Info

```
GET /api/Utility/getAccountInfo/{apiToken}
```

Returns information about your API account.

### Usage

- Verify authentication and account status
- Check subscription tier and access level

---

## Caching Strategy

Utility endpoints return slowly-changing reference data. Cache aggressively to reduce API calls and improve performance.

| Endpoint | Cache Duration | Reason |
|----------|---------------|--------|
| Airframe Types | Static | Enum-level data (`FixedWing`, `Rotary`) -- never changes |
| Lifecycle Status | Long-lived (weekly+) | Rarely changes |
| Make List | Long-lived (weekly+) | OEM list is stable |
| JNIQ Sizes | Long-lived (weekly+) | Classification taxonomy, rarely modified |
| Weight Classes | Long-lived (weekly+) | Regulatory categories, stable |
| Event Categories | Long-lived (weekly+) | Domain groupings, rarely modified |
| Event Types | Long-lived (weekly+) | Specific signals per category, stable |
| Business Types | Long-lived (weekly+) | Company classification, stable |
| Relationship Types | Long-lived (weekly+) | Relationship vocabulary, stable |
| History Trans Types | Long-lived (weekly+) | Transaction categories, stable |
| Country List | Long-lived (weekly+) | Countries rarely added |
| State List | Long-lived (weekly+) | States/provinces rarely change |
| Model List | Daily refresh | Occasionally expanded with new models |
| Make Type List | Long-lived (weekly+) | Propulsion categories, stable |
| Product Codes | Session-level | Account-specific, check at startup |

### Recommended Pattern

```python
import json, os, time

CACHE_DIR = ".cache/jetnet"
CACHE_TTL = 86400

def get_cached_or_fetch(name, fetch_fn):
    path = f"{CACHE_DIR}/{name}.json"
    if os.path.exists(path):
        age = time.time() - os.path.getmtime(path)
        if age < CACHE_TTL:
            with open(path) as f:
                return json.load(f)
    data = fetch_fn()
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)
    return data
```

---

## Data Architecture Role

These utility endpoints form the **metadata backbone** that all other JETNET APIs depend on:

```
┌─────────────────────────────────────────────┐
│           Operational Endpoints             │
│  Aircraft · Companies · Contacts · Flights  │
│  Events · History · Snapshots · Trends      │
├─────────────────────────────────────────────┤
│           Reference Layer (Utility)         │
│  Models · Makes · Lifecycle · Airframe      │
│  JNIQ Sizes · Event Cats · Business Types   │
│  Countries · States · Relationships         │
└─────────────────────────────────────────────┘
```

Without the utility layer:
- You cannot resolve `modelid` values for trend queries
- You cannot validate enum filter values before sending requests
- You risk sending invalid filter strings that return errors inside `responsestatus`
- You cannot build reliable cascading filters (Airframe → Make → Model)

---

## Integration Priority

**Tier 1 -- Required immediately:**
- Aircraft Model List (`modelid` is used everywhere)
- Lifecycle Status (core filter for fleet analytics)

**Tier 2 -- Strongly recommended:**
- Make List (manufacturer taxonomy)
- JNIQ Sizes (category segmentation)
- Event Categories / Event Types (if using events)

**Tier 3 -- Supportive metadata:**
- Airframe Types (static enum, can hardcode)
- Weight Classes
- Business Types, Relationship Types, History Trans Types
- Country / State Lists
- Product Codes, Account Info

---

## See Also

- [Enum Reference](../docs/enum-reference.md) -- enum values and their meanings
- [Events](events.md) -- event queries that depend on event category/type utilities
- [Trends](trends.md) -- market trends that depend on `modelid` from Model List
- [Snapshots](snapshots.md) -- snapshots using lifecycle and model filters
- [ID System](id-system.md) -- how `modelid` and other IDs connect entities
- [Common Mistakes](common-mistakes.md) -- gotchas including enum strictness
- [Airports](airports.md) -- `getAirportList` (also in Utility namespace)
