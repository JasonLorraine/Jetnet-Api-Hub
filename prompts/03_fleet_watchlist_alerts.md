# Prompt: Fleet Watchlist Alerts

## App goal

Build a monitoring tool that tracks a fleet of aircraft by model type, detects ownership changes or transaction events, and alerts the user when something changes — useful for brokers, MROs, and competitive intelligence teams.

## UI screens

1. **Watchlist setup** — Select aircraft models to monitor (e.g., G650, Citation CJ3+), set check interval (default: daily), optional geographic filter by base state/country
2. **Dashboard** — Summary cards showing: total aircraft tracked, new ownership changes since last check, recent transactions
3. **Change log** — Table of detected changes: aircraft reg, old owner, new owner, transaction type, transaction date
4. **Aircraft detail** — Click a row to see full aircraft card with current relationships and flight activity

## API workflow

Call these endpoints in this exact order:

1. **Login** — `POST /api/Admin/APILogin` with `{ "emailAddress": "...", "password": "..." }`
   - Store `bearerToken` and `apiToken` server-side
2. **Fleet snapshot** — `POST /api/Aircraft/getCondensedOwnerOperatorsPaged/{apiToken}/100/1`
   - Body: `{ "modlist": [MODEL_IDS], "lifecycle": "InOperation", "aclist": [], "modlist": [MODEL_IDS], "actiondate": "", "exactMatchReg": false, "showHistoricalAcRefs": false }`
   - Page through all results — treat `maxpages: 0` as 1 page
   - Response key is `aircraftowneroperators`
   - Store as baseline on first run
3. **Change detection (subsequent runs)** — Same endpoint with `actiondate` set to last check time
   - `actiondate`: `"MM/DD/YYYY"` of last successful check
   - `enddate`: today's date
   - Only records changed since `actiondate` are returned
4. **Transaction history for changed aircraft** — `POST /api/Aircraft/getHistoryListPaged/{apiToken}/100/1`
   - Body: `{ "aclist": [CHANGED_AIRCRAFT_IDS], "transtype": ["None"], "allrelationships": true, "startdate": "MM/DD/YYYY", "enddate": "MM/DD/YYYY", "modlist": [] }`
   - This reveals who sold, who bought, transaction type, and dates
5. **Detail drill-down (on demand)** — For a specific aircraft:
   - `GET /api/Aircraft/getRegNumber/{reg}/{apiToken}` — aircraft identity
   - `POST /api/Aircraft/getRelationships/{apiToken}` — current owner/operator
   - `POST /api/Aircraft/getFlightDataPaged/{apiToken}/100/1` — recent flights

## Response shaping contract

Normalize change alerts into this shape:

```json
{
  "aircraft": {
    "id": 211461,
    "reg": "N123AB",
    "make": "GULFSTREAM",
    "model": "G650",
    "year": 2018
  },
  "change": {
    "type": "Full Sale - Retail to Retail",
    "date": "2026-01-15",
    "previousOwner": {
      "companyId": 350427,
      "companyName": "Old Owner LLC"
    },
    "newOwner": {
      "companyId": 789,
      "companyName": "New Owner Corp"
    }
  },
  "currentOperator": {
    "companyId": 456,
    "companyName": "Flight Ops Inc."
  },
  "detectedAt": "2026-02-10T14:30:00Z"
}
```

- `previousOwner` and `newOwner` come from history records — look for `relationtype` of `"Seller"` and `"Purchaser"` in `companyrelationships`
- `currentOperator` comes from `getCondensedOwnerOperators` or `getRelationships`
- `detectedAt` is the timestamp your system noticed the change

## Auth/session rules

- Use the session helpers from `src/jetnet/session.py` (Python) or `src/jetnet/session.js` (JavaScript)
- Call `ensureSession()` / `ensure_session()` before every API request — this validates the token via `GET /api/Utility/getAccountInfo/{apiToken}` and re-logs in automatically if the token is invalid
- Use `jetnetRequest()` / `jetnet_request()` for all API calls — it handles auth headers, token insertion, and single retry on `INVALID SECURITY TOKEN`
- Token TTL is 60 minutes; session helpers proactively refresh at 50 minutes
- For long-running polling jobs, session helpers handle automatic token renewal — do not implement your own refresh loop
- Store all credentials and tokens server-side only

## Error rules

- Always check `responsestatus` in every JETNET response — HTTP 200 does not mean success
- If `responsestatus` contains `"ERROR"`, surface the message to the user
- On `"ERROR: INVALID SECURITY TOKEN"`, re-login once and retry — do not loop
- If the retry also fails, surface the error
- When paging, if `maxpages` is 0, treat as 1 page — do not skip
- `transtype` request values are category prefixes (e.g., `"FullSale"`, `"Lease"`), but response values are full strings (e.g., `"Full Sale - Retail to Retail"`) — do not compare them directly

## Definition of done

- [ ] User can select models to watch and see a fleet dashboard
- [ ] First run captures a baseline fleet snapshot
- [ ] Subsequent runs use `actiondate` for incremental change detection
- [ ] Ownership changes are detected and displayed in the change log
- [ ] Transaction history is fetched for changed aircraft to show buyer/seller
- [ ] Login uses `emailAddress` (capital A)
- [ ] `bearerToken` in header, `apiToken` in URL path
- [ ] `responsestatus` is checked on every response
- [ ] Token is validated via `/getAccountInfo` using session helpers
- [ ] Dates use `MM/DD/YYYY` format, computed dynamically
- [ ] Pagination handles `maxpages: 0` correctly
- [ ] Drill-down shows full aircraft detail on demand

## Do not do

- Do not poll more frequently than necessary — daily is usually sufficient for ownership changes
- Do not hardcode dates or model IDs — compute dates at runtime, make model IDs configurable
- Do not re-pull the entire fleet every run — use `actiondate` for incremental sync
- Do not send raw JETNET responses to the frontend — normalize first
- Do not send tokens or credentials to the browser
- Do not retry on auth failure more than once
- Do not ignore `responsestatus` — HTTP 200 can still be an error
- Do not use `emailaddress` (lowercase a) — the field is `emailAddress`
- Do not put `apiToken` in headers or request body — it goes in the URL path only
- Do not swap `bearerToken` and `apiToken`
- Do not compare `transtype` request values to response values directly — they use different formats
- Do not implement your own token refresh loop — use the session helpers which call `/getAccountInfo` for validation
