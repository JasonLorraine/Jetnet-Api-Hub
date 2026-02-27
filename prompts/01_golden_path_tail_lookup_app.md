# Prompt 01: Golden Path Tail-Number Lookup App

> Paste this into Cursor Composer or GitHub Copilot Chat.
> Fill in the [PLACEHOLDER] values before pasting.

---

Build a Next.js 14 App Router page that lets a user type an aircraft tail number
and see ownership and contact information from the JETNET API.

## Project context

- Framework: Next.js 14 with App Router and TypeScript
- Styling: Tailwind CSS
- JETNET base URL: https://customer.jetnetconnect.com
- Auth: dual-token -- bearerToken in Authorization header, apiToken in URL path
- Session helper: use `src/jetnet/session.ts` (already in this repo)

## What to build

### 1. Server action or API route: `app/api/aircraft/route.ts`

- Accepts a POST with body `{ tailNumber: string }`
- Calls `GET /api/Aircraft/getRegNumber/{tailNumber}/{apiToken}` with Bearer header
- Returns the normalized `GoldenPathResult` shape (see `docs/response-shapes.md`)
- Handles errors: invalid tail, no result, token expired

### 2. UI page: `app/page.tsx`

- Text input for tail number (placeholder: "N12345")
- Submit button that calls the server action
- Loading state while fetching
- Result card showing:
  - Aircraft: make, model, year, tail number, category size
  - Owner: company name, city, state, contact name, title, phone, email
  - Operator: company name if different from owner
  - Base airport and ICAO code
  - Market status badge (For Sale / Not For Sale)
- Error state: "Tail number not found" or "API error"

### 3. Environment variables

Read credentials from:
- `JETNET_EMAIL` -- emailAddress (CRITICAL: capital A in the API field name)
- `JETNET_PASSWORD`

### 4. JETNET response normalization

The raw JETNET response has this structure:
```json
{
  "responsestatus": "SUCCESS",
  "aircraftresult": {
    "regnbr": "N12345",
    "make": "GULFSTREAM",
    "model": "G550",
    "companyrelationships": [
      {
        "companyrelation": "Owner",
        "companyname": "Acme Aviation LLC",
        "companycity": "Dallas",
        "companystate": "Texas",
        "contactfirstname": "John",
        "contactlastname": "Smith",
        "contacttitle": "CEO",
        "contactemail": "john@acme.com",
        "contactbestphone": "214-555-1234"
      }
    ]
  }
}
```

Use `companyrelation` (not `relationtype`) to filter Owner vs Operator.
Map flat prefixed fields (companyname, contactfirstname) to your UI -- do not nest.

### 5. Error handling rules

- HTTP 200 with `responsestatus` starting with "ERROR" or "INVALID" = application error
- `responsestatus: "SUCCESS"` but empty `aircraftresult` = tail not found
- Network timeout: show retry button

### 6. Auth/session rules

- Token TTL is 60 minutes; proactively refresh at 50 minutes
- Validate tokens via `GET /api/Admin/getAccountInfo/{apiToken}` before long workflows
- On `INVALID SECURITY TOKEN`: re-login once and retry -- do not loop
- Store all credentials server-side -- never expose to the browser

## Output files

Produce:
1. `app/api/aircraft/route.ts`
2. `app/page.tsx`
3. `lib/jetnet.ts` (thin JETNET fetch wrapper using session.ts)
4. `.env.example` with `JETNET_EMAIL=` and `JETNET_PASSWORD=` stubs

## Constraints

- No `localStorage` or browser storage
- All JETNET calls server-side only (never expose bearerToken to the browser)
- TypeScript strict mode
- Tailwind only for styling (no other CSS libraries)
