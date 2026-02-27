# Prompt: FBO Airport Activity Leads

## App goal

Build a lead generation tool for FBOs (Fixed Base Operators) that shows which aircraft are flying into or out of a specific airport, identifies the operating companies and decision-maker contacts, and produces a prospect list for outreach.

## UI screens

1. **Airport input screen** — Input field for airport ICAO code (e.g., `KTEB`), direction toggle (arrivals / departures / both), date range selector (default: last 90 days)
2. **Activity feed** — Table of flights showing: tail number, make/model, origin, destination, date, operator name
3. **Lead detail** — Click a row to see: aircraft card, owner/operator info, contact names and titles
4. **Export** — Button to download the prospect list as CSV

## API workflow

Call these endpoints in this exact order:

1. **Login** — `POST /api/Admin/APILogin` with `{ "emailAddress": "...", "password": "..." }`
   - Store `bearerToken` and `apiToken` server-side
2. **Flight activity search** — `POST /api/Aircraft/getFlightDataPaged/{apiToken}/100/1`
   - For arrivals: set `destination` to the ICAO code, leave `origin` empty
   - For departures: set `origin` to the ICAO code, leave `destination` empty
   - Body: `{ "origin": "KTEB", "destination": "", "startdate": "MM/DD/YYYY", "enddate": "MM/DD/YYYY", "aclist": [], "modlist": [], "exactMatchReg": true }`
   - Page through all results using `maxpages` — treat `maxpages: 0` as 1 page (JETNET quirk)
3. **Deduplicate aircraft** — Collect unique `aircraftid` values from flight results
4. **Bulk relationships** — `POST /api/Aircraft/getRelationships/{apiToken}` with `aclist` containing all unique aircraft IDs
   - Body: `{ "aclist": [id1, id2, ...], "modlist": [], "actiondate": "", "showHistoricalAcRefs": false }`
   - This returns all owner/operator/contact info in one call
5. **Contact enrichment (optional)** — For high-priority leads, call `GET /api/Company/getContacts/{companyid}/{apiToken}` to get full contact details including titles, email, phone

## Response shaping contract

Normalize into this shape per lead:

```json
{
  "aircraft": {
    "id": 211461,
    "reg": "N123AB",
    "make": "GULFSTREAM",
    "model": "G650",
    "year": 2018
  },
  "flights": [
    { "date": "2026-02-10", "origin": "KTEB", "dest": "KPBI", "minutes": 165 }
  ],
  "operator": {
    "companyId": 456,
    "companyName": "Flight Ops Inc."
  },
  "owner": {
    "companyId": 350427,
    "companyName": "Example Owner LLC"
  },
  "contacts": [
    { "name": "Jane Doe", "title": "Chief Pilot", "email": "jane@example.com", "phone": "555-0100" }
  ],
  "flightCount": 12
}
```

- Sort leads by `flightCount` descending — most active operators first
- Filter contacts for relevant titles: Chief Pilot, Director of Aviation, Scheduler, Dispatcher, Director of Flight Operations
- `owner` and `operator` may be `null`
- Relationships use the nested schema (`relationtype`, `company {}`, `contact {}`)

## Auth/session rules

- Use the session helpers from `src/jetnet/session.py` (Python) or `src/jetnet/session.js` (JavaScript)
- Call `ensureSession()` / `ensure_session()` before every API request — this validates the token via `GET /api/Utility/getAccountInfo/{apiToken}` and re-logs in automatically if the token is invalid
- Use `jetnetRequest()` / `jetnet_request()` for all API calls — it handles auth headers, token insertion, and single retry on `INVALID SECURITY TOKEN`
- Token TTL is 60 minutes; session helpers proactively refresh at 50 minutes
- Store all credentials and tokens server-side only

## Error rules

- Always check `responsestatus` in every JETNET response — HTTP 200 does not mean success
- If `responsestatus` contains `"ERROR"`, surface the message to the user
- On `"ERROR: INVALID SECURITY TOKEN"`, re-login once and retry — do not loop
- If the retry also fails, surface the error
- When paging, if `maxpages` is 0, treat as 1 page (single-page result) — do not skip

## Definition of done

- [ ] User can enter an airport ICAO code and see flight activity
- [ ] Arrivals and departures can be filtered independently
- [ ] Aircraft are deduplicated before calling `getRelationships`
- [ ] Bulk `getRelationships` is used (pass `aclist`) instead of looping per aircraft
- [ ] Leads are sorted by flight count (most active operators first)
- [ ] Contacts are filtered for decision-maker titles
- [ ] Login uses `emailAddress` (capital A)
- [ ] `bearerToken` in header, `apiToken` in URL path
- [ ] `responsestatus` is checked on every response
- [ ] Token is validated via `/getAccountInfo` using session helpers
- [ ] Dates are computed dynamically (default 90-day window)
- [ ] Pagination handles `maxpages: 0` correctly
- [ ] CSV export works

## Do not do

- Do not loop `getRegNumber` per tail for bulk lookups — use `getRelationships` with `aclist` instead
- Do not hardcode dates — compute at runtime using `MM/DD/YYYY` format
- Do not send raw JETNET responses to the frontend — normalize first
- Do not send tokens or credentials to the browser
- Do not retry on auth failure more than once
- Do not ignore `responsestatus` — HTTP 200 can still be an error
- Do not use `emailaddress` (lowercase a) — the field is `emailAddress`
- Do not put `apiToken` in headers or request body — it goes in the URL path only
- Do not swap `bearerToken` and `apiToken`
- Do not confuse the flat schema from `getRegNumber` with the nested schema from `getRelationships` — they use different field names (`companyrelation` vs `relationtype`)
