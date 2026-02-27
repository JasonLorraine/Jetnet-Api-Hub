# Authentication

## Login Endpoint

All JETNET API calls require authentication via the login endpoint:

```http
POST https://customer.jetnetconnect.com/api/Admin/APILogin
Content-Type: application/json

{
  "emailAddress": "YOUR_EMAIL@example.com",
  "password": "YOUR_PASSWORD"
}
```

> **Important:** The field is `emailAddress` with a capital **A**. This is the single most common auth mistake. It is not `email`, `emailaddress`, or `email_address`.

## Response Tokens

A successful login returns two tokens:

| Token | Purpose |
|-------|---------|
| `bearerToken` | Sent in the `Authorization` header on every request |
| `apiToken` | Inserted into the URL path on every request (also called `securityToken` in some docs — same field) |

## Using Tokens on Subsequent Calls

Every API call after login requires both tokens:

1. **Header:** `Authorization: Bearer {bearerToken}`
2. **URL path:** Replace `{apiToken}` in the endpoint path with your actual `apiToken` value

The `apiToken` goes **in the URL path only** — never in headers or the JSON body.

### Example

```
GET /api/Aircraft/getRegNumber/N123AB/{apiToken}
Authorization: Bearer {bearerToken}
```

## Two-Tier Model

JETNET uses a two-tier model for API usage:

| Tier | Use Case | Characteristics |
|------|----------|----------------|
| **Tier A — Interactive** | Tail lookup, owner/operator, pictures, quick flight summary, CRM enrichment | One aircraft at a time, low volume, user is waiting |
| **Tier B — Bulk / Data Engineering** | Nightly sync, history exports, analytics pipelines, large event windows | Always paged, run async, never drive a live UI off these |

If building an app or a script for a salesperson: **Tier A**.
If a customer asks about bulk export, nightly refresh, or history across thousands of aircraft: **Tier B**.

## Environment Variable Setup

Store your credentials in environment variables — never hard-code them:

```bash
export JETNET_EMAIL="your_email@example.com"
export JETNET_PASSWORD="your_password"
```

## Token Refresh Pattern

Tokens expire after **60 minutes**. For long-running pipelines, proactively re-login before expiry rather than waiting for a failure.

### Python

```python
import time, os, requests

BASE = "https://customer.jetnetconnect.com"
token_issued = 0
TOKEN_TTL = 50 * 60  # refresh after 50 min (tokens last 60 min)

def login(email, password):
    r = requests.post(f"{BASE}/api/Admin/APILogin",
                      json={"emailAddress": email, "password": password})
    r.raise_for_status()
    d = r.json()
    return d["bearerToken"], d["apiToken"]

def get_tokens():
    global bearer, token, token_issued
    if time.time() - token_issued > TOKEN_TTL:
        bearer, token = login(os.environ["JETNET_EMAIL"], os.environ["JETNET_PASSWORD"])
        token_issued = time.time()
    return bearer, token
```

### JavaScript

```javascript
const BASE = "https://customer.jetnetconnect.com";
let bearerToken, apiToken, tokenIssued = 0;
const TOKEN_TTL = 50 * 60 * 1000; // 50 minutes in ms

async function login(email, password) {
  const res = await fetch(`${BASE}/api/Admin/APILogin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emailAddress: email, password })
  });
  if (!res.ok) throw new Error(`Login failed: ${res.status}`);
  const data = await res.json();
  return { bearerToken: data.bearerToken, apiToken: data.apiToken };
}

async function getTokens() {
  if (Date.now() - tokenIssued > TOKEN_TTL) {
    const tokens = await login(process.env.JETNET_EMAIL, process.env.JETNET_PASSWORD);
    bearerToken = tokens.bearerToken;
    apiToken = tokens.apiToken;
    tokenIssued = Date.now();
  }
  return { bearerToken, apiToken };
}
```

## Retry on INVALID SECURITY TOKEN

When you receive `"ERROR: INVALID SECURITY TOKEN"` in the `responsestatus` field:

1. Re-login to get fresh tokens
2. Retry the failed request once with the new tokens
3. **Never loop** — if it fails again, surface the error

```python
def api(method, path, bearer, token, body=None):
    url = f"{BASE}{path}".replace("{apiToken}", token)
    headers = {"Authorization": f"Bearer {bearer}", "Content-Type": "application/json"}
    r = requests.request(method, url, headers=headers, json=body)
    r.raise_for_status()
    result = r.json()
    status = result.get("responsestatus", "").upper()
    if "INVALID SECURITY TOKEN" in status:
        bearer, token = login(os.environ["JETNET_EMAIL"], os.environ["JETNET_PASSWORD"])
        r = requests.request(method, url.replace(token, token), headers=headers, json=body)
        r.raise_for_status()
        result = r.json()
    if "ERROR" in result.get("responsestatus", "").upper():
        raise ValueError(f"JETNET error: {result['responsestatus']}")
    return result
```

## Security Best Practices

- Never expose tokens in client-side code (browser or mobile app)
- Always proxy JETNET calls through your own backend
- Store credentials in environment variables or a secrets manager
- Do not log tokens in production
