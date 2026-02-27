# JETNET Vertical Playbooks

One page per industry vertical. Each playbook follows the same format:
the business question, the endpoint(s) that answer it, a minimal payload,
and what to do with the response.

---

## 1. Aircraft Sales and Brokerage

**The business question:** Who owns this aircraft, is it for sale, what is the
asking price, what is its flight activity, and who are the decision makers?

**Primary use case:** A broker wants to research a specific tail or a segment of
the market before approaching a seller or buyer.

### Tail research workflow

```
getRegNumber → get aircraftid
getPictures  → show the aircraft
getRelationships → confirm current owner and operator, get contacts
getFlightData → understand utilization (active vs parked)
getHistoryList → see prior transaction prices and ownership chain
```

### Market scan workflow (find for-sale inventory by model)

```
POST /api/Aircraft/getAircraftList/{apiToken}
{
  "maketype": "BusinessJet",
  "modlist": [145, 634],       // G550, G600
  "forsale": "true",
  "lifecycle": "InOperation",
  "aclist": []
}
```

Response key is `aircraft`. Filter on `asking`/`askingprice` for price ranges.

### Market trend context (how long do they sit, what do they sell for)

```
POST /api/Model/getModelMarketTrends/{apiToken}
{
  "modlist": [145, 634],
  "displayRange": 24,
  "startdate": "COMPUTE_24_MONTHS_AGO",
  "productcode": ["None"]
}
```

Key fields: `avg_asking_price`, `avg_daysonmarket`, `aircraft_for_sale_count`.

### Who to call (decision makers)

Once you have `companyid` from a relationship record:
```
POST /api/Company/getContacts/{companyid}/{apiToken}
```

Returns contacts with title, email, phone. Filter on title for CEO, VP, Director.

---

## 2. OEM Competitive Intelligence

**The business question:** How is our model performing in the market vs competitors?
Who is operating our aircraft and where? What is the delivery and transaction pace?

### Market share by model

```
POST /api/Model/getModelMarketTrends/{apiToken}
{
  "modlist": [YOUR_MODELS + COMPETITOR_MODELS],
  "displayRange": 36,
  "startdate": "COMPUTE_36_MONTHS_AGO",
  "productcode": ["None"]
}
```

Compare `in_operation_count`, `aircraft_for_sale_count`, `avg_asking_price`,
`avg_daysonmarket` across models over time. A rising `avg_daysonmarket` is a
demand signal.

### Delivery and transaction pace (new aircraft entering the fleet)

```
POST /api/Aircraft/getHistoryListPaged/{apiToken}/100/1
{
  "modlist": [YOUR_MODEL_IDS],
  "transtype": ["Full Sale - Manufacturer to New"],
  "startdate": "01/01/2024",
  "enddate": "COMPUTE_TODAY",
  "isnewaircraft": "Yes",
  "allrelationships": true,
  "aclist": []
}
```

`Purchaser` in `companyrelationships` is the first buyer. Use this to map which
operators are taking delivery and at what pace.

### Fleet in operation by geography

```
POST /api/Aircraft/getAircraftList/{apiToken}
{
  "modlist": [YOUR_MODEL_IDS],
  "lifecycle": "InOperation",
  "aclist": []
}
```

Group by `basecountry` and `basestate` for territory coverage maps.

### Performance specs (for competitive comparison)

```
POST /api/Model/getModelPerformanceSpecs/{apiToken}
{
  "modlist": [YOUR_MODEL_ID, COMPETITOR_MODEL_ID],
  "airframetype": "None",
  "maketype": "None",
  "make": "",
  "annualhours": 0,
  "fuelprice": 0
}
```

---

## 3. FBO Territory and Traffic Analysis

**The business question:** What aircraft are based near us, who are the operators
flying in and out, and which routes are most active?

### Aircraft based in your territory

```
POST /api/Aircraft/getAircraftList/{apiToken}
{
  "airframetype": "FixedWing",
  "maketype": "BusinessJet",
  "lifecycle": "InOperation",
  "basestate": ["TX", "OK", "LA"],
  "basecountry": "US",
  "aclist": [],
  "modlist": []
}
```

This gives you the local fleet. Cross with `getRelationships` using bulk `aclist`
to get owner/operator contact info for the entire list in one call.

### Traffic into your airport (origin/destination filtering)

```
POST /api/Aircraft/getFlightDataPaged/{apiToken}/100/1
{
  "origin": "KDAL",
  "destination": "",
  "startdate": "COMPUTE_90_DAYS_AGO",
  "enddate": "COMPUTE_TODAY",
  "aclist": [],
  "modlist": []
}
```

Swap `origin` for `destination` to see inbound traffic. Use `aircraftid` from
results with `getRelationships` to identify which operators are most active.

### Operator targeting (companies most active in your market)

Aggregate flight records by `aircraftid`, count legs, then bulk-call `getRelationships`
with the top-N aircraft IDs as `aclist`. This gives you the operators flying the
most in your territory with their contact info.

---

## 4. MRO Targeting and Fleet Monitoring

**The business question:** Which aircraft in our target segment are due for
maintenance, who operates them, and who are the decision makers?

### Fleet snapshot for a model segment

```
POST /api/Aircraft/getBulkAircraftExportPaged/{apiToken}/100/1
{
  "maketype": "BusinessJet",
  "modlist": [TARGET_MODEL_IDS],
  "lifecycle": "InOperation",
  "actiondate": "",
  "forsale": "",
  "aclist": []
}
```

Full aircraft records including `aftt` (airframe total time), `estaftt`,
engine serial numbers, and maintenance tracking fields. Page through all results.

### High-airframe-time aircraft (maintenance trigger)

From the bulk export, filter on `estaftt` above your threshold. These are the
aircraft most likely to need heavy maintenance. Take their `aircraftid` list and
call `getRelationships` in bulk to get the MRO decision maker contacts.

### Change tracking (new operators, recent transactions)

```
POST /api/Aircraft/getHistoryListPaged/{apiToken}/100/1
{
  "modlist": [TARGET_MODEL_IDS],
  "startdate": "COMPUTE_90_DAYS_AGO",
  "enddate": "COMPUTE_TODAY",
  "transtype": ["None"],
  "allrelationships": true,
  "aclist": []
}
```

New operator = new MRO relationship opportunity. Filter `transtype` for sale
events to catch aircraft changing hands.

### Contact lookup for decision makers

```
POST /api/Company/getContacts/{companyid}/{apiToken}
```

Filter by title for Director of Maintenance, VP of Operations, Chief Pilot.
These are the MRO buyers.

---

## 5. Finance and Investment Diligence

**The business question:** What is the asset worth, how has it traded historically,
what are comparable transactions, and is the fleet in the collateral pool in good
standing?

### Single asset valuation context

```
POST /api/Model/getModelMarketTrends/{apiToken}
{
  "modlist": [ASSET_MODEL_ID],
  "displayRange": 60,
  "startdate": "COMPUTE_60_MONTHS_AGO",
  "productcode": ["None"]
}
```

60 months of `avg_asking_price`, `low_asking_price`, `high_asking_price`, and
`avg_daysonmarket` gives you price trend and liquidity context for the model.

### Transaction history for the specific aircraft

```
POST /api/Aircraft/getHistoryListPaged/{apiToken}/100/1
{
  "aclist": [AIRCRAFT_ID],
  "transtype": ["None"],
  "allrelationships": true,
  "startdate": "01/01/2000",
  "enddate": "COMPUTE_TODAY",
  "aclist": [AIRCRAFT_ID],
  "modlist": []
}
```

Full chain of ownership for the asset. `soldprice` and `askingprice` fields on
transaction records show actual deal prices where available.

### Comparable sales (same model, recent transactions)

```
POST /api/Aircraft/getHistoryListPaged/{apiToken}/100/1
{
  "modlist": [ASSET_MODEL_ID],
  "transtype": ["Full Sale - Preowned"],
  "startdate": "COMPUTE_24_MONTHS_AGO",
  "enddate": "COMPUTE_TODAY",
  "ispreownedtrans": "Yes",
  "allrelationships": true,
  "aclist": []
}
```

Filter for `isretailtrans: true` to isolate arm's length transactions. Use
`soldprice` for comps.

### Fleet-level collateral monitoring

Given a list of aircraft IDs in the collateral pool:
```
POST /api/Aircraft/getCondensedOwnerOperators/{apiToken}
{
  "aclist": [ID1, ID2, ID3, ...],
  "modlist": []
}
```

Response key is `aircraftowneroperators`. Each record has `comp1relation`,
`comp1name`, and `datepurchased`. Use `actiondate` parameter to pull only
records that changed since your last snapshot -- essential for incremental
monitoring without re-pulling the entire pool.

---

## 6. Charter Supplemental Lift -- Fractional Owner Targeting

**The business question:** Which fractional owners of large jets in my target
markets have had a recent record update? These are the prospects most likely to
need supplemental lift -- they own fractional shares but occasionally need more
capacity or a different aircraft category.

**Primary use case:** A charter company wants to identify business jet fractional
owners in the Northeast with recent activity and approach them with supplemental
lift offerings.

### Find fractional owners by geography and aircraft type

```
POST /api/Aircraft/getAcCompanyFractionalReportPaged/{apiToken}/{pagesize}/{page}
{
  "airframetype": "FixedWing",
  "maketype": "BusinessJet",
  "regnbr": "",
  "make": "",
  "actiondate": "COMPUTE_30_DAYS_AGO",
  "enddate": "COMPUTE_TODAY",
  "basestate": ["NY", "CT", "MA", "RI", "NJ"],
  "modlist": [],
  "relationship": ["Fractional Owner"]
}
```

Response key is `aircraftcompfractionalrefs`. Page through all results using
`maxpages`. Each page returns `count` records (typically 25-100 per page).

**Key fields for outreach:**

| Field | What it tells you |
|-------|-------------------|
| `company` | Fractional owner company or individual name |
| `contactFirstName` / `contactLastName` | Decision maker name |
| `contactEmailAddress` | Direct email |
| `contactMobile` | Mobile number |
| `fractionPercentOwned` | `"100.00"` = sole owner; partial% = true fractional share |
| `make` / `model` | Aircraft type they own (e.g., CHALLENGER 604) |
| `regnbr` | Tail number |
| `compCity` / `compState` | Billing address / home base |
| `programManager` | Fractional program operator (may be "UNKNOWN") |
| `programHolder` | Program holding entity (may be "UNKNOWN") |
| `lastFractionPurchaseDate` | When they last bought in -- recency signal |

**Filter for actual owners only:** `fractionPercentOwned != "0.00"` -- the
response includes operators and managers on the same aircraft with `"0.00"`.
Pass `"relationship": ["Fractional Owner"]` in the request to pre-filter, but
also post-filter in code to be safe.

### Targeting by specific aircraft model (e.g., heavy jets only)

```
POST /api/Aircraft/getAcCompanyFractionalReportPaged/{apiToken}/{pagesize}/{page}
{
  "airframetype": "FixedWing",
  "maketype": "BusinessJet",
  "regnbr": "",
  "make": "",
  "actiondate": "COMPUTE_90_DAYS_AGO",
  "enddate": "COMPUTE_TODAY",
  "basestate": [],
  "modlist": [33, 34, 35],
  "relationship": ["Fractional Owner"]
}
```

Pass model IDs in `modlist` to narrow to specific aircraft types. Use
`getAircraftModelList` or `references/id-glossary.md` to find model IDs.
Leave `basestate: []` for national scope.

### Enrichment workflow (from fractional record to full relationship picture)

```
1. getAcCompanyFractionalReportPaged  --> aircraftid + companyid + contact info
2. getRelationships (bulk aclist)      --> confirm current operator structure
3. getFlightDataPaged (per aircraftid) --> utilization (is the fraction being used?)
```

High utilization + fractional share = strong candidate for supplemental lift.
Low utilization may indicate a program exit or aircraft transition -- also a
sales signal for a new purchase.

### Common mistakes on this endpoint

- Response key is `aircraftcompfractionalrefs` -- not `aircraft`, not `fractionalowners`
- Each aircraft appears multiple times (one row per relation type) -- deduplicate on `aircraftid` + `companyid` before building a contact list
- `relationship` filter is an array: `["Fractional Owner"]` -- not a string
- `basestate` is an array of abbreviations: `["NY", "CT"]` -- not full state names
- `actiondate` / `enddate` use `MM/DD/YYYY` format with leading zeros
- `programManager` and `programHolder` are often `"UNKNOWN"` for self-managed programs -- do not filter on these fields expecting clean data

Known-good example: `examples/fractional-owner-report.json`

---

## 7. FBO Ramp Contact Targeting

**The business question:** Which companies and decision makers are flying into
my FBO? I want to reach chief pilots, directors of aviation, schedulers, and
dispatchers to win their fuel, handling, and services business over competitors.

**Primary use case:** An FBO collects tail numbers from ramp activity or ADS-B
data, then uses JETNET to identify the right contacts at each company for a
targeted outreach campaign.

### Single tail lookup (Tier A -- Golden Path start)

```
GET /api/Aircraft/getRegNumber/{regnbr}/{apiToken}
```

No request body. Returns `aircraftresult` with a `companyrelationships` array.

**CRITICAL -- getRegNumber uses a flat schema, not nested objects:**

| Field | What it contains |
|-------|-----------------|
| `companyrelation` | Relation type: `"Owner"`, `"Operator"`, `"Chief Pilot"`, etc. |
| `companyname` | Company name (prefixed, not nested) |
| `contactfirstname` / `contactlastname` | Contact name |
| `contacttitle` | Job title -- filter on this for outreach targeting |
| `contactemail` | Email address |
| `contactbestphone` | Best phone (office or mobile) |
| `contactofficephone` / `contactmobilephone` | Phone details |
| `baseicao` | Home airport ICAO code |

### Filter for the right contacts

```python
TARGET_TITLES = {"chief pilot", "director of aviation", "scheduler",
                 "dispatcher", "director of flight operations", "flight coordinator"}

contacts = [
    r for r in aircraft["companyrelationships"]
    if r.get("contacttitle", "").lower() in TARGET_TITLES
       or r.get("companyrelation") in ("Chief Pilot", "Operator")
]
```

Note: field is `companyrelation` (not `relationtype`) -- this is unique to
`getRegNumber`. See `references/id-glossary.md` for the full schema comparison.

### Bulk ramp list workflow (many tails at once)

For a ramp list of 10+ tails, use `getRelationships` with `aclist` in bulk
rather than looping `getRegNumber` per tail:

```
1. getRegNumber per tail           --> aircraftid for each tail
2. getRelationships (bulk aclist)  --> all relationships in one POST
3. getContacts per companyid       --> full contact list for each company
```

`getRelationships` bulk returns the nested schema (`relationtype`, `company {}`,
`contact {}` sub-objects) -- different from `getRegNumber` flat schema.

### Aircraft based at your airport (proactive prospecting)

```
POST /api/Aircraft/getAircraftList/{apiToken}
{
  "airframetype": "FixedWing",
  "maketype": "BusinessJet",
  "lifecycle": "InOperation",
  "baseicao": "KSDL",
  "aclist": [],
  "modlist": []
}
```

Returns all jets based at your airport. Take their `aircraftid` list into
`getRelationships` bulk to get all contacts in one call.

Known-good example: `examples/fbo-contact-lookup.json`

---

## 8. Dealer-Broker Hourly Market Intelligence Feed

**The business question:** What changed in the JETNET database in the last hour?
A dealer-broker runs this on the hour, 24/7/365, to recompute market dynamics
the moment JETNET data updates -- new listings, price changes, ownership
transfers, or status changes.

**Primary use case:** Automated pipeline that detects every aircraft record
change in a 1-hour window and feeds a live market dashboard or pricing model.

### Hourly change query (Tier B -- always paged)

```
POST /api/Aircraft/getBulkAircraftExportPaged/{apiToken}/{pagesize}/{page}
{
  "airframetype": "None",
  "maketype": "BusinessJet",
  "lifecycle": "InOperation",
  "actiondate": "MM/DD/YYYY HH:MM:SS",
  "enddate":    "MM/DD/YYYY HH:MM:SS",
  "exactMatchReg": false,
  "showHistoricalAcRefs": false,
  "showAwaitingDocsCompanies": false,
  "showMaintenance": false,
  "showAdditionalEquip": false,
  "showExterior": false,
  "showInterior": false
}
```

Set `actiondate` = last run time, `enddate` = current time. Store last run
time after each successful call and use it as the next `actiondate`.

**CRITICAL datetime format:** `actiondate` and `enddate` accept full datetime
with time component: `"02/26/2026 10:00:00"`. Date-only strings also work
but miss sub-day changes. Always include time for hourly polling.

### Paging quirk -- maxpages: 0 on small result sets

```python
# WRONG -- will miss single-page results
while page <= data["maxpages"]:  # maxpages=0 exits immediately!

# CORRECT -- treat maxpages <= 1 as a single page
total_pages = max(data.get("maxpages", 1), 1)
while page <= total_pages:
    ...
```

When all results fit in one call, JETNET returns `maxpages: 0` and
`currentpage: 0` -- this is not an error. The `aircraft` array still
contains all records.

### Decoding the responsestatus summary

```python
# "SUCCESS: Ac Count: 12 Comp Count: 28 Cont Count: 24 ..."
status = data["responsestatus"]
# Parse counts if needed:
import re
counts = dict(re.findall(r'(\w[\w ]+\w):\s*(\d+)', status))
# {"Ac Count": "12", "Comp Count": "28", ...}
```

### Flat prefixed relationship schema

`getBulkAircraftExport` uses a unique flat prefixed schema -- every relationship
is embedded directly in the aircraft record with role-based prefixes:

| Prefix | Role |
|--------|------|
| `owr*` | Owner (`owrcompanyname`, `owrfname`, `owrtitle`, `owremail`, `owrphone1`) |
| `opr*` | Operator |
| `chp*` | Chief Pilot |
| `excbrk1*` / `excbrk2*` | Exclusive Brokers |
| `addl1*` / `addl2*` / `addl3*` | Additional relationships |

`forsale` in this endpoint is `"Y"` / `"N"` / `""` -- NOT `"true"`/`"false"`
as in `getAircraftList`.

`datepurchased` is `YYYYMMDD` format -- convert before comparing to other dates.

### Embedded sub-arrays (avoid extra API calls)

Each aircraft record contains embedded arrays controlled by the `show*` flags:

| Flag | Array | Use when |
|------|-------|----------|
| `showMaintenance: true` | `acmaintenance[]` | MRO targeting |
| `showAdditionalEquip: true` | `acaddequipment[]` | Equipment research |
| `showExterior: true` | `acexteriors[]` | Refurb/paint targeting |
| `showInterior: true` | `acinteriors[]` | Interior upgrade targeting |
| Always included | `acevents[]` | Ownership/status change history |
| Always included | `flightdata[]` | Monthly flight hour summary |

Keep all `show*` flags false for hourly polling -- reduces payload size
significantly. Enable only the sub-arrays your pipeline actually processes.

### Hourly polling scheduler (Python skeleton)

```python
import time, datetime

def poll_hourly(bearer, token, maketype="BusinessJet"):
    last_run = datetime.datetime.now() - datetime.timedelta(hours=1)
    while True:
        now = datetime.datetime.now()
        body = {
            "airframetype": "None",
            "maketype": maketype,
            "lifecycle": "InOperation",
            "actiondate": last_run.strftime("%m/%d/%Y %H:%M:%S"),
            "enddate":    now.strftime("%m/%d/%Y %H:%M:%S"),
            "exactMatchReg": False,
            "showHistoricalAcRefs": False,
            "showAwaitingDocsCompanies": False,
            "showMaintenance": False,
            "showAdditionalEquip": False,
            "showExterior": False,
            "showInterior": False,
        }
        changes = get_bulk_export(bearer, token, body, pagesize=100)
        process_changes(changes)    # your pipeline here
        last_run = now
        time.sleep(3600)            # sleep until next hour
```

Known-good example: `examples/bulk-export-hourly.json`

---

## 9. Transaction and Sale History Search

**The business question:** What aircraft in this model segment sold or leased
in a given time window? Who were the buyers, sellers, and brokers? What were
the asking prices and deal terms?

**Primary use cases:** Brokers researching comparable sales ("comps") for a
listing; analysts tracking market velocity; dealers sourcing aircraft that
recently changed hands; CRM teams identifying new owners to approach.

### Find all sales and leases for a model in a date range

```
POST /api/Aircraft/getHistoryListPaged/{apiToken}/{pagesize}/{page}
{
  "make": "",
  "modelid": 0,
  "modlist": [1194],
  "transtype": ["FullSale", "Lease"],
  "startdate": "MM/DD/YYYY",
  "enddate":   "MM/DD/YYYY",
  "isinternaltrans": "No",
  "isnewaircraft": "No",
  "allrelationships": true,
  "aclist": []
}
```

`modlist: [1194]` = Citation CJ3+. Use `getAircraftModelList` or the
`references/id-glossary.md` to find model IDs for other types.

**`transtype` request values are category prefixes, not full strings:**

| Request value | What it matches in response |
|---------------|-----------------------------|
| `"None"` | All transaction types |
| `"FullSale"` | Full Sale - Retail to Retail, Full Sale - Retail to Unidentified, Full Sale - Retail to Leasing Company, etc. |
| `"Lease"` | Lease - Leasing Company to Retail, Lease - Operator to Operator, etc. |
| `"InternalSale"` | Internal/intra-company transfers |
| `"Management"` | Management company changes |
| `"Insurance"` | Insurance claims/write-offs |

**Filter flags (all tristate: `"Yes"` / `"No"` / `"Ignore"`):**
- `isinternaltrans: "No"` -- exclude intra-company transfers for real market deals
- `isnewaircraft: "No"` -- exclude new deliveries (preowned only)
- `ispreownedtrans` -- explicit preowned filter (alternative to `isnewaircraft`)

### Key response fields per transaction record

| Field | What it means |
|-------|--------------|
| `transid` | JETNET transaction ID -- use as join key for deduplication |
| `transtype` | Full descriptive string (e.g., `"Full Sale - Retail to Retail"`) |
| `transdate` | Actual transaction date (ISO timestamp) |
| `actiondate` | When JETNET last updated this record (ISO timestamp) |
| `transretail` | `true` = arm's length transaction -- use for comp analysis |
| `internaltrans` | `false` = not an intra-company transfer |
| `newac` | `"preowned"` or `"new"` |
| `soldprice` | Actual sale price -- often `null` (confidential deals) |
| `askingprice` | Listed asking price -- more often populated than soldprice |
| `listdate` | Date aircraft was first listed for sale |
| `pageurl` | Link to JETNET Evolution web app detail page |
| `description` | Human-readable transaction summary, e.g., `"Sold from X to Y"` |

### companyrelationships in history records

History records use the **nested schema** (same as `getRelationships`):
`company: {}` and `contact: {}` sub-objects. The `relationtype` values
specific to transactions are:

`"Seller"`, `"Purchaser"`, `"Operator"`, `"Seller's Broker"`, `"Purchaser's Broker"`

Pass `allrelationships: true` to get all parties in one call.

### Comp analysis workflow (find comparable sales)

```
1. getHistoryListPaged           --> all transactions matching model + date range
2. Filter: transretail=true      --> arm's length deals only
3. Filter: internaltrans=false   --> exclude internal transfers
4. Extract: askingprice, soldprice, transdate, regnbr, estaftt
5. getRelationships (bulk aclist) --> current owner for each aircraft transacted
```

`soldprice` is null on most deals. For pricing intelligence, use
`askingprice` + `getModelMarketTrends` for published comps.

### maxpages: 0 quirk on small result sets

When results fit in a single response, `maxpages: 0` and `currentpage: 0`
are returned -- this is normal, not an error. `paginate.py` handles this
automatically. Raw callers should use `max(maxpages, 1)` in their loop.

Known-good example: `examples/history-transaction-search.json`
