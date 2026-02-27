# JETNET API Documentation Repository

## Overview
A comprehensive public documentation repository for the JETNET API (Jetnet Connect) -- the aviation industry's aircraft intelligence database. Contains documentation, code examples, helper scripts, AI prompts, starter templates, and session helpers. Targets vibe coders, developers, and JETNET API customers.

## Structure
- `START_HERE.md` - Choose your adventure entry point
- `src/jetnet/` - Session helpers (Python + JS) with auto-refresh and /getAccountInfo validation
- `docs/` - Core documentation (auth, pagination, response handling, response shapes, IDs, common mistakes, enums)
- `templates/` - One-click starter apps (Next.js tail lookup, FastAPI golden path)
- `prompts/` - AI prompts for Cursor/Copilot/ChatGPT (4 recipes)
- `examples/python/` - 8 Python examples (requests + Flask)
- `examples/javascript/` - 8 JavaScript examples (fetch + Express)
- `scripts/` - Production-ready utilities (paginate.py, validate_payload.py, token_probe.py)
- `references/` - Complete endpoint reference, vertical playbooks, buildkit
- `snippets/` - Quick reference snippets (fleet, ownership, usage, specs, valuation)

## Key Technical Details
- **JETNET API Base URL:** `https://customer.jetnetconnect.com`
- **Auth:** POST to `/api/Admin/APILogin` with `emailAddress` (capital A) and `password`
- **Two tokens:** `bearerToken` (in Authorization header) and `apiToken` (in URL path only)
- **Token lifetime:** 60 minutes, refresh proactively after 50 minutes
- **Token validation:** `/api/Utility/getAccountInfo/{apiToken}` as lightweight health check
- **Session helpers:** `src/jetnet/session.py` (Python) and `src/jetnet/session.js` (JS) handle login, refresh, validation, and auto-retry
- **Date format:** `MM/DD/YYYY` with leading zeros
- **Pagination:** 1-based pages, use `maxpages` for loop control
- **HTTP 200 != success:** Always check `responsestatus` for `"ERROR"`

## Dependencies
- Python 3.11 (requests, flask)
- No Node.js runtime needed (examples are standalone reference code)

## User Preferences
- Documentation-focused repository for public GitHub
- Target audience: vibe coders, developers, JETNET API customers
- Language-agnostic examples (Python + JavaScript)
- Focus areas: Fleet, Ownership, Usage, Spec Data Review, Valuation
- AI-native: prompts that generate working apps when pasted into IDE agents
- Templates: one-click starter apps that run with just .env setup
