from __future__ import annotations
import argparse,csv,hashlib,io,json,time,zipfile
from datetime import datetime,timezone
from pathlib import Path
import requests
TARGETS=[
{"date":"2019-10-27","symbol":"HDFC","session":"Sunday Diwali Muhurat","isin":"INE001A01036"},
{"date":"2020-02-01","symbol":"HDFC","session":"Saturday Union Budget special session","isin":"INE001A01036"},
{"date":"2020-11-14","symbol":"HDFC","session":"Saturday Diwali Muhurat","isin":"INE001A01036"}]
HEADERS={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36","Accept":"*/*","Referer":"https://www.nseindia.com/"}
HOSTS=["https://archives.nseindia.com","https://nsearchives.nseindia.com"]
def urls(day):
 d=datetime.strptime(day,"%Y-%m-%d"); fn=f"cm{d.strftime('%d%b%Y').upper()}bhav.csv.zip"
 path=f"/content/historical/EQUITIES/{d.year}/{d.strftime('%b').upper()}/{fn}"
 return [host+path for host in HOSTS]
def norm(v): return str(v or "").strip().upper()
def parse_archive(blob,item,url):
 with zipfile.ZipFile(io.BytesIO(blob)) as z:
  names=[n for n in z.namelist() if n.lower().endswith(".csv")]
  if len(names)!=1: raise ValueError("CSV_MEMBER_COUNT_"+str(len(names)))
  text=z.read(names[0]).decode("utf-8-sig",errors="replace")
 reader=csv.DictReader(io.StringIO(text))
 if not reader.fieldnames: raise ValueError("CSV_HEADER_MISSING")
 matches=[]
 for row in reader:
  r={norm(k):v for k,v in row.items() if k is not None}
  if norm(r.get("SYMBOL"))!=item["symbol"] or norm(r.get("SERIES"))!="EQ": continue
  raw=str(r.get("DATE1","")).strip()
  parsed=None
  for fmt in ("%d-%b-%Y","%d-%B-%Y","%Y-%m-%d","%d/%m/%Y"):
   try: parsed=datetime.strptime(raw,fmt).strftime("%Y-%m-%d"); break
   except ValueError: pass
  if parsed==item["date"]: matches.append(r)
 if len(matches)!=1:
  return {"status":"NO_EQ_ROW_IN_DIRECT_NSE_ARCHIVE" if not matches else "DUPLICATE_EQ_ROWS_IN_DIRECT_NSE_ARCHIVE","row_count":len(matches),"ohlc_valid":False,"volume_valid":False}
 r=matches[0]
 def num(*keys):
  for k in keys:
   if k in r and str(r[k]).strip():
    try:return float(str(r[k]).replace(",",""))
    except ValueError:return float("nan")
  return float("nan")
 op=num("OPEN_PRICE","OPEN"); hi=num("HIGH_PRICE","HIGH"); lo=num("LOW_PRICE","LOW"); cl=num("CLOSE_PRICE","CLOSE")
 vol=num("TTL_TRD_QNTY","TOTTRDQTY","TOTAL_TRADED_QUANTITY")
 finite=all(v==v and abs(v)!=float("inf") for v in (op,hi,lo,cl))
 ohlc=bool(finite and min(op,hi,lo,cl)>0 and lo<=min(op,cl)<=max(op,cl)<=hi)
 volume=bool(vol==vol and abs(vol)!=float("inf") and vol>=0)
 isin=norm(r.get("ISIN"))
 identity="NOT_PUBLISHED_IN_LEGACY_FILE" if not isin else ("MATCH" if isin==item["isin"] else "MISMATCH")
 ok=ohlc and volume and identity in ("MATCH","NOT_PUBLISHED_IN_LEGACY_FILE")
 return {"status":"VALID_DIRECT_NSE_EQ_OHLCV_ROW" if ok else "INVALID_DIRECT_NSE_ROW","row_count":1,"ohlc_valid":ohlc,"volume_valid":volume,"identity_status":identity,"source_url":url,"source_archive_sha256":hashlib.sha256(blob).hexdigest(),"raw_values_published":False}
def check(item):
 errors=[]
 for url in urls(item["date"]):
  for attempt in range(2):
   try:
    resp=requests.get(url,headers=HEADERS,timeout=45)
    if resp.status_code!=200: errors.append("HTTP_"+str(resp.status_code)); break
    if not resp.content.startswith(b"PK"): errors.append("INVALID_ZIP_SIGNATURE"); break
    return {**item,**parse_archive(resp.content,item,url)}
   except (requests.RequestException,zipfile.BadZipFile,ValueError,UnicodeError) as exc: errors.append(type(exc).__name__)
   if attempt==0:time.sleep(2)
 return {**item,"status":"DIRECT_NSE_ARCHIVE_UNAVAILABLE","row_count":0,"ohlc_valid":False,"volume_valid":False,"source_error_categories":sorted(set(errors))}
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",default=".");p.add_argument("--run-id",default="");a=p.parse_args()
 results=[check(x) for x in TARGETS]; good=sum(x["status"]=="VALID_DIRECT_NSE_EQ_OHLCV_ROW" for x in results)
 now=datetime.now(timezone.utc).isoformat()
 report={"schema_version":1,"methodology_version":"bup01-c1-direct-nse-special-session-v1","updated_at_utc":now,"github_actions_run_id":a.run_id or None,"status":"PASS_ALL_THREE" if good==3 else "PARTIAL_DIRECT_ARCHIVE_COVERAGE","summary":{"special_sessions":3,"valid_direct_nse_rows":good,"raw_prices_or_volume_published":False},"source":{"publisher":"National Stock Exchange of India","archive_format":"Legacy CM equity bhavcopy ZIP/CSV","url_pattern":"https://archives.nseindia.com/content/historical/EQUITIES/YYYY/MON/cmDDMONYYYYbhav.csv.zip","independent_of_third_party_mirror":True},"results":results,"limitations":["Legacy CSV may omit ISIN; identity is then symbol/series/date only.","HTTP 404 is unavailable, not proof of no trade.","OHLCV validation does not complete the corporate-action adjustment ledger."]}
 root=Path(a.root);out=root/"research/constituent_weekly/C1_DIRECT_NSE_SPECIAL_SESSION_AUDIT.json";md=root/"research/constituent_weekly/C1_DIRECT_NSE_SPECIAL_SESSION_AUDIT.md";out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 lines=["# C1 Direct NSE Special-session Bhavcopy Audit","",f"Updated: {now}",f"Status: {report['status']}","",f"Direct NSE EQ OHLCV rows validated: {good}/3.","","| Date | Security | Session | Result | OHLC | Volume |","|---|---|---|---|---|---|"]
 for x in results:lines.append(f"| {x['date']} | {x['symbol']} | {x['session']} | {x['status']} | {'PASS' if x.get('ohlc_valid') else '—'} | {'PASS' if x.get('volume_valid') else '—'} |")
 lines += ["","## Method","", "Fetched each exact legacy NSE cash-market bhavcopy ZIP from both documented archive hosts, parsed its CSV, filtered exact SYMBOL/EQ/DATE1, validated OHLC ordering and nonnegative volume. Only source URL, archive SHA-256 and validation flags are retained; raw values are not published.","","## Interpretation","", "A missing file or absent row is not automatically classified as a holiday/no-trade day. All three dates remain in the expected-session denominator unless exchange evidence supports a registered exclusion.","","## Limitations",*["- "+x for x in report["limitations"]]]
 md.write_text("\n".join(lines)+"\n",encoding="utf-8")
 print(json.dumps(report["summary"],sort_keys=True))
if __name__=="__main__":main()
