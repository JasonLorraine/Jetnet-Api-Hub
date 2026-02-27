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

async function bulkExportAllPages(bearerToken, apiToken, body, pageSize = 100) {
  const allAircraft = [];
  let page = 1;

  while (true) {
    const data = await jetnetFetch(
      bearerToken,
      apiToken,
      `/api/Aircraft/getBulkAircraftExportPaged/{apiToken}/${pageSize}/${page}`,
      { method: "POST", body: JSON.stringify(body) }
    );

    const aircraft = data.aircraft || [];
    allAircraft.push(...aircraft);

    const totalPages = Math.max(data.maxpages ?? 1, 1);
    console.log(
      `  Page ${page} of ${totalPages} — ${aircraft.length} records this page`
    );

    if (page >= totalPages) break;
    page++;
  }

  return allAircraft;
}

async function main() {
  const { bearerToken, apiToken } = await login();

  const body = {
    airframetype: "None",
    maketype: "BusinessJet",
    modlist: [145],
    lifecycle: "InOperation",
    actiondate: "",
    enddate: "",
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

  console.log("Bulk exporting G550 aircraft (modelid 145)...\n");

  const aircraft = await bulkExportAllPages(bearerToken, apiToken, body);

  console.log(`\nTotal aircraft exported: ${aircraft.length}\n`);

  for (const ac of aircraft.slice(0, 10)) {
    const forSale = ac.forsale === "Y" ? "For Sale" : "";
    const owner = ac.owrcompanyname || "N/A";
    const operator = ac.oprcompanyname || "N/A";

    console.log(
      `  ${ac.regnbr || "N/A"} | ${ac.make} ${ac.model} | SN: ${ac.serialnbr || "N/A"} | Owner: ${owner} | Operator: ${operator} ${forSale}`
    );
  }

  if (aircraft.length > 10) {
    console.log(`\n  ... and ${aircraft.length - 10} more aircraft.`);
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
