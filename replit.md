# JETNET API Documentation Repository

## Overview
A comprehensive public documentation repository for the JETNET API (Jetnet Connect) -- the aviation industry's aircraft intelligence database. Contains documentation, code examples, helper scripts, and quick reference snippets.

## Structure
- `docs/` - Core documentation (auth, pagination, response handling, IDs, common mistakes, enums)
- `examples/python/` - 8 Python examples (requests + Flask)
- `examples/javascript/` - 8 JavaScript examples (fetch + Express)
- `scripts/` - Production-ready utilities (paginate.py, validate_payload.py)
- `references/` - Complete endpoint reference, vertical playbooks, buildkit
- `snippets/` - Quick reference snippets (fleet, ownership, usage, specs, valuation)

## Key Technical Details
- **JETNET API Base URL:** `https://customer.jetnetconnect.com`
- **Auth:** POST to `/api/Admin/APILogin` with `emailAddress` (capital A) and `password`
- **Two tokens:** `bearerToken` (in Authorization header) and `apiToken` (in URL path only)
- **Token lifetime:** 60 minutes, refresh proactively after 50 minutes
- **Date format:** `MM/DD/YYYY` with leading zeros
- **Pagination:** 1-based pages, use `maxpages` for loop control

## Dependencies
- Python 3.11 (requests, flask)
- No Node.js runtime needed (examples are standalone reference code)

## User Preferences
- Documentation-focused repository for public GitHub
- Target audience: vibe coders, developers, JETNET API customers
- Language-agnostic examples (Python + JavaScript)
- Focus areas: Fleet, Ownership, Usage, Spec Data Review, Valuation
