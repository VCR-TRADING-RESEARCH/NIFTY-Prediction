#!/usr/bin/env python3
"""Run one secured, issue-triggered Dhan/ExtraTrees prediction in GitHub Actions."""
from __future__ import annotations
import json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from live_api.app import PublicPredictionError, _do_prediction, parse_as_of_date

def main() -> int:
    raw_date = os.environ.get("NIFTY_AS_OF_DATE", "").strip()
    issue_number = os.environ.get("NIFTY_REQUEST_ISSUE", "").strip()
    output_dir = ROOT / "docs" / "assets" / "predictions"
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_date = raw_date if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date) else "invalid-date"
    output_path = output_dir / f"{safe_date}.json"
    result = {"status": "failed", "as_of_date": safe_date,
      "request_issue_number": int(issue_number) if issue_number.isdigit() else None,
      "request_started_at_utc": os.environ.get("NIFTY_REQUEST_STARTED_AT", datetime.now(timezone.utc).isoformat()),
      "generated_at_utc": datetime.now(timezone.utc).isoformat(),
      "error": "Prediction did not complete. Check the linked GitHub Actions run."}
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
            raise PublicPredictionError("Request date must use YYYY-MM-DD format.")
        as_of = parse_as_of_date(raw_date)
        result = _do_prediction(as_of)
        result.update({"status": "succeeded", "request_issue_number": int(issue_number) if issue_number.isdigit() else None,
          "request_started_at_utc": os.environ.get("NIFTY_REQUEST_STARTED_AT", datetime.now(timezone.utc).isoformat())})
    except PublicPredictionError as exc:
        result["error"] = str(exc)
    except Exception as exc:
        result["error"] = "Prediction failed internally (" + type(exc).__name__ + "). Sensitive details were withheld."
    result["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    output_path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("PREDICTION_STATUS:", result.get("status", "failed"))
    print("PREDICTION_DATE:", safe_date)
    print("PREDICTION_OUTPUT:", output_path.relative_to(ROOT).as_posix())
    if result.get("status") != "succeeded": print("PREDICTION_ERROR:", result.get("error", "No safe diagnostic available."))
    return 0
if __name__ == "__main__": raise SystemExit(main())
