# JETNET Bulk Export Integration

## Endpoint

`POST /api/Aircraft/getBulkAircraftExportPaged/{apiToken}/{pagesize}/{page}`

The bulk export endpoint is not a simple aircraft query -- it is a **data graph engine**. Each execution builds a relational dataset including aircraft, companies, contacts, phones, events, and flight summaries. Entity counts scale nonlinearly with aircraft count because joins are automatically expanded.

---

## Two Operating Modes

### Snapshot Mode

Omit `aircraftchanges` or leave it blank. Returns a full dataset snapshot matching your filters.

```json
{
  "modlist": [278, 288],
  "maketype": "None",
  "airframetype": "None",
  "forsale": "",
  "actiondate": "",
  "enddate": "",
  "aclist": []
}
```

Use snapshot mode for:
- Initial full data ingestion
- Periodic full refreshes
- One-time exports

### Delta Mode

Set `aircraftchanges` to `true`. Returns aircraft with qualifying changes since `actiondate`.

```json
{
  "modlist": [278, 288],
  "maketype": "None",
  "airframetype": "None",
  "forsale": "",
  "actiondate": "02/26/2026 10:00:00",
  "enddate": "02/27/2026 10:00:00",
  "aircraftchanges": true,
  "aclist": []
}
```

Delta mode still returns **full records**, not field-level diffs. When an aircraft qualifies, you get the entire relational graph for that aircraft -- not just the fields that changed.

---

## Graph-Based Change Detection

An aircraft qualifies for inclusion in a delta pull if **any related entity** changes -- not just the aircraft record itself.

Changes that trigger inclusion:

| Entity | Example |
|--------|---------|
| Aircraft record | Tail number change, lifecycle update |
| Ownership | New owner, operator change |
| Company relationships | Company name change, address update |
| Contacts | New chief pilot, contact info update |
| Events | Maintenance event, inspection |
| Flight activity | New flight records |

This is graph-level change detection. A contact phone number change on the owner company will cause the aircraft to appear in the delta, even though nothing about the aircraft itself changed.

---

## actiondate as a Watermark

`actiondate` acts as a change cursor (watermark) for delta pulls:

- **Older dates** expand result size (more changes accumulated)
- **Recent dates** reduce payloads but still rebuild full relational objects
- **Empty** `actiondate` with `aircraftchanges=true` has no lower bound

For incremental sync, track your last successful pull timestamp and use it as the next `actiondate`:

```python
last_sync = load_last_sync_timestamp()

body = {
    "modlist": [278, 288],
    "aircraftchanges": True,
    "actiondate": last_sync.strftime("%m/%d/%Y %H:%M:%S"),
    "enddate": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
    "aclist": [],
    "maketype": "None",
    "airframetype": "None",
    "forsale": ""
}

results = get_all_pages(bearer, token, path, body)
save_last_sync_timestamp(datetime.now())
```

---

## Entity Scaling

Each aircraft record expands into related entities. A query returning 100 aircraft does not mean 100 flat records -- it means 100 aircraft plus their full relationship graphs:

```
Aircraft
 ├── Owner company + contacts + phones
 ├── Operator company + contacts + phones
 ├── Chief pilot contact
 ├── Exclusive brokers (up to 2) + contacts
 ├── Additional relationships (up to 3)
 ├── Events
 └── Flight summary
```

A fleet of 100 aircraft could produce thousands of related entity records. Always use `modlist` or `aclist` to bound your scope.

---

## Correct Integration Pattern

### Step 1: Initial Snapshot

Run a full snapshot export to populate your local store.

```python
body = {
    "modlist": TARGET_MODELS,
    "maketype": "None",
    "airframetype": "None",
    "forsale": "",
    "actiondate": "",
    "enddate": "",
    "aclist": []
}
all_aircraft = get_all_pages(bearer, token, bulk_path, body)
upsert_all(all_aircraft)
```

### Step 2: Periodic Delta Pulls

Run delta pulls on a schedule (hourly, daily) using `aircraftchanges=true` and your last sync timestamp as `actiondate`.

### Step 3: Upsert Entire Records

Delta mode returns complete records, not patches. Always **upsert the entire aircraft record** rather than trying to diff individual fields:

```python
for aircraft in delta_results:
    db.upsert(
        table="aircraft",
        key={"aircraft_id": aircraft["aircraftid"]},
        data=normalize(aircraft)
    )
```

---

## Common Pitfalls

| Pitfall | Why It Fails | Fix |
|---------|-------------|-----|
| Using bulk export for UI search | Exports are synchronous and built inline -- too slow for live dashboards | Use `getRegNumber` or `getAircraftList` for interactive queries |
| No scope filters | Unbounded `modlist: []` + `aclist: []` creates massive payloads | Always filter by `modlist`, `aclist`, or `maketype` |
| Mixing test/production tokens | Authentication failures with no clear error | Use separate environment variables for each environment |
| Patching individual fields from delta | Delta returns full records, not diffs | Upsert the entire record |
| Expecting field-level change info | Delta tells you *which aircraft changed*, not *what changed* | Compare against your stored copy if you need change details |

---

## Response Format

The bulk export uses a **flat prefixed schema** for relationships. See [Response Handling](response-handling.md) for the full schema comparison.

| Prefix | Role |
|--------|------|
| `owr*` | Owner |
| `opr*` | Operator |
| `chp*` | Chief Pilot |
| `excbrk1*` / `excbrk2*` | Exclusive Brokers |
| `addl1*` / `addl2*` / `addl3*` | Additional relationships |

Other bulk export quirks:
- `forsale` is `"Y"` / `"N"` (not `"true"` / `"false"`)
- `datepurchased` is `YYYYMMDD` format (not `MM/DD/YYYY`)
- `maxpages: 0` means single page -- use `max(maxpages, 1)` in your loop
- `actiondate` accepts `MM/DD/YYYY HH:MM:SS` for hourly polling windows

See [Common Mistakes](common-mistakes.md) and [Pagination](pagination.md) for details on these quirks.
