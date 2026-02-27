"""
token_probe.py -- JETNET token lifetime measurement script

Logs in and polls /getAccountInfo every N seconds until the token expires,
measuring the actual token TTL so you can tune your refresh window.

Usage:
    python scripts/token_probe.py

Environment variables:
    JETNET_EMAIL     -- emailAddress (capital A)
    JETNET_PASSWORD  -- account password
    JETNET_BASE_URL  -- default: https://customer.jetnetconnect.com
    PROBE_INTERVAL   -- seconds between polls, default 60

Output:
    [HH:MM:SS] age=0:00:00 -- OK (acc: yourname@example.com)
    [HH:MM:SS] age=0:05:00 -- OK
    ...
    [HH:MM:SS] age=0:57:00 -- EXPIRED after 0:57:00
    Token lifetime: 0:57:00

Typical results: JETNET tokens last ~60 minutes from issuance.
Recommended refresh: 50 minutes (TOKEN_TTL = 3000 in session.py).
"""

import os
import sys
import time
import datetime
import requests

BASE_URL   = os.getenv("JETNET_BASE_URL", "https://customer.jetnetconnect.com")
EMAIL      = os.getenv("JETNET_EMAIL", "")
PASSWORD   = os.getenv("JETNET_PASSWORD", "")
INTERVAL   = int(os.getenv("PROBE_INTERVAL", "60"))


def ts() -> str:
    """Current local time as HH:MM:SS."""
    return datetime.datetime.now().strftime("%H:%M:%S")


def elapsed(start: float) -> str:
    """Format seconds elapsed as H:MM:SS."""
    secs = int(time.time() - start)
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"


def login() -> tuple[str, str]:
    """
    Log in and return (bearerToken, apiToken).

    CRITICAL: field is 'emailAddress' with capital A.
    """
    url = f"{BASE_URL}/api/Admin/APILogin"
    r = requests.post(
        url,
        json={"emailAddress": EMAIL, "password": PASSWORD},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    status = data.get("responsestatus", "")
    if "ERROR" in status.upper() or "INVALID" in status.upper():
        raise RuntimeError(f"Login failed: {status}")
    bearer = data.get("bearerToken", "")
    token  = data.get("apiToken", "")
    if not bearer or not token:
        raise RuntimeError(f"Login returned no tokens: {data}")
    return bearer, token


def probe(bearer: str, token: str) -> dict:
    """
    Call /getAccountInfo and return the parsed response.
    Raises on HTTP error or JETNET application error.
    """
    url = f"{BASE_URL}/api/Admin/getAccountInfo/{token}"
    r = requests.get(
        url,
        headers={"Authorization": f"Bearer {bearer}"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    status = data.get("responsestatus", "")
    if "ERROR" in status.upper() or "INVALID" in status.upper():
        raise RuntimeError(f"Token invalid: {status}")
    return data


def main():
    if not EMAIL or not PASSWORD:
        print("ERROR: Set JETNET_EMAIL and JETNET_PASSWORD environment variables.")
        sys.exit(1)

    print(f"Logging in as {EMAIL} ...")
    bearer, token = login()
    start = time.time()
    print(f"[{ts()}] Login OK -- probing every {INTERVAL}s\n")

    consecutive_errors = 0

    while True:
        try:
            info = probe(bearer, token)
            account = info.get("emailaddress") or info.get("emailAddress") or "?"
            print(f"[{ts()}] age={elapsed(start)} -- OK (acc: {account})")
            consecutive_errors = 0

        except RuntimeError as e:
            age = elapsed(start)
            print(f"[{ts()}] age={age} -- EXPIRED: {e}")
            print(f"\nToken lifetime: {age}")
            print(
                "Recommendation: set TOKEN_TTL in session.py to "
                f"{int(time.time() - start) - INTERVAL}s "
                f"(i.e. {(time.time() - start - INTERVAL) / 60:.0f}m) "
                "to refresh before expiry."
            )
            sys.exit(0)

        except requests.HTTPError as e:
            consecutive_errors += 1
            print(f"[{ts()}] age={elapsed(start)} -- HTTP error: {e} (attempt {consecutive_errors})")
            if consecutive_errors >= 3:
                print("3 consecutive HTTP errors -- aborting.")
                sys.exit(2)

        except requests.RequestException as e:
            consecutive_errors += 1
            print(f"[{ts()}] age={elapsed(start)} -- Network error: {e} (attempt {consecutive_errors})")
            if consecutive_errors >= 3:
                print("3 consecutive network errors -- aborting.")
                sys.exit(2)

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
