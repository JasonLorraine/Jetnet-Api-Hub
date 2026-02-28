"""
JETNET MCP Server — jetnet_mcp
===============================
Model Context Protocol server for the JETNET API (Jetnet Connect).
Enables AI agents (Claude, Cursor, Copilot) to query aviation intelligence
data natively: aircraft lookups, ownership, flight activity, fleet search,
market trends, and more.

Install:
    pip install mcp httpx pydantic

Run (stdio — for Claude Desktop, Cursor, etc.):
    JETNET_EMAIL=you@co.com JETNET_PASSWORD=secret python jetnet_mcp.py

Run (HTTP — for remote/multi-client):
    TRANSPORT=http JETNET_EMAIL=you@co.com JETNET_PASSWORD=secret python jetnet_mcp.py
"""

from __future__ import annotations

import json
import os
import sys
import time
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("jetnet_mcp")

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

BASE_URL = os.environ.get("JETNET_BASE_URL", "https://customer.jetnetconnect.com")
TOKEN_TTL_SECONDS = 50 * 60
DEFAULT_PAGESIZE = 100
MAX_PAGES = 50
CHARACTER_LIMIT = 50_000

logger = logging.getLogger("jetnet_mcp")

LIST_KEYS = frozenset({
    "history", "flightdata", "events", "aircraft",
    "aircraftowneroperators", "companylist", "contactlist",
    "relationships", "aircraftcompfractionalrefs", "pictures",
})


class JetnetSession:
    """Manages JETNET authentication and token lifecycle."""

    def __init__(self) -> None:
        self.bearer: str = ""
        self.api_token: str = ""
        self.login_time: float = 0.0
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)

    @property
    def is_expired(self) -> bool:
        return time.time() - self.login_time > TOKEN_TTL_SECONDS

    async def login(self) -> None:
        email = os.environ.get("JETNET_EMAIL", "")
        password = os.environ.get("JETNET_PASSWORD", "")
        if not email or not password:
            raise ValueError(
                "Missing JETNET credentials. Set JETNET_EMAIL and JETNET_PASSWORD "
                "environment variables."
            )
        resp = await self.client.post(
            "/api/Admin/APILogin",
            json={"emailAddress": email, "password": password},
        )
        resp.raise_for_status()
        data = resp.json()
        self.bearer = data["bearerToken"]
        self.api_token = data["apiToken"]
        self.login_time = time.time()
        logger.info("JETNET login successful. Token: %s...", self.api_token[:8])

    async def ensure_valid(self) -> None:
        if not self.bearer or self.is_expired:
            await self.login()

    async def request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        await self.ensure_valid()

        url = path.replace("{apiToken}", self.api_token)
        headers = {"Authorization": f"Bearer {self.bearer}"}

        resp = await self.client.request(method, url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()

        status = data.get("responsestatus", "")
        if "INVALID SECURITY TOKEN" in status.upper():
            await self.login()
            url = path.replace("{apiToken}", self.api_token)
            headers = {"Authorization": f"Bearer {self.bearer}"}
            resp = await self.client.request(method, url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            status = data.get("responsestatus", "")

        if "ERROR" in status.upper():
            raise ValueError(f"JETNET API error: {status}")

        return data

    async def get_all_pages(
        self,
        path: str,
        body: Dict[str, Any],
        pagesize: int = DEFAULT_PAGESIZE,
        max_pages: int = MAX_PAGES,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        page = 1
        while page <= max_pages:
            data = await self.request("POST", f"{path}/{pagesize}/{page}", body)
            for key in LIST_KEYS:
                if key in data and isinstance(data[key], list):
                    results.extend(data[key])
                    break
            if page >= data.get("maxpages", 1):
                break
            page += 1
        return results

    async def close(self) -> None:
        await self.client.aclose()


@asynccontextmanager
async def jetnet_lifespan():
    session = JetnetSession()
    try:
        await session.login()
        yield {"session": session}
    finally:
        await session.close()


mcp = FastMCP("jetnet_mcp", lifespan=jetnet_lifespan)


class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


class AirframeType(str, Enum):
    NONE = "None"
    FIXED_WING = "FixedWing"
    ROTARY = "Rotary"


class MakeType(str, Enum):
    NONE = "None"
    JET_AIRLINER = "JetAirliner"
    BUSINESS_JET = "BusinessJet"
    TURBOPROP = "Turboprop"
    PISTON = "Piston"
    TURBINE = "Turbine"


def _truncate(text: str) -> str:
    if len(text) <= CHARACTER_LIMIT:
        return text
    return text[:CHARACTER_LIMIT] + "\n\n[... truncated — use pagination or filters to narrow results]"


def _format_aircraft_md(ac: Dict[str, Any]) -> str:
    reg = ac.get("regnbr", "N/A")
    make = ac.get("make", "")
    model = ac.get("model", "")
    sn = ac.get("serialnbr", "N/A")
    yom = ac.get("yearofmfr", "N/A")
    status = ac.get("lifecyclestatus", "N/A")
    forsale = ac.get("forsale", "false")
    aid = ac.get("aircraftid", "")
    lines = [
        f"## {reg} — {make} {model}",
        f"- **Aircraft ID**: {aid}",
        f"- **Serial Number**: {sn}",
        f"- **Year**: {yom}",
        f"- **Lifecycle**: {status}",
        f"- **For Sale**: {forsale}",
    ]
    return "\n".join(lines)


def _get_session(ctx) -> JetnetSession:
    return ctx.request_context.lifespan_state["session"]


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: TAIL NUMBER LOOKUP (Golden Path — Step 1)
# ═══════════════════════════════════════════════════════════════════════════════

class TailLookupInput(BaseModel):
    """Look up an aircraft by tail/registration number."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    registration: str = Field(
        ...,
        description="Aircraft tail/registration number (e.g., 'N650GD', 'C-GLBR', 'VP-BDJ')",
        min_length=1,
        max_length=20,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data",
    )

    @field_validator("registration")
    @classmethod
    def clean_registration(cls, v: str) -> str:
        return v.upper().strip()


@mcp.tool(
    name="jetnet_lookup_aircraft",
    annotations={
        "title": "Look Up Aircraft by Tail Number",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_lookup_aircraft(params: TailLookupInput, ctx=None) -> str:
    """Look up an aircraft by tail/registration number. Returns aircraft details
    including make, model, serial number, year, lifecycle status, and owner/operator
    relationships. This is the starting point for most JETNET workflows — the returned
    aircraftid is the join key for all other endpoints (pictures, relationships,
    flight data, history).

    Args:
        params: TailLookupInput with registration number and response format.

    Returns:
        Aircraft profile with specifications and current owner/operator info.
        The aircraftid field is needed for subsequent calls to other JETNET tools.
    """
    session = _get_session(ctx)
    reg = params.registration

    data = await session.request("GET", f"/api/Aircraft/getRegNumber/{reg}/{{apiToken}}")
    ac = data.get("aircraftresult", {})

    if not ac:
        return f"No aircraft found for registration '{reg}'. Check the tail number and try again."

    if params.response_format == ResponseFormat.JSON:
        return json.dumps(ac, indent=2, default=str)

    return _format_aircraft_md(ac)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: GET RELATIONSHIPS (Golden Path — Step 2)
# ═══════════════════════════════════════════════════════════════════════════════

class RelationshipsInput(BaseModel):
    """Get owner/operator/manager relationships for an aircraft."""
    model_config = ConfigDict(extra="forbid")

    aircraftid: int = Field(
        ...,
        description="JETNET aircraft ID (get this from jetnet_lookup_aircraft first)",
        gt=0,
    )
    show_historical: bool = Field(
        default=False,
        description="Include historical relationships (previous owners). Default: current only.",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


@mcp.tool(
    name="jetnet_get_relationships",
    annotations={
        "title": "Get Aircraft Owner/Operator Relationships",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_get_relationships(params: RelationshipsInput, ctx=None) -> str:
    """Get owner, operator, and manager relationships for an aircraft.
    Requires an aircraftid from jetnet_lookup_aircraft.

    Returns company names, contact info, and relationship types
    (Owner, Operator, Manager, Trustee, etc.).
    """
    session = _get_session(ctx)

    body = {
        "aircraftid": params.aircraftid,
        "aclist": [params.aircraftid],
        "modlist": [],
        "actiondate": "",
        "showHistoricalAcRefs": params.show_historical,
    }
    data = await session.request("POST", "/api/Aircraft/getRelationships/{apiToken}", body)
    rels = data.get("relationships", [])

    if not rels:
        return f"No relationships found for aircraft ID {params.aircraftid}."

    if params.response_format == ResponseFormat.JSON:
        return _truncate(json.dumps(rels, indent=2, default=str))

    lines = [f"## Relationships for Aircraft ID {params.aircraftid}", ""]
    for r in rels:
        rtype = r.get("relationtype", "Unknown")
        name = r.get("name", "N/A")
        city = r.get("company", {}).get("city", "")
        state = r.get("company", {}).get("state", "")
        country = r.get("company", {}).get("country", "")
        loc = ", ".join(filter(None, [city, state, country]))
        lines.append(f"- **{rtype}**: {name}" + (f" ({loc})" if loc else ""))

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: FLIGHT ACTIVITY (Golden Path — Step 2, parallel)
# ═══════════════════════════════════════════════════════════════════════════════

class FlightDataInput(BaseModel):
    """Query flight activity for an aircraft."""
    model_config = ConfigDict(extra="forbid")

    aircraftid: int = Field(
        ..., description="JETNET aircraft ID", gt=0,
    )
    start_date: str = Field(
        ...,
        description="Start date in MM/DD/YYYY format with leading zeros (e.g., '01/01/2024')",
        pattern=r"^\d{2}/\d{2}/\d{4}$",
    )
    end_date: str = Field(
        ...,
        description="End date in MM/DD/YYYY format with leading zeros (e.g., '12/31/2024')",
        pattern=r"^\d{2}/\d{2}/\d{4}$",
    )
    max_records: int = Field(
        default=50,
        description="Maximum flight records to return (default: 50, max: 500)",
        ge=1, le=500,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format",
    )


@mcp.tool(
    name="jetnet_get_flight_data",
    annotations={
        "title": "Get Aircraft Flight Activity",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_get_flight_data(params: FlightDataInput, ctx=None) -> str:
    """Get flight activity records for an aircraft within a date range.
    Returns departure/arrival airports, flight dates, and utilization data.

    IMPORTANT: Dates must be MM/DD/YYYY with leading zeros.
    Use '01/01/2024' not '1/1/2024'.
    """
    session = _get_session(ctx)

    body = {
        "aclist": [params.aircraftid],
        "modlist": [],
        "startdate": params.start_date,
        "enddate": params.end_date,
    }

    pagesize = min(params.max_records, DEFAULT_PAGESIZE)
    max_p = (params.max_records // pagesize) + 1

    flights = await session.get_all_pages(
        "/api/Aircraft/getFlightDataPaged/{apiToken}",
        body, pagesize=pagesize, max_pages=max_p,
    )

    flights = flights[:params.max_records]

    if not flights:
        return f"No flight data found for aircraft {params.aircraftid} between {params.start_date} and {params.end_date}."

    if params.response_format == ResponseFormat.JSON:
        return _truncate(json.dumps(flights, indent=2, default=str))

    lines = [f"## Flight Activity — Aircraft {params.aircraftid}", f"**Period**: {params.start_date} to {params.end_date} | **Records**: {len(flights)}", ""]
    for f in flights[:20]:
        dep = f.get("departureicao", "????")
        arr = f.get("arrivalicao", "????")
        dt = f.get("flightdate", "")
        lines.append(f"- {dt}: {dep} → {arr}")
    if len(flights) > 20:
        lines.append(f"\n*...and {len(flights) - 20} more flights. Use json format for complete data.*")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: FLEET SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

class FleetSearchInput(BaseModel):
    """Search for aircraft by model, make, and filters."""
    model_config = ConfigDict(extra="forbid")

    modlist: List[int] = Field(
        default_factory=list,
        description="Model IDs to filter by (e.g., [145] for G550, [278] for G650). Empty = all models. Use jetnet_search_models to find model IDs.",
        max_length=50,
    )
    for_sale: Optional[str] = Field(
        default=None,
        description="Filter by for-sale status: 'true', 'false', or None/empty for all",
        pattern=r"^(true|false)?$",
    )
    airframe_type: AirframeType = Field(
        default=AirframeType.NONE,
        description="Airframe type filter: None (all), FixedWing, or Rotary",
    )
    make_type: MakeType = Field(
        default=MakeType.NONE,
        description="Make type filter: None (all), BusinessJet, Turboprop, JetAirliner, Piston, Turbine",
    )
    country: str = Field(
        default="",
        description="Country filter (e.g., 'United States', 'Canada', 'Brazil'). Empty = all countries.",
    )
    max_results: int = Field(
        default=25,
        description="Maximum aircraft to return (default: 25, max: 200)",
        ge=1, le=200,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format",
    )


@mcp.tool(
    name="jetnet_search_fleet",
    annotations={
        "title": "Search Aircraft Fleet / Inventory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_search_fleet(params: FleetSearchInput, ctx=None) -> str:
    """Search the JETNET fleet database by model, make type, for-sale status,
    and country. Use this to find aircraft inventory, for-sale listings, or
    fleet composition by type.

    NOTE: getAircraftList is NOT paged — use filters to control result size.
    To find model IDs for the modlist parameter, use jetnet_search_models first.

    Common model IDs: G550=145, G650=278, Citation XLS+=326, Challenger 350=634,
    Global 7500=753, Falcon 8X=704, King Air 350=255.
    """
    session = _get_session(ctx)

    body: Dict[str, Any] = {
        "modlist": params.modlist,
        "aclist": [],
        "airframetype": params.airframe_type.value,
        "maketype": params.make_type.value,
        "forsale": params.for_sale or "",
        "country": params.country,
        "lifecycle": "None",
        "isnewaircraft": "Ignore",
    }

    data = await session.request("POST", "/api/Aircraft/getAircraftList/{apiToken}", body)
    aircraft = data.get("aircraft", [])[:params.max_results]

    if not aircraft:
        return "No aircraft found matching those filters. Try broader criteria or check model IDs."

    count = data.get("count", len(aircraft))

    if params.response_format == ResponseFormat.JSON:
        return _truncate(json.dumps({"total": count, "aircraft": aircraft}, indent=2, default=str))

    lines = [f"## Fleet Search Results", f"**Total matching**: {count} | **Showing**: {len(aircraft)}", ""]
    for ac in aircraft:
        reg = ac.get("regnbr", "N/A")
        make = ac.get("make", "")
        model = ac.get("model", "")
        yom = ac.get("yearofmfr", "")
        forsale = "For Sale" if ac.get("forsale") == "true" else ""
        lines.append(f"- **{reg}** — {make} {model} ({yom}) {forsale}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: TRANSACTION HISTORY
# ═══════════════════════════════════════════════════════════════════════════════

class HistoryInput(BaseModel):
    """Query aircraft transaction history."""
    model_config = ConfigDict(extra="forbid")

    modlist: List[int] = Field(
        default_factory=list,
        description="Model IDs to filter by. Empty = all models.",
    )
    aclist: List[int] = Field(
        default_factory=list,
        description="Specific aircraft IDs. Empty = all aircraft matching modlist.",
    )
    start_date: str = Field(
        ..., description="Start date MM/DD/YYYY", pattern=r"^\d{2}/\d{2}/\d{4}$",
    )
    end_date: str = Field(
        ..., description="End date MM/DD/YYYY", pattern=r"^\d{2}/\d{2}/\d{4}$",
    )
    max_records: int = Field(
        default=50, description="Max records (default 50, max 500)", ge=1, le=500,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format",
    )


@mcp.tool(
    name="jetnet_get_history",
    annotations={
        "title": "Get Aircraft Transaction History",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_get_history(params: HistoryInput, ctx=None) -> str:
    """Get transaction history (sales, deliveries, registrations) for aircraft.
    Filter by model IDs and/or specific aircraft IDs within a date range.

    IMPORTANT: Use transtype '["None"]' to get ALL transaction types.
    Dates must be MM/DD/YYYY with leading zeros.
    """
    session = _get_session(ctx)

    body = {
        "modlist": params.modlist,
        "aclist": params.aclist,
        "startdate": params.start_date,
        "enddate": params.end_date,
        "transtype": ["None"],
        "allrelationships": False,
        "airframetype": "None",
        "maketype": "None",
        "isnewaircraft": "Ignore",
    }

    pagesize = min(params.max_records, DEFAULT_PAGESIZE)
    max_p = (params.max_records // pagesize) + 1

    history = await session.get_all_pages(
        "/api/Aircraft/getHistoryListPaged/{apiToken}",
        body, pagesize=pagesize, max_pages=max_p,
    )
    history = history[:params.max_records]

    if not history:
        return "No transaction history found for those filters and date range."

    if params.response_format == ResponseFormat.JSON:
        return _truncate(json.dumps(history, indent=2, default=str))

    lines = [f"## Transaction History", f"**Period**: {params.start_date} to {params.end_date} | **Records**: {len(history)}", ""]
    for h in history[:25]:
        reg = h.get("regnbr", "N/A")
        trans = h.get("transtype", "N/A")
        date = h.get("transdate", "")
        buyer = h.get("name", "N/A")
        lines.append(f"- {date}: **{reg}** — {trans} → {buyer}")
    if len(history) > 25:
        lines.append(f"\n*...and {len(history) - 25} more. Use json format for complete data.*")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: MARKET TRENDS
# ═══════════════════════════════════════════════════════════════════════════════

class MarketTrendsInput(BaseModel):
    """Query market trends for an aircraft model."""
    model_config = ConfigDict(extra="forbid")

    modelid: int = Field(
        ..., description="JETNET model ID (e.g., 145 for G550, 278 for G650). Use jetnet_search_models to find IDs.", gt=0,
    )
    start_date: str = Field(
        ..., description="Start date MM/DD/YYYY", pattern=r"^\d{2}/\d{2}/\d{4}$",
    )
    end_date: str = Field(
        ..., description="End date MM/DD/YYYY", pattern=r"^\d{2}/\d{2}/\d{4}$",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format",
    )


@mcp.tool(
    name="jetnet_get_market_trends",
    annotations={
        "title": "Get Model Market Trends",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_get_market_trends(params: MarketTrendsInput, ctx=None) -> str:
    """Get market trends for an aircraft model: for-sale count, average asking
    price, days on market, and inventory levels over time.

    Perfect for valuation research, market analysis, and investment diligence.
    """
    session = _get_session(ctx)

    body = {
        "modelid": params.modelid,
        "startdate": params.start_date,
        "enddate": params.end_date,
    }

    data = await session.request("POST", "/api/Model/getModelMarketTrends/{apiToken}", body)

    if params.response_format == ResponseFormat.JSON:
        return _truncate(json.dumps(data, indent=2, default=str))

    trends = data.get("modelmarkettrends", data.get("trends", []))
    if not trends:
        return f"No market trend data found for model {params.modelid} in that date range."

    lines = [f"## Market Trends — Model {params.modelid}", ""]
    if isinstance(trends, list):
        for t in trends:
            period = t.get("period", t.get("date", "N/A"))
            fs_count = t.get("forsalecount", "N/A")
            avg_price = t.get("avgaskingprice", "N/A")
            dom = t.get("avgdaysonmarket", "N/A")
            lines.append(f"- **{period}**: {fs_count} for sale, avg ${avg_price:,.0f}, {dom} days on market" if isinstance(avg_price, (int, float)) else f"- **{period}**: {fs_count} for sale, avg {avg_price}, {dom} days on market")
    else:
        lines.append(json.dumps(trends, indent=2, default=str))

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: MODEL SEARCH (Utility — find model IDs)
# ═══════════════════════════════════════════════════════════════════════════════

class ModelSearchInput(BaseModel):
    """Search for JETNET model IDs by name."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    query: str = Field(
        ...,
        description="Search term: model name, make, or ICAO code (e.g., 'G550', 'Citation', 'GLF5', 'Challenger')",
        min_length=2,
        max_length=50,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format",
    )


@mcp.tool(
    name="jetnet_search_models",
    annotations={
        "title": "Search Aircraft Model IDs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_search_models(params: ModelSearchInput, ctx=None) -> str:
    """Search the JETNET model reference table for model IDs (AMODID values).
    Use the returned model IDs in the modlist parameter of other tools.

    Example: Search 'G550' → returns AMODID=145 which you use as modlist=[145].
    """
    session = _get_session(ctx)

    data = await session.request("GET", "/api/Utility/getAircraftModelList/{apiToken}")
    models = data.get("models", data.get("aircraftmodellist", []))

    if not models:
        return "Could not retrieve model list. The utility endpoint may be unavailable."

    query_lower = params.query.lower()
    matches = [
        m for m in models
        if query_lower in str(m.get("model", "")).lower()
        or query_lower in str(m.get("make", "")).lower()
        or query_lower in str(m.get("icaocode", "")).lower()
        or query_lower in str(m.get("makemodelname", "")).lower()
    ]

    if not matches:
        return f"No models found matching '{params.query}'. Try a broader search (e.g., 'Gulfstream' instead of 'G-550')."

    if params.response_format == ResponseFormat.JSON:
        return json.dumps(matches[:50], indent=2, default=str)

    lines = [f"## Model Search: '{params.query}'", f"**Matches**: {len(matches)}", ""]
    for m in matches[:30]:
        mid = m.get("amodid", m.get("modelid", "?"))
        make = m.get("make", "")
        model = m.get("model", "")
        icao = m.get("icaocode", "")
        mtype = m.get("maketype", "")
        lines.append(f"- **AMODID={mid}** — {make} {model}" + (f" (ICAO: {icao})" if icao else "") + (f" [{mtype}]" if mtype else ""))

    if len(matches) > 30:
        lines.append(f"\n*...{len(matches) - 30} more. Use json format for complete list.*")

    lines.append(f"\n**Usage**: Use the AMODID values in `modlist` parameter of other tools.")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: FLEET SNAPSHOT (getCondensedSnapshot)
# ═══════════════════════════════════════════════════════════════════════════════

class SnapshotInput(BaseModel):
    """Get fleet snapshot at a point in time."""
    model_config = ConfigDict(extra="forbid")

    modlist: List[int] = Field(
        default_factory=list,
        description="Model IDs to filter by. Empty = all models.",
    )
    snapshot_date: str = Field(
        ...,
        description="Snapshot date MM/DD/YYYY (e.g., '01/01/2025')",
        pattern=r"^\d{2}/\d{2}/\d{4}$",
    )
    country: str = Field(
        default="",
        description="Country filter. Empty = all countries.",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format",
    )


@mcp.tool(
    name="jetnet_get_snapshot",
    annotations={
        "title": "Get Fleet Snapshot at Point in Time",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_get_snapshot(params: SnapshotInput, ctx=None) -> str:
    """Get a condensed fleet snapshot at a specific point in time.
    Shows fleet size, for-sale count, and composition for a model
    on a given date. Perfect for year-over-year fleet comparisons
    and historical fleet analysis.
    """
    session = _get_session(ctx)
    body = {
        "modlist": params.modlist,
        "snapshotdate": params.snapshot_date,
        "country": params.country,
        "airframetype": "None",
        "maketype": "None",
    }
    data = await session.request(
        "POST", "/api/Aircraft/getCondensedSnapshot/{apiToken}", body
    )
    if params.response_format == ResponseFormat.JSON:
        return _truncate(json.dumps(data, indent=2, default=str))

    snapshot = data.get("snapshotowneroperators", data.get("snapshot", []))
    lines = ["## Fleet Snapshot", f"**Date**: {params.snapshot_date}", ""]
    if isinstance(snapshot, list):
        lines.append(f"**Records**: {len(snapshot)}")
        for item in snapshot[:20]:
            lines.append(f"- {json.dumps(item, default=str)}")
        if len(snapshot) > 20:
            lines.append(f"\n*...{len(snapshot) - 20} more. Use json format for complete list.*")
    elif isinstance(snapshot, dict):
        for k, v in snapshot.items():
            if k != "responsestatus":
                lines.append(f"- **{k}**: {v}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: MODEL SPECS (getModelPerformanceSpecs)
# ═══════════════════════════════════════════════════════════════════════════════

class ModelSpecsInput(BaseModel):
    """Get performance specifications for an aircraft model."""
    model_config = ConfigDict(extra="forbid")

    modelid: int = Field(
        ..., description="JETNET model ID. Use jetnet_search_models to find it.", gt=0,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format",
    )


@mcp.tool(
    name="jetnet_get_model_specs",
    annotations={
        "title": "Get Aircraft Model Specifications",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_get_model_specs(params: ModelSpecsInput, ctx=None) -> str:
    """Get performance specifications for an aircraft model: range, speed,
    cabin dimensions, max passengers, payload, and engine details.

    Use jetnet_search_models first to find the modelid.
    """
    session = _get_session(ctx)
    body = {"modelid": params.modelid}
    data = await session.request(
        "POST", "/api/Model/getModelPerformanceSpecs/{apiToken}", body
    )
    if params.response_format == ResponseFormat.JSON:
        return _truncate(json.dumps(data, indent=2, default=str))

    specs = data.get("specs", data.get("modelperformancespecs", data))
    lines = [f"## Model Specifications -- Model {params.modelid}", ""]
    if isinstance(specs, dict):
        for k, v in specs.items():
            if k != "responsestatus" and v:
                label = k.replace("_", " ").title()
                lines.append(f"- **{label}**: {v}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════

class HealthCheckInput(BaseModel):
    """Check JETNET connection health."""
    model_config = ConfigDict(extra="forbid")


@mcp.tool(
    name="jetnet_health_check",
    annotations={
        "title": "Check JETNET Connection",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_health_check(params: HealthCheckInput, ctx=None) -> str:
    """Check if JETNET credentials are valid and the API is reachable.
    Call this first if other tools are returning errors.
    """
    session = _get_session(ctx)
    try:
        await session.ensure_valid()
        data = await session.request(
            "GET", "/api/Admin/getAccountInfo/{apiToken}"
        )
        return f"Connected to JETNET. Token valid. Account: {json.dumps(data, indent=2, default=str)}"
    except Exception as e:
        return f"Connection failed: {str(e)}. Check JETNET_EMAIL and JETNET_PASSWORD."


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL: GOLDEN PATH (Composite — full aircraft profile)
# ═══════════════════════════════════════════════════════════════════════════════

class GoldenPathInput(BaseModel):
    """Complete aircraft profile lookup via the Golden Path workflow."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    registration: str = Field(
        ..., description="Tail/registration number (e.g., 'N650GD')", min_length=1, max_length=20,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format",
    )

    @field_validator("registration")
    @classmethod
    def clean_reg(cls, v: str) -> str:
        return v.upper().strip()


@mcp.tool(
    name="jetnet_golden_path",
    annotations={
        "title": "Complete Aircraft Profile (Golden Path)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_golden_path(params: GoldenPathInput, ctx=None) -> str:
    """Execute the JETNET Golden Path: look up an aircraft by tail number and
    return a complete profile including specifications, owner/operator
    relationships, and pictures — all in a single call.

    This is the recommended starting point for most queries. It combines
    getRegNumber + getRelationships + getPictures into one workflow.
    """
    session = _get_session(ctx)

    data = await session.request("GET", f"/api/Aircraft/getRegNumber/{params.registration}/{{apiToken}}")
    ac = data.get("aircraftresult", {})

    if not ac:
        return f"No aircraft found for '{params.registration}'. Verify the tail number."

    aid = ac.get("aircraftid")
    if not aid:
        return f"Aircraft found but no aircraftid returned. Unexpected response."

    try:
        rel_data = await session.request("POST", "/api/Aircraft/getRelationships/{apiToken}", {
            "aircraftid": aid, "aclist": [aid], "modlist": [], "actiondate": "", "showHistoricalAcRefs": False,
        })
        rels = rel_data.get("relationships", [])
    except Exception:
        rels = []

    try:
        pic_data = await session.request("GET", f"/api/Aircraft/getPictures/{aid}/{{apiToken}}")
        pics = pic_data.get("pictures", [])
    except Exception:
        pics = []

    if params.response_format == ResponseFormat.JSON:
        return _truncate(json.dumps({
            "aircraft": ac,
            "relationships": rels,
            "pictures": pics,
        }, indent=2, default=str))

    reg = ac.get("regnbr", "N/A")
    make = ac.get("make", "")
    model = ac.get("model", "")
    lines = [
        f"# {reg} — {make} {model}",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Aircraft ID | {aid} |",
        f"| Serial Number | {ac.get('serialnbr', 'N/A')} |",
        f"| Year | {ac.get('yearofmfr', 'N/A')} |",
        f"| Lifecycle | {ac.get('lifecyclestatus', 'N/A')} |",
        f"| For Sale | {ac.get('forsale', 'N/A')} |",
        f"| Base Airport | {ac.get('baseairport', 'N/A')} |",
        "",
    ]

    if rels:
        lines.append("## Owner / Operator")
        for r in rels:
            rtype = r.get("relationtype", "Unknown")
            name = r.get("name", "N/A")
            lines.append(f"- **{rtype}**: {name}")
        lines.append("")

    if pics:
        lines.append(f"## Pictures ({len(pics)} available)")
        for p in pics[:3]:
            url = p.get("url", p.get("pictureurl", ""))
            if url:
                lines.append(f"- {url}")
        lines.append("")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRYPOINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    transport = os.environ.get("TRANSPORT", "stdio")
    if transport == "http":
        port = int(os.environ.get("PORT", "8000"))
        mcp.run(transport="streamable_http", port=port)
    else:
        mcp.run()
