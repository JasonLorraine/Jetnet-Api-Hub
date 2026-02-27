# Enum Reference

## airframetype

Filters by aircraft airframe category.

| Value | Description |
|-------|-------------|
| `None` | No filter (all airframe types) |
| `FixedWing` | Fixed-wing aircraft |
| `Rotary` | Rotorcraft (helicopters) |

## maketype

Filters by aircraft propulsion/category.

| Value | Description |
|-------|-------------|
| `None` | No filter (all make types) |
| `JetAirliner` | Commercial jet airliners |
| `BusinessJet` | Business jets |
| `Turboprop` | Turboprop aircraft |
| `Piston` | Piston-engine aircraft |
| `Turbine` | Turbine-powered (helicopters) |

## lifecycle

Filters by aircraft operational status.

| Value | Description |
|-------|-------------|
| `None` | No filter (all lifecycle stages) |
| `InProduction` | Currently being manufactured |
| `NewWithManufacturer` | Completed but not yet delivered |
| `InOperation` | Active and in service |
| `Retired` | Permanently out of service |
| `InStorage` | Temporarily inactive / stored |

## forsale (Request)

Filters by for-sale status in request payloads. These are **string values**, not booleans.

| Value | Description |
|-------|-------------|
| `"true"` | Only aircraft listed for sale |
| `"false"` | Only aircraft not listed for sale |
| `""` | No filter (all aircraft) |

> **Note:** In `getBulkAircraftExport` responses, `forsale` uses `"Y"` / `"N"` instead.

## isnewaircraft / ispreownedtrans / isinternaltrans

Three-state filters used in history and transaction queries.

| Value | Description |
|-------|-------------|
| `"Yes"` | Include only matching records |
| `"No"` | Exclude matching records |
| `"Ignore"` | No filter on this field |

## transtype (Request)

Transaction type categories used in history list request payloads. These are **category labels**, not the full descriptive strings returned in responses.

| Value | Description |
|-------|-------------|
| `"None"` | All transaction types (no filter) |
| `"FullSale"` | Full sale transactions |
| `"Lease"` | Lease transactions |
| `"InternalSale"` | Internal/corporate transfers |
| `"Management"` | Management changes |
| `"Insurance"` | Insurance-related transactions |
| `"Repossession"` | Repossession events |
| `"Registration"` | Registration changes |

> **Important:** Use `["None"]` (not `[]`) to retrieve all transaction types.

## transtype (Response)

In **response** records, `transtype` is a full descriptive string. These are different from the request category values.

Examples of response values:
- `"Full Sale - Retail to Retail"`
- `"Full Sale - Retail to Wholesale"`
- `"Lease - Operating Lease"`
- `"Internal Sale - Corporate Restructure"`

Do not use response `transtype` values in request payloads — they will not match.

## Make Names

Make names in the API are **all-caps strings**:

| Value | Manufacturer |
|-------|-------------|
| `"GULFSTREAM"` | Gulfstream Aerospace |
| `"BOMBARDIER"` | Bombardier Aviation |
| `"DASSAULT"` | Dassault Aviation |
| `"CESSNA"` | Cessna / Textron Aviation |
| `"EMBRAER"` | Embraer |
| `"BEECHCRAFT"` | Beechcraft / Textron Aviation |
| `"PILATUS"` | Pilatus Aircraft |
| `"AIRBUS"` | Airbus |
| `"BOEING"` | Boeing |

Use `getAircraftMakeList` to get the complete list of valid make names.
