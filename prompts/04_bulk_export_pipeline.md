# Prompt 04: Bulk Export Market Intelligence Pipeline

> Paste this into Cursor Composer or GitHub Copilot Chat.
> Fill in the [PLACEHOLDER] values before pasting.

---

Build a Python FastAPI service that runs an hourly JETNET bulk export poll,
stores aircraft records in a SQLite database, and exposes a REST API for querying
market dynamics -- for-sale counts, ownership turnover, and fleet composition by
model category.

## Project context

- Language: Python 3.11+
- Framework: FastAPI + uvicorn
- Database: SQLite via SQLAlchemy (swap for Postgres by changing the connection string)
- JETNET base URL: https://customer.jetnetconnect.com
- Paginator: use `scripts/paginate.py` (`get_bulk_export`)
- Session helper: use `src/jetnet/session.py`

## What to build

### Files

```
main.py             -- FastAPI app + scheduler
db.py               -- SQLAlchemy models + session
jetnet_poll.py      -- JETNET bulk export polling logic
```

### Database schema: `aircraft` table

```sql
CREATE TABLE aircraft (
    aircraft_id     INTEGER PRIMARY KEY,
    model_id        INTEGER,
    tail_number     TEXT,
    serial_number   TEXT,
    make            TEXT,
    model           TEXT,
    year_mfr        INTEGER,
    year_delivered  INTEGER,
    make_type       TEXT,
    for_sale        TEXT,           -- 'Y' | 'N' | ''
    asking_price    TEXT,
    market_status   TEXT,
    lifecycle       TEXT,
    owner_company   TEXT,
    owner_city      TEXT,
    owner_state     TEXT,
    owner_country   TEXT,
    operator_company TEXT,
    est_aftt        INTEGER,
    est_cycles      INTEGER,
    last_action_date TEXT,          -- from JETNET actiondate
    last_polled_at  TEXT            -- ISO datetime this row was last updated
);
```

### Polling logic: `jetnet_poll.py`

#### Hourly incremental poll

```python
def poll_bulk_export(session, db, last_run_dt: datetime) -> int:
    """
    Fetch all BusinessJet aircraft records changed since last_run_dt.
    Upsert into the database. Return count of records processed.
    """
```

POST body to `getBulkAircraftExportPaged`:
```python
{
    "airframetype": "None",
    "maketype": "BusinessJet",
    "lifecycle": "InOperation",
    "actiondate": last_run_dt.strftime("%m/%d/%Y %H:%M:%S"),
    "enddate": now.strftime("%m/%d/%Y %H:%M:%S"),
    "exactMatchReg": False,
    "showHistoricalAcRefs": False,
    "showAwaitingDocsCompanies": False,
    "showMaintenance": False,
    "showAdditionalEquip": False,
    "showExterior": False,
    "showInterior": False,
}
```

IMPORTANT: `actiondate` and `enddate` MUST include time (`HH:MM:SS`) for hourly polling.
`maxpages: 0` means all results fit in one page -- not an error.

#### Flat schema parsing

The bulk export uses prefixed flat fields for relationships:
- `owrcompanyname`, `owrcity`, `owrstate`, `owrcountry` -- owner
- `oprcompanyname` -- operator
- `forsale` -- "Y" / "N" string (not boolean like other endpoints)
- `asking` -- asking price string ("Inquire", "$4,500,000", etc.)
- `status` -- market status string

#### Initial full load

On first run (no `last_polled_at` in DB), fetch the full fleet with no date filter:
omit `actiondate` and `enddate`, or set `actiondate` to `"01/01/2000 00:00:00"`.

### FastAPI endpoints: `main.py`

```
GET /health
    Returns: { "status": "ok", "last_poll": ISO_DATETIME, "aircraft_count": N }

GET /market/summary
    Returns: {
        "for_sale_count": N,
        "not_for_sale_count": N,
        "unknown_count": N,
        "by_make": { "GULFSTREAM": N, "CITATION": N, ... }
    }

GET /aircraft?tail=N12345
    Returns: single aircraft row as JSON

GET /aircraft?for_sale=true&make=GULFSTREAM
    Returns: filtered list (limit 100)

GET /market/trends?days=30
    Returns: for-sale count per day for the last N days
             (requires tracking historical for_sale changes)
```

### Auth/session rules

- Token TTL is 60 minutes; proactively refresh at 50 minutes
- Validate tokens via `GET /api/Admin/getAccountInfo/{apiToken}` before long workflows
- On `INVALID SECURITY TOKEN`: re-login once and retry -- do not loop
- `emailAddress` has a capital A

### Environment variables

```
JETNET_EMAIL
JETNET_PASSWORD
JETNET_BASE_URL     # optional
DATABASE_URL        # optional, default: sqlite:///./jetnet.db
POLL_INTERVAL_HOURS # optional, default: 1
MAKETYPE_FILTER     # optional, default: BusinessJet
```

## Output

Produce all three files: `main.py`, `db.py`, `jetnet_poll.py`

Also produce `requirements.txt`:
```
fastapi
uvicorn
sqlalchemy
apscheduler
requests
python-dotenv
```

And `.env.example`:
```
JETNET_EMAIL=you@example.com
JETNET_PASSWORD=yourpassword
DATABASE_URL=sqlite:///./jetnet.db
```
