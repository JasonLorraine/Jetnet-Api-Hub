# Valuation Snippets

Quick copy-paste snippets for valuation workflows: model market trends, comparable sales via transaction history, and price trend analysis.

---

## Model Market Trends

Get monthly for-sale count, asking prices, and days-on-market for a model over time.

**Endpoint:** `POST /api/Model/getModelMarketTrends/{apiToken}`
**Response key:** `modelMarketTrends`

### Python

```python
from datetime import datetime
from dateutil.relativedelta import relativedelta

start = (datetime.now() - relativedelta(months=24)).strftime("%m/%d/%Y")

body = {
    "modlist": [145],
    "displayRange": 24,
    "startdate": start,
    "productcode": ["None"]
}

data = api("POST", f"/api/Model/getModelMarketTrends/{token}", bearer, token, body)
for t in data["modelMarketTrends"]:
    print(f"{t.get('month', '')}  "
          f"For sale: {t.get('aircraft_for_sale_count', 0)}  "
          f"Avg asking: ${t.get('avg_asking_price', 0):,.0f}  "
          f"Days on market: {t.get('avg_daysonmarket', 0)}")
```

### JavaScript

```javascript
const now = new Date();
const start = new Date(now.getFullYear(), now.getMonth() - 24, 1);
const startStr = `${String(start.getMonth() + 1).padStart(2, "0")}/${String(start.getDate()).padStart(2, "0")}/${start.getFullYear()}`;

const body = {
  modlist: [145],
  displayRange: 24,
  startdate: startStr,
  productcode: ["None"],
};

const data = await api("POST", `/api/Model/getModelMarketTrends/${token}`, bearer, body);
for (const t of data.modelMarketTrends) {
  console.log(`${t.month ?? ""}  ` +
    `For sale: ${t.aircraft_for_sale_count ?? 0}  ` +
    `Avg asking: $${(t.avg_asking_price ?? 0).toLocaleString()}  ` +
    `Days on market: ${t.avg_daysonmarket ?? 0}`);
}
```

**Common gotchas:**
- `displayRange` is in months (e.g., `24` for 2 years)
- `productcode: ["None"]` means no product code filter
- Key fields: `avg_asking_price`, `low_asking_price`, `high_asking_price`, `avg_daysonmarket`, `aircraft_for_sale_count`, `in_operation_count`

---

## Compare Multiple Models

Compare market trends across competing models side by side.

### Python

```python
body = {
    "modlist": [145, 634, 33],
    "displayRange": 36,
    "startdate": start_36_months_ago,
    "productcode": ["None"]
}

data = api("POST", f"/api/Model/getModelMarketTrends/{token}", bearer, token, body)

from collections import defaultdict
by_model = defaultdict(list)
for t in data["modelMarketTrends"]:
    by_model[t.get("modelid")].append(t)

for model_id, trend_data in by_model.items():
    latest = trend_data[-1] if trend_data else {}
    print(f"Model {model_id}: "
          f"For sale: {latest.get('aircraft_for_sale_count', 0)}, "
          f"Avg asking: ${latest.get('avg_asking_price', 0):,.0f}, "
          f"Avg DOM: {latest.get('avg_daysonmarket', 0)}")
```

### JavaScript

```javascript
const body = {
  modlist: [145, 634, 33],
  displayRange: 36,
  startdate: start36MonthsAgo,
  productcode: ["None"],
};

const data = await api("POST", `/api/Model/getModelMarketTrends/${token}`, bearer, body);

const byModel = {};
for (const t of data.modelMarketTrends) {
  const mid = t.modelid;
  if (!byModel[mid]) byModel[mid] = [];
  byModel[mid].push(t);
}

for (const [modelId, trendData] of Object.entries(byModel)) {
  const latest = trendData[trendData.length - 1] ?? {};
  console.log(`Model ${modelId}: ` +
    `For sale: ${latest.aircraft_for_sale_count ?? 0}, ` +
    `Avg asking: $${(latest.avg_asking_price ?? 0).toLocaleString()}, ` +
    `Avg DOM: ${latest.avg_daysonmarket ?? 0}`);
}
```

---

## Comparable Sales (Transaction History)

Find recent preowned sales of the same model for valuation comps.

**Endpoint:** `POST /api/Aircraft/getHistoryListPaged/{apiToken}/{pagesize}/{page}`
**Response key:** `history`

### Python

```python
body = {
    "modlist": [145],
    "transtype": ["FullSale"],
    "startdate": "01/01/2023",
    "enddate": "12/31/2024",
    "ispreownedtrans": "Yes",
    "isinternaltrans": "No",
    "allrelationships": True,
    "aclist": []
}

comps = []
page = 1
while True:
    data = api("POST",
               f"/api/Aircraft/getHistoryListPaged/{token}/100/{page}",
               bearer, token, body)
    comps.extend(data.get("history", []))
    if page >= data.get("maxpages", 1):
        break
    page += 1

retail_comps = [c for c in comps if c.get("transretail")]
for c in retail_comps:
    print(f"{c.get('regnbr', '')}  {c.get('transdate', '')}  "
          f"Asking: ${c.get('askingprice', 'N/A')}  "
          f"Sold: ${c.get('soldprice', 'N/A')}")
```

### JavaScript

```javascript
const body = {
  modlist: [145],
  transtype: ["FullSale"],
  startdate: "01/01/2023",
  enddate: "12/31/2024",
  ispreownedtrans: "Yes",
  isinternaltrans: "No",
  allrelationships: true,
  aclist: [],
};

const comps = [];
let page = 1;
while (true) {
  const data = await api("POST",
    `/api/Aircraft/getHistoryListPaged/${token}/100/${page}`,
    bearer, body);
  comps.push(...(data.history || []));
  if (page >= (data.maxpages ?? 1)) break;
  page++;
}

const retailComps = comps.filter((c) => c.transretail);
for (const c of retailComps) {
  console.log(`${c.regnbr ?? ""}  ${c.transdate ?? ""}  ` +
    `Asking: $${c.askingprice ?? "N/A"}  ` +
    `Sold: $${c.soldprice ?? "N/A"}`);
}
```

**Common gotchas:**
- `transtype` in the request uses category prefixes: `"FullSale"`, `"Lease"` -- not the full response string
- `transtype: ["None"]` returns all transaction types
- `isinternaltrans: "No"` excludes intra-company transfers for real market deals
- `ispreownedtrans: "Yes"` filters to preowned-only transactions
- Filter `transretail: true` for arm's length transactions suitable for comps
- `soldprice` is often `null` (confidential) -- `askingprice` is more frequently populated

---

## Single Aircraft Transaction History

Get full ownership and transaction chain for a specific asset.

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

history = []
page = 1
while True:
    data = api("POST",
               f"/api/Aircraft/getHistoryListPaged/{token}/100/{page}",
               bearer, token, body)
    history.extend(data.get("history", []))
    if page >= data.get("maxpages", 1):
        break
    page += 1

for h in history:
    print(f"{h.get('transdate', '')}  {h.get('transtype', '')}")
    print(f"  Asking: {h.get('askingprice', 'N/A')}  Sold: {h.get('soldprice', 'N/A')}")
    for cr in h.get("companyrelationships", []):
        print(f"  {cr.get('relationtype', '')}: {cr.get('company', {}).get('name', '')}")
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

const history = [];
let page = 1;
while (true) {
  const data = await api("POST",
    `/api/Aircraft/getHistoryListPaged/${token}/100/${page}`,
    bearer, body);
  history.push(...(data.history || []));
  if (page >= (data.maxpages ?? 1)) break;
  page++;
}

for (const h of history) {
  console.log(`${h.transdate ?? ""}  ${h.transtype ?? ""}`);
  console.log(`  Asking: ${h.askingprice ?? "N/A"}  Sold: ${h.soldprice ?? "N/A"}`);
  for (const cr of h.companyrelationships ?? []) {
    console.log(`  ${cr.relationtype ?? ""}: ${cr.company?.name ?? ""}`);
  }
}
```

---

## Price Trend Analysis

Calculate price depreciation rate from market trend data.

### Python

```python
body = {
    "modlist": [145],
    "displayRange": 60,
    "startdate": start_60_months_ago,
    "productcode": ["None"]
}

data = api("POST", f"/api/Model/getModelMarketTrends/{token}", bearer, token, body)
trends = data["modelMarketTrends"]

if len(trends) >= 2:
    first = trends[0]
    last = trends[-1]
    start_price = first.get("avg_asking_price", 0)
    end_price = last.get("avg_asking_price", 0)

    if start_price > 0:
        total_change_pct = ((end_price - start_price) / start_price) * 100
        monthly_change_pct = total_change_pct / len(trends)
        annual_change_pct = monthly_change_pct * 12

        print(f"Period: {first.get('month', '')} to {last.get('month', '')}")
        print(f"Start avg asking: ${start_price:,.0f}")
        print(f"End avg asking: ${end_price:,.0f}")
        print(f"Total change: {total_change_pct:+.1f}%")
        print(f"Annual rate: {annual_change_pct:+.1f}%")
```

### JavaScript

```javascript
const body = {
  modlist: [145],
  displayRange: 60,
  startdate: start60MonthsAgo,
  productcode: ["None"],
};

const data = await api("POST", `/api/Model/getModelMarketTrends/${token}`, bearer, body);
const trends = data.modelMarketTrends;

if (trends.length >= 2) {
  const first = trends[0];
  const last = trends[trends.length - 1];
  const startPrice = first.avg_asking_price ?? 0;
  const endPrice = last.avg_asking_price ?? 0;

  if (startPrice > 0) {
    const totalChangePct = ((endPrice - startPrice) / startPrice) * 100;
    const monthlyChangePct = totalChangePct / trends.length;
    const annualChangePct = monthlyChangePct * 12;

    console.log(`Period: ${first.month ?? ""} to ${last.month ?? ""}`);
    console.log(`Start avg asking: $${startPrice.toLocaleString()}`);
    console.log(`End avg asking: $${endPrice.toLocaleString()}`);
    console.log(`Total change: ${totalChangePct > 0 ? "+" : ""}${totalChangePct.toFixed(1)}%`);
    console.log(`Annual rate: ${annualChangePct > 0 ? "+" : ""}${annualChangePct.toFixed(1)}%`);
  }
}
```

**Common gotchas:**
- 60 months of data gives the best long-term trend context for finance/investment use cases
- Rising `avg_daysonmarket` = weakening demand signal
- Falling `aircraft_for_sale_count` with stable prices = tightening supply
- Use `low_asking_price` and `high_asking_price` along with `avg_asking_price` for range context
