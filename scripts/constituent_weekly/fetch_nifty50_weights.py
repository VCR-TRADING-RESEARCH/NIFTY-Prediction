from __future__ import annotations

import hashlib
import json
from io import BytesIO
from pathlib import Path
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "constituent_weekly" / "nifty50_weights_monthly.csv"
AUDIT_PATH = ROOT / "research" / "constituent_weekly" / "C1_NIFTY50_WEIGHT_AUDIT.json"
SOURCE_REVISION = "c15498388ae4d346f42291c4e5937235e56ae67c"
SOURCE_URL = (
    "https://huggingface.co/datasets/AMP4010/"
    "Historical_Nifty_50_Constituent_Weights_20Y/resolve/"
    + SOURCE_REVISION + "/weights.csv"
)
LICENSE = "CC BY-NC-SA 4.0"


def validate_weights_payload(payload: bytes) -> dict:
    if not payload or not payload.lstrip().startswith(b"DATE,"):
        raise ValueError("Downloaded file is empty or does not begin with the expected DATE header.")
    frame = pd.read_csv(BytesIO(payload), low_memory=False)
    if "DATE" not in frame.columns or len(frame.columns) < 51:
        raise ValueError("Weight file must contain DATE and at least 50 ticker columns.")
    dates = pd.to_datetime(frame["DATE"], errors="coerce")
    if dates.isna().any() or dates.duplicated().any() or not dates.is_monotonic_increasing:
        raise ValueError("Weight dates must be valid, unique and ascending.")
    weights = frame.drop(columns=["DATE"]).apply(pd.to_numeric, errors="coerce")
    if weights.isna().any().any():
        raise ValueError("Weight matrix contains missing or non-numeric values.")
    values = weights.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0.0).any() or (values > 100.0).any():
        raise ValueError("Weight values must be finite and in [0, 100].")
    row_sums = weights.sum(axis=1)
    deviations = (row_sums - 100.0).abs()
    max_deviation = float(deviations.max())
    if max_deviation > 1e-6:
        raise ValueError("At least one row does not sum to 100 within 1e-6.")
    return {
        "rows": int(len(frame)),
        "ticker_columns": int(weights.shape[1]),
        "first_date": dates.min().date().isoformat(),
        "last_date": dates.max().date().isoformat(),
        "min_row_sum": float(row_sums.min()),
        "max_row_sum": float(row_sums.max()),
        "max_abs_row_sum_deviation": max_deviation,
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def main() -> int:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    audit = {
        "track": "BUP-01",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "AMP4010 Historical Nifty 50 Constituent Weights (Rolling 20-Year Window)",
        "creator": "Sukrit Bera",
        "citation": "Bera, S. (2025), Figshare DOI 10.6084/m9.figshare.30217915",
        "source_url": SOURCE_URL,
        "source_revision": SOURCE_REVISION,
        "license": LICENSE,
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "commercial_use_permitted": False,
        "source_method_limitations": [
            "Dataset card says weights are compiled from official Nifty Indices reports.",
            "Intra-month reconstitution weights are estimated/extrapolated in some cases.",
            "Corporate-action handling and normalization are performed by the dataset author.",
            "The dataset card reports coverage through 2025-08-31; it does not cover 2025-09 onward.",
        ],
        "status": "NOT_CHECKED",
    }
    try:
        if DATA_PATH.exists():
            payload = DATA_PATH.read_bytes()
            stats = validate_weights_payload(payload)
            audit["status"] = "CACHE_VALIDATED"
        else:
            response = requests.get(SOURCE_URL, timeout=90, headers={"User-Agent": "NIFTY-Prediction-Research/1.0"})
            response.raise_for_status()
            payload = response.content
            stats = validate_weights_payload(payload)
            DATA_PATH.write_bytes(payload)
            audit["status"] = "DOWNLOADED_AND_VALIDATED"
        audit.update(stats)
    except Exception as exc:
        audit["status"] = "FAILED_OR_NOT_AVAILABLE"
        audit["error_type"] = type(exc).__name__
        audit["error_message"] = str(exc)[:240]
    AUDIT_PATH.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print("NIFTY50_WEIGHT_SOURCE_AUDIT", json.dumps(audit, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
