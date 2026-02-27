# Ownership Snippets

Quick copy-paste snippets for ownership lookups: relationships (single and bulk), ownership history, condensed owner/operators, and parsing `companyrelationships`.

---

## Get Relationships -- Single Aircraft

Look up current owner, operator, and contacts for one aircraft.

**Endpoint:** `POST /api/Aircraft/getRelationships/{apiToken}`
**Response key:** `relationships`

### Python

```python
body = {
    "aircraftid": 211461,
    "aclist": [],
    "modlist": [],
    "actiondate": "",
    "showHistoricalAcRefs": False
}

data = api("POST", f"/api/Aircraft/getRelationships/{token}", bearer, token, body)
for rel in data["relationships"]:
    print(f"{rel['relationtype']}: {rel['name']}  (aircraft: {rel['regnbr']})")
    if rel.get("company"):
        print(f"  Company: {rel['company'].get('name', '')}")
    if rel.get("contact"):
        print(f"  Contact: {rel['contact'].get('firstname', '')} {rel['contact'].get('lastname', '')}")
```

### JavaScript

```javascript
const body = {
  aircraftid: 211461,
  aclist: [],
  modlist: [],
  actiondate: "",
  showHistoricalAcRefs: false,
};

const data = await api("POST", `/api/Aircraft/getRelationships/${token}`, bearer, body);
for (const rel of data.relationships) {
  console.log(`${rel.relationtype}: ${rel.name}  (aircraft: ${rel.regnbr})`);
  if (rel.company) console.log(`  Company: ${rel.company.name ?? ""}`);
  if (rel.contact) console.log(`  Contact: ${rel.contact.firstname ?? ""} ${rel.contact.lastname ?? ""}`);
}
```

**Common gotchas:**
- Uses nested schema: `relationtype`, `company {}`, `contact {}` sub-objects
- Field is `relationtype` (not `companyrelation`)
- `relationtype` values: `"Owner"`, `"Operator"`, `"Seller"`, `"Purchaser"`, `"Seller's Broker"`

---

## Get Relationships -- Bulk (Multiple Aircraft)

Look up relationships for many aircraft in one call.

### Python

```python
body = {
    "aclist": [7103, 8542, 11200],
    "modlist": [],
    "actiondate": "",
    "showHistoricalAcRefs": False
}

data = api("POST", f"/api/Aircraft/getRelationships/{token}", bearer, token, body)
print(f"Aircraft count: {data['aircraftcount']}, Relationship records: {data['count']}")

for rel in data["relationships"]:
    print(f"[{rel['aircraftid']}] {rel['regnbr']} - {rel['relationtype']}: {rel['name']}")
```

### JavaScript

```javascript
const body = {
  aclist: [7103, 8542, 11200],
  modlist: [],
  actiondate: "",
  showHistoricalAcRefs: false,
};

const data = await api("POST", `/api/Aircraft/getRelationships/${token}`, bearer, body);
console.log(`Aircraft count: ${data.aircraftcount}, Relationship records: ${data.count}`);

for (const rel of data.relationships) {
  console.log(`[${rel.aircraftid}] ${rel.regnbr} - ${rel.relationtype}: ${rel.name}`);
}
```

**Common gotchas:**
- When using bulk `aclist`, omit `aircraftid` from the body
- `aircraftcount` = distinct aircraft, `count` = total relationship rows
- Empty `aclist: []` means no filter (not empty results)

---

## Ownership History (Paged)

Get the full ownership chain for an aircraft over time.

**Endpoint:** `POST /api/Aircraft/getHistoryListPaged/{apiToken}/{pagesize}/{page}`
**Response key:** `history`

### Python

```python
body = {
    "aclist": [211461],
    "transtype": ["None"],
    "allrelationships": True,
    "startdate": "01/01/2000",
    "enddate": "12/31/2025",
    "modlist": []
}

all_history = []
page = 1
while True:
    data = api("POST",
               f"/api/Aircraft/getHistoryListPaged/{token}/100/{page}",
               bearer, token, body)
    all_history.extend(data.get("history", []))
    if page >= data.get("maxpages", 1):
        break
    page += 1

for h in all_history:
    print(f"{h['transdate']}  {h['transtype']}  sold: {h.get('soldprice', 'N/A')}")
```

### JavaScript

```javascript
const body = {
  aclist: [211461],
  transtype: ["None"],
  allrelationships: true,
  startdate: "01/01/2000",
  enddate: "12/31/2025",
  modlist: [],
};

const allHistory = [];
let page = 1;
while (true) {
  const data = await api("POST",
    `/api/Aircraft/getHistoryListPaged/${token}/100/${page}`,
    bearer, body);
  allHistory.push(...(data.history || []));
  if (page >= (data.maxpages ?? 1)) break;
  page++;
}

for (const h of allHistory) {
  console.log(`${h.transdate}  ${h.transtype}  sold: ${h.soldprice ?? "N/A"}`);
}
```

**Common gotchas:**
- `transtype: ["None"]` means all transaction types (not `[]`)
- Date format: `MM/DD/YYYY` with leading zeros
- `allrelationships: true` includes Seller, Purchaser, Broker details

---

## Condensed Owner/Operators

Quick snapshot of current owner and operator per aircraft. Useful for portfolio monitoring.

**Endpoint:** `POST /api/Aircraft/getCondensedOwnerOperators/{apiToken}`
**Response key:** `aircraftowneroperators`

### Python

```python
body = {
    "aclist": [7103, 8542, 11200],
    "modlist": []
}

data = api("POST", f"/api/Aircraft/getCondensedOwnerOperators/{token}", bearer, token, body)
for rec in data["aircraftowneroperators"]:
    print(f"{rec['regnbr']}  Owner: {rec.get('comp1name', '')}  Purchased: {rec.get('datepurchased', '')}")
```

### JavaScript

```javascript
const body = {
  aclist: [7103, 8542, 11200],
  modlist: [],
};

const data = await api("POST",
  `/api/Aircraft/getCondensedOwnerOperators/${token}`, bearer, body);
for (const rec of data.aircraftowneroperators) {
  console.log(`${rec.regnbr}  Owner: ${rec.comp1name ?? ""}  Purchased: ${rec.datepurchased ?? ""}`);
}
```

**Common gotchas:**
- Fields use `comp1relation`, `comp1name` naming convention
- Use `actiondate` parameter to pull only records changed since your last snapshot

---

## Parsing companyrelationships -- Schema Differences

The `companyrelationships` structure differs by endpoint. This is the most common source of bugs.

| Endpoint | Schema | Relation field | Example values |
|----------|--------|----------------|----------------|
| `getRegNumber` | Flat prefixed | `companyrelation` | `"Owner"`, `"Operator"`, `"Chief Pilot"` |
| `getRelationships` | Nested objects | `relationtype` | `"Owner"`, `"Operator"`, `"Seller"` |
| `getBulkAircraftExport` | Flat role-prefixed | Field prefix | `owr*`, `opr*`, `chp*` |
| `getAcCompanyFractionalReportPaged` | Flat top-level | `relation` | `"Owner"`, `"Flight Department"` |

### getRegNumber (flat schema)

```python
ac = api("GET", f"/api/Aircraft/getRegNumber/N100XX/{token}", bearer, token)
for rel in ac["aircraftresult"]["companyrelationships"]:
    print(f"{rel['companyrelation']}: {rel['companyname']}")
    print(f"  Contact: {rel.get('contactfirstname', '')} {rel.get('contactlastname', '')}")
```

### getRelationships (nested schema)

```python
for rel in data["relationships"]:
    print(f"{rel['relationtype']}: {rel['name']}")
    company = rel.get("company", {})
    contact = rel.get("contact", {})
```

### getBulkAircraftExport (flat prefixed)

```python
for ac in data["aircraft"]:
    print(f"Owner: {ac.get('owrcompanyname', '')}")
    print(f"Operator: {ac.get('oprcompanyname', '')}")
    print(f"Chief Pilot: {ac.get('chpfname', '')} {ac.get('chplname', '')}")
```
