"""
JETNET API -- Bulk Aircraft Export with Pagination

Demonstrates how to use getBulkAircraftExportPaged to export aircraft records
in bulk, including the critical maxpages:0 quirk handling.

Key points:
- getBulkAircraftExport returns maxpages:0 when all results fit in one page
- Use max(maxpages, 1) to avoid skipping single-page results
- Response uses flat prefixed schema: owr* = owner, opr* = operator, chp* = chief pilot
- forsale is "Y"/"N" (not "true"/"false")
- datepurchased is YYYYMMDD format

Required environment variables:
    JETNET_EMAIL    -- Your JETNET account email
    JETNET_PASSWORD -- Your JETNET account password
"""

import os
import sys
import requests
from datetime import datetime, timedelta

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


def get_bulk_export(bearer, token, body, pagesize=100):
    """Fetch all pages of a bulk aircraft export.

    Handles the maxpages:0 quirk where JETNET returns maxpages=0
    when all results fit in a single response.
    """
    all_aircraft = []
    page = 1

    while True:
        data = api(
            "POST",
            f"/api/Aircraft/getBulkAircraftExportPaged/{{apiToken}}/{pagesize}/{page}",
            bearer, token, body,
        )

        aircraft = data.get("aircraft", [])
        all_aircraft.extend(aircraft)

        total_pages = max(data.get("maxpages", 1), 1)

        print(f"  Page {page}/{total_pages} -- {len(aircraft)} records (total so far: {len(all_aircraft)})")

        if page >= total_pages:
            break
        page += 1

    return all_aircraft


def main():
    email = os.environ.get("JETNET_EMAIL")
    password = os.environ.get("JETNET_PASSWORD")
    if not email or not password:
        print("Set JETNET_EMAIL and JETNET_PASSWORD environment variables.")
        sys.exit(1)

    bearer, token = login(email, password)

    print("--- Bulk Export: In-Operation Business Jets by Model ---\n")

    body = {
        "airframetype": "FixedWing",
        "maketype": "BusinessJet",
        "lifecycle": "InOperation",
        "modlist": [145],
        "aclist": [],
        "actiondate": "",
        "forsale": "",
        "exactMatchReg": False,
        "showHistoricalAcRefs": False,
        "showAwaitingDocsCompanies": False,
        "showMaintenance": False,
        "showAdditionalEquip": False,
        "showExterior": False,
        "showInterior": False,
    }

    aircraft = get_bulk_export(bearer, token, body, pagesize=100)
    print(f"\nTotal aircraft exported: {len(aircraft)}\n")

    for i, ac in enumerate(aircraft[:5], 1):
        reg = ac.get("regnbr", "N/A")
        make = ac.get("make", "")
        model = ac.get("model", "")
        sn = ac.get("serialnbr", "N/A")
        year = ac.get("yearmfr", "N/A")
        forsale = ac.get("forsale", "N/A")
        owner = ac.get("owrcompanyname", "N/A")
        operator = ac.get("oprcompanyname", "N/A")

        print(f"  {i}. {reg:10s}  {make} {model}  SN: {sn}  Year: {year}")
        print(f"     For Sale: {forsale}  Owner: {owner}  Operator: {operator}")

    print("\n\n--- Hourly Change Detection (actiondate window) ---\n")

    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)

    body_hourly = {
        "airframetype": "None",
        "maketype": "BusinessJet",
        "lifecycle": "InOperation",
        "actiondate": one_hour_ago.strftime("%m/%d/%Y %H:%M:%S"),
        "enddate": now.strftime("%m/%d/%Y %H:%M:%S"),
        "exactMatchReg": False,
        "showHistoricalAcRefs": False,
        "showAwaitingDocsCompanies": False,
        "showMaintenance": False,
        "showAdditionalEquip": False,
        "showExterior": False,
        "showInterior": False,
    }

    changes = get_bulk_export(bearer, token, body_hourly, pagesize=100)
    print(f"\nAircraft records changed in the last hour: {len(changes)}")

    for ac in changes[:5]:
        reg = ac.get("regnbr", "N/A")
        make = ac.get("make", "")
        model = ac.get("model", "")
        print(f"  - {reg}  {make} {model}")


if __name__ == "__main__":
    main()
