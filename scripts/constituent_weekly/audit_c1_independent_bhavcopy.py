from __future__ import annotations
import argparse, hashlib, json, re, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import requests

SOURCE_REPO="floyds1995/Auto-Index-Constituents-Tracker"
SOURCE_REVISION="aa57b1050383c33e436f81844230ad2a4d52c949"
RAW_ROOT="https://raw.githubusercontent.com/"+SOURCE_REPO+"/"+SOURCE_REVISION+"/NSE/RawDataOHLCV/parquet"
CHECKS=[
 {"date":"2018-11-07","symbol":"HDFC","session":"Diwali Muhurat","expected_isin":"INE001A01036"},
 {"date":"2019-10-27","symbol":"HDFC","session":"Diwali Muhurat (Sunday)","expected_isin":"INE001A01036"},
 {"date":"2020-02-01","symbol":"HDFC","session":"Union Budget special session","expected_isin":"INE001A01036"},
 {"date":"2020-11-14","symbol":"HDFC","session":"Diwali Muhurat (Saturday)","expected_isin":"INE001A01036"},
 {"date":"2021-11-04","symbol":"HDFC","session":"Diwali Muhurat","expected_isin":"INE001A01036"},
 {"date":"2022-10-24","symbol":"HDFC","session":"Diwali Muhurat","expected_isin":"INE001A01036"},
 {"date":"2025-10-21","symbol":"TATAMOTORS","session":"Diwali Muhurat (13:45-14:45)","expected_isin":"INE155A01022"},
]
BEGIN="<!-- C1_INDEPENDENT_BHAVCOPY_START -->"
END="<!-- C1_INDEPENDENT_BHAVCOPY_END -->"

def sha256(data): return hashlib.sha256(data).hexdigest()

def fetch_partition(month,folder):
 path=folder/(month+".parquet")
 url=RAW_ROOT+"/"+month+".parquet"
 error=None
 for attempt in range(3):
  try:
   response=requests.get(url,headers={"User-Agent":"BUP-01-personal-research/1.0","Accept":"application/octet-stream"},timeout=60)
   if response.status_code!=200: error="HTTP_"+str(response.status_code)
   elif not response.content.startswith(b"PAR1"): error="INVALID_PARQUET_MAGIC"
   else:
    path.write_bytes(response.content)
    return path,sha256(response.content),None
  except requests.RequestException as exc: error=type(exc).__name__
  if attempt<2: time.sleep(1.5*(attempt+1))
 return None,None,error or "DOWNLOAD_FAILED"

def validate_row(path,item,file_sha):
 columns=pq.read_schema(path).names
 wanted=[c for c in ["SYMBOL","SERIES","DATE","OPEN","HIGH","LOW","CLOSE","VOLUME","ISIN"] if c in columns]
 df=pd.read_parquet(path,columns=wanted)
 required={"SYMBOL","SERIES","DATE","OPEN","HIGH","LOW","CLOSE","VOLUME"}
 if not required.issubset(df.columns):
  return {**item,"status":"SOURCE_SCHEMA_INCOMPLETE","row_count":0,"ohlc_valid":False,"volume_valid":False,"identity_status":"NOT_CHECKED","source_file_sha256":file_sha}
 dates=pd.to_datetime(df["DATE"],errors="coerce").dt.strftime("%Y-%m-%d")
 symbols=df["SYMBOL"].astype("string").str.upper().str.strip()
 series=df["SERIES"].astype("string").str.upper().str.strip()
 rows=df.loc[dates.eq(item["date"]) & symbols.eq(item["symbol"]) & series.eq("EQ")].copy()
 if len(rows)!=1:
  return {**item,"status":"NO_EQ_ROW_IN_MIRROR" if len(rows)==0 else "DUPLICATE_EQ_ROWS_IN_MIRROR","row_count":int(len(rows)),"ohlc_valid":False,"volume_valid":False,"identity_status":"NOT_CHECKED","source_file_sha256":file_sha}
 row=rows.iloc[0]
 v={k:pd.to_numeric(pd.Series([row[k]]),errors="coerce").iloc[0] for k in ["OPEN","HIGH","LOW","CLOSE","VOLUME"]}
 finite=all(np.isfinite(float(v[k])) for k in ["OPEN","HIGH","LOW","CLOSE"])
 positive=finite and all(float(v[k])>0 for k in ["OPEN","HIGH","LOW","CLOSE"])
 ohlc=bool(positive and float(v["LOW"])<=min(float(v["OPEN"]),float(v["CLOSE"])) and float(v["HIGH"])>=max(float(v["OPEN"]),float(v["CLOSE"])) and float(v["HIGH"])>=float(v["LOW"]))
 volume=bool(np.isfinite(float(v["VOLUME"])) and float(v["VOLUME"])>=0)
 isin=""
 if "ISIN" in rows.columns and pd.notna(row.get("ISIN")): isin=str(row.get("ISIN")).strip().upper()
 identity="ISIN_NOT_PUBLISHED_IN_MIRROR" if not isin else ("MATCH" if isin==item["expected_isin"] else "MISMATCH")
 valid=ohlc and volume and identity in ("MATCH","ISIN_NOT_PUBLISHED_IN_MIRROR")
 return {**item,"status":"VALID_EQ_OHLCV_ROW" if valid else "INVALID_OR_IDENTITY_REVIEW","row_count":1,"ohlc_valid":ohlc,"volume_valid":volume,"identity_status":identity,"isin_available":bool(isin),"source_file_sha256":file_sha,"raw_values_published":False}

def replace_marked(text,block):
 if BEGIN in text and END in text:
  a=text.index(BEGIN); b=text.index(END,a)+len(END)
  return text[:a]+block+text[b:]
 return text.rstrip()+"\n\n"+block+"\n"

def replace_heading(text,heading,body):
 if heading in text:
  a=text.index(heading)
  nxt=re.search(r"(?m)^## ",text[a+len(heading):])
  b=a+len(heading)+nxt.start() if nxt else len(text)
  return text[:a]+body.rstrip()+"\n\n"+text[b:].lstrip("\n")
 return text.rstrip()+"\n\n"+body.rstrip()+"\n"

def publish(root,results,updated,run_id):
 matched=sum(x.get("status")=="VALID_EQ_OHLCV_ROW" for x in results)
 no_row=sum(x.get("status")=="NO_EQ_ROW_IN_MIRROR" for x in results)
 dup=sum(x.get("status")=="DUPLICATE_EQ_ROWS_IN_MIRROR" for x in results)
 unavailable=sum(x.get("status")=="SOURCE_PARTITION_UNAVAILABLE" for x in results)
 status="PASS_ALL_SEVEN" if matched==len(CHECKS) else "PARTIAL_SOURCE_COVERAGE"
 report={
  "schema_version":1,"methodology_version":"bup01-c1-independent-bhavcopy-mirror-v1",
  "updated_at_utc":updated,"github_actions_run_id":run_id or None,"status":status,
  "summary":{"target_security_date_pairs":7,"valid_independent_eq_ohlcv_rows":matched,"mirror_has_no_eq_row":no_row,"duplicate_eq_rows":dup,"source_partitions_unavailable":unavailable,"raw_prices_or_volume_published":False,"coverage_interpretation":"Mirror no-row is not proof of no exchange bar. Its README describes a weekday-only collection loop; weekend Muhurat and Saturday Budget sessions are outside its reliable absence coverage."},
  "source":{"repository":SOURCE_REPO,"revision":SOURCE_REVISION,"readme":"https://github.com/"+SOURCE_REPO+"/blob/"+SOURCE_REVISION+"/README.md","updater":"https://github.com/"+SOURCE_REPO+"/blob/"+SOURCE_REVISION+"/NSE/RawDataOHLCV/update_ohlcv.py","source_provenance":"Repository README states NSE equity daily bhavcopy is collected from NSE archive endpoints and stored by month as Parquet.","software_license":"MIT (repository code)","market_data_license":"No separate data licence identified; raw data are processed only in runner temporary storage and are not redistributed in this project."},
  "results":results,
  "limitations":["Independent public mirror, not a direct exchange response or a second broker feed.","The source collector enumerates weekdays only; absence on 2019-10-27, 2020-02-01 and 2020-11-14 is structural and cannot resolve those genuine special sessions.","The newer source schema may omit ISIN; missing ISIN is reported explicitly, not silently inferred.","A valid daily bar does not complete the separate corporate-action adjustment ledger.","No raw OHLCV values, security prices or volume observations are copied into the report."]
 }
 out=root/"research/constituent_weekly/C1_INDEPENDENT_BHAVCOPY_AUDIT.json"
 md=root/"research/constituent_weekly/C1_INDEPENDENT_BHAVCOPY_AUDIT.md"
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 lines=["# C1 Independent NSE Bhavcopy Mirror Cross-check","",f"Updated: {updated}",f"Status: {status}","","## Result","",f"- Valid independent EQ OHLCV rows: {matched}/7.",f"- No EQ row in mirror: {no_row} (not proof that the exchange bar did not exist).",f"- Duplicate rows: {dup}; source partitions unavailable: {unavailable}.","- Raw prices and volume values are not published in this report.","","| Security | Date | Session | Mirror disposition | OHLC | Volume | Identity |","|---|---|---|---|---|---|---|"]
 for x in results:
  lines.append("| "+x["symbol"]+" | "+x["date"]+" | "+x["session"]+" | "+x["status"]+" | "+("PASS" if x.get("ohlc_valid") else "-")+" | "+("PASS" if x.get("volume_valid") else "-")+" | "+x.get("identity_status","-")+" |")
 lines += ["","## Source and provenance","", "- Repository: https://github.com/"+SOURCE_REPO,"- Pinned revision: "+SOURCE_REVISION,"- README: https://github.com/"+SOURCE_REPO+"/blob/"+SOURCE_REVISION+"/README.md","- Downloader: https://github.com/"+SOURCE_REPO+"/blob/"+SOURCE_REVISION+"/NSE/RawDataOHLCV/update_ohlcv.py","- Source README says NSE daily records originate from NSE bhavcopy archive endpoints. MIT licence covers repository code; no separate data licence was found. Raw data are not retained or redistributed.","","## Interpretation","","The mirror can corroborate rows it collected. Its downloader computes missing weekdays only; it does not systematically enumerate weekend exchange sessions. An absent row for 2019-10-27, 2020-02-01 or 2020-11-14 therefore cannot be read as evidence that no bhavcopy existed. Those dates remain unresolved pending a source with explicit special-session coverage.","No dates were removed from the denominator, no OHLCV values were inferred, and no adjustment factor was applied. Corporate-action audit remains a separate C1 blocker.","","## Reproducibility","", "- Per-month Parquet SHA-256 hashes are recorded in the JSON report.", "- C1_DAILY_COVERAGE.json remains the source of record for the original 106,385 / 106,392 coverage calculation."]
 md.write_text("\n".join(lines)+"\n",encoding="utf-8")
 block="\n".join([BEGIN,"## C1 independent bhavcopy mirror cross-check — 2026-11-02","",f"- Independent mirror returned {matched}/7 valid exact-date NSE EQ OHLCV rows.",f"- {no_row} target dates have no row in this mirror; its weekday-only collector cannot resolve the Sunday/Saturday special sessions.","- No raw values were republished and no missing bars were inferred. Original daily coverage remains 106,385/106,392 until every residual session is independently resolved or handled by a registered exclusion rule.","- Full audit report: C1_INDEPENDENT_BHAVCOPY_AUDIT.md; machine result: C1_INDEPENDENT_BHAVCOPY_AUDIT.json.","- Overall C1 remains PARTIAL / NOT PASSED; corporate-action verification remains incomplete; C2 stays locked.",END])
 sp=root/"research/constituent_weekly/STATUS.md"
 st=re.sub(r"(?m)^\*\*Last updated:\*\*.*$","**Last updated:** 2026-11-02  ",sp.read_text(encoding="utf-8"),count=1)
 sp.write_text(replace_marked(st,block),encoding="utf-8")
 rh="## 2026-11-02 — Independent NSE bhavcopy mirror cross-check"
 rb=rh+"\n\n"+f"- Audited seven exact security/date pairs using the pinned public NSE bhavcopy mirror.\n- Valid EQ OHLCV rows: {matched}/7; mirror no-row: {no_row}; duplicate rows: {dup}; unavailable source partitions: {unavailable}.\n- The mirror collector enumerates weekdays only, so no-row on 2019-10-27, 2020-02-01 and 2020-11-14 is inconclusive for those special sessions.\n- No raw prices/volumes were copied, no bar was fabricated, and the daily coverage denominator was unchanged. Corporate-action review remains open.\n- Evidence: C1_INDEPENDENT_BHAVCOPY_AUDIT.md and C1_INDEPENDENT_BHAVCOPY_AUDIT.json."
 p=root/"logs/RESEARCH_LOG.md"; p.write_text(replace_heading(p.read_text(encoding="utf-8"),rh,rb),encoding="utf-8")
 eh="## E0087 — 2026-11-02 — Independent-source calendar coverage limitation"
 eb=eh+"\n\n- Class: Data-source coverage limitation, not a market-data disagreement.\n"+f"- Observed: pinned independent NSE bhavcopy mirror returned {matched}/7 valid exact-date EQ OHLCV rows; {no_row} dates had no EQ row in that mirror.\n- Limitation: the mirror collector enumerates weekdays only. It cannot prove absence for Sunday 2019-10-27 or Saturdays 2020-02-01 / 2020-11-14, all genuine special sessions.\n- Correction: treat mirror no-row as INCONCLUSIVE; retain all seven dates in the denominator; use a source with explicit special-session capture for remaining dates. No price was imputed.\n- Impact: no change to 106,385/106,392 daily coverage. C1 remains PARTIAL and C2 remains gated."
 p=root/"logs/ERROR_LOG.md"; p.write_text(replace_heading(p.read_text(encoding="utf-8"),eh,eb),encoding="utf-8")
 ch="## 2026-11-02 — User resumed C1 residual-bar audit"
 cb=ch+"\n\n- Inspected the C1 branch, registered plan, status, daily-coverage JSON, corporate-action catalogue, research/error logs and latest workflow results before continuing.\n- Added a bounded independent-source check against a pinned public NSE bhavcopy mirror; it validates exact EQ rows and publishes no raw price/volume values.\n"+f"- Result: {matched}/7 valid rows; {no_row} no-row cases are not treated as missing exchange data because the mirror collector is weekday-only and omits weekend special sessions.\n- All seven sessions remain in the denominator; C1 remains partial and the corporate-action gate remains open. No hidden reasoning or credentials are written to this log."
 p=root/"logs/CONVERSATION_LOG.md"; p.write_text(replace_heading(p.read_text(encoding="utf-8"),ch,cb),encoding="utf-8")
 rp=root/"README.md"
 rblock="\n".join([BEGIN,"## C1 independent NSE bhavcopy mirror audit — 2026-11-02","",f"The pinned independent source returned {matched}/7 valid exact-date EQ OHLCV rows. Remaining mirror no-row results are inconclusive because its collector enumerates weekdays only and does not capture Sunday/Saturday special sessions. No values were imputed or republished; C1 remains PARTIAL / NOT PASSED and the corporate-action gate remains open.","","- Full audit report: https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_INDEPENDENT_BHAVCOPY_AUDIT.md","- Machine result: https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_INDEPENDENT_BHAVCOPY_AUDIT.json","- Method note: https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_INDEPENDENT_BHAVCOPY_METHOD.md",END])
 rp.write_text(replace_marked(rp.read_text(encoding="utf-8"),rblock),encoding="utf-8")
 print(json.dumps(report["summary"],sort_keys=True))
 return report

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--root",default=".")
 parser.add_argument("--run-id",default="")
 args=parser.parse_args()
 results=[]
 with tempfile.TemporaryDirectory(prefix="bup01-independent-bhavcopy-") as td:
  folder=Path(td); monthly={}
  for item in CHECKS:
   month=item["date"][:7]
   if month not in monthly: monthly[month]=fetch_partition(month,folder)
   path,digest,error=monthly[month]
   if path is None:
    results.append({**item,"status":"SOURCE_PARTITION_UNAVAILABLE","row_count":0,"ohlc_valid":False,"volume_valid":False,"identity_status":"NOT_CHECKED","source_error_category":error})
   else: results.append(validate_row(path,item,digest or ""))
 return publish(Path(args.root).resolve(),results,datetime.now(timezone.utc).isoformat(),args.run_id) and 0

if __name__=="__main__": raise SystemExit(main())
