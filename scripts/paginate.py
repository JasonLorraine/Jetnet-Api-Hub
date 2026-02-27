"""
paginate.py -- JETNET generic pagination helper

Fetches all pages from any JETNET paged endpoint and returns the combined
record list. Works with any endpoint that returns maxpages + a list key.

Usage:
    from scripts.paginate import paginate_all, build_paged_url

    # Example: all G550 ownership history for 2024
    all_history = paginate_all(
        bearer=bearer,
        token=token,
        base_path="/api/Aircraft/getHistoryListPaged",
        body={
            "modlist": [145],
            "startdate": "01/01/2024",
            "enddate": "12/31/2024",
            "transtype": ["None"],
            "allrelationships": False,
            "airframetype": "None",
            "maketype": "None",
            "isnewaircraft": "Ignore",
            "aclist": []
        },
        pagesize=100
    )
    print(f"Total records: {len(all_history)}")
"""

import requests
import os
from typing import Any

BASE_URL = os.getenv("JETNET_BASE_URL", "https://customer.jetnetconnect.com")

# The response list keys for each paged endpoint.
# The paginator auto-detects the list from this set.
LIST_KEYS = {
    "history",
    "flightdata",
    "events",
    "aircraft",
    "aircraftowneroperators",
    "companylist",
    "contactlist",
    "relationships",
    "aircraftcompfractionalrefs",
}


def build_paged_url(base_path: str, token: str, pagesize: int, page: int) -> str:
    """
    Build the full URL for a paged endpoint.

    JETNET paged URL format:
        {base_path}/{token}/{pagesize}/{page}

    E.g.: /api/Aircraft/getHistoryListPaged/TOKEN/100/1
    """
    clean_path = base_path.rstrip("/")
    return f"{BASE_URL}{clean_path}/{token}/{pagesize}/{page}"


def _find_records(data: dict) -> list:
    """Extract the record list from a response dict by matching known list keys."""
    for key, value in data.items():
        if isinstance(value, list) and key in LIST_KEYS:
            return value
    return []


def paginate_all(
    bearer: str,
    token: str,
    base_path: str,
    body: dict,
    pagesize: int = 100,
    max_pages: int = None,
    on_page: callable = None,
) -> list:
    """
    Fetch all pages from a JETNET paged endpoint.

    Args:
        bearer:    bearerToken from APILogin
        token:     apiToken from APILogin
        base_path: endpoint path without token/pagesize/page,
                   e.g. '/api/Aircraft/getHistoryListPaged'
        body:      POST body dict (same for every page)
        pagesize:  records per page (100-500 recommended)
        max_pages: optional hard cap on pages to fetch (None = no cap)
        on_page:   optional callback(page_number, page_data, records_so_far)
                   called after each page completes

    Returns:
        Combined list of all records across all pages.

    Raises:
        ValueError: if JETNET returns an ERROR responsestatus
        requests.HTTPError: on HTTP error
    """
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json",
    }

    all_records = []
    page = 1

    while True:
        url = build_paged_url(base_path, token, pagesize, page)
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()

        status = data.get("responsestatus", "")
        if "ERROR" in status.upper():
            raise ValueError(f"JETNET error on page {page}: {status}")

        records = _find_records(data)
        all_records.extend(records)

        # getBulkAircraftExport and getHistoryList (non-paged variant) return
        # maxpages=0 / currentpage=0 when all results fit in one call.
        # Treat maxpages <= 1 as a single-page result (not an error).
        total_pages = max(data.get("maxpages", 1), 1)
        current    = data.get("currentpage", page)

        if on_page:
            on_page(page, data, all_records)

        # Stop conditions
        if page >= total_pages:
            break
        if max_pages and page >= max_pages:
            break

        page += 1

    return all_records


def paginate_with_summary(
    bearer: str,
    token: str,
    base_path: str,
    body: dict,
    pagesize: int = 100,
) -> dict:
    """
    Like paginate_all but also returns metadata about the run.

    Returns:
        {
            "records": [...],
            "total_pages": N,
            "total_records": N,
            "pagesize": N,
        }
    """
    meta = {"total_pages": 0, "pagesize": pagesize}

    def capture(page_num, page_data, records_so_far):
        meta["total_pages"] = page_data.get("maxpages", page_num)

    records = paginate_all(bearer, token, base_path, body, pagesize, on_page=capture)
    meta["total_records"] = len(records)

    return {"records": records, **meta}


# ---------------------------------------------------------------------------
# Convenience wrappers for the most common paged endpoints
# ---------------------------------------------------------------------------

def get_all_history(bearer, token, body, pagesize=100):
    """Fetch all ownership history records. response key: history"""
    return paginate_all(bearer, token, "/api/Aircraft/getHistoryListPaged", body, pagesize)


def get_all_flight_data(bearer, token, body, pagesize=100):
    """Fetch all flight records. response key: flightdata"""
    return paginate_all(bearer, token, "/api/Aircraft/getFlightDataPaged", body, pagesize)


def get_all_events(bearer, token, body, pagesize=100):
    """Fetch all event records. response key: events"""
    return paginate_all(bearer, token, "/api/Aircraft/getEventListPaged", body, pagesize)


def get_bulk_export(bearer, token, body, pagesize=50):
    """Fetch full aircraft export records. response key: aircraft"""
    return paginate_all(bearer, token, "/api/Aircraft/getBulkAircraftExportPaged", body, pagesize)


def get_all_companies(bearer, token, body, pagesize=100):
    """Fetch all company search results. response key: companylist"""
    return paginate_all(bearer, token, "/api/Company/getCompanyListPaged", body, pagesize)


def get_all_contacts(bearer, token, body, pagesize=100):
    """Fetch all contact search results. response key: contactlist"""
    return paginate_all(bearer, token, "/api/Contact/getContactListPaged", body, pagesize)


def get_fractional_owners(bearer, token, body, pagesize=100):
    """
    Fetch all fractional owner records. response key: aircraftcompfractionalrefs

    Typical body:
        {
            "airframetype": "FixedWing",
            "maketype": "BusinessJet",
            "regnbr": "",
            "make": "",
            "actiondate": "MM/DD/YYYY",   # start of update window
            "enddate": "MM/DD/YYYY",       # end of update window
            "basestate": ["NY", "CT"],     # state abbreviation array; [] = all states
            "modlist": [],                 # model ID filter; [] = all models
            "relationship": ["Fractional Owner"]  # relation filter array
        }

    Post-processing tip: filter on fractionPercentOwned != "0.00" to get
    actual fractional owners (excluding operators/managers on the same aircraft).
    """
    return paginate_all(
        bearer, token,
        "/api/Aircraft/getAcCompanyFractionalReportPaged",
        body, pagesize
    )


if __name__ == "__main__":
    # Self-test: validate URL building
    tests = [
        ("/api/Aircraft/getHistoryListPaged", "MYTOKEN", 100, 1,
         "https://customer.jetnetconnect.com/api/Aircraft/getHistoryListPaged/MYTOKEN/100/1"),
        ("/api/Aircraft/getFlightDataPaged", "MYTOKEN", 200, 3,
         "https://customer.jetnetconnect.com/api/Aircraft/getFlightDataPaged/MYTOKEN/200/3"),
    ]
    print("URL builder tests:")
    for base, tok, ps, pg, expected in tests:
        result = build_paged_url(base, tok, ps, pg)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {result}")

    print("\nList key detection tests:")
    samples = [
        ("history", {"history": [{"aircraftid": 1}, {"aircraftid": 2}]}),
        ("aircraftcompfractionalrefs", {"aircraftcompfractionalrefs": [{"aircraftid": 6976}]}),
    ]
    for key, sample in samples:
        sample.update({"responsestatus": "SUCCESS: PAGE [ 1 of 1 ]", "count": 1, "maxpages": 1, "currentpage": 1})
        records = _find_records(sample)
        print(f"  {'✓' if len(records) >= 1 else '✗'} found {len(records)} records in '{key}' key")
