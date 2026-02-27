"""
JETNET API -- Ownership / Relationships

Demonstrates two patterns for retrieving aircraft relationships:
1. Single aircraft lookup (Tier A / Golden Path)
2. Bulk fleet lookup (Tier B -- many aircraft IDs at once)

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


def get_relationships_single(bearer, token, aircraft_id):
    """Get relationships for a single aircraft (Tier A)."""
    body = {
        "aircraftid": aircraft_id,
        "aclist": [],
        "modlist": [],
        "actiondate": "",
        "showHistoricalAcRefs": False,
    }
    result = api("POST", "/api/Aircraft/getRelationships/{apiToken}", bearer, token, body)
    return result.get("relationships", [])


def get_relationships_bulk(bearer, token, aircraft_ids):
    """Get relationships for multiple aircraft at once (Tier B)."""
    body = {
        "aclist": aircraft_ids,
        "modlist": [],
        "actiondate": "",
        "showHistoricalAcRefs": False,
    }
    result = api("POST", "/api/Aircraft/getRelationships/{apiToken}", bearer, token, body)
    return result.get("relationships", [])


def resolve_tail(bearer, token, tail):
    """Resolve a tail number to an aircraft ID."""
    result = api("GET", f"/api/Aircraft/getRegNumber/{tail}/{{apiToken}}", bearer, token)
    ac = result.get("aircraftresult", {})
    return ac.get("aircraftid")


def print_relationships(relationships):
    """Print relationship records grouped by aircraft."""
    by_aircraft = {}
    for rel in relationships:
        ac_id = rel.get("aircraftid")
        by_aircraft.setdefault(ac_id, []).append(rel)

    for ac_id, rels in by_aircraft.items():
        reg = rels[0].get("regnbr", "N/A")
        print(f"\n  Aircraft {reg} (ID: {ac_id}):")
        for rel in rels:
            rel_type = rel.get("relationtype", "N/A")
            name = rel.get("name", "N/A")
            company = rel.get("company", {})
            city = company.get("city", "")
            state = company.get("state", "")
            location = f"{city}, {state}" if city else ""
            print(f"    {rel_type:20s}  {name}")
            if location:
                print(f"    {'':20s}  Location: {location}")


def main():
    email = os.environ.get("JETNET_EMAIL")
    password = os.environ.get("JETNET_PASSWORD")
    if not email or not password:
        print("Set JETNET_EMAIL and JETNET_PASSWORD environment variables.")
        sys.exit(1)

    bearer, token = login(email, password)

    tail = "N1KE"
    print(f"Resolving tail {tail} to aircraft ID...")
    aircraft_id = resolve_tail(bearer, token, tail)
    if not aircraft_id:
        print(f"Aircraft '{tail}' not found.")
        sys.exit(1)
    print(f"  Aircraft ID: {aircraft_id}")

    print(f"\n--- Single Aircraft Relationships (Tier A) ---")
    rels = get_relationships_single(bearer, token, aircraft_id)
    print(f"Found {len(rels)} relationship records.")
    print_relationships(rels)

    print(f"\n\n--- Bulk Fleet Relationships (Tier B) ---")
    tails = ["N1KE", "N2KE"]
    aircraft_ids = []
    for t in tails:
        aid = resolve_tail(bearer, token, t)
        if aid:
            aircraft_ids.append(aid)
            print(f"  {t} -> {aid}")

    if aircraft_ids:
        rels = get_relationships_bulk(bearer, token, aircraft_ids)
        print(f"\nFound {len(rels)} total relationship records across {len(aircraft_ids)} aircraft.")
        print_relationships(rels)


if __name__ == "__main__":
    main()
