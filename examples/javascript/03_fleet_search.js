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

  const body = {
    maketype: "BusinessJet",
    modlist: [145, 634],
    forsale: "true",
    lifecycle: "InOperation",
    aclist: [],
  };

  console.log("Searching for-sale business jets (G550, G600)...\n");

  const data = await jetnetFetch(
    bearerToken,
    apiToken,
    `/api/Aircraft/getAircraftList/{apiToken}`,
    { method: "POST", body: JSON.stringify(body) }
  );

  console.log(`Response status: ${data.responsestatus}`);

  const aircraft = data.aircraft || [];
  console.log(`Found ${aircraft.length} aircraft for sale.\n`);

  for (const ac of aircraft.slice(0, 10)) {
    const price = ac.askingprice || ac.asking || "N/A";
    console.log(
      `  ${ac.regnbr || "N/A"} | ${ac.make} ${ac.model} | Year: ${ac.yearmfr || "N/A"} | Base: ${ac.baseicao || "N/A"} | Asking: ${price}`
    );
  }

  if (aircraft.length > 10) {
    console.log(`\n  ... and ${aircraft.length - 10} more.`);
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
