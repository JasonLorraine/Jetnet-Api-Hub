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

async function main() {
  const { bearerToken, apiToken } = await login();

  const tail = process.argv[2] || "N650GD";
  console.log(`Looking up tail: ${tail}\n`);

  const data = await jetnetFetch(
    bearerToken,
    apiToken,
    `/api/Aircraft/getRegNumber/${tail.toUpperCase()}/{apiToken}`,
    { method: "GET" }
  );

  const ac = data.aircraftresult;
  if (!ac || !ac.aircraftid) {
    console.log("Aircraft not found.");
    return;
  }

  console.log("Aircraft Details:");
  console.log(`  Aircraft ID : ${ac.aircraftid}`);
  console.log(`  Registration: ${ac.regnbr}`);
  console.log(`  Make        : ${ac.make}`);
  console.log(`  Model       : ${ac.model}`);
  console.log(`  Serial      : ${ac.serialnbr}`);
  console.log(`  Year Mfr    : ${ac.yearmfr}`);
  console.log(`  Base ICAO   : ${ac.baseicao || "N/A"}`);
  console.log(`  Base Airport: ${ac.baseairport || "N/A"}`);
  console.log(`  For Sale    : ${ac.forsale || "N/A"}`);

  const rels = ac.companyrelationships || [];
  if (rels.length > 0) {
    console.log("\nRelationships (flat schema from getRegNumber):");
    for (const r of rels) {
      console.log(
        `  ${r.companyrelation}: ${r.companyname} — ${r.contactfirstname || ""} ${r.contactlastname || ""} (${r.contacttitle || "N/A"})`
      );
    }
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
