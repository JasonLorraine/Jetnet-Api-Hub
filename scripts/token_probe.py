"""
token_probe.py -- Measure JETNET API token TTL by polling /getAccountInfo.

Logs in via src/jetnet/session.py, then polls /getAccountInfo every 60 seconds
until the token is rejected. Records the observed TTL and saves the result
to .cache/token_probe.json.

Usage:
    python scripts/token_probe.py

Environment variables:
    JETNET_EMAIL     -- JETNET account email
    JETNET_PASSWORD  -- JETNET account password
    JETNET_BASE_URL  -- (optional) API base URL
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.jetnet.session import (
    login,
    get_account_info,
    JetnetApiError,
    JetnetAuthError,
    DEFAULT_BASE_URL,
)

POLL_INTERVAL_SECONDS = 60
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"


def run_probe(email: str, password: str, base_url: str = DEFAULT_BASE_URL) -> dict:
    """Login and poll /getAccountInfo until the token expires.

    Returns:
        A dict with probe results including observed TTL.
    """
    print(f"Logging in as {email} ...")
    session = login(email, password, base_url)
    login_time = time.time()
    print(f"Login successful. apiToken starts with: {session.api_token[:8]}...")
    print(f"Polling /getAccountInfo every {POLL_INTERVAL_SECONDS}s until failure.\n")

    poll_count = 0

    while True:
        time.sleep(POLL_INTERVAL_SECONDS)
        poll_count += 1
        elapsed = time.time() - login_time
        elapsed_label = _format_duration(elapsed)

        try:
            get_account_info(session)
            print(f"  Poll #{poll_count:>4d}  |  {elapsed_label}  |  OK")
        except (JetnetAuthError, JetnetApiError, Exception) as exc:
            print(f"  Poll #{poll_count:>4d}  |  {elapsed_label}  |  FAILED: {exc}")
            failure_time = time.time()
            ttl_seconds = failure_time - login_time
            ttl_label = _format_duration(ttl_seconds)
            print(f"\nObserved token TTL: {ttl_label}")
            return {
                "login_at": datetime.fromtimestamp(login_time, tz=timezone.utc).isoformat(),
                "failure_at": datetime.fromtimestamp(failure_time, tz=timezone.utc).isoformat(),
                "ttl_seconds": round(ttl_seconds, 2),
                "ttl_human": ttl_label,
                "polls": poll_count,
                "poll_interval_seconds": POLL_INTERVAL_SECONDS,
            }


def _format_duration(seconds: float) -> str:
    """Format a duration in seconds as '12m 34s'."""
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s:02d}s"


def save_result(result: dict) -> Path:
    """Write probe results to .cache/token_probe.json."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CACHE_DIR / "token_probe.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Result saved to {out_path}")
    return out_path


def main():
    email = os.getenv("JETNET_EMAIL", "")
    password = os.getenv("JETNET_PASSWORD", "")
    base_url = os.getenv("JETNET_BASE_URL", DEFAULT_BASE_URL)

    if not email or not password:
        print("Error: Set JETNET_EMAIL and JETNET_PASSWORD environment variables.")
        sys.exit(1)

    result = run_probe(email, password, base_url)
    save_result(result)


if __name__ == "__main__":
    main()
