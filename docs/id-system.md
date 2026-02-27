# JETNET ID System

## The Core Principle

JETNET uses several distinct ID systems. None of them are the same thing. The most common mistake is confusing `regnbr` (the tail number humans use) with `aircraftid` (the integer the API uses). Once you have `aircraftid`, almost everything else follows from it.

## Quick Reference

| Goal | ID to Use |
|------|-----------|
| Look up an aircraft by tail number | `regnbr` (input to `getRegNumber`) |
| Call any aircraft sub-record endpoint | `aircraftid` |
| Filter a list by aircraft type | `modelid` (in `modlist`) |
| Filter a list to specific aircraft | `aircraftid` (in `aclist`) |
| Pull a company's full record or contacts | `companyid` |
| Cross-reference with manufacturer records | `serialnbr` |
| Deduplicate history sync records | `transid` |
| Geographic analysis and territory maps | `baseicao` |
| Store as permanent external key in your database | `aircraftid` (not `regnbr`) |

## Aircraft Identifiers

### `aircraftid` (integer)

JETNET's internal primary key for an aircraft. Every aircraft in the database has a unique `aircraftid` that never changes even if the registration number changes.

**Where you get it:** From `getRegNumber`, `getAircraftList`, `getBulkAircraftExport`, or any history/event record.

**When to use it:** As the join key for all sub-record calls — pictures, relationships, flight data, history. This is the ID to store if you are building a database or CRM integration.

**Example:** `144322`

### `regnbr` (string)

The registration number (tail number) — the human-readable identifier printed on the aircraft. In the US this is typically `N` followed by numbers and letters (e.g., `N131SF`). International registrations follow country-specific formats.

**Where you get it:** User input, or any aircraft record.

**When to use it:** As input to `getRegNumber` for a tail lookup. Do not use `regnbr` as a database primary key — it can change when an aircraft is re-registered. `aircraftid` is stable; `regnbr` is not.

**Example:** `"N131SF"`, `"G-XBEK"`, `"VH-NSX"`

### `serialnbr` (string)

The manufacturer's serial number (MSN). This is the number stamped on the airframe at the factory and never changes.

**Where you get it:** Any aircraft record — `getRegNumber`, `getAircraft`, `getAircraftList`.

**When to use it:** Cross-referencing with manufacturer records, logbooks, or export certificates. If you need a permanent external identifier that predates JETNET, this is it.

**Example:** `"UC-131"`, `"2192"`, `"20564"`

### `modelid` (integer)

JETNET's internal ID for a specific aircraft model (make + model combination). The Gulfstream G550 has one `modelid`; the Gulfstream G600 has a different one.

**Where you get it:** From any aircraft record, or from `getAircraftModelList` which returns a full list of models with their IDs for a given make.

**When to use it:** As input to `modlist` in any list, history, or flight endpoint when you want to filter by aircraft type.

**Example:** `145` (G550), `634` (G600), `1188` (Challenger 350)

### `icaotype` (string)

The four-character ICAO aircraft type designator. Used in flight planning systems and ATC.

**Where you get it:** Aircraft records — `getRegNumber`, `getAircraft`.

**When to use it:** Cross-referencing with flight tracking systems, ADS-B data, or ICAO databases. Not used as a JETNET filter parameter.

**Example:** `"GLF5"` (Gulfstream V/G550), `"A319"` (Airbus A319/ACJ319)

## Company Identifiers

### `companyid` (integer)

JETNET's internal primary key for a company (legal entity). Owners, operators, manufacturers, and fractional providers all have `companyid` values.

**Where you get it:** From any relationship record — `getRelationships`, `getHistoryList`, `getRegNumber` companyrelationships, `getCompanyList`.

**When to use it:** As input to company sub-record endpoints: `getCompany/{companyid}`, `getContacts/{companyid}`, `getRelatedcompanies/{companyid}`, `getAircraftrelationships/{companyid}`.

**Example:** `4425`, `350427`

### `parentcompanyid` (integer)

The `companyid` of the parent company if the company is a subsidiary. Zero (`0`) means no parent — the company is a standalone entity.

**Where you get it:** Company records and nested `company` objects in relationship arrays.

**When to use it:** Building corporate hierarchy trees, identifying subsidiaries for fleet analysis, or understanding if an "operator" is actually a wholly owned subsidiary of the named owner.

## Contact Identifiers

### `contactid` (integer)

JETNET's internal primary key for an individual person.

**Where you get it:** From relationship records in `getRelationships`, `getHistoryList`, and `getRegNumber` companyrelationships.

**When to use it:** As input to `getContact/{contactid}/{apiToken}` to pull the full contact record. Also used to de-duplicate contacts across multiple aircraft or company records.

**Example:** `747133`, `524808`

## Airport and Geography Identifiers

### `baseicao` / `icao` (string)

The four-character ICAO airport code for the aircraft's home base. More precise than IATA codes and the preferred identifier for aviation data systems.

**Where you get it:** Aircraft records (`baseicao`), flight records (`origin`, `destination`).

**When to use it:** For geographic analysis, territory mapping, and filtering. Use `getAirportList` to get a full airport list with ICAO codes and coordinates.

**Example:** `"KOMA"` (Omaha Eppley), `"KTEB"` (Teterboro), `"LLBG"` (Tel Aviv Ben Gurion)

### `baseiata` / `iata` (string)

The three-character IATA airport code. More familiar to non-aviation audiences but less precise than ICAO (some airports have ICAO but no IATA).

**Where you get it:** Aircraft records and flight records.

**When to use it:** When displaying to end users who expect airline-style codes. Prefer ICAO for data joins.

**Example:** `"OMA"`, `"TEB"`, `"TLV"`

## Transaction and Event Identifiers

### `transid` (integer)

The unique ID for a specific history transaction record. Every ownership change, sale, or update event has a `transid`.

**Where you get it:** From `getHistoryList` records.

**When to use it:** For deduplication when building incremental sync pipelines. The JETNET transaction detail URL also uses `transid`:

```
http://www.jetnetevolution.com/DisplayAircraftDetail.aspx?acid={aircraftid}&jid={transid}
```
