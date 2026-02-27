"""
jetnet/session.py -- Local copy of the JETNET session helper.

This is a subset of src/jetnet/session.py from the JETNET API docs repo,
copied here so the FastAPI template is self-contained. For the full version
with docstrings and type hints, see the root repo's src/jetnet/session.py.
"""

from __future__ import annotations
import os
import time
import requests
from dataclasses import dataclass, field
from typing import Optional

BASE_URL = os.getenv("JETNET_BASE_URL", "https://customer.jetnetconnect.com")
TOKEN_TTL_SECONDS = int(os.getenv("JETNET_TOKEN_TTL", "3000"))


@dataclass
class SessionState:
    base_url: str
    email: str
    password: str
    bearer_token: str
    api_token: str
    created_at: float = field(default_factory=time.time)

    def is_stale(self, ttl: int = TOKEN_TTL_SECONDS) -> bool:
        return (time.time() - self.created_at) > ttl


class JetnetError(Exception):
    def __init__(self, message: str, raw_status: str = ""):
        self.raw_status = raw_status
        super().__init__(message)


def normalize_error(data: dict) -> Optional[JetnetError]:
    status = data.get("responsestatus", "")
    if status:
        upper = status.upper()
        if upper.startswith("ERROR") or "INVALID" in upper:
            return JetnetError(f"JETNET error: {status}", raw_status=status)
    if "title" in data or "type" in data:
        title = data.get("title", data.get("type", "Unknown error"))
        return JetnetError(f"API error: {title}", raw_status=str(data.get("status", "")))
    return None


def login(email: Optional[str] = None, password: Optional[str] = None, base_url: Optional[str] = None) -> SessionState:
    email = email or os.environ["JETNET_EMAIL"]
    password = password or os.environ["JETNET_PASSWORD"]
    url = (base_url or BASE_URL).rstrip("/")
    r = requests.post(f"{url}/api/Admin/APILogin",
                      json={"emailAddress": email, "password": password}, timeout=30)
    r.raise_for_status()
    data = r.json()
    err = normalize_error(data)
    if err:
        raise err
    return SessionState(
        base_url=url, email=email, password=password,
        bearer_token=data["bearerToken"],
        api_token=data.get("apiToken") or data.get("securityToken"),
    )


def ensure_session(session: SessionState) -> SessionState:
    if session.is_stale():
        return login(session.email, session.password, session.base_url)
    try:
        r = requests.get(
            f"{session.base_url}/api/Admin/getAccountInfo/{session.api_token}",
            headers={"Authorization": f"Bearer {session.bearer_token}"}, timeout=15)
        r.raise_for_status()
        err = normalize_error(r.json())
        if err:
            raise err
        return session
    except Exception:
        return login(session.email, session.password, session.base_url)


def jetnet_request(method: str, path: str, session: SessionState, json: Optional[dict] = None) -> dict:
    url = f"{session.base_url}{path}".replace("{apiToken}", session.api_token)
    headers = {"Authorization": f"Bearer {session.bearer_token}", "Content-Type": "application/json"}
    r = requests.request(method, url, headers=headers, json=json, timeout=60)
    r.raise_for_status()
    data = r.json()
    err = normalize_error(data)
    if err:
        if "INVALID" in err.raw_status.upper():
            refreshed = login(session.email, session.password, session.base_url)
            return jetnet_request(method, path, refreshed, json=json)
        raise err
    return data
