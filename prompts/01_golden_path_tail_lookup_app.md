# Prompt: Golden Path Tail Lookup App

## App goal

Build a web app where a user enters an aircraft registration number (tail number) and gets back a full aircraft profile card showing identity, owner, operator, and recent flight activity.

## UI screens

1. **Search screen** — Single input field for tail number (e.g., `N123AB`), a submit button
2. **Results screen** — Aircraft card displaying:
   - Aircraft identity: registration, make, model, year, serial number
   - Base airport (ICAO code and name)
   - Photos (if available)
   - Owner and operator company names
   - Recent flight activity (last 6 months, up to 20 flights)
3. **Error screen** — Clear error message if aircraft not found or API error occurs

## API workflow

Call these endpoints in this exact order:

1. **Login** — `POST /api/Admin/APILogin` with `{ "emailAddress": "...", "password": "..." }`
   - Store `bearerToken` and `apiToken` server-side
2. **Tail lookup** — `GET /api/Aircraft/getRegNumber/{reg}/{apiToken}`
   - Extract `aircraftid` from `aircraftresult` — this is required before any other call
   - If `aircraftid` is missing, return "Aircraft not found"
3. **Fan out in parallel** (all three at once):
   - **Pictures** — `GET /api/Aircraft/getPictures/{aircraftid}/{apiToken}`
   - **Relationships** — `POST /api/Aircraft/getRelationships/{apiToken}` with body `{ "aircraftid": ID, "aclist": [], "modlist": [], "actiondate": "", "showHistoricalAcRefs": false }`
   - **Flight activity** — `POST /api/Aircraft/getFlightDataPaged/{apiToken}/100/1` with body `{ "aircraftid": ID, "startdate": "MM/DD/YYYY", "enddate": "MM/DD/YYYY", "origin": "", "destination": "", "aclist": [], "modlist": [], "exactMatchReg": true }`
   - Compute `startdate` as 6 months ago and `enddate` as today — never hardcode dates

## Response shaping contract

Normalize all JETNET responses into this shape before sending to the frontend:

```json
{
  "aircraft": {
    "id": 211461,
    "reg": "N123AB",
    "serialNbr": "6789",
    "make": "GULFSTREAM",
    "model": "G650",
    "year": 2018
  },
  "base": {
    "icao": "KTEB",
    "airport": "Teterboro"
  },
  "photos": [
    { "description": "Exterior", "date": "2022-08-11", "url": "https://..." }
  ],
  "owner": {
    "companyId": 350427,
    "companyName": "Example Owner LLC"
  },
  "operator": {
    "companyId": 456,
    "companyName": "Example Operator Inc."
  },
  "flights": [
    { "date": "2026-02-10", "origin": "KTEB", "dest": "KPBI", "minutes": 165 }
  ]
}
```

- `owner` and `operator` may be `null` if not present in relationships
- Filter relationships by `relationtype`: `"Owner"` and `"Operator"`
- Photos `url` is a pre-signed S3 URL — display immediately, do not cache longer than 1 hour
- Limit flights to 20 most recent

## Auth/session rules

- Use the session helpers from `src/jetnet/session.py` (Python) or `src/jetnet/session.js` (JavaScript)
- Call `ensureSession()` / `ensure_session()` before every API request — this validates the token via `GET /api/Utility/getAccountInfo/{apiToken}` and re-logs in automatically if the token is invalid
- Use `jetnetRequest()` / `jetnet_request()` for all API calls — it handles auth headers, token insertion, and single retry on `INVALID SECURITY TOKEN`
- Token TTL is 60 minutes; session helpers proactively refresh at 50 minutes
- Store all credentials and tokens server-side only — never expose to the browser

## Error rules

- Always check `responsestatus` in every JETNET response — HTTP 200 does not mean success
- If `responsestatus` contains `"ERROR"`, surface the message to the user
- On `"ERROR: INVALID SECURITY TOKEN"`, re-login once and retry — do not loop
- If the retry also fails, surface the error — do not retry again
- Handle network errors and non-JSON responses gracefully

## Definition of done

- [ ] User can enter a tail number and see a full aircraft profile
- [ ] Login uses `emailAddress` (capital A) in the request body
- [ ] `bearerToken` is sent in `Authorization: Bearer` header on every request
- [ ] `apiToken` is inserted into URL paths (not headers or body)
- [ ] `aircraftid` is resolved from `getRegNumber` before any other endpoint is called
- [ ] Pictures, relationships, and flights load in parallel after tail lookup
- [ ] Response is normalized to the contract shape above
- [ ] `responsestatus` is checked on every response
- [ ] Token is validated via `/getAccountInfo` using session helpers
- [ ] Dates are computed dynamically (6-month window for flights)
- [ ] Error states are displayed to the user
- [ ] Credentials are never sent to the client

## Do not do

- Do not hardcode dates — compute `startdate` and `enddate` at runtime
- Do not send raw JETNET responses to the frontend — always normalize
- Do not cache `pictureurl` longer than 1 hour (pre-signed S3 URLs expire)
- Do not send tokens or credentials to the browser/mobile client
- Do not retry on auth failure more than once
- Do not call `getRelationships`, `getPictures`, or `getFlightDataPaged` without first resolving `aircraftid` from `getRegNumber`
- Do not use `emailaddress` (lowercase a) — the field is `emailAddress`
- Do not put `apiToken` in headers or request body — it goes in the URL path only
- Do not ignore `responsestatus` — HTTP 200 can still be an error
- Do not swap `bearerToken` and `apiToken` — bearer goes in the header, apiToken goes in the URL path
