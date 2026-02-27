const BASE = process.env.JETNET_BASE_URL || "https://customer.jetnetconnect.com";
const EMAIL = process.env.JETNET_EMAIL;
const PASS = process.env.JETNET_PASSWORD;

if (!EMAIL || !PASS) {
  console.error("Set JETNET_EMAIL and JETNET_PASSWORD environment variables.");
  process.exit(1);
}

async function login() {
  const res = await fetch(`${BASE}/api/Admin/APILogin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emailAddress: EMAIL, password: PASS }),
  });
  if (!res.ok) throw new Error(`Login failed: HTTP ${res.status}`);
  const data = await res.json();
  return {
    bearerToken: data.bearerToken,
    apiToken: data.apiToken || data.securityToken,
  };
}

function isJetnetError(json) {
  return (
    json?.responsestatus &&
    String(json.responsestatus).toUpperCase().includes("ERROR")
  );
}

async function jetnetFetch(bearerToken, apiToken, path, opts = {}) {
  const url = `${BASE}${path}`.replaceAll("{apiToken}", apiToken);
  const res = await fetch(url, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${bearerToken}`,
      ...(opts.headers || {}),
    },
  });
  const json = await res.json();
  if (!res.ok || isJetnetError(json)) {
    throw new Error(
      isJetnetError(json) ? json.responsestatus : `HTTP ${res.status}`
    );
  }
  return json;
}

function formatDate(date) {
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  const yyyy = date.getFullYear();
  return `${mm}/${dd}/${yyyy}`;
}

function daysAgo(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return formatDate(d);
}

const LIST_KEYS = new Set([
  "history",
  "flightdata",
  "events",
  "aircraft",
  "aircraftowneroperators",
  "companylist",
  "contactlist",
  "relationships",
  "aircraftcompfractionalrefs",
]);

async function getAllPages(
  bearerToken,
  apiToken,
  pagedPath,
  body,
  pageSize = 100
) {
  const results = [];
  let page = 1;

  while (true) {
    const data = await jetnetFetch(
      bearerToken,
      apiToken,
      `${pagedPath}/${pageSize}/${page}`,
      { method: "POST", body: JSON.stringify(body) }
    );

    for (const [key, value] of Object.entries(data)) {
      if (Array.isArray(value) && LIST_KEYS.has(key)) {
        results.push(...value);
        break;
      }
    }

    const maxPages = data.maxpages || 1;
    console.log(`  Page ${page} of ${maxPages} — ${data.count || 0} records`);

    if (page >= maxPages) break;
    page++;
  }

  return results;
}

async function main() {
  const { bearerToken, apiToken } = await login();

  const aircraftId = 211461;
  const startDate = daysAgo(180);
  const endDate = formatDate(new Date());

  console.log(`Fetching flight data for aircraft ${aircraftId}`);
  console.log(`Date range: ${startDate} to ${endDate}\n`);

  const body = {
    aircraftid: aircraftId,
    startdate: startDate,
    enddate: endDate,
    origin: "",
    destination: "",
    aclist: [],
    modlist: [],
    exactMatchReg: true,
  };

  const flights = await getAllPages(
    bearerToken,
    apiToken,
    `/api/Aircraft/getFlightDataPaged/{apiToken}`,
    body
  );

  console.log(`\nTotal flight records: ${flights.length}\n`);

  for (const f of flights.slice(0, 15)) {
    console.log(
      `  ${f.flightdate || "N/A"} | ${f.origin || "?"} → ${f.destination || "?"} | ${f.flightminutes || "N/A"} min`
    );
  }

  if (flights.length > 15) {
    console.log(`\n  ... and ${flights.length - 15} more flights.`);
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
