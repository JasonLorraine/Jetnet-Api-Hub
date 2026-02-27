# JETNET Golden Path -- FastAPI Starter

Look up any aircraft by tail number. Returns a normalized GoldenPathResult with
owner, operator, and contact information.

## Quick start

```bash
cp .env.example .env
# Edit .env and add your JETNET credentials

pip install -r requirements.txt
uvicorn main:app --reload
# Open http://localhost:8000/lookup?tail=N12345
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `JETNET_EMAIL` | Yes | Your JETNET account email |
| `JETNET_PASSWORD` | Yes | Your JETNET account password |
| `JETNET_BASE_URL` | No | Default: `https://customer.jetnetconnect.com` |

## How it works

1. On startup, the app logs in to JETNET and validates the session.
2. `GET /lookup?tail=N12345` calls `getRegNumber`, normalizes the flat `companyrelationships` schema, and returns a `GoldenPathResult`.
3. The `jetnet/session.py` helper handles token refresh and auto-retry on `INVALID SECURITY TOKEN`.

See `docs/response-shapes.md` in the repo root for the full normalization reference.
