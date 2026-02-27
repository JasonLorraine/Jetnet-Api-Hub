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

function monthsAgo(n) {
  const d = new Date();
  d.setMonth(d.getMonth() - n);
  return formatDate(d);
}

async function main() {
  const { bearerToken, apiToken } = await login();

  const modlist = [145];
  const displayRange = 24;

  console.log("Fetching model market trends for G550 (modelid 145)...");
  console.log(`Display range: ${displayRange} months\n`);

  const body = {
    modlist: modlist,
    displayRange: displayRange,
    startdate: monthsAgo(displayRange),
    productcode: ["None"],
  };

  const data = await jetnetFetch(
    bearerToken,
    apiToken,
    `/api/Model/getModelMarketTrends/{apiToken}`,
    { method: "POST", body: JSON.stringify(body) }
  );

  console.log(`Response status: ${data.responsestatus}\n`);

  const trends = data.modelmarkettrends || data.trends || [];

  if (Array.isArray(trends) && trends.length > 0) {
    console.log("Monthly Market Trends:");
    console.log(
      "  Month | For Sale | Avg Asking | Low Asking | High Asking | Avg Days on Market"
    );
    console.log("  " + "-".repeat(85));

    for (const t of trends.slice(0, 12)) {
      const month = t.month || t.trendmonth || "N/A";
      const forSale =
        t.aircraft_for_sale_count ?? t.forsalecount ?? "N/A";
      const avgAsking =
        t.avg_asking_price ?? t.avgaskingprice ?? "N/A";
      const lowAsking =
        t.low_asking_price ?? t.lowaskingprice ?? "N/A";
      const highAsking =
        t.high_asking_price ?? t.highaskingprice ?? "N/A";
      const avgDays =
        t.avg_daysonmarket ?? t.avgdaysonmarket ?? "N/A";

      console.log(
        `  ${String(month).padEnd(7)} | ${String(forSale).padEnd(8)} | ${String(avgAsking).padEnd(10)} | ${String(lowAsking).padEnd(10)} | ${String(highAsking).padEnd(11)} | ${avgDays}`
      );
    }

    if (trends.length > 12) {
      console.log(`\n  ... and ${trends.length - 12} more months.`);
    }
  } else {
    console.log("Raw response keys:", Object.keys(data));
    console.log(
      "No trend data found. Check modlist and date range parameters."
    );
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
