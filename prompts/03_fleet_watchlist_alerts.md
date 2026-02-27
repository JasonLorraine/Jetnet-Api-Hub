# Prompt 03: Fleet Watchlist Change Alerts

> Paste this into Cursor Composer or GitHub Copilot Chat.
> Fill in the [PLACEHOLDER] values before pasting.

---

Build a Python script that monitors a watchlist of aircraft for ownership changes,
market status changes, and new "for sale" listings, then sends a summary alert
email (or Slack message) when anything changes.

## Project context

- Language: Python 3.11+
- JETNET base URL: https://customer.jetnetconnect.com
- Session helper: use `src/jetnet/session.py` (already in this repo)
- Paginator: use `scripts/paginate.py` (`get_bulk_export`)
- State storage: JSON file (`watchlist_state.json`) for simplicity; swap for a DB later
- Alert: email via SMTP or Slack webhook (configurable via env vars)

## What to build

### Script: `fleet_watchlist.py`

#### Watchlist input

A JSON file `watchlist.json` defining the aircraft to monitor. Two modes:

Mode 1: specific tail numbers
```json
{ "tails": ["N12345", "N67890", "N11111"] }
```

Mode 2: model filter (all aircraft of a given model)
```json
{ "modlist": [145, 1194], "maketype": "BusinessJet" }
```

#### JETNET call

Use `getBulkAircraftExportPaged` with `actiondate` set to the last run time
(stored in state file). This returns only aircraft records that changed since
the last poll.

POST body:
```json
{
  "airframetype": "None",
  "maketype": "BusinessJet",
  "lifecycle": "InOperation",
  "actiondate": "MM/DD/YYYY HH:MM:SS",
  "enddate": "MM/DD/YYYY HH:MM:SS",
  "exactMatchReg": false,
  "showHistoricalAcRefs": false,
  "showAwaitingDocsCompanies": false,
  "showMaintenance": false,
  "showAdditionalEquip": false,
  "showExterior": false,
  "showInterior": false
}
```

IMPORTANT: `actiondate` and `enddate` accept datetime strings (`MM/DD/YYYY HH:MM:SS`),
not just dates. `maxpages: 0` means single-page result -- not an error.

#### Flat schema fields to track

The bulk export uses a prefixed flat schema:
- `forsale` -- "Y" / "N" / "" (string, not boolean)
- `status` -- "For Sale, Immediate" / "Not For Sale" / etc.
- `asking` -- asking price string
- `owrcompanyname` -- owner company name
- `owrfname`, `owrlname` -- owner contact
- `oprcompanyname` -- operator company name

#### Change detection

Compare each aircraft record to `watchlist_state.json`. Flag changes in:
- `forsale` flipped to "Y"
- `status` changed
- `owrcompanyname` changed (ownership change)
- `asking` changed

#### Alert content

Build a plain-text or HTML summary of all changes found:
```
JETNET Fleet Alert -- 3 changes detected (2026-02-27 10:00 UTC)

N12345 -- GULFSTREAM G550 (2019)
  OWNERSHIP CHANGE: Acme Corp -> Beta Holdings LLC
  NEW CONTACT: Jane Doe, Director of Aviation, jane@beta.com

N67890 -- CITATION CJ3+ (2022)
  NOW FOR SALE: For Sale, Immediate | Asking: Inquire
```

#### Alert delivery

Configurable via env vars:
- `ALERT_MODE=email` -- SMTP
- `ALERT_MODE=slack` -- POST to `SLACK_WEBHOOK_URL`
- `ALERT_MODE=print` -- stdout only (default for dev/testing)

#### State management

- On first run: fetch all watchlist aircraft, store current state, send no alert.
- On subsequent runs: compare to stored state, alert on changes, update state.
- Store state in `watchlist_state.json` as `{ "last_run": "ISO_DATETIME", "aircraft": { "N12345": {...snapshot...} } }`

#### Auth/session rules

- Token TTL is 60 minutes; proactively refresh at 50 minutes
- Validate tokens via `GET /api/Admin/getAccountInfo/{apiToken}` before long workflows
- On `INVALID SECURITY TOKEN`: re-login once and retry -- do not loop
- `emailAddress` has a capital A

#### Environment variables

```
JETNET_EMAIL
JETNET_PASSWORD
JETNET_BASE_URL     # optional
WATCHLIST_FILE      # default: watchlist.json
STATE_FILE          # default: watchlist_state.json
ALERT_MODE          # email | slack | print (default: print)
SLACK_WEBHOOK_URL   # if ALERT_MODE=slack
SMTP_HOST           # if ALERT_MODE=email
SMTP_PORT           # if ALERT_MODE=email
SMTP_USER           # if ALERT_MODE=email
SMTP_PASSWORD       # if ALERT_MODE=email
ALERT_FROM          # if ALERT_MODE=email
ALERT_TO            # if ALERT_MODE=email
```

## Output

Produce: `fleet_watchlist.py`

Make it runnable as a cron job:
```bash
0 * * * * JETNET_EMAIL=... python /path/to/fleet_watchlist.py
```

Print progress to stdout with timestamps:
```
[2026-02-27 10:00:01] Polling JETNET for changes since 2026-02-27 09:00:00 ...
[2026-02-27 10:00:03] 3 aircraft changed. Sending alert.
[2026-02-27 10:00:04] Alert sent. State updated.
```
