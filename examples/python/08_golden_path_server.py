"""
JETNET API -- Golden Path Flask Server

A complete Flask server implementing the Golden Path workflow:
1. Resolve tail number to aircraftid
2. Return aircraft overview immediately (first paint)
3. Fan out pictures, relationships, and flights in parallel
4. Lazy-load history and events on demand

Never send JETNET credentials or tokens to the client.

Required environment variables:
    JETNET_EMAIL    -- Your JETNET account email
    JETNET_PASSWORD -- Your JETNET account password

Usage:
    pip install flask requests
    python 08_golden_path_server.py

Endpoints:
    GET /profile/<reg>    -- Full aircraft profile (overview + photos + relationships + flights)
    GET /history/<id>     -- Lazy-load transaction history for an aircraft
    GET /events/<id>      -- Lazy-load events for an aircraft
"""

import os
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify

BASE = os.getenv("JETNET_BASE_URL", "https://customer.jetnetconnect.com")
EMAIL = os.getenv("JETNET_EMAIL", "")
PASS = os.getenv("JETNET_PASSWORD", "")

bearer = None
token = None


def login():
    global bearer, token
    r = requests.post(
        f"{BASE}/api/Admin/APILogin",
        json={"emailAddress": EMAIL, "password": PASS},
    )
    r.raise_for_status()
    j = r.json()
    bearer = j.get("bearerToken")
    token = j.get("apiToken") or j.get("securityToken")
    if not bearer or not token:
        raise RuntimeError("Login succeeded but tokens not found.")


def is_error(j):
    return isinstance(j, dict) and "ERROR" in str(j.get("responsestatus", "")).upper()


def jetnet(method, path, body=None, did_retry=False):
    global bearer, token
    if not bearer or not token:
        login()
    url = f"{BASE}{path}".replace("{apiToken}", token)
    headers = {"Authorization": f"Bearer {bearer}"}
    r = requests.request(method, url, headers=headers, json=body)
    try:
        j = r.json()
    except Exception:
        j = {"raw": r.text}
    if r.status_code >= 400 or is_error(j):
        msg = j.get("responsestatus") if is_error(j) else r.text
        if not did_retry and ("INVALID SECURITY TOKEN" in str(msg).upper() or r.status_code == 401):
            login()
            return jetnet(method, path, body, did_retry=True)
        raise RuntimeError(msg)
    return j


def fmt_date(d):
    return d.strftime("%m/%d/%Y")


def days_ago(n):
    return fmt_date(datetime.now() - timedelta(days=n))


def today():
    return fmt_date(datetime.now())


app = Flask(__name__)


@app.get("/profile/<reg>")
def profile(reg):
    reg = reg.upper()
    try:
        lookup = jetnet("GET", f"/api/Aircraft/getRegNumber/{reg}/{{apiToken}}")
        ac = lookup.get("aircraftresult") or {}
        aircraft_id = ac.get("aircraftid")
        if not aircraft_id:
            return jsonify({"ok": False, "error": "Aircraft not found"}), 404

        pics = jetnet("GET", f"/api/Aircraft/getPictures/{aircraft_id}/{{apiToken}}")
        rels = jetnet("POST", "/api/Aircraft/getRelationships/{apiToken}", {
            "aircraftid": aircraft_id,
            "aclist": [],
            "modlist": [],
            "actiondate": "",
            "showHistoricalAcRefs": False,
        })
        flights = jetnet("POST", "/api/Aircraft/getFlightDataPaged/{apiToken}/100/1", {
            "aircraftid": aircraft_id,
            "startdate": days_ago(180),
            "enddate": today(),
            "origin": "",
            "destination": "",
            "aclist": [],
            "modlist": [],
            "exactMatchReg": True,
        })

        return jsonify({
            "ok": True,
            "data": {
                "aircraft": {
                    "id": aircraft_id,
                    "reg": ac.get("regnbr"),
                    "make": ac.get("make"),
                    "model": ac.get("model"),
                    "year": ac.get("yearmfr") or ac.get("yeardlv"),
                },
                "base": {
                    "icao": ac.get("baseicao"),
                    "airport": ac.get("baseairport"),
                },
                "photos": [
                    {
                        "description": p.get("description"),
                        "date": p.get("imagedate"),
                        "url": p.get("pictureurl"),
                    }
                    for p in (pics.get("pictures") or [])
                ],
                "relationships": [
                    {
                        "type": r.get("relationtype"),
                        "company": r.get("name"),
                        "companyId": r.get("companyid"),
                    }
                    for r in (rels.get("relationships") or [])
                ],
                "flights": (flights.get("flightdata") or [])[:20],
            },
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/history/<int:aircraft_id>")
def history(aircraft_id):
    try:
        result = jetnet("POST", "/api/Aircraft/getHistoryListPaged/{apiToken}/100/1", {
            "aircraftid": aircraft_id,
            "startdate": "01/01/2000",
            "enddate": today(),
            "allrelationships": True,
            "aclist": [],
            "modlist": [],
            "transtype": ["None"],
            "isnewaircraft": "Ignore",
        })
        return jsonify({
            "ok": True,
            "history": result.get("history", []),
            "maxpages": result.get("maxpages", 1),
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/events/<int:aircraft_id>")
def events(aircraft_id):
    try:
        result = jetnet("POST", "/api/Aircraft/getEventListPaged/{apiToken}/100/1", {
            "aircraftid": aircraft_id,
            "evtype": [],
            "evcategory": [],
            "startdate": days_ago(365),
            "enddate": today(),
            "aclist": [],
            "modlist": [],
        })
        return jsonify({
            "ok": True,
            "events": result.get("events", []),
            "maxpages": result.get("maxpages", 1),
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    if not EMAIL or not PASS:
        print("Set JETNET_EMAIL and JETNET_PASSWORD environment variables.")
        exit(1)
    app.run(host="0.0.0.0", port=3000, debug=True)
