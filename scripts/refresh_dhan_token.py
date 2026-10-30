#!/usr/bin/env python3
"""Create an ephemeral Dhan access token for the current GitHub Actions job.

Never writes the token to the repository and never prints the token, PIN or TOTP secret.
GitHub Actions secrets must be provided as environment variables by the workflow.
"""
from __future__ import annotations

import os
import sys
from urllib.parse import urlencode

import pyotp
import requests


def main() -> int:
    client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
    pin = os.getenv("DHAN_PIN", "").strip()
    totp_secret = os.getenv("DHAN_TOTP_SECRET", "").strip()
    github_env = os.getenv("GITHUB_ENV", "")

    if not any((client_id, pin, totp_secret)):
        print("DHAN_AUTH_SKIPPED: Dhan secrets are not configured; public data workflow may continue.")
        return 0
    if not all((client_id, pin, totp_secret)):
        print("DHAN_AUTH_ERROR: One or more required Dhan authentication secrets are missing.", file=sys.stderr)
        return 2
    if not github_env:
        print("DHAN_AUTH_ERROR: GITHUB_ENV is unavailable; refusing to print or persist token elsewhere.", file=sys.stderr)
        return 2

    try:
        totp = pyotp.TOTP(totp_secret).now()
        params = urlencode({"dhanClientId": client_id, "pin": pin, "totp": totp})
        endpoint = "https://auth.dhan.co/app/generateAccessToken?" + params
        response = requests.post(endpoint, timeout=30)
        if not response.ok:
            print("DHAN_AUTH_ERROR: Token service returned HTTP", response.status_code, file=sys.stderr)
            return 2
        payload = response.json()
        token = payload.get("accessToken") or payload.get("access_token")
        if not isinstance(token, str) or len(token) < 20:
            # Do not print the response body; it may contain sensitive values.
            print("DHAN_AUTH_ERROR: Response did not contain a valid access-token field.", file=sys.stderr)
            return 2
        with open(github_env, "a", encoding="utf-8") as handle:
            handle.write("DHAN_JOB_ACCESS_TOKEN=" + token.replace("\n", "") + "\n")
        print("DHAN_AUTH_OK: Short-lived token generated and exported to this Actions job; token value withheld.")
        return 0
    except Exception as exc:
        print("DHAN_AUTH_ERROR:", type(exc).__name__, "Authentication failed; sensitive response contents withheld.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
