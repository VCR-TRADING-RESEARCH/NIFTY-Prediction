#!/usr/bin/env python3
"""Create an ephemeral Dhan access token for the current GitHub Actions job.

Never writes the token to the repository and never prints the token, PIN or TOTP secret.
GitHub Actions secrets must be provided as environment variables by the workflow.
"""
from __future__ import annotations
import os
import sys
import requests
import pyotp

def find_access_token(value):
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).replace("_", "").replace("-", "").lower()
            if normalized == "accesstoken" and isinstance(item, str) and len(item) >= 20:
                return item
        for item in value.values():
            found = find_access_token(item)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_access_token(item)
            if found:
                return found
    return None

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
        response = requests.post(
            "https://auth.dhan.co/app/generateAccessToken",
            params={"dhanClientId": client_id, "pin": pin, "totp": totp},
            timeout=30,
        )
        if not response.ok:
            print("DHAN_AUTH_ERROR: Token service returned HTTP", response.status_code, file=sys.stderr)
            return 2
        payload = response.json()
        token = find_access_token(payload)
        if not token:
            keys = sorted(str(k) for k in payload.keys()) if isinstance(payload, dict) else [type(payload).__name__]
            status = payload.get("status") if isinstance(payload, dict) else None
            error_code = payload.get("errorCode") or payload.get("error_code") if isinstance(payload, dict) else None
            message = str(payload.get("message", "")).lower() if isinstance(payload, dict) else ""
            if "totp" in message or "otp" in message:
                reason = "TOTP_REJECTED_OR_NOT_ENABLED"
            elif "pin" in message:
                reason = "PIN_REJECTED"
            elif "client" in message or "dhan" in message:
                reason = "CLIENT_AUTH_REJECTED"
            else:
                reason = "AUTH_REJECTED_UNCLASSIFIED"
            print("DHAN_AUTH_ERROR: No access token in response; keys=", ",".join(keys),
                  "status=", str(status)[:32], "error_code=", str(error_code)[:32],
                  "reason=", reason, file=sys.stderr)
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
