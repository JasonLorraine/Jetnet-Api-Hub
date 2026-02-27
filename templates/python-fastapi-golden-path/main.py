import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

from jetnet.session import login, ensure_session, jetnet_request, SessionState

load_dotenv()

session: Optional[SessionState] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global session
    session = login()
    session = ensure_session(session)
    print(f"JETNET session ready (token: {session.api_token[:8]}...)")
    yield
    print("Shutting down.")


app = FastAPI(title="JETNET Golden Path", lifespan=lifespan)


def _days_ago(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).strftime("%m/%d/%Y")


def _today() -> str:
    return datetime.now().strftime("%m/%d/%Y")


def _get_session() -> SessionState:
    global session
    session = ensure_session(session)
    return session


def _build_company_card(rel: dict) -> dict:
    first = rel.get("contactfirstname") or ""
    last = rel.get("contactlastname") or ""
    return {
        "companyId": rel.get("companyid"),
        "name": rel.get("companyname"),
        "city": rel.get("companycity"),
        "state": rel.get("companystateabbr") or rel.get("companystate"),
        "country": rel.get("companycountry"),
        "contact": {
            "fullName": f"{first} {last}".strip(),
            "title": rel.get("contacttitle"),
            "email": rel.get("contactemail"),
            "phone": rel.get("contactbestphone"),
        },
    }


@app.get("/lookup")
def lookup(tail: str = Query(..., description="Aircraft registration / tail number")):
    tail = tail.strip().upper()
    if not tail:
        raise HTTPException(status_code=400, detail="tail query parameter is required")

    s = _get_session()
    ac_data = jetnet_request("GET", f"/api/Aircraft/getRegNumber/{tail}/{{apiToken}}", s)
    ac = ac_data.get("aircraftresult") or {}
    aircraft_id = ac.get("aircraftid")
    if not aircraft_id:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    rels = ac.get("companyrelationships", [])
    owner = None
    operator = None
    for rel in rels:
        relation = rel.get("companyrelation", "")
        if relation == "Owner" and not owner:
            owner = _build_company_card(rel)
        elif relation == "Operator" and not operator:
            operator = _build_company_card(rel)

    page_url = f"http://www.jetnetevolution.com/DisplayAircraftDetail.aspx?acid={aircraft_id}"

    return {
        "aircraftId": aircraft_id,
        "tailNumber": ac.get("regnbr") or tail,
        "make": ac.get("make"),
        "model": ac.get("model"),
        "yearMfr": ac.get("yearmfr"),
        "yearDelivered": ac.get("yeardlv"),
        "categorySize": ac.get("categorysize"),
        "weightClass": ac.get("weightclass"),
        "makeType": ac.get("maketype"),
        "usage": ac.get("usage"),
        "forSale": bool(ac.get("forsale")),
        "baseIcao": ac.get("baseicao"),
        "baseAirport": ac.get("baseairport"),
        "baseCountry": ac.get("basecountry"),
        "owner": owner,
        "operator": operator,
        "jetnetPageUrl": page_url,
        "dataSource": "JETNET",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "session_active": session is not None and not session.is_stale(),
    }
