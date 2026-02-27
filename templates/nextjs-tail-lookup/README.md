# JETNET Tail Lookup -- Next.js 14 Starter

Type a tail number, see owner + operator + contact info from the JETNET API.

## Quick start

```bash
cp .env.example .env.local
# Edit .env.local and add your JETNET credentials

npm install
npm run dev
# Open http://localhost:3000
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `JETNET_EMAIL` | Yes | Your JETNET account email (sent as `emailAddress` in API) |
| `JETNET_PASSWORD` | Yes | Your JETNET account password |
| `JETNET_BASE_URL` | No | Default: `https://customer.jetnetconnect.com` |

## How it works

1. User types a tail number and clicks Search.
2. `app/page.tsx` calls the server action in `app/api/aircraft/route.ts`.
3. The route calls `lib/jetnet.ts` which authenticates and calls `getRegNumber`.
4. The raw JETNET response is normalized using `lib/normalize.ts` into a `GoldenPathResult`.
5. The result is rendered in `app/page.tsx`.

All JETNET calls are server-side. Credentials never reach the browser.

## File structure

```
app/
  page.tsx              -- UI: search form + result card
  api/aircraft/
    route.ts            -- Server route: calls JETNET, returns normalized JSON
lib/
  jetnet.ts             -- JETNET auth + getRegNumber fetch
  normalize.ts          -- Raw response -> GoldenPathResult shape
.env.example
package.json
README.md
```

## JETNET response notes

- Response key is `aircraftresult` (not `aircraft`)
- `companyrelationships` uses a flat schema: `companyrelation`, `companyname`, `contactfirstname`, etc.
- `maxpages: 0` on this endpoint is normal -- getRegNumber is not paged
- See `docs/response-shapes.md` in the skill root for full normalization reference
