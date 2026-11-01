"""Strict arithmetic helpers for a future, rights-cleared NIFTY IWF reconstruction.

This module does not infer exclusion categories or turn aggregate XBRL rows into
official IWF. Callers must first build a point-in-time, de-duplicated list of
unique excluded share positions from an authorised source.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Mapping, Sequence

IWF_EXCLUSION_IDS: tuple[int, ...] = tuple(range(1, 23))
_ACCEPTED_COVERAGE = {
    "QUANTIFIED",
    "CONFIRMED_ZERO",
    "APPROVED_NOT_IDENTIFIABLE",
}


class IWFInputError(ValueError):
    """Raised when an IWF input is incomplete or mathematically invalid."""


def assess_exclusion_coverage(status_by_id: Mapping[int, str]) -> dict:
    """Check whether all 22 exclusions have an explicit evidence disposition.

    APPROVED_NOT_IDENTIFIABLE must mean an independently documented acceptance
    under the official "where identifiable separately" language, not a silent
    missing value. UNRESOLVED and absent statuses fail the gate.
    """
    invalid_ids = sorted(set(status_by_id) - set(IWF_EXCLUSION_IDS))
    missing_ids = [i for i in IWF_EXCLUSION_IDS if i not in status_by_id]
    unresolved_ids = [
        i for i in IWF_EXCLUSION_IDS
        if i in status_by_id and str(status_by_id[i]).upper() not in _ACCEPTED_COVERAGE
    ]
    return {
        "passed": not invalid_ids and not missing_ids and not unresolved_ids,
        "expected_exclusion_count": len(IWF_EXCLUSION_IDS),
        "covered_count": sum(
            1 for i in IWF_EXCLUSION_IDS
            if i in status_by_id and str(status_by_id[i]).upper() in _ACCEPTED_COVERAGE
        ),
        "missing_ids": missing_ids,
        "unresolved_ids": unresolved_ids,
        "invalid_ids": invalid_ids,
    }


def calculate_iwf(
    total_shares: int,
    excluded_positions: Sequence[tuple[str, int]],
) -> Decimal:
    """Calculate IWF from total shares and a deduplicated list of share positions.

    The denominator is TOTAL shares, as shown in NSE Indices' published IWF
    worked example. It is not a shareholding-pattern percentage denominator.
    Each position ID must occur once, even when a position meets multiple
    exclusion descriptions. Amounts must be integer share counts.
    """
    if isinstance(total_shares, bool) or not isinstance(total_shares, int):
        raise IWFInputError("total_shares must be an integer share count")
    if total_shares <= 0:
        raise IWFInputError("total_shares must be positive")

    seen: set[str] = set()
    excluded_total = 0
    for position_id, shares in excluded_positions:
        if not isinstance(position_id, str) or not position_id.strip():
            raise IWFInputError("each excluded position needs a stable non-empty ID")
        if position_id in seen:
            raise IWFInputError(f"duplicate excluded position ID: {position_id}")
        seen.add(position_id)
        if isinstance(shares, bool) or not isinstance(shares, int) or shares < 0:
            raise IWFInputError("excluded shares must be non-negative integer share counts")
        excluded_total += shares

    if excluded_total > total_shares:
        raise IWFInputError("excluded shares cannot exceed total shares")

    raw_iwf = (Decimal(total_shares) - Decimal(excluded_total)) / Decimal(total_shares)
    return raw_iwf.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def calculate_freefloat_weights(
    records: Iterable[tuple[str, int, Decimal | str | float]],
) -> dict[str, Decimal]:
    """Normalise (symbol, full_market_cap, IWF) tuples into free-float weights.

    This is a mathematical primitive only. The source, date, share capital,
    price convention, index capping and as-of eligibility must be validated
    independently before using these weights in BUP-01.
    """
    freefloat_caps: dict[str, Decimal] = {}
    for symbol, market_cap, iwf_value in records:
        if not isinstance(symbol, str) or not symbol.strip():
            raise IWFInputError("each weight record needs a symbol")
        if symbol in freefloat_caps:
            raise IWFInputError(f"duplicate symbol: {symbol}")
        if isinstance(market_cap, bool) or not isinstance(market_cap, int) or market_cap <= 0:
            raise IWFInputError("market_cap must be a positive integer")
        try:
            iwf = Decimal(str(iwf_value))
        except Exception as exc:
            raise IWFInputError("IWF must be numeric") from exc
        if not iwf.is_finite() or iwf < 0 or iwf > 1:
            raise IWFInputError("IWF must be between 0 and 1")
        freefloat_caps[symbol] = Decimal(market_cap) * iwf

    denominator = sum(freefloat_caps.values(), Decimal(0))
    if not freefloat_caps or denominator <= 0:
        raise IWFInputError("positive free-float market capitalisation is required")

    return {
        symbol: (cap / denominator).quantize(Decimal("0.000000000001"), rounding=ROUND_HALF_UP)
        for symbol, cap in freefloat_caps.items()
    }
