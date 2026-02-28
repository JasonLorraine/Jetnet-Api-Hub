# JETNET API Documentation Repository

## Overview
A comprehensive public documentation repository for the JETNET API (Jetnet Connect) -- the aviation industry's aircraft intelligence database. Contains documentation, code examples, helper scripts, AI prompts, starter templates, session helpers, and eval test cases. Targets vibe coders, developers, and JETNET API customers.

## Structure
- `START_HERE.md` - Choose your adventure entry point (5 paths: demo UI, bulk data, CRM enrichment, AI agent, MCP zero-code)
- `llms.txt` - Concise AI/LLM reference (~150 lines, fits small context windows)
- `llms-full.txt` - Complete AI/LLM reference (~3100 lines, all docs concatenated)
- `src/jetnet/` - Session helpers (Python + TypeScript) with auto-refresh and /getAccountInfo validation
  - `session.py` - Python: SessionState dataclass, login(), ensure_session(), jetnet_request(), normalize_error(), refresh_session()
  - `session.ts` - TypeScript: login(), ensureSession(), jetnetRequest(), normalizeError(), refreshAndRequest()
- `docs/` - Core documentation (auth, pagination, response handling, response shapes, flight data, IDs, common mistakes, enums)
  - `bulk-export.md` - Bulk export: snapshot vs delta mode, graph-based change detection, entity scaling, integration pattern
  - `history.md` - Transaction history: ownership timeline, comparable sales, leasing intelligence, enrichment pattern
  - `snapshots.md` - Historical fleet state: getCondensedSnapshot, snapshotdate, non-paged, caching strategy
  - `trends.md` - Market trends & time-series: getModelMarketTrends, composite indicators, data collection architecture
  - `events.md` - Aircraft events: getEventListPaged, lifecycle changes, market velocity, causal analytics layer
  - `contacts.md` - 7 Contact endpoints: getContact, getContactList(Paged), getIdentification, getPhonenumbers, getOtherlistings, getContAircraftRelationships
  - `companies.md` - 9 Company endpoints: getCompany, getIdentification, getPhonenumbers, getRelatedcompanies, getAircraftrelationships, getCompanyCertifications, getCompanyHistory, getCompanyList(Paged)
  - `model-data.md` - Model reference: getModelOperationCosts, getModelPerformanceSpecs, getModelIntelligence
  - `airports.md` - Airport reference data: getAirportList, geographic dimension table for joins
  - `utility-endpoints.md` - Cacheable reference/dimension tables: lifecycle, makes, models, JNIQ sizes, airframe types, event categories
  - `data-model.md` - Entity graph: Aircraft (aircraftid) ↔ Company (companyid) ↔ Contact (contactid) relationships, Golden Path traversal, best practices
  - `aircraft.md` - 21 Aircraft endpoints: getAircraft (full record), 14 sub-record GETs (identification, airframe, engine, apu, avionics, features, additionalequipment, interior, exterior, maintenance, leases, pictures, status, companyrelationships), tail/hex lookup (getRegNumber, getHexNumber), fleet search (getAircraftList), batch relationships, getAllAircraftObjects
  - `flight-data.md` - Flight data integration: getFlightData (per-flight detail) vs getFlights (monthly summary), ingestion strategy, CRM signals
  - `response-shapes.md` - Normalized UI contracts: AircraftCard, CompanyCard, ContactCard, GoldenPathResult with Python/TS factories
- `templates/` - One-click starter apps
  - `nextjs-tail-lookup/` - Next.js 14 App Router + Tailwind: lib/jetnet.ts, lib/normalize.ts, app/api/aircraft/route.ts (POST), app/page.tsx
  - `python-fastapi-golden-path/` - FastAPI with local jetnet/session.py copy, /lookup?tail= endpoint, lifespan-based session init
- `prompts/` - AI prompts for Cursor/Copilot/ChatGPT (5 recipes: tail lookup, FBO leads, fleet watchlist, bulk export, MCP agent workflow)
- `examples/python/` - 8 Python examples (requests + Flask)
- `examples/javascript/` - 8 JavaScript examples (fetch + Express)
- `examples/responses/` - 16 known-good JSON response examples from v5 (tail-lookup, bulk-export, history, relationships, etc.)
- `mcp/` - MCP server for AI agent integration (Claude Desktop, Cursor, Copilot)
  - `jetnet_mcp.py` - Python MCP server: 11 tools (golden_path, lookup, relationships, flights, fleet search, history, trends, model search, snapshot, model specs, health check)
  - `README.md` - MCP setup, tool reference, example conversations, architecture
  - `requirements.txt` - mcp>=1.0.0, httpx>=0.27.0, pydantic>=2.0.0
  - `claude_desktop_config.example.json` - Example config for Claude Desktop
- `evals/` - AI eval test cases (evals.json)
- `scripts/` - Production-ready utilities
  - `paginate.py` - Generic pagination helper for all paged endpoints
  - `validate_payload.py` - Payload validator (catches common mistakes before sending)
  - `token_probe.py` - Standalone token lifetime measurement script (polls /getAccountInfo until failure)
  - `model_search.py` - CLI search tool for model IDs (by make, model, or ICAO type)
- `references/` - Complete endpoint reference, vertical playbooks, buildkit, model ID lookup
  - `model-ids.md` - 872 aircraft models with AMODID values for modlist, grouped by maketype
  - `model-id-table.json` - Machine-readable deduplicated model reference (872 entries with fleet counts)
  - `model-id-table.csv` - Same data in CSV for spreadsheet users
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
- **Model IDs (AMODID):** 872 unique model IDs from the master table; used in `modlist` arrays. 5 make types: Business Jet (268), Turboprop (186), Jet Airliner (252), Turbine/Helicopter (127), Piston (39). 67 unique makes. Airframe types: F=FixedWing, R=Rotary. `modlist: []` = no filter (all models). Reference at `references/model-id-table.json`

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
