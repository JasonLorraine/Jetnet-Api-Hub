# Specifications Snippets

Quick copy-paste snippets for aircraft specification data: performance specs, operating costs, full aircraft records, engine details, maintenance, and avionics.

---

## Model Performance Specs

Get range, speed, cabin dimensions, and payload specs for one or more models.

**Endpoint:** `POST /api/Model/getModelPerformanceSpecs/{apiToken}`
**Response key:** `specs`

### Python

```python
body = {
    "modlist": [145, 634],
    "airframetype": "None",
    "maketype": "None",
    "make": "",
    "annualhours": 0,
    "fuelprice": 0
}

data = api("POST", f"/api/Model/getModelPerformanceSpecs/{token}", bearer, token, body)
for spec in data["specs"]:
    print(f"{spec['make']} {spec['model']}")
    print(f"  Range: {spec.get('range_nm', 'N/A')} nm")
    print(f"  Max Speed: {spec.get('max_speed', 'N/A')} ktas")
    print(f"  Cabin Length: {spec.get('cabin_length', 'N/A')}")
    print(f"  Max Pax: {spec.get('max_pax', 'N/A')}")
```

### JavaScript

```javascript
const body = {
  modlist: [145, 634],
  airframetype: "None",
  maketype: "None",
  make: "",
  annualhours: 0,
  fuelprice: 0,
};

const data = await api("POST", `/api/Model/getModelPerformanceSpecs/${token}`, bearer, body);
for (const spec of data.specs) {
  console.log(`${spec.make} ${spec.model}`);
  console.log(`  Range: ${spec.range_nm ?? "N/A"} nm`);
  console.log(`  Max Speed: ${spec.max_speed ?? "N/A"} ktas`);
  console.log(`  Cabin Length: ${spec.cabin_length ?? "N/A"}`);
  console.log(`  Max Pax: ${spec.max_pax ?? "N/A"}`);
}
```

**Common gotchas:**
- Pass `modlist` with specific model IDs -- use `getAircraftModelList` to look them up
- Set `annualhours` and `fuelprice` to `0` if you only need performance data (not costs)

---

## Model Operating Costs

Get annual operating cost estimates for aircraft models.

**Endpoint:** `POST /api/Model/getModelOperationCosts/{apiToken}`
**Response key:** `costs`

### Python

```python
body = {
    "modlist": [145],
    "airframetype": "None",
    "maketype": "None",
    "make": "",
    "annualhours": 400,
    "fuelprice": 6.50
}

data = api("POST", f"/api/Model/getModelOperationCosts/{token}", bearer, token, body)
for cost in data["costs"]:
    print(f"{cost['make']} {cost['model']}")
    print(f"  Variable cost/hr: ${cost.get('variable_cost_per_hour', 'N/A')}")
    print(f"  Fixed cost/yr: ${cost.get('fixed_cost_per_year', 'N/A')}")
    print(f"  Total annual: ${cost.get('total_annual_cost', 'N/A')}")
```

### JavaScript

```javascript
const body = {
  modlist: [145],
  airframetype: "None",
  maketype: "None",
  make: "",
  annualhours: 400,
  fuelprice: 6.50,
};

const data = await api("POST", `/api/Model/getModelOperationCosts/${token}`, bearer, body);
for (const cost of data.costs) {
  console.log(`${cost.make} ${cost.model}`);
  console.log(`  Variable cost/hr: $${cost.variable_cost_per_hour ?? "N/A"}`);
  console.log(`  Fixed cost/yr: $${cost.fixed_cost_per_year ?? "N/A"}`);
  console.log(`  Total annual: $${cost.total_annual_cost ?? "N/A"}`);
}
```

**Common gotchas:**
- `annualhours` affects variable cost calculations -- use a realistic estimate (typically 200-600)
- `fuelprice` is price per gallon in USD

---

## Full Aircraft Record

Get the complete data record for a single aircraft by ID.

**Endpoint:** `GET /api/Aircraft/getAircraft/{id}/{apiToken}`

### Python

```python
data = api("GET", f"/api/Aircraft/getAircraft/211461/{token}", bearer, token)
ac = data
print(f"Tail: {ac.get('regnbr', '')}")
print(f"S/N: {ac.get('serialnbr', '')}")
print(f"Make/Model: {ac.get('make', '')} {ac.get('model', '')}")
print(f"Year: {ac.get('yearmfr', '')}")
print(f"Base: {ac.get('baseicao', '')} ({ac.get('basecity', '')}, {ac.get('basestate', '')})")
print(f"For Sale: {ac.get('forsale', '')}")
print(f"AFTT: {ac.get('aftt', '')}")
```

### JavaScript

```javascript
const data = await api("GET", `/api/Aircraft/getAircraft/211461/${token}`, bearer);
console.log(`Tail: ${data.regnbr ?? ""}`);
console.log(`S/N: ${data.serialnbr ?? ""}`);
console.log(`Make/Model: ${data.make ?? ""} ${data.model ?? ""}`);
console.log(`Year: ${data.yearmfr ?? ""}`);
console.log(`Base: ${data.baseicao ?? ""} (${data.basecity ?? ""}, ${data.basestate ?? ""})`);
console.log(`For Sale: ${data.forsale ?? ""}`);
console.log(`AFTT: ${data.aftt ?? ""}`);
```

---

## Engine Details

Get engine information for an aircraft.

**Endpoint:** `GET /api/Aircraft/getEngine/{id}/{apiToken}`

### Python

```python
data = api("GET", f"/api/Aircraft/getEngine/211461/{token}", bearer, token)
engines = data.get("engines", [])
for eng in engines:
    print(f"Engine {eng.get('engineposition', '')}: {eng.get('enginemake', '')} {eng.get('enginemodel', '')}")
    print(f"  S/N: {eng.get('engineserialnbr', '')}")
    print(f"  Total Time: {eng.get('enginetotaltime', '')}")
    print(f"  Cycles: {eng.get('enginecycles', '')}")
```

### JavaScript

```javascript
const data = await api("GET", `/api/Aircraft/getEngine/211461/${token}`, bearer);
for (const eng of data.engines ?? []) {
  console.log(`Engine ${eng.engineposition ?? ""}: ${eng.enginemake ?? ""} ${eng.enginemodel ?? ""}`);
  console.log(`  S/N: ${eng.engineserialnbr ?? ""}`);
  console.log(`  Total Time: ${eng.enginetotaltime ?? ""}`);
  console.log(`  Cycles: ${eng.enginecycles ?? ""}`);
}
```

---

## Maintenance Records

Get maintenance tracking data for an aircraft.

**Endpoint:** `GET /api/Aircraft/getMaintenance/{id}/{apiToken}`

### Python

```python
data = api("GET", f"/api/Aircraft/getMaintenance/211461/{token}", bearer, token)
maint = data.get("maintenance", [])
for m in maint:
    print(f"{m.get('inspectiontype', '')}: Due {m.get('duedate', '')} at {m.get('duehours', '')}h")
    print(f"  Last done: {m.get('lastdonedate', '')} at {m.get('lastdonehours', '')}h")
```

### JavaScript

```javascript
const data = await api("GET", `/api/Aircraft/getMaintenance/211461/${token}`, bearer);
for (const m of data.maintenance ?? []) {
  console.log(`${m.inspectiontype ?? ""}: Due ${m.duedate ?? ""} at ${m.duehours ?? ""}h`);
  console.log(`  Last done: ${m.lastdonedate ?? ""} at ${m.lastdonehours ?? ""}h`);
}
```

---

## Avionics

Get avionics equipment list for an aircraft.

**Endpoint:** `GET /api/Aircraft/getAvionics/{id}/{apiToken}`

### Python

```python
data = api("GET", f"/api/Aircraft/getAvionics/211461/{token}", bearer, token)
avionics = data.get("avionics", [])
for av in avionics:
    print(f"{av.get('avionicstype', '')}: {av.get('avionicsmake', '')} {av.get('avionicsmodel', '')}")
```

### JavaScript

```javascript
const data = await api("GET", `/api/Aircraft/getAvionics/211461/${token}`, bearer);
for (const av of data.avionics ?? []) {
  console.log(`${av.avionicstype ?? ""}: ${av.avionicsmake ?? ""} ${av.avionicsmodel ?? ""}`);
}
```

**Common gotchas:**
- All single-aircraft GET endpoints use the aircraft `id` (integer `aircraftid`), not the tail number
- Get the `aircraftid` first via `getRegNumber/{tailnumber}/{apiToken}`
- These are Tier A endpoints -- one aircraft at a time, not for bulk operations
