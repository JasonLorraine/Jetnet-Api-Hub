import os
import time
from datetime import datetime, timedelta
from typing import Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

load_dotenv()

BASE_URL = os.getenv("JETNET_BASE_URL", "https://customer.jetnetconnect.com")
EMAIL = os.getenv("JETNET_EMAIL", "")
PASSWORD = os.getenv("JETNET_PASSWORD", "")

PROACTIVE_REFRESH_SECONDS = 50 * 60

app = FastAPI(title="JETNET Golden Path")

session_state = {
    "bearer_token": None,
    "api_token": None,
    "created_at": 0.0,
}


def _login():
    r = requests.post(
        f"{BASE_URL}/api/Admin/APILogin",
        json={"emailAddress": EMAIL, "password": PASSWORD},
    )
    r.raise_for_status()
    data = r.json()
    _check_responsestatus(data)
    bearer = data.get("bearerToken")
    api_token = data.get("apiToken") or data.get("securityToken")
    if not bearer or not api_token:
        raise RuntimeError("Login succeeded but tokens missing from response.")
    session_state["bearer_token"] = bearer
    session_state["api_token"] = api_token
    session_state["created_at"] = time.time()


def _check_responsestatus(data: dict):
    if not isinstance(data, dict):
        return
    status = str(data.get("responsestatus", "")).upper()
    if "ERROR" in status:
        if "INVALID SECURITY TOKEN" in status:
            raise PermissionError(data["responsestatus"])
        raise RuntimeError(data["responsestatus"])
    if "type" in data and "title" in data and "status" in data:
        raise RuntimeError(f"{data['title']} (status={data['status']})")


def _ensure_session():
    token_age = time.time() - session_state["created_at"]
    if not session_state["bearer_token"] or token_age >= PROACTIVE_REFRESH_SECONDS:
        _login()
        return
    try:
        url = f"{BASE_URL}/api/Utility/getAccountInfo/{session_state['api_token']}"
        headers = {
            "Authorization": f"Bearer {session_state['bearer_token']}",
            "Content-Type": "application/json",
        }
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        _check_responsestatus(r.json())
    except Exception:
        _login()


def _jetnet_request(method: str, path: str, body: Optional[dict] = None) -> dict:
    _ensure_session()
    try:
        return _do_request(method, path, body)
    except PermissionError:
        _login()
        return _do_request(method, path, body)


def _do_request(method: str, path: str, body: Optional[dict] = None) -> dict:
    url = f"{BASE_URL}{path}".replace("{apiToken}", session_state["api_token"] or "")
    headers = {
        "Authorization": f"Bearer {session_state['bearer_token'] or ''}",
        "Content-Type": "application/json",
    }
    r = requests.request(method, url, headers=headers, json=body)
    r.raise_for_status()
    data = r.json()
    _check_responsestatus(data)
    return data


def _days_ago(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).strftime("%m/%d/%Y")


def _today() -> str:
    return datetime.now().strftime("%m/%d/%Y")


def _build_aircraft_card(ac: dict) -> dict:
    return {
        "aircraftId": ac.get("aircraftid"),
        "regNbr": ac.get("regnbr"),
        "serialNbr": ac.get("serialnbr", ""),
        "make": ac.get("make"),
        "model": ac.get("model"),
        "year": ac.get("yearmfr") or ac.get("yeardlv"),
        "ownerCompanyId": None,
        "operatorCompanyId": None,
    }


def _build_company_card(rel: dict) -> dict:
    return {
        "companyId": rel.get("companyid") or rel.get("company", {}).get("companyid"),
        "companyName": rel.get("name") or rel.get("company", {}).get("name"),
        "segment": None,
        "location": None,
        "primaryPhone": None,
    }


@app.get("/lookup")
def lookup(tail: str = Query(..., description="Aircraft registration / tail number")):
    tail = tail.strip().upper()
    if not tail:
        raise HTTPException(status_code=400, detail="tail query parameter is required")

    ac_data = _jetnet_request("GET", f"/api/Aircraft/getRegNumber/{tail}/{{apiToken}}")
    ac = ac_data.get("aircraftresult") or {}
    aircraft_id = ac.get("aircraftid")
    if not aircraft_id:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    aircraft_card = _build_aircraft_card(ac)

    rels_data = _jetnet_request(
        "POST",
        "/api/Aircraft/getRelationships/{apiToken}",
        {
            "aircraftid": aircraft_id,
            "aclist": [],
            "modlist": [],
            "actiondate": "",
            "showHistoricalAcRefs": False,
        },
    )

    owner = None
    operator = None
    for rel in rels_data.get("relationships", []):
        if rel.get("relationtype") == "Owner" and rel.get("relationseqno") == 1:
            owner = _build_company_card(rel)
            aircraft_card["ownerCompanyId"] = owner["companyId"]
        elif rel.get("relationtype") == "Operator" and rel.get("relationseqno") == 1:
            operator = _build_company_card(rel)
            aircraft_card["operatorCompanyId"] = operator["companyId"]

    flights_data = _jetnet_request(
        "POST",
        "/api/Aircraft/getFlightDataPaged/{apiToken}/100/1",
        {
            "aircraftid": aircraft_id,
            "startdate": _days_ago(180),
            "enddate": _today(),
            "origin": "",
            "destination": "",
            "aclist": [],
            "modlist": [],
            "exactMatchReg": True,
        },
    )

    flight_list = flights_data.get("flightdata") or []
    utilization = None
    if flight_list:
        utilization = {
            "periodDays": 180,
            "totalFlights": len(flight_list),
        }

    return {
        "aircraft": aircraft_card,
        "owner": owner,
        "operator": operator,
        "utilization": utilization,
        "_debug": {
            "endpoints": [
                "getRegNumber",
                "getRelationships",
                "getFlightDataPaged",
            ],
            "rawResponsestatuses": [
                ac_data.get("responsestatus", ""),
                rels_data.get("responsestatus", ""),
                flights_data.get("responsestatus", ""),
            ],
        },
    }
