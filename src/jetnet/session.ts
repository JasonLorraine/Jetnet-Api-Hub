/**
 * session.ts -- JETNET session helper (Node / TypeScript)
 *
 * Drop-in equivalent of session.py for Node / Next.js / Bun projects.
 *
 * Usage:
 *   import { login, ensureSession, jetnetRequest } from './session'
 *
 *   const session = await login()                        // reads env vars
 *   const data    = await jetnetRequest('GET',
 *                     '/api/Aircraft/getRegNumber/N12345/{apiToken}',
 *                     session)
 *
 * Environment variables (same names as Python helper):
 *   JETNET_EMAIL     -- emailAddress (capital A matters on the server)
 *   JETNET_PASSWORD  -- password
 *   JETNET_BASE_URL  -- default: https://customer.jetnetconnect.com
 */

const DEFAULT_BASE_URL = 'https://customer.jetnetconnect.com'

export interface SessionState {
  baseUrl: string
  email: string
  password: string
  bearerToken: string
  apiToken: string
  createdAt: number
  lastValidatedAt: number
}

export interface JetnetErrorBody {
  endpoint: string
  status: string
  detail?: string
}

export class JetnetError extends Error {
  endpoint: string
  status: string

  constructor(endpoint: string, status: string, detail?: string) {
    super(`JETNET error [${endpoint}]: ${status}${detail ? ' -- ' + detail : ''}`)
    this.name = 'JetnetError'
    this.endpoint = endpoint
    this.status = status
  }
}

function nowSeconds(): number {
  return Date.now() / 1000
}

/**
 * Detect JETNET application-level errors in a parsed response JSON.
 * JETNET uses two error styles:
 *   1. responsestatus starting with "ERROR" or "INVALID" (most endpoints)
 *   2. RFC 7807: { "title": "...", "status": 400, "detail": "..." }
 */
function normalizeError(
  responseJson: Record<string, unknown>,
  endpoint = ''
): JetnetError | null {
  const rs = responseJson['responsestatus']
  if (typeof rs === 'string') {
    const upper = rs.toUpperCase()
    if (upper.startsWith('ERROR') || upper.startsWith('INVALID')) {
      return new JetnetError(endpoint, rs)
    }
  }

  if ('title' in responseJson && 'status' in responseJson) {
    const title = String(responseJson['title'] ?? '')
    const detail = responseJson['detail'] ? String(responseJson['detail']) : undefined
    return new JetnetError(endpoint, title, detail)
  }

  return null
}

const TOKEN_TTL_SECONDS = 50 * 60  // 50 min (tokens last ~60 min)

/**
 * Authenticate and return a new SessionState.
 *
 * CRITICAL: The field name is `emailAddress` with a capital A.
 * Sending `email` or `emailaddress` returns HTTP 200 with an error body.
 */
export async function login(
  email?: string,
  password?: string,
  baseUrl?: string
): Promise<SessionState> {
  const resolvedBaseUrl = baseUrl ?? process.env['JETNET_BASE_URL'] ?? DEFAULT_BASE_URL
  const resolvedEmail = email ?? process.env['JETNET_EMAIL']
  const resolvedPassword = password ?? process.env['JETNET_PASSWORD']

  if (!resolvedEmail || !resolvedPassword) {
    throw new Error(
      'JETNET credentials missing. Set JETNET_EMAIL and JETNET_PASSWORD env vars ' +
      'or pass email/password to login().'
    )
  }

  const url = `${resolvedBaseUrl}/api/Admin/APILogin`
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ emailAddress: resolvedEmail, password: resolvedPassword }),
  })

  if (!response.ok) {
    throw new Error(`JETNET login HTTP ${response.status}: ${await response.text()}`)
  }

  const data = (await response.json()) as Record<string, unknown>
  const err = normalizeError(data, 'APILogin')
  if (err) throw err

  const bearerToken = String(data['bearerToken'] ?? '')
  const apiToken = String(data['apiToken'] ?? '')

  if (!bearerToken || !apiToken) {
    throw new Error(
      'JETNET login returned no tokens. Check credentials. ' +
      `Response: ${JSON.stringify(data).slice(0, 200)}`
    )
  }

  const now = nowSeconds()
  return {
    baseUrl: resolvedBaseUrl,
    email: resolvedEmail,
    password: resolvedPassword,
    bearerToken,
    apiToken,
    createdAt: now,
    lastValidatedAt: now,
  }
}

/**
 * Call /getAccountInfo as a lightweight token health-check.
 * Returns the raw response dict.
 */
export async function getAccountInfo(
  session: SessionState
): Promise<Record<string, unknown>> {
  const url = `${session.baseUrl}/api/Admin/getAccountInfo/${session.apiToken}`
  const response = await fetch(url, {
    method: 'GET',
    headers: { Authorization: `Bearer ${session.bearerToken}` },
  })

  if (!response.ok) {
    throw new Error(`getAccountInfo HTTP ${response.status}`)
  }

  const data = (await response.json()) as Record<string, unknown>
  const err = normalizeError(data, 'getAccountInfo')
  if (err) throw err

  return data
}

/**
 * Return a valid session, refreshing if the token is stale.
 *
 * Strategy (three-tier defense):
 *   1. Age check: if token is < TOKEN_TTL old, return as-is.
 *   2. Probe /getAccountInfo; if it succeeds, update lastValidatedAt and return.
 *   3. Full re-login. If that fails, throw -- do not swallow the error.
 */
export async function ensureSession(
  session: SessionState
): Promise<SessionState> {
  const age = nowSeconds() - session.createdAt

  if (age < TOKEN_TTL_SECONDS) {
    return session
  }

  try {
    await getAccountInfo(session)
    return { ...session, lastValidatedAt: nowSeconds() }
  } catch {
    // Fall through to re-login
  }

  return await login(session.email, session.password, session.baseUrl)
}

/**
 * Make an authenticated JETNET request.
 *
 * - Substitutes `{apiToken}` in the path automatically.
 * - Retries once after a fresh login if the token appears invalid.
 * - Throws JetnetError for application-level errors.
 *
 * @param method   'GET' | 'POST'
 * @param path     Endpoint path, e.g. '/api/Aircraft/getRegNumber/N12345/{apiToken}'
 * @param session  Current SessionState
 * @param body     Optional POST body (will be JSON-serialized)
 */
export async function jetnetRequest(
  method: 'GET' | 'POST',
  path: string,
  session: SessionState,
  body?: Record<string, unknown>
): Promise<Record<string, unknown>> {
  const resolvedPath = path.replace('{apiToken}', session.apiToken)
  const url = `${session.baseUrl}${resolvedPath}`

  const headers: Record<string, string> = {
    Authorization: `Bearer ${session.bearerToken}`,
    'Content-Type': 'application/json',
  }

  const init: RequestInit = {
    method,
    headers,
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  }

  let response = await fetch(url, init)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} ${response.statusText} -- ${url}`)
  }

  let data = (await response.json()) as Record<string, unknown>
  let err = normalizeError(data, path)

  if (err && typeof err.status === 'string' && err.status.toUpperCase().startsWith('INVALID')) {
    const fresh = await login(session.email, session.password, session.baseUrl)
    Object.assign(session, fresh)

    const retryPath = path.replace('{apiToken}', fresh.apiToken)
    const retryUrl = `${fresh.baseUrl}${retryPath}`
    response = await fetch(retryUrl, {
      ...init,
      headers: { ...headers, Authorization: `Bearer ${fresh.bearerToken}` },
    })
    data = (await response.json()) as Record<string, unknown>
    err = normalizeError(data, path)
  }

  if (err) throw err
  return data
}

/**
 * Convenience: call ensureSession then jetnetRequest in one step.
 * Returns [updatedSession, responseData].
 */
export async function refreshAndRequest(
  method: 'GET' | 'POST',
  path: string,
  session: SessionState,
  body?: Record<string, unknown>
): Promise<[SessionState, Record<string, unknown>]> {
  const fresh = await ensureSession(session)
  const data = await jetnetRequest(method, path, fresh, body)
  return [fresh, data]
}
