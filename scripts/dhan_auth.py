"""Safe Dhan TOTP input handling and clock diagnostics.

Accepts either a raw Base32 TOTP seed or an otpauth://totp provisioning URI.
Never returns or logs the underlying seed or generated OTP.
"""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

import pyotp


def build_totp(secret: str):
    value = str(secret or "").strip()
    if not value:
        raise ValueError("TOTP secret is empty")
    if value.lower().startswith("otpauth://"):
        parsed = pyotp.parse_uri(value)
        if not isinstance(parsed, pyotp.TOTP):
            raise ValueError("Provisioning URI is not a TOTP credential")
        return parsed
    # GitHub secret editors sometimes preserve accidental whitespace/newlines.
    # Remove whitespace only; do not guess at prefixes or rewrite other characters.
    compact = "".join(value.split()).upper()
    return pyotp.TOTP(compact)


def server_clock_skew_seconds(date_header: str | None, *, now: datetime | None = None) -> int | None:
    """Return integer (HTTP server time - local UTC time), or None if unavailable."""
    if not date_header:
        return None
    try:
        server_time = parsedate_to_datetime(date_header)
        if server_time.tzinfo is None:
            server_time = server_time.replace(tzinfo=timezone.utc)
        local_time = now or datetime.now(timezone.utc)
        if local_time.tzinfo is None:
            local_time = local_time.replace(tzinfo=timezone.utc)
        return int(round((server_time.astimezone(timezone.utc) - local_time.astimezone(timezone.utc)).total_seconds()))
    except (TypeError, ValueError, OverflowError):
        return None
