"""
JETNET API -- Tail Number Lookup

Demonstrates how to look up an aircraft by registration (tail) number
and print key identification fields.

Required environment variables:
    JETNET_EMAIL    -- Your JETNET account email
    JETNET_PASSWORD -- Your JETNET account password
"""

import os
import sys
import requests

BASE = "https://customer.jetnetconnect.com"


def login(email, password):
    r = requests.post(
        f"{BASE}/api/Admin/APILogin",
        json={"emailAddress": email, "password": password},
    )
    r.raise_for_status()
    data = r.json()
    return data["bearerToken"], data["apiToken"]


def api(method, path, bearer, token, body=None):
    url = f"{BASE}{path}".replace("{apiToken}", token)
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json",
    }
    r = requests.request(method, url, headers=headers, json=body)
    r.raise_for_status()
    result = r.json()
    if "ERROR" in str(result.get("responsestatus", "")).upper():
        raise ValueError(f"JETNET error: {result['responsestatus']}")
    return result


def lookup_tail(bearer, token, tail_number):
    """Look up an aircraft by tail number. Returns the aircraftresult dict."""
    result = api("GET", f"/api/Aircraft/getRegNumber/{tail_number}/{{apiToken}}", bearer, token)
    return result.get("aircraftresult", {})


def main():
    email = os.environ.get("JETNET_EMAIL")
    password = os.environ.get("JETNET_PASSWORD")
    if not email or not password:
        print("Set JETNET_EMAIL and JETNET_PASSWORD environment variables.")
        sys.exit(1)

    tail = sys.argv[1] if len(sys.argv) > 1 else "N1KE"

    bearer, token = login(email, password)

    print(f"Looking up tail number: {tail}")
    ac = lookup_tail(bearer, token, tail.upper())

    if not ac.get("aircraftid"):
        print(f"Aircraft '{tail}' not found.")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"  Aircraft ID:    {ac.get('aircraftid')}")
    print(f"  Registration:   {ac.get('regnbr')}")
    print(f"  Serial Number:  {ac.get('serialnbr')}")
    print(f"  Make:           {ac.get('make')}")
    print(f"  Model:          {ac.get('model')}")
    print(f"  Year Mfr:       {ac.get('yearmfr')}")
    print(f"  Year Delivered:  {ac.get('yeardlv')}")
    print(f"  Base ICAO:      {ac.get('baseicao')}")
    print(f"  Base Airport:   {ac.get('baseairport')}")
    print(f"  For Sale:       {ac.get('forsale')}")
    print(f"  Lifecycle:      {ac.get('lifecycle')}")
    print(f"{'='*50}")

    relationships = ac.get("companyrelationships", [])
    if relationships:
        print(f"\n  Company Relationships ({len(relationships)}):")
        for rel in relationships:
            print(f"    - {rel.get('companyrelation', 'N/A')}: {rel.get('companyname', 'N/A')}")
            contact = f"{rel.get('contactfirstname', '')} {rel.get('contactlastname', '')}".strip()
            if contact:
                print(f"      Contact: {contact} ({rel.get('contacttitle', '')})")


if __name__ == "__main__":
    main()
