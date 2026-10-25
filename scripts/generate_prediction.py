#!/usr/bin/env python3
"""Generate a leakage-checked as-of-date ExtraTrees prediction record."""
from __future__ import annotations
import json, os, sys
from datetime import datetime, date, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd
IST=ZoneInfo("Asia/Kolkata")
ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/"artifacts/extratrees_model.joblib"
FEATURES=ROOT/"data/processed/prediction_features.csv"
CALENDAR=ROOT/"data/reference/nifty_expiry_calendar.csv"
OUT=ROOT/"docs/data/predictions.json"

def main():
    requested=os.getenv("AS_OF_DATE",datetime.now(IST).date().isoformat())
    asof=date.fromisoformat(requested)
    record={"as_of_date":requested,"status":"unavailable","prediction_label":None,"class_probability":None,"expiry_date":None,"model_version":None,"generated_at_ist":datetime.now(IST).isoformat(),"feature_cutoff":requested,"message":None}
    try:
        missing=[str(p.relative_to(ROOT)) for p in (MODEL,FEATURES,CALENDAR) if not p.is_file()]
        if missing: raise FileNotFoundError("Missing prerequisites: "+", ".join(missing))
        import joblib
        model=joblib.load(MODEL)
        frame=pd.read_csv(FEATURES)
        if "as_of_date" not in frame: raise ValueError("Feature CSV must contain as_of_date.")
        frame["as_of_date"]=pd.to_datetime(frame["as_of_date"],errors="raise").dt.date
        eligible=frame.loc[frame["as_of_date"]==asof].copy()
        if eligible.empty: raise ValueError(f"No feature row exists for as-of date {requested}; refusing to substitute another date.")
        if len(eligible)!=1: raise ValueError(f"Expected exactly one feature row for {requested}, found {len(eligible)}.")
        calendar=pd.read_csv(CALENDAR)
        if "expiry_date" not in calendar: raise ValueError("Expiry calendar must contain expiry_date.")
        expiries=sorted(set(pd.to_datetime(calendar["expiry_date"],errors="raise").dt.date))
        future=[d for d in expiries if d>asof]
        if not future: raise ValueError(f"No verified expiry after {requested}.")
        expiry=future[0]
        meta={"as_of_date","expiry_date","target","label","direction","timestamp","datetime","date"}
        trained=list(getattr(model,"feature_names_in_",[]))
        if not trained: raise ValueError("Model does not expose feature_names_in_; exact feature mapping cannot be verified.")
        absent=[c for c in trained if c not in eligible.columns]
        if absent: raise ValueError("Missing trained model features: "+", ".join(absent))
        # Guard timestamped features if the dataset provides a source timestamp.
        if "feature_timestamp" in eligible:
            ts=pd.to_datetime(eligible["feature_timestamp"],errors="raise",utc=True)
            cutoff=pd.Timestamp(asof,tz=IST).tz_convert("UTC")
            if (ts>cutoff).any(): raise ValueError("Feature row contains information timestamped after the as-of-date cutoff.")
        X=eligible[trained]
        if X.isna().any().any(): raise ValueError("Feature row contains missing values; no silent imputation is allowed at inference.")
        pred=model.predict(X)[0]
        classes=list(getattr(model,"classes_",[]))
        label_map={1:"Bullish",0:"Bearish",-1:"Bearish"}
        label=label_map.get(pred,str(pred))
        prob=None
        if hasattr(model,"predict_proba"):
            probs=model.predict_proba(X)[0]
            if len(classes)==len(probs):
                idx=classes.index(pred) if pred in classes else None
                if idx is not None: prob=float(probs[idx])
        record.update(status="ok",prediction_label=label,class_probability=prob,expiry_date=expiry.isoformat(),model_version=os.getenv("MODEL_VERSION","extratrees_model.joblib"),message="Model output only; probability is not a profit probability.")
    except Exception as exc:
        record["message"]=f"{type(exc).__name__}: {exc}"
        print("PREDICTION_UNAVAILABLE:",record["message"],file=sys.stderr)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    old={"predictions":[]}
    if OUT.exists():
        try: old=json.loads(OUT.read_text())
        except Exception: pass
    rows=[x for x in old.get("predictions",[]) if x.get("as_of_date")!=requested]
    rows.append(record); rows.sort(key=lambda x:x.get("as_of_date",""))
    payload={"schema_version":1,"generated_at_utc":datetime.now(timezone.utc).isoformat(),"message":"Predictions are only published when compatible model/data/calendar checks pass; unavailable records are retained for audit.","predictions":rows}
    OUT.write_text(json.dumps(payload,indent=2)+"\n")
    print("PREDICTION_STATUS:",record["status"],"AS_OF_DATE:",requested,"EXPIRY:",record.get("expiry_date") or "unavailable")
    return 0 if record["status"]=="ok" else 2
if __name__=="__main__": raise SystemExit(main())
