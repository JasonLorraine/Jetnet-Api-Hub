# Prompt 02: FBO Airport Activity Lead Enrichment

> Paste this into Cursor Composer or GitHub Copilot Chat.
> Fill in the [PLACEHOLDER] values before pasting.

---

Build a Python script that takes a list of aircraft tail numbers observed at an FBO
and enriches each one with owner and contact information from the JETNET API,
outputting a CSV ready for CRM import.

## Project context

- Language: Python 3.11+
- JETNET base URL: https://customer.jetnetconnect.com
- Session helper: use `src/jetnet/session.py` (already in this repo)
- Output: CSV file for CRM import

## What to build

### Script: `fbo_lead_enrichment.py`

#### Input

A text file or hardcoded list of tail numbers, one per line:
```
N12345
N67890
N11111
```

Read from `TAIL_FILE` env var or a default `tails.txt` in the same directory.

#### JETNET call per tail

For each tail number, call:
```
GET /api/Aircraft/getRegNumber/{tailNumber}/{apiToken}
```

With header: `Authorization: Bearer {bearerToken}`

#### Response parsing

The response key is `aircraftresult` (not `aircraft`).
`companyrelationships` uses a FLAT schema with these field names:
- `companyrelation` -- "Owner", "Operator", "Chief Pilot", etc.
- `companyname`, `companycity`, `companystate`, `companycountry`
- `contactfirstname`, `contactlastname`, `contacttitle`
- `contactemail`, `contactbestphone`, `contactofficephone`, `contactmobilephone`
- `baseicao`, `baseairport` -- aircraft home base

#### Target contacts

Filter `companyrelationships` where `contacttitle` contains any of:
- "Chief Pilot"
- "Director of Aviation"
- "Scheduler"
- "Dispatcher"

If no such title found, fall back to the Owner's primary contact.

#### Output CSV columns

```
tail_number, make, model, year, category_size,
base_icao, base_airport, base_country,
company_name, company_city, company_state, company_country,
contact_first, contact_last, contact_title,
contact_email, contact_best_phone, contact_office_phone, contact_mobile,
for_sale, market_status,
jetnet_url
```

The `jetnet_url` for manual research:
`http://www.jetnetevolution.com/DisplayAircraftDetail.aspx?acid={aircraftid}`

#### Rate limiting

Sleep 0.5 seconds between API calls. Print progress: `[5/20] N12345 -- OK`.

#### Error handling

- Tail not found: write a row with `make=NOT_FOUND`, skip contact fields
- JETNET error: log warning, write row with `make=ERROR:{status}`
- Network error: retry once, then skip

#### Auth/session rules

- Token TTL is 60 minutes; proactively refresh at 50 minutes
- Validate tokens via `GET /api/Admin/getAccountInfo/{apiToken}` before long workflows
- On `INVALID SECURITY TOKEN`: re-login once and retry -- do not loop
- `emailAddress` has a capital A -- this is the single most common auth mistake

#### Environment variables

```
JETNET_EMAIL      # emailAddress -- CRITICAL: capital A in the JSON field
JETNET_PASSWORD
JETNET_BASE_URL   # optional, default: https://customer.jetnetconnect.com
TAIL_FILE         # optional, default: tails.txt
OUTPUT_FILE       # optional, default: fbo_leads.csv
```

## Auth pattern

```python
# Use session helper (recommended)
from src.jetnet.session import login, ensure_session, jetnet_request

session = login()
session = ensure_session(session)
result = jetnet_request("GET", "/api/Aircraft/getRegNumber/N12345/{apiToken}", session)
```

## Output

Produce one file: `fbo_lead_enrichment.py`

Print a summary at the end:
```
Done. 18/20 tails enriched. 2 not found. Output: fbo_leads.csv
```
