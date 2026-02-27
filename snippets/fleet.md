# Fleet Search Snippets

Quick copy-paste snippets for fleet search operations: finding aircraft by model, for-sale inventory, bulk export, and model list lookups.

---

## Search For-Sale Business Jets by Model

Find all for-sale aircraft for specific models (e.g., G550 and G600).

**Endpoint:** `POST /api/Aircraft/getAircraftList/{apiToken}`
**Response key:** `aircraft`

### Python

```python
body = {
    "maketype": "BusinessJet",
    "modlist": [145, 634],
    "forsale": "true",
    "lifecycle": "InOperation",
    "aclist": []
}

data = api("POST", f"/api/Aircraft/getAircraftList/{token}", bearer, token, body)
for ac in data["aircraft"]:
    print(f"{ac['regnbr']}  {ac['make']} {ac['model']}  asking: {ac.get('askingprice', 'N/A')}")
```

### JavaScript

```javascript
const body = {
  maketype: "BusinessJet",
  modlist: [145, 634],
  forsale: "true",
  lifecycle: "InOperation",
  aclist: [],
};

const data = await api("POST", `/api/Aircraft/getAircraftList/${token}`, bearer, body);
for (const ac of data.aircraft) {
  console.log(`${ac.regnbr}  ${ac.make} ${ac.model}  asking: ${ac.askingprice ?? "N/A"}`);
}
```

**Common gotchas:**
- `forsale` is a string: `"true"`, `"false"`, or `""` (any)
- `getAircraftList` has **no paged variant** -- use filters to control result size
- `modlist: []` means no model filter (returns all models)

---

## Search by Geography

Find all jets based in specific states.

**Endpoint:** `POST /api/Aircraft/getAircraftList/{apiToken}`
**Response key:** `aircraft`

### Python

```python
body = {
    "airframetype": "FixedWing",
    "maketype": "BusinessJet",
    "lifecycle": "InOperation",
    "basestate": ["TX", "OK", "LA"],
    "basecountry": "US",
    "aclist": [],
    "modlist": []
}

data = api("POST", f"/api/Aircraft/getAircraftList/{token}", bearer, token, body)
print(f"Found {len(data['aircraft'])} aircraft")
```

### JavaScript

```javascript
const body = {
  airframetype: "FixedWing",
  maketype: "BusinessJet",
  lifecycle: "InOperation",
  basestate: ["TX", "OK", "LA"],
  basecountry: "US",
  aclist: [],
  modlist: [],
};

const data = await api("POST", `/api/Aircraft/getAircraftList/${token}`, bearer, body);
console.log(`Found ${data.aircraft.length} aircraft`);
```

---

## Search by Base Airport

Find all jets based at a specific airport (e.g., Scottsdale).

### Python

```python
body = {
    "airframetype": "FixedWing",
    "maketype": "BusinessJet",
    "lifecycle": "InOperation",
    "baseicao": "KSDL",
    "aclist": [],
    "modlist": []
}

data = api("POST", f"/api/Aircraft/getAircraftList/{token}", bearer, token, body)
```

### JavaScript

```javascript
const body = {
  airframetype: "FixedWing",
  maketype: "BusinessJet",
  lifecycle: "InOperation",
  baseicao: "KSDL",
  aclist: [],
  modlist: [],
};

const data = await api("POST", `/api/Aircraft/getAircraftList/${token}`, bearer, body);
```

---

## Bulk Aircraft Export (Paged)

Export full aircraft records with pagination. Essential for data pipelines.

**Endpoint:** `POST /api/Aircraft/getBulkAircraftExportPaged/{apiToken}/{pagesize}/{page}`
**Response key:** `aircraft`

### Python

```python
body = {
    "maketype": "BusinessJet",
    "modlist": [145],
    "lifecycle": "InOperation",
    "actiondate": "",
    "forsale": "",
    "aclist": [],
    "exactMatchReg": False,
    "showHistoricalAcRefs": False,
    "showAwaitingDocsCompanies": False,
    "showMaintenance": False,
    "showAdditionalEquip": False,
    "showExterior": False,
    "showInterior": False
}

all_aircraft = []
page = 1
while True:
    data = api("POST",
               f"/api/Aircraft/getBulkAircraftExportPaged/{token}/100/{page}",
               bearer, token, body)
    all_aircraft.extend(data.get("aircraft", []))
    total_pages = max(data.get("maxpages", 1), 1)
    if page >= total_pages:
        break
    page += 1

print(f"Exported {len(all_aircraft)} aircraft records")
```

### JavaScript

```javascript
const body = {
  maketype: "BusinessJet",
  modlist: [145],
  lifecycle: "InOperation",
  actiondate: "",
  forsale: "",
  aclist: [],
  exactMatchReg: false,
  showHistoricalAcRefs: false,
  showAwaitingDocsCompanies: false,
  showMaintenance: false,
  showAdditionalEquip: false,
  showExterior: false,
  showInterior: false,
};

const allAircraft = [];
let page = 1;
while (true) {
  const data = await api("POST",
    `/api/Aircraft/getBulkAircraftExportPaged/${token}/100/${page}`,
    bearer, body);
  allAircraft.push(...(data.aircraft || []));
  const totalPages = Math.max(data.maxpages ?? 1, 1);
  if (page >= totalPages) break;
  page++;
}

console.log(`Exported ${allAircraft.length} aircraft records`);
```

**Common gotchas:**
- `maxpages` returns `0` when all results fit in one page -- use `max(maxpages, 1)` or you skip all records
- `forsale` in this endpoint is `"Y"` / `"N"` (not `"true"` / `"false"`)
- `datepurchased` is `YYYYMMDD` format (not `MM/DD/YYYY`)
- Flat prefixed relationship schema: `owr*` = Owner, `opr*` = Operator, `chp*` = Chief Pilot

---

## Get Aircraft Model List

Look up model IDs for use in `modlist` filters.

**Endpoint:** `POST /api/Model/getAircraftModelList/{apiToken}`
**Response key:** `models`

### Python

```python
body = {
    "airframetype": "FixedWing",
    "maketype": "BusinessJet",
    "make": ""
}

data = api("POST", f"/api/Model/getAircraftModelList/{token}", bearer, token, body)
for m in data["models"]:
    print(f"ID: {m['modelid']}  {m['make']} {m['model']}")
```

### JavaScript

```javascript
const body = {
  airframetype: "FixedWing",
  maketype: "BusinessJet",
  make: "",
};

const data = await api("POST", `/api/Model/getAircraftModelList/${token}`, bearer, body);
for (const m of data.models) {
  console.log(`ID: ${m.modelid}  ${m.make} ${m.model}`);
}
```

**Common gotchas:**
- Make names are all-caps: `"GULFSTREAM"`, `"BOMBARDIER"`, `"DASSAULT"`, `"CESSNA"`
- Use `modelid` values in the `modlist` array for all other endpoints
