#!/usr/bin/env python3
"""Compare the 10:00–10:03 NIFTY spot anchor across two published minute archives.

Neither public archive is official ground truth and the secondary provider lineage is
unverified. This is a diagnostic cross-check, not permission to train confirmatory models.
"""
from __future__ import annotations
import hashlib, json, sys, time
from datetime import date
from pathlib import Path
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/"data/cache/alternative-minute"
OUT=ROOT/"data/reconciliation"
SECONDARY_URL="https://raw.githubusercontent.com/sandeepkapri/Nifty50-Minute-Data/main/nifty50_candlestick_data.csv"
START=date(2019,2,1); END=date(2024,3,27)

def secondary_minutes(force=False):
    path=CACHE/"sandeep_nifty50_candlestick_data.csv"
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or force:
        response=requests.get(SECONDARY_URL,headers={"User-Agent":"NIFTYPredictionResearch/1.0"},timeout=(10,180))
        response.raise_for_status()
        payload=response.content
        if len(payload)<1_000_000: raise ValueError("Secondary CSV unexpectedly small")
        tmp=path.with_suffix(".tmp"); tmp.write_bytes(payload); tmp.replace(path)
    payload=path.read_bytes()
    frame=pd.read_csv(path,low_memory=False)
    cols={str(c).strip().casefold():c for c in frame.columns}
    def col(*names):
        for name in names:
            if name.casefold() in cols: return cols[name.casefold()]
        raise ValueError("Missing expected source column: "+"/".join(names))
    d=frame[col("Date")].astype(str).str.strip()
    t=frame[col("Time")].astype(str).str.strip()
    parsed=pd.to_datetime(d,format="%d-%m-%y",errors="coerce")
    mask=parsed.isna()
    if mask.any(): parsed.loc[mask]=pd.to_datetime(d.loc[mask],errors="coerce",dayfirst=True)
    ts=pd.to_datetime(parsed.dt.strftime("%Y-%m-%d")+" "+t,errors="coerce")
    result=pd.DataFrame({"timestamp":ts,"open":pd.to_numeric(frame[col("Open")],errors="coerce"),
                         "high":pd.to_numeric(frame[col("High")],errors="coerce"),
                         "low":pd.to_numeric(frame[col("Low")],errors="coerce"),
                         "close":pd.to_numeric(frame[col("Close")],errors="coerce")})
    result=result.dropna().sort_values("timestamp").drop_duplicates("timestamp",keep="last")
    result=result[(result.timestamp.dt.date>=START)&(result.timestamp.dt.date<=END)]
    result=result[(result.timestamp.dt.time>=pd.Timestamp("09:15").time())&(result.timestamp.dt.time<=pd.Timestamp("15:29:59").time())]
    result=result[(result[["open","high","low","close"]]>0).all(axis=1)]
    return result,{"source_url":SECONDARY_URL,"sha256":hashlib.sha256(payload).hexdigest(),"bytes":len(payload),"bars":len(result),
                   "lineage_independently_verified":False,"official_source":False}

def anchors(frame, prefix):
    frame=frame.copy()
    frame["session_date"]=frame.timestamp.dt.date
    frame=frame[(frame.timestamp.dt.time>=pd.Timestamp("10:00").time())&
                (frame.timestamp.dt.time<=pd.Timestamp("10:03").time())]
    frame=frame.sort_values("timestamp").drop_duplicates("session_date",keep="first")
    return frame[["session_date","timestamp","open"]].rename(columns={"timestamp":prefix+"_timestamp","open":prefix+"_anchor_open"})

def main():
    force=False
    try:
        from scripts.research_core import load_minute_files
    except ImportError:
        sys.path.insert(0,str(ROOT/"scripts"))
        from research_core import load_minute_files
    primary_files=sorted((ROOT/"data/raw/nifty50").glob("*.csv"))
    if not primary_files: raise FileNotFoundError("Primary archive absent; run scripts/fetch_data.py first")
    primary,_=load_minute_files(primary_files)
    primary=primary[(primary.timestamp.dt.date>=START)&(primary.timestamp.dt.date<=END)]
    second,manifest=secondary_minutes(force)
    pa=anchors(primary,"primary"); sa=anchors(second,"secondary")
    joined=pa.merge(sa,on="session_date",how="inner",validate="one_to_one")
    joined["timestamp_match"]=joined.primary_timestamp.eq(joined.secondary_timestamp)
    joined["absolute_anchor_open_difference"]=(joined.primary_anchor_open-joined.secondary_anchor_open).abs()
    joined["mismatch_over_1_point"]=joined.absolute_anchor_open_difference>1.0
    OUT.mkdir(parents=True,exist_ok=True)
    joined.to_csv(OUT/"anchor_source_comparison.csv",index=False)
    diff=joined.absolute_anchor_open_difference
    report={
      "generated_utc":pd.Timestamp.now(tz="UTC").isoformat(),
      "status":"DIAGNOSTIC_ONLY",
      "primary_source":"technovusin/nifty50-historical-data; this is the pipeline's current input archive",
      "secondary_source":manifest,
      "window":{"start":str(START),"end":str(END)},
      "counts":{"primary_anchors":int(len(pa)),"secondary_anchors":int(len(sa)),"overlap_sessions":int(len(joined)),
                "exact_timestamp_matches":int(joined.timestamp_match.sum()),"anchor_open_mismatches_over_1_point":int(joined.mismatch_over_1_point.sum())},
      "absolute_difference_points":{"median":float(diff.median()) if len(diff) else None,"p95":float(diff.quantile(.95)) if len(diff) else None,"max":float(diff.max()) if len(diff) else None},
      "acceptance":"Does not pass the independent-anchor gate: both datasets are non-official and the secondary provider lineage is unverified. Use results to locate discrepant dates only.",
      "output":"data/reconciliation/anchor_source_comparison.csv"
    }
    (OUT/"anchor_source_comparison_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
