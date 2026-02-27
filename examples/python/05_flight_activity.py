"""
JETNET API -- Flight Activity Data

Demonstrates how to retrieve flight data for an aircraft using
getFlightDataPaged with date range filtering and pagination.

Required environment variables:
    JETNET_EMAIL    -- Your JETNET account email
    JETNET_PASSWORD -- Your JETNET account password
"""

import os
import sys
import requests
from datetime import datetime, timedelta

BASE = "https://customer.jetnetconnect.com"

LIST_KEYS = {
    "history", "flightdata", "events", "aircraft",
    "aircraftowneroperators", "companylist", "contactlist",
    "relationships", "aircraftcompfractionalrefs",
}


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


def get_all_pages(bearer, token, paged_path, body, pagesize=100):
    """Paginate through all pages of a paged endpoint."""
    results = []
    page = 1
    while True:
        data = api("POST", f"{paged_path}/{pagesize}/{page}", bearer, token, body)
        page_items = next(
            (v for k, v in data.items() if isinstance(v, list) and k in LIST_KEYS),
            [],
        )
        results.extend(page_items)
        if page >= data.get("maxpages", 1):
            break
        page += 1
    return results


def fmt_date(d):
    return d.strftime("%m/%d/%Y")


def main():
    email = os.environ.get("JETNET_EMAIL")
    password = os.environ.get("JETNET_PASSWORD")
    if not email or not password:
        print("Set JETNET_EMAIL and JETNET_PASSWORD environment variables.")
        sys.exit(1)

    bearer, token = login(email, password)

    tail = sys.argv[1] if len(sys.argv) > 1 else "N1KE"
    print(f"Looking up tail {tail}...")
    result = api("GET", f"/api/Aircraft/getRegNumber/{tail}/{{apiToken}}", bearer, token)
    ac = result.get("aircraftresult", {})
    aircraft_id = ac.get("aircraftid")
    if not aircraft_id:
        print(f"Aircraft '{tail}' not found.")
        sys.exit(1)

    print(f"  Aircraft: {ac.get('make')} {ac.get('model')} (ID: {aircraft_id})")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    print(f"\nFetching flight data from {fmt_date(start_date)} to {fmt_date(end_date)}...")

    body = {
        "aircraftid": aircraft_id,
        "startdate": fmt_date(start_date),
        "enddate": fmt_date(end_date),
        "origin": "",
        "destination": "",
        "aclist": [],
        "modlist": [],
        "exactMatchReg": True,
    }

    flights = get_all_pages(
        bearer, token,
        "/api/Aircraft/getFlightDataPaged/{apiToken}",
        body,
        pagesize=100,
    )

    print(f"Found {len(flights)} flight records.\n")

    for i, flight in enumerate(flights[:20], 1):
        origin = flight.get("origin", "N/A")
        dest = flight.get("destination", "N/A")
        date = flight.get("flightdate", "N/A")
        minutes = flight.get("flightminutes", "")
        print(f"  {i:3d}. {date:12s}  {origin:6s} -> {dest:6s}  ({minutes} min)")

    if len(flights) > 20:
        print(f"\n  ... and {len(flights) - 20} more flights.")

    if flights:
        total_minutes = sum(f.get("flightminutes", 0) or 0 for f in flights)
        total_hours = total_minutes / 60
        print(f"\n  Summary:")
        print(f"    Total flights:  {len(flights)}")
        print(f"    Total hours:    {total_hours:.1f}")
        print(f"    Avg per flight: {total_minutes / len(flights):.0f} min")


if __name__ == "__main__":
    main()
