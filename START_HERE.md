# Start Here

New to the JETNET API? Pick your path and get running in minutes.

---

## What You Need

- A JETNET API account (email + password)
- Base URL: `https://customer.jetnetconnect.com`
- Environment variables set: `JETNET_EMAIL`, `JETNET_PASSWORD`

## How Auth Works

1. POST credentials to `/api/Admin/APILogin` (field is `emailAddress` with a capital A)
2. Response gives you two tokens: `bearerToken` and `apiToken`
3. Every call after login: `bearerToken` in the `Authorization` header, `apiToken` in the URL path
4. Tokens expire after 60 minutes
5. Validate your session with `/api/Utility/getAccountInfo/{apiToken}` before long workflows
6. On `INVALID SECURITY TOKEN`: re-login once and retry. Never loop.

## HTTP 200 Does Not Mean Success

JETNET returns HTTP 200 even for errors. Always check `responsestatus` in the JSON body:

```
if responsestatus starts with "ERROR" → it failed, even though HTTP said 200
```

---

## Choose Your Path

### Path A: "I want a demo UI in 5 minutes"

You want to see a working app, type in a tail number, and get results.

1. Go to [`templates/nextjs-tail-lookup/`](templates/nextjs-tail-lookup/)
2. Copy `.env.example` to `.env.local`, fill in your credentials
3. `npm install && npm run dev`
4. Open `http://localhost:3000`, enter a tail number

That's it. You have a working aircraft lookup app.

**Also available:** [`templates/python-fastapi-golden-path/`](templates/python-fastapi-golden-path/) if you prefer Python.

---

### Path B: "I want bulk/export data"

You want to sync fleet data, export history, or build analytics pipelines.

1. Read the [Pagination Guide](docs/pagination.md) (1-based pages, `maxpages` loop)
2. Look at [`examples/python/07_bulk_export.py`](examples/python/07_bulk_export.py) for the pattern
3. Use [`scripts/paginate.py`](scripts/paginate.py) to handle pagination automatically
4. For a full pipeline prompt, paste [`prompts/04_bulk_export_pipeline.md`](prompts/04_bulk_export_pipeline.md) into your IDE agent

Key gotcha: `getBulkAircraftExportPaged` returns `maxpages: 0` for single-page results. Use `max(maxpages, 1)`.

---

### Path C: "I want CRM enrichment"

You want to enrich contacts, generate leads, or monitor ownership changes.

1. For FBO/airport leads: paste [`prompts/02_fbo_airport_activity_leads.md`](prompts/02_fbo_airport_activity_leads.md) into your IDE agent
2. For fleet watchlist/alerts: paste [`prompts/03_fleet_watchlist_alerts.md`](prompts/03_fleet_watchlist_alerts.md) into your IDE agent
3. Use the [`templates/python-fastapi-golden-path/`](templates/python-fastapi-golden-path/) as your backend starting point
4. See [`snippets/ownership.md`](snippets/ownership.md) for quick copy-paste relationship lookups

---

## Session Helpers

We provide production-ready session modules that handle login, token refresh, and validation automatically:

- **Python:** [`src/jetnet/session.py`](src/jetnet/session.py)
- **JavaScript:** [`src/jetnet/session.js`](src/jetnet/session.js)

These use `/getAccountInfo` as a lightweight health check to validate your token before long workflows, and auto re-login once if the token has expired.

---

## Where to Go Next

| Resource | When to use it |
|----------|---------------|
| [Authentication Guide](docs/authentication.md) | Deep dive into tokens, refresh, retry |
| [Response Shapes](docs/response-shapes.md) | Normalized objects for your UI (AircraftCard, CompanyCard, etc.) |
| [Common Mistakes](docs/common-mistakes.md) | Save yourself hours of debugging |
| [Prompts](prompts/) | Paste into Cursor/Copilot to generate working apps |
| [Full Endpoint Reference](references/endpoints.md) | Every endpoint with all parameters |
