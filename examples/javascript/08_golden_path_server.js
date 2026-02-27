import express from "express";

const app = express();
app.use(express.json());

const BASE = process.env.JETNET_BASE_URL || "https://customer.jetnetconnect.com";
const EMAIL = process.env.JETNET_EMAIL || "";
const PASS = process.env.JETNET_PASSWORD || "";

let bearerToken = null;
let apiToken = null;

async function login() {
  const res = await fetch(`${BASE}/api/Admin/APILogin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emailAddress: EMAIL, password: PASS }),
  });
  const json = await res.json();
  bearerToken = json.bearerToken;
  apiToken = json.apiToken || json.securityToken;
  if (!bearerToken || !apiToken) {
    throw new Error("Login succeeded but tokens not found.");
  }
}

function isJetnetError(json) {
  return (
    json?.responsestatus &&
    String(json.responsestatus).toUpperCase().includes("ERROR")
  );
}

async function jetnetFetch(path, opts = {}, didRetry = false) {
  if (!bearerToken || !apiToken) await login();

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
    if (
      !didRetry &&
      (String(msg).toUpperCase().includes("INVALID SECURITY TOKEN") ||
        res.status === 401)
    ) {
      await login();
      return jetnetFetch(path, opts, true);
    }
    throw new Error(msg);
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

function today() {
  return formatDate(new Date());
}

app.get("/profile/:reg", async (req, res) => {
  try {
    const reg = req.params.reg.toUpperCase();

    const lookup = await jetnetFetch(
      `/api/Aircraft/getRegNumber/${reg}/{apiToken}`,
      { method: "GET" }
    );
    const ac = lookup.aircraftresult;
    if (!ac?.aircraftid) {
      return res.status(404).json({ ok: false, error: "Aircraft not found." });
    }

    const id = ac.aircraftid;

    const [pics, rels, flights] = await Promise.all([
      jetnetFetch(`/api/Aircraft/getPictures/${id}/{apiToken}`, {
        method: "GET",
      }),
      jetnetFetch(`/api/Aircraft/getRelationships/{apiToken}`, {
        method: "POST",
        body: JSON.stringify({
          aircraftid: id,
          aclist: [],
          modlist: [],
          actiondate: "",
          showHistoricalAcRefs: false,
        }),
      }),
      jetnetFetch(`/api/Aircraft/getFlightDataPaged/{apiToken}/100/1`, {
        method: "POST",
        body: JSON.stringify({
          aircraftid: id,
          startdate: daysAgo(180),
          enddate: today(),
          origin: "",
          destination: "",
          aclist: [],
          modlist: [],
          exactMatchReg: true,
        }),
      }),
    ]);

    res.json({
      ok: true,
      data: {
        aircraft: {
          id,
          reg: ac.regnbr,
          make: ac.make,
          model: ac.model,
          year: ac.yearmfr || ac.yeardlv || null,
        },
        base: {
          icao: ac.baseicao || null,
          airport: ac.baseairport || null,
        },
        photos: (pics.pictures || []).map((p) => ({
          description: p.description,
          date: p.imagedate,
          url: p.pictureurl,
        })),
        relationships: (rels.relationships || []).map((r) => ({
          type: r.relationtype,
          company: r.name,
          companyId: r.companyid,
        })),
        flights: (flights.flightdata || []).slice(0, 20),
      },
    });
  } catch (err) {
    res.status(500).json({ ok: false, error: String(err.message || err) });
  }
});

app.get("/health", (_req, res) => {
  res.json({ ok: true, status: "running" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`JETNET Golden Path server running on :${PORT}`);
});
