"""
session.py -- JETNET API session manager

Handles login, token storage, health-checking via /getAccountInfo,
and auto-refresh on token expiry. Use this as the single source of
truth for all JETNET auth in your application.

Usage:
    from src.jetnet.session import login, ensure_session, jetnet_request

    session = login("you@example.com", "yourpassword")
    result  = jetnet_request("GET", "/api/Aircraft/getRegNumber/N12345/{apiToken}", session)
"""

from __future__ import annotations
import os
import time
import requests
from dataclasses import dataclass, field
from typing import Optional

BASE_URL = os.getenv("JETNET_BASE_URL", "https://customer.jetnetconnect.com")
TOKEN_TTL_SECONDS = int(os.getenv("JETNET_TOKEN_TTL", "3000"))  # 50 min (tokens last ~60 min)


@dataclass
class SessionState:
    base_url: str
    email: str
    password: str
    bearer_token: str
    api_token: str
    created_at: float = field(default_factory=time.time)
    last_validated_at: float = field(default_factory=time.time)

    def age_seconds(self) -> float:
        return time.time() - self.created_at

    def seconds_since_validated(self) -> float:
        return time.time() - self.last_validated_at

    def is_stale(self, ttl: int = TOKEN_TTL_SECONDS) -> bool:
        """True if the token has likely expired based on wall-clock age."""
        return self.age_seconds() > ttl


class JetnetError(Exception):
    """Raised when JETNET returns an application-level error (HTTP 200 + bad status)."""
    def __init__(self, message: str, endpoint: str = "", raw_status: str = ""):
        self.endpoint = endpoint
        self.raw_status = raw_status
        super().__init__(message)


def normalize_error(response_json: dict, endpoint: str = "") -> Optional[JetnetError]:
    """
    Detect application-level errors that arrive with HTTP 200.

    JETNET can signal errors in two ways:
      1. responsestatus starts with "ERROR" or contains "INVALID"
      2. RFC-style error body with a "title" or "type" field

    Returns a JetnetError if an error is detected, None otherwise.
    """
    status = response_json.get("responsestatus", "")
    if status:
        upper = status.upper()
        if upper.startswith("ERROR") or "INVALID" in upper:
            return JetnetError(
                f"JETNET error: {status}",
                endpoint=endpoint,
                raw_status=status,
            )

    if "title" in response_json or "type" in response_json:
        title = response_json.get("title", response_json.get("type", "Unknown error"))
        return JetnetError(
            f"API error: {title}",
            endpoint=endpoint,
            raw_status=str(response_json.get("status", "")),
        )

    return None


def login(
    email: Optional[str] = None,
    password: Optional[str] = None,
    base_url: Optional[str] = None,
) -> SessionState:
    """
    Authenticate with the JETNET API and return a SessionState.

    Reads JETNET_EMAIL / JETNET_PASSWORD / JETNET_BASE_URL from environment
    if not passed directly.

    IMPORTANT: emailAddress has a capital A -- this function handles that for you.
    """
    email    = email    or os.environ["JETNET_EMAIL"]
    password = password or os.environ["JETNET_PASSWORD"]
    url      = (base_url or BASE_URL).rstrip("/")

    r = requests.post(
        f"{url}/api/Admin/APILogin",
        json={"emailAddress": email, "password": password},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()

    err = normalize_error(data, endpoint="APILogin")
    if err:
        raise err

    return SessionState(
        base_url=url,
        email=email,
        password=password,
        bearer_token=data["bearerToken"],
        api_token=data.get("apiToken") or data.get("securityToken"),
    )


def get_account_info(session: SessionState) -> dict:
    """
    Call /getAccountInfo -- a lightweight, read-only probe endpoint.

    Use this to:
      - Verify a token is still valid before starting a long workflow
      - Observe practical token TTL (see scripts/token_probe.py)
      - Confirm the session is healthy after re-login

    Returns the account info dict, or raises JetnetError if the token is invalid.
    """
    r = requests.get(
        f"{session.base_url}/api/Admin/getAccountInfo/{session.api_token}",
        headers={"Authorization": f"Bearer {session.bearer_token}"},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()

    err = normalize_error(data, endpoint="getAccountInfo")
    if err:
        raise err

    session.last_validated_at = time.time()
    return data


def ensure_session(session: SessionState) -> SessionState:
    """
    Validate the session before starting any workflow. Auto-refreshes once on expiry.

    Call this at the start of any multi-step workflow (Golden Path, bulk export, etc.)
    to prevent mid-workflow token failures.

    Strategy:
      1. If token looks stale by age, skip the probe and re-login immediately.
      2. Otherwise call /getAccountInfo.
      3. If /getAccountInfo fails, re-login once and retry.
      4. If it still fails, raise -- credentials or service issue.
    """
    if session.is_stale():
        return login(session.email, session.password, session.base_url)

    try:
        get_account_info(session)
        return session
    except (JetnetError, requests.HTTPError):
        pass

    try:
        refreshed = login(session.email, session.password, session.base_url)
        get_account_info(refreshed)
        return refreshed
    except Exception as e:
        raise JetnetError(
            f"Session refresh failed. Check credentials and connectivity. Original error: {e}",
            endpoint="ensure_session",
        ) from e


def jetnet_request(
    method: str,
    path: str,
    session: SessionState,
    json: Optional[dict] = None,
    timeout: int = 60,
    auto_refresh: bool = True,
) -> dict:
    """
    Make an authenticated JETNET API request.

    Handles:
      - Bearer token in Authorization header
      - apiToken substitution in URL path
      - Application-level error detection (HTTP 200 but responsestatus = ERROR)
      - One automatic re-auth on INVALID SECURITY TOKEN

    Args:
        method:       "GET" or "POST"
        path:         e.g. "/api/Aircraft/getRegNumber/N12345/{apiToken}"
                      Use literal {apiToken} -- it will be substituted automatically.
        session:      SessionState from login() or ensure_session()
        json:         POST body dict (None for GET requests)
        timeout:      Request timeout in seconds
        auto_refresh: If True, re-login once on token error and retry

    Returns:
        Parsed JSON response dict

    Raises:
        JetnetError: on application-level errors
        requests.HTTPError: on HTTP 4xx/5xx errors
    """
    url = f"{session.base_url}{path}".replace("{apiToken}", session.api_token)
    headers = {
        "Authorization": f"Bearer {session.bearer_token}",
        "Content-Type": "application/json",
    }

    r = requests.request(method, url, headers=headers, json=json, timeout=timeout)
    r.raise_for_status()
    data = r.json()

    err = normalize_error(data, endpoint=path)
    if err:
        if auto_refresh and "INVALID" in err.raw_status.upper():
            refreshed = login(session.email, session.password, session.base_url)
            return jetnet_request(method, path, refreshed, json=json,
                                  timeout=timeout, auto_refresh=False)
        raise err

    return data


def refresh_session(session: SessionState) -> SessionState:
    """Force a fresh login regardless of token age. Returns a new SessionState."""
    return login(session.email, session.password, session.base_url)
