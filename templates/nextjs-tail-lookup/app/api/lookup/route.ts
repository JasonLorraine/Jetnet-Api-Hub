import { NextRequest, NextResponse } from "next/server";

const BASE_URL = process.env.JETNET_BASE_URL || "https://customer.jetnetconnect.com";
const EMAIL = process.env.JETNET_EMAIL || "";
const PASSWORD = process.env.JETNET_PASSWORD || "";

let bearerToken: string | null = null;
let apiToken: string | null = null;
let tokenCreatedAt = 0;
const REFRESH_AT_MS = 50 * 60 * 1000;

async function login() {
  const res = await fetch(`${BASE_URL}/api/Admin/APILogin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emailAddress: EMAIL, password: PASSWORD }),
  });

  if (!res.ok) {
    throw new Error(`Login failed: HTTP ${res.status}`);
  }

  const data = await res.json();
  normalizeError(data);

  bearerToken = data.bearerToken;
  apiToken = data.apiToken || data.securityToken;
  tokenCreatedAt = Date.now();

  if (!bearerToken || !apiToken) {
    throw new Error("Login succeeded but tokens not found in response.");
  }
}

function normalizeError(json: Record<string, unknown>) {
  if (!json || typeof json !== "object") return;

  const status = json.responsestatus;
  if (status && String(status).toUpperCase().includes("ERROR")) {
    throw new Error(`JETNET error: ${status}`);
  }

  if (json.type && json.title && json.status) {
    throw new Error(`JETNET RFC error: ${json.status} ${json.title} (${json.type})`);
  }
}

async function ensureSession() {
  if (!bearerToken || !apiToken || Date.now() - tokenCreatedAt > REFRESH_AT_MS) {
    await login();
    return;
  }

  try {
    const url = `${BASE_URL}/api/Utility/getAccountInfo/${apiToken}`;
    const res = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${bearerToken}`,
      },
    });
    const data = await res.json();
    normalizeError(data);
  } catch {
    await login();
  }
}

async function jetnetFetch(path: string, opts: RequestInit = {}, didRetry = false): Promise<Record<string, unknown>> {
  await ensureSession();

  const url = `${BASE_URL}${path}`.replaceAll("{apiToken}", apiToken!);
  const res = await fetch(url, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${bearerToken}`,
      ...(opts.headers || {}),
    },
  });

  const text = await res.text();
  let json: Record<string, unknown>;
  try {
    json = JSON.parse(text);
  } catch {
    json = { raw: text };
  }

  const statusStr = json?.responsestatus ? String(json.responsestatus).toUpperCase() : "";
  const isInvalidToken = res.status === 401 || statusStr.includes("INVALID SECURITY TOKEN");

  if (isInvalidToken && !didRetry) {
    await login();
    return jetnetFetch(path, opts, true);
  }

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${JSON.stringify(json)}`);
  }

  normalizeError(json);
  return json;
}

function daysAgo(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return `${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")}/${d.getFullYear()}`;
}

export async function GET(request: NextRequest) {
  const tail = request.nextUrl.searchParams.get("tail")?.trim().toUpperCase();

  if (!tail) {
    return NextResponse.json(
      { code: "MISSING_PARAM", message: "Query parameter 'tail' is required", endpoint: null, rawResponsestatus: null },
      { status: 400 }
    );
  }

  try {
    const lookup = await jetnetFetch(`/api/Aircraft/getRegNumber/${tail}/{apiToken}`, { method: "GET" });
    const ac = lookup.aircraftresult as Record<string, unknown> | undefined;

    if (!ac?.aircraftid) {
      return NextResponse.json(
        { code: "AIRCRAFT_NOT_FOUND", message: `No aircraft found for tail ${tail}`, endpoint: "getRegNumber", rawResponsestatus: null },
        { status: 404 }
      );
    }

    const aircraftId = ac.aircraftid as number;

    const [rels, flights] = await Promise.all([
      jetnetFetch("/api/Aircraft/getRelationships/{apiToken}", {
        method: "POST",
        body: JSON.stringify({
          aircraftid: aircraftId,
          aclist: [],
          modlist: [],
          actiondate: "",
          showHistoricalAcRefs: false,
        }),
      }),
      jetnetFetch("/api/Aircraft/getFlightDataPaged/{apiToken}/100/1", {
        method: "POST",
        body: JSON.stringify({
          aircraftid: aircraftId,
          startdate: daysAgo(180),
          enddate: daysAgo(0),
          origin: "",
          destination: "",
          aclist: [],
          modlist: [],
          exactMatchReg: true,
        }),
      }),
    ]);

    const relationships = (rels.relationships || []) as Record<string, unknown>[];
    let owner = null;
    let operator = null;

    for (const rel of relationships) {
      const card = {
        companyId: (rel.companyid as number) || ((rel.company as Record<string, unknown>)?.companyid as number) || null,
        companyName: (rel.name as string) || ((rel.company as Record<string, unknown>)?.name as string) || null,
        segment: null,
        location: null,
        primaryPhone: null,
      };
      if (rel.relationtype === "Owner" && rel.relationseqno === 1 && !owner) {
        owner = card;
      } else if (rel.relationtype === "Operator" && rel.relationseqno === 1 && !operator) {
        operator = card;
      }
    }

    const flightData = (flights.flightdata || []) as unknown[];
    const totalFlights = flightData.length;

    const result = {
      aircraft: {
        aircraftId,
        regNbr: ac.regnbr || tail,
        serialNbr: ac.serialnbr || "",
        make: ac.make || "",
        model: ac.model || "",
        year: ac.yearmfr || ac.yeardlv || null,
        ownerCompanyId: owner?.companyId || null,
        operatorCompanyId: operator?.companyId || null,
      },
      owner,
      operator,
      utilization: totalFlights > 0 ? { periodDays: 180, totalFlights } : null,
      _debug: {
        endpoints: ["getRegNumber", "getRelationships", "getFlightDataPaged"],
        rawResponsestatuses: [
          lookup.responsestatus || "SUCCESS",
          rels.responsestatus || "SUCCESS",
          flights.responsestatus || "SUCCESS",
        ],
      },
    };

    return NextResponse.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      { code: "JETNET_ERROR", message, endpoint: null, rawResponsestatus: null },
      { status: 500 }
    );
  }
}
