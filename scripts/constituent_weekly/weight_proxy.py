"""Point-in-time proxy-weight utilities for BUP-01.

All weights are returned as fractions summing to one. Callers must provide only
equity constituent holdings; cash, debt and derivative collateral are not stocks.
"""
from __future__ import annotations

from math import isfinite, sqrt
from typing import Mapping


def _validate_values(values: Mapping[str, float], *, strictly_positive: bool = False) -> None:
    if not values:
        raise ValueError("weights/prices cannot be empty")
    for symbol, value in values.items():
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("symbols must be non-empty strings")
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"non-numeric value for {symbol}") from exc
        if not isfinite(number):
            raise ValueError(f"non-finite value for {symbol}")
        if strictly_positive and number <= 0:
            raise ValueError(f"value for {symbol} must be positive")
        if not strictly_positive and number < 0:
            raise ValueError(f"value for {symbol} cannot be negative")


def normalize_equity_weights(weights_pct_nav: Mapping[str, float]) -> dict[str, float]:
    """Normalize disclosed equity % of NAV to 0..1 equity-only weights."""
    _validate_values(weights_pct_nav)
    total = sum(float(v) for v in weights_pct_nav.values())
    if not isfinite(total) or total <= 0:
        raise ValueError("equity weight total must be positive")
    return {k: float(v) / total for k, v in weights_pct_nav.items()}


def drift_weights(
    base_weights: Mapping[str, float],
    price_relatives: Mapping[str, float],
) -> dict[str, float]:
    """Drift a fixed-share basket by price relatives, preserving exact membership.

    price_relatives are adjusted-price(t) / adjusted-price(snapshot). This
    does not model share-count changes, IWF changes, rebalances or corporate
    events; callers must break/reseed the series at those events.
    """
    _validate_values(base_weights)
    _validate_values(price_relatives, strictly_positive=True)
    if set(base_weights) != set(price_relatives):
        missing_prices = sorted(set(base_weights) - set(price_relatives))
        extra_prices = sorted(set(price_relatives) - set(base_weights))
        raise ValueError(f"symbol mismatch: missing_prices={missing_prices}, extra_prices={extra_prices}")
    base = normalize_equity_weights(base_weights)
    unscaled = {k: base[k] * float(price_relatives[k]) for k in base}
    total = sum(unscaled.values())
    if not isfinite(total) or total <= 0:
        raise ValueError("drifted total must be positive")
    return {k: v / total for k, v in unscaled.items()}


def compare_weight_vectors(
    reference: Mapping[str, float],
    candidate: Mapping[str, float],
) -> dict[str, float | int]:
    """Compare two weight vectors after independent normalization."""
    _validate_values(reference)
    _validate_values(candidate)
    if set(reference) != set(candidate):
        raise ValueError("reference and candidate symbols must match exactly")
    a = normalize_equity_weights(reference)
    b = normalize_equity_weights(candidate)
    diffs = [a[k] - b[k] for k in sorted(a)]
    mae = sum(abs(x) for x in diffs) / len(diffs)
    rmse = sqrt(sum(x * x for x in diffs) / len(diffs))
    max_abs = max(abs(x) for x in diffs)
    mean_a = sum(a.values()) / len(a)
    mean_b = sum(b.values()) / len(b)
    cov = sum((a[k] - mean_a) * (b[k] - mean_b) for k in a)
    var_a = sum((a[k] - mean_a) ** 2 for k in a)
    var_b = sum((b[k] - mean_b) ** 2 for k in b)
    corr = cov / sqrt(var_a * var_b) if var_a > 0 and var_b > 0 else float("nan")
    return {
        "n": len(a),
        "mae_fraction": mae,
        "rmse_fraction": rmse,
        "max_abs_fraction": max_abs,
        "pearson_r": corr,
    }
