"""
JETNET API -- Fleet Search (For-Sale Business Jets)

Demonstrates how to search for aircraft using getAircraftList with filters
for make type, model, lifecycle, and for-sale status.

Note: getAircraftList has no paged variant. Use filters to control result size.

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


def search_for_sale_jets(bearer, token, model_ids=None):
    """Search for business jets currently for sale.

    Args:
        model_ids: List of JETNET model IDs to filter by (e.g., [145, 634] for G550/G600).
                   Empty list means no model filter.
    """
    body = {
        "airframetype": "FixedWing",
        "maketype": "BusinessJet",
        "lifecycle": "InOperation",
        "forsale": "true",
        "aclist": [],
        "modlist": model_ids or [],
    }
    result = api("POST", "/api/Aircraft/getAircraftList/{apiToken}", bearer, token, body)
    return result.get("aircraft", [])


def main():
    email = os.environ.get("JETNET_EMAIL")
    password = os.environ.get("JETNET_PASSWORD")
    if not email or not password:
        print("Set JETNET_EMAIL and JETNET_PASSWORD environment variables.")
        sys.exit(1)

    bearer, token = login(email, password)

    model_ids = [145, 634]
    print(f"Searching for-sale business jets (model IDs: {model_ids})...")

    aircraft = search_for_sale_jets(bearer, token, model_ids)
    print(f"Found {len(aircraft)} aircraft for sale.\n")

    for i, ac in enumerate(aircraft[:10], 1):
        print(f"  {i}. {ac.get('regnbr', 'N/A'):10s}  {ac.get('make', '')} {ac.get('model', '')}")
        print(f"     Year: {ac.get('yearmfr', 'N/A')}  |  Serial: {ac.get('serialnbr', 'N/A')}")
        print(f"     Base: {ac.get('baseicao', 'N/A')} ({ac.get('baseairport', 'N/A')})")
        print(f"     For Sale: {ac.get('forsale', 'N/A')}  |  Asking: {ac.get('askingprice', 'N/A')}")
        print()

    if len(aircraft) > 10:
        print(f"  ... and {len(aircraft) - 10} more.")

    print("\nSearching all for-sale business jets (no model filter)...")
    all_jets = search_for_sale_jets(bearer, token)
    print(f"Found {len(all_jets)} total business jets for sale.")

    makes = {}
    for ac in all_jets:
        make = ac.get("make", "UNKNOWN")
        makes[make] = makes.get(make, 0) + 1

    print("\nBreakdown by make:")
    for make, count in sorted(makes.items(), key=lambda x: -x[1]):
        print(f"  {make:20s}  {count}")


if __name__ == "__main__":
    main()
