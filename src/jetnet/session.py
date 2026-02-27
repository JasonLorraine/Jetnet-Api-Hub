"""
JETNET API Session Helper

Provides self-healing session management for the JETNET API with automatic
token validation via /getAccountInfo and transparent re-login on expiry.

Usage:
    from src.jetnet.session import login, ensure_session, jetnet_request

    session = login("you@example.com", "password")
    session = ensure_session(session)
    data = jetnet_request("GET", "/api/Aircraft/getRegNumber/N1KE/{apiToken}", session)
"""

import time
from dataclasses import dataclass, field
from typing import Any, Optional

import requests

TOKEN_TTL_SECONDS = 60 * 60
PROACTIVE_REFRESH_SECONDS = 50 * 60
DEFAULT_BASE_URL = "https://customer.jetnetconnect.com"


@dataclass
class SessionState:
    """Holds JETNET authentication state and token metadata.

    Attributes:
        base_url: The JETNET API base URL.
        email: Account email used for login.
        password: Account password used for login.
        bearer_token: The Bearer token for the Authorization header.
        api_token: The token inserted into URL paths (also called securityToken).
        created_at: Epoch timestamp when the session was first created via login.
        last_validated_at: Epoch timestamp of the last successful /getAccountInfo call.
    """

    base_url: str = DEFAULT_BASE_URL
    email: str = ""
    password: str = ""
    bearer_token: Optional[str] = None
    api_token: Optional[str] = None
    created_at: float = 0.0
    last_validated_at: float = 0.0


class JetnetAuthError(Exception):
    """Raised when JETNET returns an authentication or authorization error."""
    pass


class JetnetApiError(Exception):
    """Raised when JETNET returns a business-logic error in responsestatus or RFC error shape."""
    pass


def login(email: str, password: str, base_url: str = DEFAULT_BASE_URL) -> SessionState:
    """Authenticate with the JETNET API and return a populated SessionState.

    Calls POST /api/Admin/APILogin with the provided credentials and extracts
    bearerToken and apiToken from the response.

    Args:
        email: JETNET account email address.
        password: JETNET account password.
        base_url: API base URL (defaults to production).

    Returns:
        A SessionState with valid tokens and timestamps.

    Raises:
        JetnetAuthError: If login fails or tokens are missing from the response.
    """
    url = f"{base_url}/api/Admin/APILogin"
    r = requests.post(url, json={"emailAddress": email, "password": password})
    r.raise_for_status()
    data = r.json()

    normalize_error(data)

    bearer_token = data.get("bearerToken")
    api_token = data.get("apiToken") or data.get("securityToken")

    if not bearer_token or not api_token:
        raise JetnetAuthError("Login succeeded but bearerToken or apiToken missing from response.")

    now = time.time()
    return SessionState(
        base_url=base_url,
        email=email,
        password=password,
        bearer_token=bearer_token,
        api_token=api_token,
        created_at=now,
        last_validated_at=now,
    )


def get_account_info(session: SessionState) -> dict:
    """Validate the current session by calling /getAccountInfo.

    This is the recommended way to check whether the current apiToken is still
    valid without making a data call.

    Args:
        session: A SessionState with a valid api_token.

    Returns:
        The parsed JSON response dict from /getAccountInfo.

    Raises:
        JetnetApiError: If the response contains an error status.
        requests.HTTPError: If the HTTP request itself fails.
    """
    url = f"{session.base_url}/api/Utility/getAccountInfo/{session.api_token}"
    headers = {
        "Authorization": f"Bearer {session.bearer_token}",
        "Content-Type": "application/json",
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    normalize_error(data)
    return data


def ensure_session(session: SessionState) -> SessionState:
    """Ensure the session is valid, refreshing proactively or on failure.

    Logic:
    1. If the token age exceeds PROACTIVE_REFRESH_SECONDS (50 min), re-login.
    2. Otherwise, call get_account_info to validate.
    3. If validation fails, re-login once and return the new session.

    Args:
        session: The current SessionState.

    Returns:
        A valid SessionState (may be the same object or a fresh one).

    Raises:
        JetnetAuthError: If re-login also fails.
    """
    token_age = time.time() - session.created_at

    if token_age >= PROACTIVE_REFRESH_SECONDS:
        return login(session.email, session.password, session.base_url)

    try:
        get_account_info(session)
        session.last_validated_at = time.time()
        return session
    except (JetnetApiError, JetnetAuthError, requests.HTTPError):
        return login(session.email, session.password, session.base_url)


def normalize_error(response_json: dict) -> None:
    """Check a JETNET response for error conditions and raise if found.

    Handles two error shapes:
    1. JETNET-native: the ``responsestatus`` field contains "ERROR" (e.g.
       ``"ERROR: INVALID SECURITY TOKEN"``).
    2. RFC 7807-style: the response contains ``type``, ``title``, and ``status``
       fields indicating a problem.

    Args:
        response_json: The parsed JSON body from a JETNET API call.

    Raises:
        JetnetAuthError: If the error indicates an invalid/expired token.
        JetnetApiError: For all other JETNET business-logic errors.
    """
    if not isinstance(response_json, dict):
        return

    responsestatus = str(response_json.get("responsestatus", "")).upper()
    if "ERROR" in responsestatus:
        if "INVALID SECURITY TOKEN" in responsestatus:
            raise JetnetAuthError(response_json["responsestatus"])
        raise JetnetApiError(response_json["responsestatus"])

    if "type" in response_json and "title" in response_json and "status" in response_json:
        status_code = response_json.get("status", 0)
        title = response_json.get("title", "Unknown error")
        detail = response_json.get("detail", "")
        msg = f"{title} (status={status_code})"
        if detail:
            msg += f": {detail}"
        if isinstance(status_code, int) and status_code in (401, 403):
            raise JetnetAuthError(msg)
        raise JetnetApiError(msg)


def jetnet_request(
    method: str,
    path: str,
    session: SessionState,
    json: Optional[dict] = None,
) -> dict:
    """Make an authenticated JETNET API request with automatic session healing.

    Replaces ``{apiToken}`` in the path, attaches the Bearer header, checks the
    response for errors, and retries once on an invalid-token error by re-logging
    in and replaying the request.

    Args:
        method: HTTP method (GET, POST, etc.).
        path: API path with ``{apiToken}`` placeholder (e.g.
            ``/api/Aircraft/getRegNumber/N1KE/{apiToken}``).
        session: A SessionState obtained from :func:`login` or :func:`ensure_session`.
        json: Optional JSON body for POST requests.

    Returns:
        The parsed JSON response dict.

    Raises:
        JetnetApiError: If the API returns a non-auth error.
        JetnetAuthError: If re-login also fails with an auth error.
        requests.HTTPError: If the HTTP request itself fails on retry.
    """
    session_to_use = ensure_session(session)

    session.bearer_token = session_to_use.bearer_token
    session.api_token = session_to_use.api_token
    session.created_at = session_to_use.created_at
    session.last_validated_at = session_to_use.last_validated_at

    try:
        return _do_request(method, path, session, json)
    except JetnetAuthError:
        refreshed = login(session.email, session.password, session.base_url)
        session.bearer_token = refreshed.bearer_token
        session.api_token = refreshed.api_token
        session.created_at = refreshed.created_at
        session.last_validated_at = refreshed.last_validated_at
        return _do_request(method, path, session, json)


def _do_request(
    method: str,
    path: str,
    session: SessionState,
    json: Optional[dict] = None,
) -> dict:
    """Execute a single JETNET API request (no retry logic).

    Args:
        method: HTTP method.
        path: API path with ``{apiToken}`` placeholder.
        session: A SessionState with valid tokens.
        json: Optional JSON body.

    Returns:
        The parsed JSON response dict.

    Raises:
        JetnetAuthError: On authentication errors.
        JetnetApiError: On business-logic errors.
        requests.HTTPError: On HTTP transport errors.
    """
    url = f"{session.base_url}{path}".replace("{apiToken}", session.api_token or "")
    headers = {
        "Authorization": f"Bearer {session.bearer_token or ''}",
        "Content-Type": "application/json",
    }
    r = requests.request(method, url, headers=headers, json=json)
    r.raise_for_status()
    data = r.json()
    normalize_error(data)
    return data
