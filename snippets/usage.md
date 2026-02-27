# Usage / Flight Data Snippets

Quick copy-paste snippets for flight activity data: querying by aircraft, by airport, date ranges, and flight summary aggregation.

---

## Flight Data by Aircraft

Get flight records for a specific aircraft in a date range.

**Endpoint:** `POST /api/Aircraft/getFlightDataPaged/{apiToken}/{pagesize}/{page}`
**Response key:** `flightdata`

### Python

```python
body = {
    "aircraftid": 211461,
    "startdate": "01/01/2024",
    "enddate": "12/31/2024",
    "aclist": [],
    "modlist": []
}

all_flights = []
page = 1
while True:
    data = api("POST",
               f"/api/Aircraft/getFlightDataPaged/{token}/100/{page}",
               bearer, token, body)
    all_flights.extend(data.get("flightdata", []))
    if page >= data.get("maxpages", 1):
        break
    page += 1

print(f"Total flight records: {len(all_flights)}")
for f in all_flights[:5]:
    print(f"{f.get('flightdate', '')}  {f.get('origin', '')} -> {f.get('destination', '')}  {f.get('flighthours', 0)}h")
```

### JavaScript

```javascript
const body = {
  aircraftid: 211461,
  startdate: "01/01/2024",
  enddate: "12/31/2024",
  aclist: [],
  modlist: [],
};

const allFlights = [];
let page = 1;
while (true) {
  const data = await api("POST",
    `/api/Aircraft/getFlightDataPaged/${token}/100/${page}`,
    bearer, body);
  allFlights.push(...(data.flightdata || []));
  if (page >= (data.maxpages ?? 1)) break;
  page++;
}

console.log(`Total flight records: ${allFlights.length}`);
for (const f of allFlights.slice(0, 5)) {
  console.log(`${f.flightdate ?? ""}  ${f.origin ?? ""} -> ${f.destination ?? ""}  ${f.flighthours ?? 0}h`);
}
```

**Common gotchas:**
- Date format: `MM/DD/YYYY` with leading zeros
- `page` is 1-based (first page = 1, not 0)
- Loop until `page >= data["maxpages"]`

---

## Flight Data by Airport (Origin)

Find all departures from a specific airport.

### Python

```python
body = {
    "origin": "KDAL",
    "destination": "",
    "startdate": "10/01/2024",
    "enddate": "12/31/2024",
    "aclist": [],
    "modlist": []
}

all_flights = []
page = 1
while True:
    data = api("POST",
               f"/api/Aircraft/getFlightDataPaged/{token}/100/{page}",
               bearer, token, body)
    all_flights.extend(data.get("flightdata", []))
    if page >= data.get("maxpages", 1):
        break
    page += 1

print(f"Departures from KDAL: {len(all_flights)}")
```

### JavaScript

```javascript
const body = {
  origin: "KDAL",
  destination: "",
  startdate: "10/01/2024",
  enddate: "12/31/2024",
  aclist: [],
  modlist: [],
};

const allFlights = [];
let page = 1;
while (true) {
  const data = await api("POST",
    `/api/Aircraft/getFlightDataPaged/${token}/100/${page}`,
    bearer, body);
  allFlights.push(...(data.flightdata || []));
  if (page >= (data.maxpages ?? 1)) break;
  page++;
}

console.log(`Departures from KDAL: ${allFlights.length}`);
```

---

## Flight Data by Airport (Destination)

Find all arrivals to a specific airport. Swap `origin` and `destination`.

### Python

```python
body = {
    "origin": "",
    "destination": "KTEB",
    "startdate": "10/01/2024",
    "enddate": "12/31/2024",
    "aclist": [],
    "modlist": []
}
```

### JavaScript

```javascript
const body = {
  origin: "",
  destination: "KTEB",
  startdate: "10/01/2024",
  enddate: "12/31/2024",
  aclist: [],
  modlist: [],
};
```

---

## Flight Data by Model Type

Get all flight data for a specific aircraft model.

### Python

```python
body = {
    "modlist": [145],
    "startdate": "01/01/2024",
    "enddate": "06/30/2024",
    "aclist": []
}

all_flights = []
page = 1
while True:
    data = api("POST",
               f"/api/Aircraft/getFlightDataPaged/{token}/100/{page}",
               bearer, token, body)
    all_flights.extend(data.get("flightdata", []))
    if page >= data.get("maxpages", 1):
        break
    page += 1
```

### JavaScript

```javascript
const body = {
  modlist: [145],
  startdate: "01/01/2024",
  enddate: "06/30/2024",
  aclist: [],
};

const allFlights = [];
let page = 1;
while (true) {
  const data = await api("POST",
    `/api/Aircraft/getFlightDataPaged/${token}/100/${page}`,
    bearer, body);
  allFlights.push(...(data.flightdata || []));
  if (page >= (data.maxpages ?? 1)) break;
  page++;
}
```

---

## Flight Summary Aggregation

Aggregate flight records to calculate utilization metrics.

### Python

```python
from collections import defaultdict

by_aircraft = defaultdict(lambda: {"legs": 0, "hours": 0.0})

for f in all_flights:
    acid = f["aircraftid"]
    by_aircraft[acid]["legs"] += 1
    by_aircraft[acid]["hours"] += f.get("flighthours", 0)

top_10 = sorted(by_aircraft.items(), key=lambda x: x[1]["hours"], reverse=True)[:10]
for acid, stats in top_10:
    print(f"Aircraft {acid}: {stats['legs']} legs, {stats['hours']:.1f} hours")
```

### JavaScript

```javascript
const byAircraft = {};

for (const f of allFlights) {
  const acid = f.aircraftid;
  if (!byAircraft[acid]) byAircraft[acid] = { legs: 0, hours: 0 };
  byAircraft[acid].legs++;
  byAircraft[acid].hours += f.flighthours ?? 0;
}

const top10 = Object.entries(byAircraft)
  .sort(([, a], [, b]) => b.hours - a.hours)
  .slice(0, 10);

for (const [acid, stats] of top10) {
  console.log(`Aircraft ${acid}: ${stats.legs} legs, ${stats.hours.toFixed(1)} hours`);
}
```

---

## Operator Activity at an Airport

Combine flight data with relationships to identify the most active operators at your airport.

### Python

```python
from collections import Counter

departures = []
page = 1
body = {
    "origin": "KSDL",
    "destination": "",
    "startdate": "07/01/2024",
    "enddate": "12/31/2024",
    "aclist": [],
    "modlist": []
}

while True:
    data = api("POST",
               f"/api/Aircraft/getFlightDataPaged/{token}/100/{page}",
               bearer, token, body)
    departures.extend(data.get("flightdata", []))
    if page >= data.get("maxpages", 1):
        break
    page += 1

leg_counts = Counter(f["aircraftid"] for f in departures)
top_aircraft_ids = [acid for acid, _ in leg_counts.most_common(20)]

rel_body = {
    "aclist": top_aircraft_ids,
    "modlist": [],
    "actiondate": "",
    "showHistoricalAcRefs": False
}
rel_data = api("POST", f"/api/Aircraft/getRelationships/{token}", bearer, token, rel_body)

for rel in rel_data["relationships"]:
    if rel["relationtype"] == "Operator":
        acid = rel["aircraftid"]
        print(f"{rel['regnbr']} ({leg_counts[acid]} legs): Operator = {rel['name']}")
```

### JavaScript

```javascript
const departures = [];
let page = 1;
const body = {
  origin: "KSDL",
  destination: "",
  startdate: "07/01/2024",
  enddate: "12/31/2024",
  aclist: [],
  modlist: [],
};

while (true) {
  const data = await api("POST",
    `/api/Aircraft/getFlightDataPaged/${token}/100/${page}`,
    bearer, body);
  departures.push(...(data.flightdata || []));
  if (page >= (data.maxpages ?? 1)) break;
  page++;
}

const legCounts = {};
for (const f of departures) {
  legCounts[f.aircraftid] = (legCounts[f.aircraftid] || 0) + 1;
}
const topIds = Object.entries(legCounts)
  .sort(([, a], [, b]) => b - a)
  .slice(0, 20)
  .map(([id]) => Number(id));

const relData = await api("POST",
  `/api/Aircraft/getRelationships/${token}`, bearer, {
    aclist: topIds,
    modlist: [],
    actiondate: "",
    showHistoricalAcRefs: false,
  });

for (const rel of relData.relationships) {
  if (rel.relationtype === "Operator") {
    console.log(`${rel.regnbr} (${legCounts[rel.aircraftid]} legs): Operator = ${rel.name}`);
  }
}
```

**Common gotchas:**
- Airport codes are ICAO format (4 letters): `"KDAL"`, `"KTEB"`, not `"DAL"`, `"TEB"`
- Use `origin` for departures, `destination` for arrivals
- Non-paged `getFlightData` will time out on large datasets -- always use the paged variant
