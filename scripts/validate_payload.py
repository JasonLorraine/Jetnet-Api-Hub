"""
validate_payload.py -- JETNET payload validator

Checks a request payload for the most common mistakes before sending it.
Returns a list of errors (empty = payload looks valid).

Usage:
    from scripts.validate_payload import validate

    errors = validate("getHistoryListPaged", {
        "modlist": [145],
        "startdate": "1/1/2024",   # will flag -- missing leading zeros
        "transtype": [],           # will flag -- use ["None"] not []
        "allrelationships": true
    })
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
"""

from datetime import datetime
import json
import os
import re

# Valid enum values
VALID_AIRFRAMETYPE = {"None", "FixedWing", "Rotary"}
VALID_MAKETYPE     = {"None", "JetAirliner", "BusinessJet", "Turboprop", "Piston", "Turbine"}
VALID_LIFECYCLE    = {"None", "InProduction", "NewWithManufacturer", "InOperation", "Retired", "InStorage"}
VALID_TRISTATE     = {"Yes", "No", "Ignore"}
VALID_FORSALE_REQ  = {"true", "false", ""}

DATE_PATTERN          = re.compile(r"^\d{2}/\d{2}/\d{4}$")
DATETIME_PATTERN      = re.compile(r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$")

# Known transtype category values for getHistoryList/Paged
VALID_TRANSTYPE_CATS = {
    "None", "FullSale", "Lease", "InternalSale", "Management",
    "Insurance", "Repossession", "Registration"
}

# Endpoints that require pagination (should never be called without /{pagesize}/{page})
MUST_BE_PAGED = {
    "getHistoryList", "getFlightData", "getEventList",
    "getBulkAircraftExport", "getCompanyList", "getContactList",
    "getCondensedOwnerOperators", "getAcCompanyFractionalReport"
}

# Known correct response keys -- useful for callers building parsers
RESPONSE_KEYS = {
    "getRegNumber":               "aircraftresult",
    "getHexNumber":               "aircraftresult",
    "getAircraftList":            "aircraft",
    "getBulkAircraftExportPaged": "aircraft",
    "getHistoryListPaged":        "history",
    "getFlightDataPaged":         "flightdata",
    "getEventListPaged":          "events",
    "getRelationships":           "relationships",
    "getCondensedOwnerOperators": "aircraftowneroperators",
    "getCompanyListPaged":        "companylist",
    "getContactListPaged":        "contactlist",
    "getModelMarketTrends":                  "modelMarketTrends",
    "getPictures":                           "pictures",
    "getAcCompanyFractionalReportPaged":     "aircraftcompfractionalrefs",
}


_MODEL_ID_CACHE = None

def _load_known_model_ids():
    global _MODEL_ID_CACHE
    if _MODEL_ID_CACHE is not None:
        return _MODEL_ID_CACHE
    table_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "model-id-table.json")
    if not os.path.exists(table_path):
        return None
    try:
        with open(table_path) as f:
            data = json.load(f)
        _MODEL_ID_CACHE = {m["amodid"] for m in data}
        return _MODEL_ID_CACHE
    except Exception:
        return None


def _check_date(value: str, field: str, errors: list):
    """Validate MM/DD/YYYY format with leading zeros."""
    if not value:
        return  # empty string is usually OK (means no filter)
    if not DATE_PATTERN.match(value):
        errors.append(
            f"'{field}': date '{value}' must be MM/DD/YYYY with leading zeros "
            f"(e.g. '01/01/2024' not '1/1/2024')"
        )
        return
    try:
        datetime.strptime(value, "%m/%d/%Y")
    except ValueError:
        errors.append(f"'{field}': '{value}' is not a valid calendar date")


def validate(endpoint_name: str, payload: dict) -> list:
    """
    Validate a JETNET request payload.

    Args:
        endpoint_name: e.g. 'getHistoryListPaged', 'getAircraftList'
        payload: the dict you intend to POST as the request body

    Returns:
        List of error strings. Empty list = no issues found.
    """
    errors = []

    if not isinstance(payload, dict):
        return ["payload must be a dict"]

    # -------------------------------------------------------------------------
    # Enum fields
    # -------------------------------------------------------------------------
    if "airframetype" in payload:
        v = payload["airframetype"]
        if v not in VALID_AIRFRAMETYPE:
            errors.append(f"'airframetype': '{v}' not valid. Use one of: {sorted(VALID_AIRFRAMETYPE)}")

    if "maketype" in payload:
        v = payload["maketype"]
        # maketype is case-insensitive in requests
        if v.lower() not in {x.lower() for x in VALID_MAKETYPE}:
            errors.append(f"'maketype': '{v}' not valid. Use one of: {sorted(VALID_MAKETYPE)}")

    if "lifecycle" in payload:
        v = payload["lifecycle"]
        if v not in VALID_LIFECYCLE:
            errors.append(f"'lifecycle': '{v}' not valid. Use one of: {sorted(VALID_LIFECYCLE)}")

    for field in ("isnewaircraft", "ispreownedtrans", "isretailtrans", "isinternaltrans"):
        if field in payload:
            v = payload[field]
            if v not in VALID_TRISTATE:
                errors.append(f"'{field}': '{v}' not valid. Use one of: {sorted(VALID_TRISTATE)}")

    if "forsale" in payload:
        v = payload["forsale"]
        if v not in VALID_FORSALE_REQ:
            errors.append(
                f"'forsale' in request must be '\"true\"', '\"false\"', or '\"\"' (string). "
                f"Got: {repr(v)}"
            )

    # -------------------------------------------------------------------------
    # Date fields -- bulk export accepts datetime with time component
    # -------------------------------------------------------------------------
    is_bulk = "BulkAircraftExport" in endpoint_name
    for date_field in ("startdate", "enddate", "actiondate", "snapshotdate"):
        if date_field in payload:
            val = payload[date_field]
            if not val:
                continue
            if is_bulk:
                # Accept either date-only or full datetime for bulk export
                if not DATE_PATTERN.match(val) and not DATETIME_PATTERN.match(val):
                    errors.append(
                        f"'{date_field}': '{val}' must be MM/DD/YYYY or MM/DD/YYYY HH:MM:SS. "
                        f"For hourly polling include the time: '02/26/2026 10:00:00'"
                    )
            else:
                _check_date(val, date_field, errors)

    # -------------------------------------------------------------------------
    # List fields -- type checks
    # -------------------------------------------------------------------------
    if "modlist" in payload:
        ml = payload["modlist"]
        if not isinstance(ml, list):
            errors.append(f"'modlist' must be a list, got {type(ml).__name__}")
        elif any(not isinstance(x, int) for x in ml):
            errors.append("'modlist' must be a list of integers (model IDs)")
        elif ml:
            known = _load_known_model_ids()
            if known is not None:
                unknown = [x for x in ml if x not in known]
                if unknown:
                    errors.append(
                        f"'modlist': ID(s) {unknown} not found in references/model-id-table.json. "
                        f"Run 'python scripts/model_search.py' to find valid IDs."
                    )

    if "aclist" in payload:
        al = payload["aclist"]
        if not isinstance(al, list):
            errors.append(f"'aclist' must be a list, got {type(al).__name__}")
        elif any(not isinstance(x, int) for x in al):
            errors.append("'aclist' must be a list of integers (aircraft IDs)")

    # -------------------------------------------------------------------------
    # transtype -- ["None"] not [] to get all types; known category values
    # -------------------------------------------------------------------------
    if "transtype" in payload:
        tt = payload["transtype"]
        if isinstance(tt, list) and len(tt) == 0:
            errors.append(
                "'transtype': empty list [] may not return all transaction types. "
                "Use [\"None\"] to get all types."
            )
        elif isinstance(tt, list):
            unknown = [v for v in tt if v not in VALID_TRANSTYPE_CATS]
            if unknown:
                errors.append(
                    f"'transtype': unrecognized value(s) {unknown}. "
                    f"Known categories: {sorted(VALID_TRANSTYPE_CATS)}"
                )

    # -------------------------------------------------------------------------
    # productcode for model endpoints
    # -------------------------------------------------------------------------
    if "productcode" in payload:
        pc = payload["productcode"]
        if isinstance(pc, list) and len(pc) == 0:
            errors.append(
                "'productcode': empty list [] may behave unexpectedly. "
                "Use [\"None\"] to use your subscription's enabled product codes."
            )

    # -------------------------------------------------------------------------
    # getAcCompanyFractionalReportPaged -- fractional-specific checks
    # -------------------------------------------------------------------------
    if "FractionalReport" in endpoint_name:
        if "relationship" in payload:
            rel = payload["relationship"]
            if not isinstance(rel, list):
                errors.append(
                    "'relationship' must be a list of strings, e.g. [\"Fractional Owner\"]. "
                    f"Got: {type(rel).__name__}"
                )
        if "basestate" in payload:
            bs = payload["basestate"]
            if not isinstance(bs, list):
                errors.append(
                    "'basestate' must be a list of state abbreviation strings, e.g. [\"NY\", \"CT\"]. "
                    f"Got: {type(bs).__name__}"
                )
            elif any(not isinstance(s, str) or len(s) != 2 for s in bs if s):
                errors.append(
                    "'basestate' entries should be 2-letter state abbreviations: [\"NY\", \"CT\", \"MA\"]"
                )

    # -------------------------------------------------------------------------
    # Warn if calling a non-paged endpoint name that should be paged
    # -------------------------------------------------------------------------
    base_name = endpoint_name.replace("Paged", "")
    if base_name in MUST_BE_PAGED and "Paged" not in endpoint_name:
        errors.append(
            f"'{endpoint_name}' should be called as '{endpoint_name}Paged' -- "
            f"the non-paged version can timeout on large datasets"
        )

    return errors


def response_key(endpoint_name: str) -> str:
    """Return the expected response data key for a given endpoint name."""
    return RESPONSE_KEYS.get(endpoint_name, "unknown -- check examples/ folder")


if __name__ == "__main__":
    # Quick self-test
    test_cases = [
        ("getHistoryListPaged", {
            "modlist": [145],
            "startdate": "1/1/2024",        # bad date format
            "enddate": "12/31/2024",
            "transtype": [],                # should be ["None"]
            "allrelationships": True,
            "airframetype": "None",
            "maketype": "BusinessJet",
            "lifecycle": "InOperatio",      # typo
            "isnewaircraft": "Ignore",
            "aclist": []
        }),
        ("getAircraftList", {
            "modlist": [145, 634],
            "forsale": True,                # should be string "true"
            "lifecycle": "InOperation",
            "maketype": "BusinessJet",
            "airframetype": "None",
            "aclist": []
        }),
        ("getHistoryList", {               # non-paged -- should warn
            "modlist": [145],
            "startdate": "01/01/2024",
            "enddate": "12/31/2024",
            "aclist": []
        }),
        ("getHistoryListPaged", {          # clean payload -- should pass
            "modlist": [145],
            "startdate": "01/01/2024",
            "enddate": "12/31/2024",
            "transtype": ["None"],
            "allrelationships": True,
            "airframetype": "None",
            "maketype": "None",
            "isnewaircraft": "Ignore",
            "aclist": []
        }),
        ("getAcCompanyFractionalReportPaged", {  # bad: relationship is string, basestate not abbrevs
            "airframetype": "FixedWing",
            "maketype": "BusinessJet",
            "regnbr": "",
            "make": "",
            "actiondate": "2/1/2026",            # bad date format
            "enddate": "02/27/2026",
            "basestate": ["New York", "Connecticut"],  # full names, not abbreviations
            "modlist": [],
            "relationship": "Fractional Owner"   # should be a list
        }),
        ("getAcCompanyFractionalReportPaged", {  # clean payload -- should pass
            "airframetype": "FixedWing",
            "maketype": "BusinessJet",
            "regnbr": "",
            "make": "",
            "actiondate": "02/01/2026",
            "enddate": "02/27/2026",
            "basestate": ["NY", "CT", "MA", "RI", "NJ"],
            "modlist": [],
            "relationship": ["Fractional Owner"]
        }),
    ]

    for name, payload in test_cases:
        errs = validate(name, payload)
        print(f"\n{name}:")
        if errs:
            for e in errs:
                print(f"  ✗ {e}")
        else:
            print(f"  ✓ payload looks valid")
        print(f"  → response key: '{response_key(name)}'")
