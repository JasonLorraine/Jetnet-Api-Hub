# Prompt: Bulk Export Pipeline

## App goal

Build a data pipeline that exports the full fleet of aircraft for a given segment (by model, airframe type, or geography), handles pagination correctly, supports incremental sync via `actiondate`, and outputs structured data for analytics or CRM ingestion.

## UI screens

1. **Pipeline config** — Select filters: airframe type (FixedWing, Rotorcraft), make type (BusinessJet, Turboprop), model IDs, lifecycle (InOperation, ForSale), base country/state. Set output format (JSON, CSV). Toggle sub-arrays: maintenance, equipment, exterior, interior.
2. **Run status** — Progress bar showing: current page / total pages, records exported so far, elapsed time, estimated time remaining
3. **Results summary** — Total records exported, file download link, timestamp of run, any errors encountered
4. **Sync history** — Log of past runs with timestamps, record counts, and `actiondate` used for each run

## API workflow

Call these endpoints in this exact order:

1. **Login** — `POST /api/Admin/APILogin` with `{ "emailAddress": "...", "password": "..." }`
   - Store `bearerToken` and `apiToken` server-side
2. **Bulk export (paged)** — `POST /api/Aircraft/getBulkAircraftExportPaged/{apiToken}/{pagesize}/{page}`
   - Start with page 1, pagesize 100
   - Body:
     ```json
     {
       "airframetype": "FixedWing",
       "maketype": "BusinessJet",
       "lifecycle": "InOperation",
       "actiondate": "",
       "enddate": "",
       "exactMatchReg": false,
       "showHistoricalAcRefs": false,
       "showAwaitingDocsCompanies": false,
       "showMaintenance": false,
       "showAdditionalEquip": false,
       "showExterior": false,
       "showInterior": false,
       "aclist": [],
       "modlist": []
     }
     ```
   - Response key is `aircraft` (array)
   - Use `maxpages` to determine total pages — treat `maxpages: 0` as 1 page
   - Page through all results: increment `page` from 1 to `max(maxpages, 1)`
3. **Incremental sync (subsequent runs)** — Same endpoint with `actiondate` set to last run timestamp
   - `actiondate`: `"MM/DD/YYYY HH:MM:SS"` of last successful run
   - `enddate`: current datetime in same format
   - Only records changed since `actiondate` are returned
   - Store last run timestamp after each successful export for the next run

## Response shaping contract

Each exported aircraft record should be normalized to:

```json
{
  "aircraft": {
    "id": 211461,
    "reg": "N123AB",
    "serialNbr": "6789",
    "make": "GULFSTREAM",
    "model": "G650",
    "year": 2018,
    "lifecycle": "In Operation",
    "baseIcao": "KTEB",
    "baseAirport": "Teterboro",
    "baseCountry": "US",
    "baseState": "NJ"
  },
  "owner": {
    "companyId": 350427,
    "companyName": "Example Owner LLC",
    "contactName": "John Doe",
    "contactTitle": "Director of Aviation",
    "contactEmail": "john@example.com",
    "contactPhone": "555-0100"
  },
  "operator": {
    "companyId": 456,
    "companyName": "Flight Ops Inc.",
    "contactName": "Jane Smith",
    "contactTitle": "Chief Pilot",
    "contactEmail": "jane@flightops.com",
    "contactPhone": "555-0200"
  },
  "forSale": false,
  "askingPrice": null,
  "datePurchased": "2020-03-15",
  "airframeHours": 4500
}
```

- `getBulkAircraftExport` uses flat prefixed relationship fields — map them:
  - `owr*` fields → `owner` object (`owrcompanyname`, `owrfname`, `owrlname`, `owrtitle`, `owremail`, `owrphone1`)
  - `opr*` fields → `operator` object
  - `chp*` fields → chief pilot info
- `forsale` in this endpoint is `"Y"` / `"N"` / `""` — not `"true"`/`"false"`
- `datepurchased` is `YYYYMMDD` format — convert to ISO date
- `estaftt` or `aftt` = airframe total time (hours)

## Auth/session rules

- Use the session helpers from `src/jetnet/session.py` (Python) or `src/jetnet/session.js` (JavaScript)
- Call `ensureSession()` / `ensure_session()` before every API request — this validates the token via `GET /api/Utility/getAccountInfo/{apiToken}` and re-logs in automatically if the token is invalid
- Use `jetnetRequest()` / `jetnet_request()` for all API calls — it handles auth headers, token insertion, and single retry on `INVALID SECURITY TOKEN`
- Token TTL is 60 minutes; session helpers proactively refresh at 50 minutes
- For long-running exports that span many pages, session helpers handle automatic token renewal mid-export — do not implement your own refresh loop
- Store all credentials and tokens server-side only

## Error rules

- Always check `responsestatus` in every JETNET response — HTTP 200 does not mean success
- If `responsestatus` contains `"ERROR"`, log the error and surface it
- On `"ERROR: INVALID SECURITY TOKEN"`, re-login once and retry — do not loop
- If the retry also fails, surface the error
- When paging: `maxpages: 0` means all results fit in one page — treat as 1 page, do not exit early
- The `responsestatus` on success contains summary counts: `"SUCCESS: Ac Count: 12 Comp Count: 28 ..."` — parse these for validation
- If a page fails mid-export, log the page number and allow resuming from that page

## Definition of done

- [ ] User can configure filters and run a bulk export
- [ ] All pages are fetched — pagination handles `maxpages: 0` correctly
- [ ] Incremental sync uses `actiondate` with full datetime format (`MM/DD/YYYY HH:MM:SS`)
- [ ] Last run timestamp is stored and used as `actiondate` for next run
- [ ] Flat prefixed relationship fields are mapped to normalized objects
- [ ] `forsale` values `"Y"`/`"N"` are converted to boolean
- [ ] `datepurchased` `YYYYMMDD` format is converted to ISO date
- [ ] Output is available as JSON and/or CSV
- [ ] Progress is shown during export
- [ ] Login uses `emailAddress` (capital A)
- [ ] `bearerToken` in header, `apiToken` in URL path
- [ ] `responsestatus` is checked on every response
- [ ] Token is validated via `/getAccountInfo` using session helpers
- [ ] `show*` flags default to false to minimize payload size

## Do not do

- Do not fetch all pages without checking `maxpages` — but also do not skip when `maxpages` is 0
- Do not hardcode dates — compute at runtime, store last run time for incremental sync
- Do not enable `show*` flags unless the user explicitly requests those sub-arrays — they increase payload size significantly
- Do not send raw JETNET responses to the frontend — normalize the flat prefixed schema
- Do not send tokens or credentials to the browser
- Do not retry on auth failure more than once
- Do not ignore `responsestatus` — HTTP 200 can still be an error
- Do not use `emailaddress` (lowercase a) — the field is `emailAddress`
- Do not put `apiToken` in headers or request body — it goes in the URL path only
- Do not swap `bearerToken` and `apiToken`
- Do not confuse `forsale` formats — `getBulkAircraftExport` uses `"Y"`/`"N"`, while `getAircraftList` uses `"true"`/`"false"`
- Do not assume `datepurchased` is in `MM/DD/YYYY` format — in bulk export it is `YYYYMMDD`
- Do not implement your own token refresh loop — use the session helpers which call `/getAccountInfo` for validation
- Do not pull the entire fleet every run when only changes are needed — use `actiondate` for incremental sync
