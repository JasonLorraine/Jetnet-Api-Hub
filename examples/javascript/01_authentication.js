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

  if (!res.ok) {
    throw new Error(`Login failed: HTTP ${res.status}`);
  }

  const data = await res.json();
  const bearerToken = data.bearerToken;
  const apiToken = data.apiToken || data.securityToken;

  if (!bearerToken || !apiToken) {
    throw new Error("Login succeeded but tokens not found in response.");
  }

  return { bearerToken, apiToken };
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

  const text = await res.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    json = { raw: text };
  }

  if (!res.ok || isJetnetError(json)) {
    const msg = isJetnetError(json)
      ? json.responsestatus
      : `HTTP ${res.status}: ${text}`;
    throw new Error(msg);
  }

  return json;
}

async function main() {
  const { bearerToken, apiToken } = await login();
  console.log("Login successful.");
  console.log("Bearer token:", bearerToken.slice(0, 20) + "...");
  console.log("API token:", apiToken);

  const tail = "N123AB";
  const data = await jetnetFetch(
    bearerToken,
    apiToken,
    `/api/Aircraft/getRegNumber/${tail}/{apiToken}`,
    { method: "GET" }
  );

  const ac = data.aircraftresult;
  if (ac) {
    console.log(`\nAircraft found: ${ac.make} ${ac.model} (${ac.regnbr})`);
    console.log(`  Serial: ${ac.serialnbr}`);
    console.log(`  Year: ${ac.yearmfr}`);
    console.log(`  Base: ${ac.baseicao || "N/A"}`);
  } else {
    console.log("No aircraft found for tail:", tail);
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
