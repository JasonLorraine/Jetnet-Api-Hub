"""
JETNET API -- Authentication Example

Demonstrates how to:
1. Log in to the JETNET API and obtain tokens
2. Use tokens for subsequent API calls
3. Handle token expiration and refresh

Required environment variables:
    JETNET_EMAIL    -- Your JETNET account email
    JETNET_PASSWORD -- Your JETNET account password
"""

import os
import sys
import time
import requests

BASE = "https://customer.jetnetconnect.com"

TOKEN_TTL = 7 * 3600


def login(email, password):
    """Authenticate and return (bearerToken, apiToken)."""
    r = requests.post(
        f"{BASE}/api/Admin/APILogin",
        json={"emailAddress": email, "password": password},
    )
    r.raise_for_status()
    data = r.json()
    bearer = data.get("bearerToken")
    api_token = data.get("apiToken") or data.get("securityToken")
    if not bearer or not api_token:
        raise RuntimeError("Login succeeded but tokens not found in response.")
    return bearer, api_token


def api(method, path, bearer, token, body=None):
    """Make an authenticated JETNET API call."""
    url = f"{BASE}{path}".replace("{apiToken}", token)
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json",
    }
    r = requests.request(method, url, headers=headers, json=body)
    r.raise_for_status()
    result = r.json()
    status = str(result.get("responsestatus", "")).upper()
    if "ERROR" in status:
        if "INVALID SECURITY TOKEN" in status:
            return None
        raise ValueError(f"JETNET error: {result['responsestatus']}")
    return result


class JetnetClient:
    """Wrapper that manages token lifecycle."""

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.bearer = None
        self.token = None
        self.token_issued = 0

    def ensure_auth(self):
        if not self.bearer or not self.token or (time.time() - self.token_issued > TOKEN_TTL):
            self.bearer, self.token = login(self.email, self.password)
            self.token_issued = time.time()

    def call(self, method, path, body=None):
        self.ensure_auth()
        result = api(method, path, self.bearer, self.token, body)
        if result is None:
            self.bearer, self.token = login(self.email, self.password)
            self.token_issued = time.time()
            result = api(method, path, self.bearer, self.token, body)
            if result is None:
                raise RuntimeError("Re-login failed; INVALID SECURITY TOKEN persists.")
        return result


def main():
    email = os.environ.get("JETNET_EMAIL")
    password = os.environ.get("JETNET_PASSWORD")
    if not email or not password:
        print("Set JETNET_EMAIL and JETNET_PASSWORD environment variables.")
        sys.exit(1)

    print("Logging in to JETNET API...")
    bearer, api_token = login(email, password)
    print(f"Login successful.")
    print(f"  bearerToken: {bearer[:20]}...")
    print(f"  apiToken:    {api_token[:20]}...")

    print("\nMaking a test call -- looking up tail N1KE...")
    result = api("GET", "/api/Aircraft/getRegNumber/N1KE/{apiToken}", bearer, api_token)
    if result:
        ac = result.get("aircraftresult", {})
        print(f"  Aircraft ID: {ac.get('aircraftid')}")
        print(f"  Make/Model:  {ac.get('make')} {ac.get('model')}")
        print(f"  Serial:      {ac.get('serialnbr')}")
        print(f"  Year:        {ac.get('yearmfr')}")
    else:
        print("  Call returned no result.")

    print("\nUsing JetnetClient wrapper with auto-refresh...")
    client = JetnetClient(email, password)
    result = client.call("GET", "/api/Aircraft/getRegNumber/N1KE/{apiToken}")
    ac = result.get("aircraftresult", {})
    print(f"  Aircraft: {ac.get('make')} {ac.get('model')} (ID: {ac.get('aircraftid')})")


if __name__ == "__main__":
    main()
