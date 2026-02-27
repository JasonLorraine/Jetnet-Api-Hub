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

async function getSingleAircraftRelationships(
  bearerToken,
  apiToken,
  aircraftId
) {
  console.log(
    `\n--- Single Aircraft Relationships (aircraftid: ${aircraftId}) ---`
  );

  const body = {
    aircraftid: aircraftId,
    aclist: [],
    modlist: [],
    actiondate: "",
    showHistoricalAcRefs: false,
  };

  const data = await jetnetFetch(
    bearerToken,
    apiToken,
    `/api/Aircraft/getRelationships/{apiToken}`,
    { method: "POST", body: JSON.stringify(body) }
  );

  const rels = data.relationships || [];
  console.log(
    `Aircraft count: ${data.aircraftcount}, Relationship records: ${data.count}`
  );

  for (const r of rels) {
    console.log(
      `  ${r.relationtype}: ${r.name} (companyid: ${r.companyid || "N/A"}) — ${r.regnbr}`
    );
  }

  return rels;
}

async function getBulkRelationships(bearerToken, apiToken, aircraftIds) {
  console.log(
    `\n--- Bulk Relationships (${aircraftIds.length} aircraft) ---`
  );

  const body = {
    aclist: aircraftIds,
    modlist: [],
    actiondate: "",
    showHistoricalAcRefs: false,
  };

  const data = await jetnetFetch(
    bearerToken,
    apiToken,
    `/api/Aircraft/getRelationships/{apiToken}`,
    { method: "POST", body: JSON.stringify(body) }
  );

  const rels = data.relationships || [];
  console.log(
    `Aircraft count: ${data.aircraftcount}, Relationship records: ${data.count}`
  );

  const grouped = {};
  for (const r of rels) {
    if (!grouped[r.aircraftid]) grouped[r.aircraftid] = [];
    grouped[r.aircraftid].push(r);
  }

  for (const [acId, acRels] of Object.entries(grouped)) {
    const reg = acRels[0]?.regnbr || "N/A";
    console.log(`\n  Aircraft ${acId} (${reg}):`);
    for (const r of acRels) {
      console.log(`    ${r.relationtype}: ${r.name}`);
    }
  }

  return rels;
}

async function main() {
  const { bearerToken, apiToken } = await login();

  await getSingleAircraftRelationships(bearerToken, apiToken, 211461);

  await getBulkRelationships(bearerToken, apiToken, [7103, 8542, 11200]);
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
