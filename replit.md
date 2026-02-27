# JETNET API Documentation Repository

## Overview
A comprehensive public documentation repository for the JETNET API (Jetnet Connect) -- the aviation industry's aircraft intelligence database. Contains documentation, code examples, helper scripts, AI prompts, starter templates, session helpers, and eval test cases. Targets vibe coders, developers, and JETNET API customers.

## Structure
- `START_HERE.md` - Choose your adventure entry point (3 paths: demo UI, bulk data, CRM enrichment)
- `src/jetnet/` - Session helpers (Python + TypeScript) with auto-refresh and /getAccountInfo validation
  - `session.py` - Python: SessionState dataclass, login(), ensure_session(), jetnet_request(), normalize_error(), refresh_session()
  - `session.ts` - TypeScript: login(), ensureSession(), jetnetRequest(), normalizeError(), refreshAndRequest()
- `docs/` - Core documentation (auth, pagination, response handling, response shapes, IDs, common mistakes, enums)
  - `response-shapes.md` - Normalized UI contracts: AircraftCard, CompanyCard, ContactCard, GoldenPathResult with Python/TS factories
- `templates/` - One-click starter apps
  - `nextjs-tail-lookup/` - Next.js 14 App Router + Tailwind: lib/jetnet.ts, lib/normalize.ts, app/api/aircraft/route.ts (POST), app/page.tsx
  - `python-fastapi-golden-path/` - FastAPI with local jetnet/session.py copy, /lookup?tail= endpoint, lifespan-based session init
- `prompts/` - AI prompts for Cursor/Copilot/ChatGPT (4 recipes: tail lookup, FBO leads, fleet watchlist, bulk export)
- `examples/python/` - 8 Python examples (requests + Flask)
- `examples/javascript/` - 8 JavaScript examples (fetch + Express)
- `examples/responses/` - 16 known-good JSON response examples from v5 (tail-lookup, bulk-export, history, relationships, etc.)
- `evals/` - AI eval test cases (evals.json)
- `scripts/` - Production-ready utilities
  - `paginate.py` - Generic pagination helper for all paged endpoints
  - `validate_payload.py` - Payload validator (catches common mistakes before sending)
  - `token_probe.py` - Standalone token lifetime measurement script (polls /getAccountInfo until failure)
- `references/` - Complete endpoint reference, vertical playbooks, buildkit
- `snippets/` - Quick reference snippets (fleet, ownership, usage, specs, valuation)

## Key Technical Details
- **JETNET API Base URL:** `https://customer.jetnetconnect.com`
- **Auth:** POST to `/api/Admin/APILogin` with `emailAddress` (capital A) and `password`
- **Two tokens:** `bearerToken` (in Authorization header) and `apiToken` (in URL path only)
- **Token lifetime:** 60 minutes, proactive refresh at 50 minutes (TOKEN_TTL_SECONDS=3000)
- **Token validation:** `/api/Admin/getAccountInfo/{apiToken}` as lightweight health check
- **Session helpers:** `src/jetnet/session.py` (Python) and `src/jetnet/session.ts` (TypeScript) handle login, refresh, validation, and auto-retry
- **Date format:** `MM/DD/YYYY` with leading zeros; bulk export also accepts `MM/DD/YYYY HH:MM:SS`
- **Pagination:** 1-based pages, use `maxpages` for loop control, `maxpages: 0` = single page (not error)
- **HTTP 200 != success:** Always check `responsestatus` for `"ERROR"` or `"INVALID"`
- **Schema differences:** `companyrelation` (getRegNumber flat) vs `relationtype` (getRelationships nested); `forsale: "Y"/"N"` in bulk export vs `forsale: "true"/"false"` in getAircraftList
- **transtype:** Use `["None"]` not `[]` for all transaction types

## Dependencies
- Python 3.11 (requests, flask)
- No Node.js runtime needed (examples are standalone reference code)

## User Preferences
- Documentation-focused repository for public GitHub
- Target audience: vibe coders, developers, JETNET API customers
- Language-agnostic examples (Python + JavaScript/TypeScript)
- Focus areas: Fleet, Ownership, Usage, Spec Data Review, Valuation
- AI-native: prompts that generate working apps when pasted into IDE agents
- Templates: one-click starter apps that run with just .env setup
