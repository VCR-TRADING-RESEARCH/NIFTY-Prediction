#!/usr/bin/env python3
"""Compare an independent public NIFTY minute archive with official daily OHLC.

Source: technovusin/nifty50-historical-data. Publisher documents IST timestamps,
remaining missing/frozen/special-session bars. This is diagnostic, not official ground truth.
"""
from __future__ import annotations
import json, time
from datetime import date
from pathlib import Path
from typing import Any
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"reconciliation"
CACHE=ROOT/"data"/"cache"/"alternative-minute"
BASE="https://raw.githubusercontent.com/technovusin/nifty50-historical-data/main/1min"
START=date(2019,2,1)
END=date(2026,10,25)
UA="Mozilla/5.0 (compatible; NIFTYPredictionResearch/1.0)"

def source_files(start:date=START,end:date=END)->list[str]:
    paths=[]
    for year in range(start.year,min(end.year,2025)+1):
        paths.append(f"{BASE}/{year}/NIFTY50_1min_{year}.csv")
    if end.year>=2026:
        for month in range(1,end.month+1):
            paths.append(f"{BASE}/2026/NIFTY50_1min_2026-{month:02d}.csv")
    return paths

def fetch_csv(url:str,path:Path,session:requests.Session,force:bool=False)->Path:
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.stat().st_size>100_000 and not force:return path
    last="unknown error"
    for attempt in range(3):
        try:
            response=session.get(url,timeout=(8,35));response.raise_for_status()
            if len(response.content)<100_000:raise ValueError(f"unexpectedly small CSV: {len(response.content)} bytes")
            temp=path.with_suffix(path.suffix+".tmp");temp.write_bytes(response.content);temp.replace(path);return path
        except Exception as exc:
            last=f"{type(exc).__name__}: {str(exc)[:220]}"
            if attempt<2:time.sleep(1.5*(attempt+1))
    raise RuntimeError(f"Could not obtain {url.rsplit('/',1)[-1]}: {last}")

def colname(frame:pd.DataFrame,names:tuple[str,...])->str|None:
    cols={str(c).strip().casefold():c for c in frame.columns}
    return next((cols[n.casefold()] for n in names if n.casefold() in cols),None)

def aggregate_minute_frame(frame:pd.DataFrame)->pd.DataFrame:
    tscol=colname(frame,("Timestamp","Datetime","DateTime","Date Time","ts"))
    if tscol:
        ts=pd.to_datetime(frame[tscol],errors="coerce")
        if getattr(ts.dt,"tz",None) is not None:ts=ts.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    else:
        datecol,timecol,epochcol=colname(frame,("Date",)),colname(frame,("Time",)),colname(frame,("Epoch","epoch"))
        if datecol and timecol:ts=pd.to_datetime(frame[datecol].astype(str)+" "+frame[timecol].astype(str),errors="coerce",dayfirst=True)
        elif epochcol:ts=pd.to_datetime(pd.to_numeric(frame[epochcol],errors="coerce"),unit="s",utc=True).dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
        else:raise ValueError("No recognized Timestamp, Date+Time or Epoch column")
    names={k:colname(frame,(k,k.title())) for k in ("open","high","low","close")}
    if any(v is None for v in names.values()):raise ValueError("Expected Open/High/Low/Close columns")
    bars=pd.DataFrame({"ts":ts,**{k:pd.to_numeric(frame[v],errors="coerce") for k,v in names.items()}})
    bars=bars.dropna(subset=["ts","open","high","low","close"])
    bars=bars[(bars.ts.dt.date>=START)&(bars.ts.dt.date<=END)]
    clock=bars.ts.dt.time
    bars=bars[(clock>=pd.Timestamp("09:15").time())&(clock<=pd.Timestamp("15:29").time())].sort_values("ts")
    bars["session_date"]=bars.ts.dt.date
    if bars.empty:return pd.DataFrame(columns=["session_date","alternative_open","alternative_high","alternative_low","alternative_close","alternative_bars","first_bar","last_bar"])
    return bars.groupby("session_date",sort=True).agg(
        alternative_open=("open","first"),alternative_high=("high","max"),alternative_low=("low","min"),
        alternative_close=("close","last"),alternative_bars=("close","size"),first_bar=("ts","min"),last_bar=("ts","max")
    ).reset_index()

def build_alternative_daily()->tuple[pd.DataFrame,list[dict[str,Any]]]:
    session=requests.Session();session.headers.update({"User-Agent":UA,"Accept":"text/csv,*/*"})
    frames=[];manifest=[]
    for url in source_files():
        filename=url.rsplit("/",1)[-1]
        try:
            path=fetch_csv(url,CACHE/filename,session)
            daily=aggregate_minute_frame(pd.read_csv(path,low_memory=False))
            if daily.empty:raise ValueError("No valid in-session rows after timestamp/OHLC validation")
            frames.append(daily);manifest.append({"file":filename,"status":"ok","bytes":path.stat().st_size,"daily_rows":len(daily)})
        except Exception as exc:manifest.append({"file":filename,"status":"error","error":f"{type(exc).__name__}: {str(exc)[:300]}"})
    if not frames:raise RuntimeError("No alternative minute-source files could be parsed")
    out=pd.concat(frames,ignore_index=True).sort_values(["session_date","last_bar"]).drop_duplicates("session_date",keep="last").reset_index(drop=True)
    return out,manifest

def compare_sources(alternative:pd.DataFrame,official:pd.DataFrame,primary:pd.DataFrame)->tuple[pd.DataFrame,pd.DataFrame,dict[str,Any]]:
    official=official.copy();official["session_date"]=pd.to_datetime(official.session_date,errors="coerce").dt.date
    official=official[["session_date"]+[c for c in ("official_open","official_high","official_low","official_close") if c in official]].drop_duplicates("session_date")
    primary=primary.copy();primary["session_date"]=pd.to_datetime(primary.session_date,errors="coerce").dt.date
    primary=primary[["session_date"]+[c for c in ("session_open","session_high","session_low","session_close") if c in primary]].drop_duplicates("session_date")
    rows=alternative.merge(official,on="session_date",how="inner",validate="one_to_one").merge(primary,on="session_date",how="left",validate="one_to_one")
    rows["year"]=pd.to_datetime(rows.session_date).dt.year
    yearly=[]
    for year,g in rows.groupby("year",sort=True):
        item={"year":int(year),"rows_compared":int(len(g))}
        for field in ("open","high","low","close"):
            off="official_close" if field=="close" else f"official_{field}"
            altcol=f"alternative_{field}";primcol=f"session_{field}"
            if off not in g:continue
            adiff=(g[altcol]-g[off]).abs()
            rows.loc[g.index,f"alternative_{field}_abs_difference"]=adiff
            rows.loc[g.index,f"alternative_{field}_over_1pt"]=adiff>1
            item[f"alternative_{field}_mismatches_over_1pt"]=int((adiff>1).sum())
            item[f"alternative_{field}_median_abs_difference"]=float(adiff.median())
            item[f"alternative_{field}_p95_abs_difference"]=float(adiff.quantile(.95))
            if primcol in g:
                pdiff=(g[primcol]-g[off]).abs()
                rows.loc[g.index,f"primary_{field}_abs_difference"]=pdiff
                item[f"primary_{field}_mismatches_over_1pt"]=int((pdiff>1).sum())
                item[f"primary_{field}_median_abs_difference"]=float(pdiff.median())
                item[f"primary_{field}_p95_abs_difference"]=float(pdiff.quantile(.95))
        yearly.append(item)
    rows["alternative_vs_primary_close_abs_difference"]=(rows.alternative_close-rows.session_close).abs()
    ad=rows["alternative_close_abs_difference"].dropna()
    pdiff=rows["primary_close_abs_difference"].dropna() if "primary_close_abs_difference" in rows else pd.Series(dtype=float)
    report={
        "generated_utc":pd.Timestamp.now(tz="UTC").isoformat(),
        "source":"technovusin/nifty50-historical-data 1-minute CSV repository",
        "source_url":"https://github.com/technovusin/nifty50-historical-data",
        "source_is_official":False,"data_status":"DIAGNOSTIC_ONLY",
        "alternative_rows":int(len(alternative)),"official_rows":int(len(official)),"sessions_compared":int(len(rows)),
        "official_session_coverage_fraction":round(len(rows)/max(1,len(official)),6),
        "alternative_close_mismatches_over_1_point":int((ad>1).sum()),
        "alternative_close_median_abs_difference_points":float(ad.median()) if len(ad) else None,
        "alternative_close_p95_abs_difference_points":float(ad.quantile(.95)) if len(ad) else None,
        "alternative_close_max_abs_difference_points":float(ad.max()) if len(ad) else None,
        "primary_close_mismatches_over_1_point":int((pdiff>1).sum()),
        "primary_close_median_abs_difference_points":float(pdiff.median()) if len(pdiff) else None,
        "primary_close_p95_abs_difference_points":float(pdiff.quantile(.95)) if len(pdiff) else None,
        "alternative_vs_primary_close_median_abs_difference_points":float(rows.alternative_vs_primary_close_abs_difference.median()) if len(rows) else None,
        "source_limitations":[
            "Third-party GitHub archive, not an NSE official source.",
            "Publisher documents residual missing bars, frozen-price stretches, and special-session exceptions.",
            "Daily OHLC is aggregated from 09:15-15:29 IST; last-bar timestamp semantics remain part of the diagnostic."
        ]
    }
    return rows,pd.DataFrame(yearly).sort_values("year"),report

def main()->int:
    OUT.mkdir(parents=True,exist_ok=True);rpath=OUT/"alternative_minute_source_report.json"
    try:
        alt,manifest=build_alternative_daily()
        op=OUT/"nifty50_official_daily.csv";pp=OUT/"minute_vs_official_daily.csv"
        if not op.exists() or not pp.exists():raise FileNotFoundError("Run official reconciliation first")
        rows,yearly,report=compare_sources(alt,pd.read_csv(op),pd.read_csv(pp))
        report["file_manifest"]=manifest
        rows.to_csv(OUT/"alternative_minute_vs_official_daily.csv",index=False)
        yearly.to_csv(OUT/"alternative_minute_comparison_by_year.csv",index=False)
        rpath.write_text(json.dumps(report,indent=2,default=str)+"\n",encoding="utf-8")
        print("ALTERNATIVE_SOURCE_AUDIT:",json.dumps({k:report[k] for k in (
            "data_status","alternative_rows","sessions_compared","official_session_coverage_fraction",
            "alternative_close_mismatches_over_1_point","alternative_close_median_abs_difference_points",
            "primary_close_mismatches_over_1_point","primary_close_median_abs_difference_points")},indent=2))
    except Exception as exc:
        report={"generated_utc":pd.Timestamp.now(tz="UTC").isoformat(),"source":"technovusin/nifty50-historical-data",
                "data_status":"SOURCE_FAILED","error":f"{type(exc).__name__}: {str(exc)[:600]}",
                "note":"Source failure does not imply the existing candidate archive passes validation."}
        rpath.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print("ALTERNATIVE_SOURCE_AUDIT_FAILED:",json.dumps(report,indent=2))
    return 0

if __name__=="__main__":raise SystemExit(main())
