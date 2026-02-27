const DEFAULT_BASE_URL = "https://customer.jetnetconnect.com";
const TOKEN_TTL_MS = 60 * 60 * 1000;
const REFRESH_AT_MS = 50 * 60 * 1000;

export function createSession(email, password, baseUrl = DEFAULT_BASE_URL) {
  return {
    baseUrl,
    email,
    password,
    bearerToken: null,
    apiToken: null,
    createdAt: null,
    lastValidatedAt: null,
  };
}

export async function login(session) {
  const res = await fetch(`${session.baseUrl}/api/Admin/APILogin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      emailAddress: session.email,
      password: session.password,
    }),
  });

  if (!res.ok) {
    throw new Error(`Login failed: HTTP ${res.status}`);
  }

  const data = await res.json();
  normalizeError(data);

  const bearerToken = data.bearerToken;
  const apiToken = data.apiToken || data.securityToken;

  if (!bearerToken || !apiToken) {
    throw new Error("Login succeeded but tokens not found in response.");
  }

  return {
    ...session,
    bearerToken,
    apiToken,
    createdAt: Date.now(),
    lastValidatedAt: Date.now(),
  };
}

export async function getAccountInfo(session) {
  if (!session.apiToken) {
    throw new Error("No apiToken — call login() first.");
  }

  const url = `${session.baseUrl}/api/Utility/getAccountInfo/${session.apiToken}`;
  const res = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.bearerToken}`,
    },
  });

  if (!res.ok) {
    throw new Error(`getAccountInfo failed: HTTP ${res.status}`);
  }

  const data = await res.json();
  normalizeError(data);
  return data;
}

export async function ensureSession(session) {
  if (!session.bearerToken || !session.apiToken) {
    return login(session);
  }

  const age = Date.now() - (session.createdAt || 0);
  if (age > REFRESH_AT_MS) {
    return login(session);
  }

  try {
    await getAccountInfo(session);
    return { ...session, lastValidatedAt: Date.now() };
  } catch {
    return login(session);
  }
}

export function normalizeError(responseJson) {
  if (!responseJson || typeof responseJson !== "object") {
    return;
  }

  const status = responseJson.responsestatus;
  if (status && String(status).toUpperCase().includes("ERROR")) {
    throw new Error(`JETNET error: ${status}`);
  }

  if (responseJson.type && responseJson.title && responseJson.status) {
    throw new Error(
      `JETNET RFC error: ${responseJson.status} ${responseJson.title} (${responseJson.type})`
    );
  }
}

export async function jetnetRequest(method, path, session, body = null) {
  let current = await ensureSession(session);

  const execute = async (s) => {
    const url = `${s.baseUrl}${path}`.replaceAll("{apiToken}", s.apiToken);
    const opts = {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${s.bearerToken}`,
      },
    };
    if (body !== null && body !== undefined) {
      opts.body = JSON.stringify(body);
    }

    const res = await fetch(url, opts);
    const text = await res.text();
    let json;
    try {
      json = JSON.parse(text);
    } catch {
      json = { raw: text };
    }

    return { res, json };
  };

  let { res, json } = await execute(current);

  const statusText = json?.responsestatus
    ? String(json.responsestatus).toUpperCase()
    : "";
  const isInvalidToken =
    res.status === 401 ||
    statusText.includes("INVALID SECURITY TOKEN");

  if (isInvalidToken) {
    const retrySession = await login(session);
    const retry = await execute(retrySession);
    res = retry.res;
    json = retry.json;
    current = retrySession;
  }

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${JSON.stringify(json)}`);
  }

  normalizeError(json);

  Object.assign(session, current);
  return json;
}
