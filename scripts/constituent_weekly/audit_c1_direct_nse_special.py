from __future__ import annotations
import argparse,csv,hashlib,io,json,time,zipfile,os
from datetime import datetime,timezone
from pathlib import Path
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_cache(payload,token,aad):
 if not token or not token.strip(): raise ValueError("HF_TOKEN required")
 key=hashlib.sha256(b"BUP01-TejHQ-EOD-cache-v1:"+token.strip().encode()).digest()
 nonce=os.urandom(12)
 return nonce+AESGCM(key).encrypt(nonce,payload,aad)

TARGETS=[
 {"date":"2018-11-07","symbol":"HDFC","isin":"INE001A01036","session":"Diwali Muhurat"},
 {"date":"2019-10-27","symbol":"HDFC","isin":"INE001A01036","session":"Sunday Diwali Muhurat"},
 {"date":"2020-02-01","symbol":"HDFC","isin":"INE001A01036","session":"Saturday Union Budget special session"},
 {"date":"2020-11-14","symbol":"HDFC","isin":"INE001A01036","session":"Saturday Diwali Muhurat"},
 {"date":"2021-11-04","symbol":"HDFC","isin":"INE001A01036","session":"Diwali Muhurat"},
 {"date":"2022-10-24","symbol":"HDFC","isin":"INE001A01036","session":"Diwali Muhurat"},
 {"date":"2025-10-21","symbol":"TATAMOTORS","isin":"INE155A01022","session":"Diwali Muhurat"},
]
HEADERS={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36","Accept":"*/*","Referer":"https://www.nseindia.com/"}
HOSTS=["https://archives.nseindia.com","https://nsearchives.nseindia.com"]
CUTOVER="2024-07-08"

def urls(day):
 if day>=CUTOVER:
  path="/content/cm/BhavCopy_NSE_CM_0_0_0_"+day.replace("-","")+"_F_0000.csv.zip"
  return ["https://nsearchives.nseindia.com"+path,"https://archives.nseindia.com"+path]
 d=datetime.strptime(day,"%Y-%m-%d")
 fn=f"cm{d.strftime('%d%b%Y').upper()}bhav.csv.zip"
 path=f"/content/historical/EQUITIES/{d.year}/{d.strftime('%b').upper()}/{fn}"
 return [host+path for host in HOSTS]

def norm(v): return str(v or "").strip().upper()
def parse_date(v):
 raw=str(v or "").strip()
 for fmt in ("%d-%b-%Y","%d-%B-%Y","%Y-%m-%d","%d/%m/%Y","%d-%m-%Y"):
  try:return datetime.strptime(raw,fmt).strftime("%Y-%m-%d")
  except ValueError:pass
 return None

def parse_archive(blob,item,url):
 with zipfile.ZipFile(io.BytesIO(blob)) as z:
  names=[n for n in z.namelist() if n.lower().endswith(".csv")]
  if len(names)!=1: raise ValueError("CSV_MEMBER_COUNT_"+str(len(names)))
  text=z.read(names[0]).decode("utf-8-sig",errors="replace")
 reader=csv.DictReader(io.StringIO(text))
 if not reader.fieldnames: raise ValueError("CSV_HEADER_MISSING")
 modern=item["date"]>=CUTOVER
 matches=[]
 for row in reader:
  r={norm(k):v for k,v in row.items() if k is not None}
  symbol=norm(r.get("TCKRSYMB") if modern else r.get("SYMBOL"))
  series=norm(r.get("SCTYSRS") if modern else r.get("SERIES"))
  day=parse_date(r.get("TRADDT") if modern else r.get("TIMESTAMP") or r.get("DATE1"))
  if symbol==item["symbol"] and series=="EQ" and day==item["date"]:
   matches.append(r)
 if len(matches)!=1:
  return {"status":"NO_EQ_ROW_IN_DIRECT_NSE_ARCHIVE" if not matches else "DUPLICATE_EQ_ROWS_IN_DIRECT_NSE_ARCHIVE","row_count":len(matches),"ohlc_valid":False,"volume_valid":False,"source_url":url,"source_archive_sha256":hashlib.sha256(blob).hexdigest()}
 r=matches[0]
 def num(*keys):
  for k in keys:
   if k in r and str(r[k]).strip():
    try:return float(str(r[k]).replace(",",""))
    except ValueError:return float("nan")
  return float("nan")
 if modern:
  op=num("OPNPRIC");hi=num("HGHPRIC");lo=num("LWPRIC");cl=num("CLSPRIC");vol=num("TTLTRADGVOL")
  isin=norm(r.get("ISIN"))
 else:
  op=num("OPEN");hi=num("HIGH");lo=num("LOW");cl=num("CLOSE");vol=num("TOTTRDQTY")
  isin=norm(r.get("ISIN"))
 finite=all(v==v and abs(v)!=float("inf") for v in (op,hi,lo,cl))
 ohlc=bool(finite and min(op,hi,lo,cl)>0 and lo<=min(op,cl)<=max(op,cl)<=hi)
 volume=bool(vol==vol and abs(vol)!=float("inf") and vol>=0)
 identity="MATCH" if isin==item["isin"] else ("NOT_PUBLISHED" if not isin else "MISMATCH")
 ok=ohlc and volume and identity in ("MATCH","NOT_PUBLISHED")
 sha=hashlib.sha256(blob).hexdigest()
 raw={"date":item["date"],"symbol":item["symbol"],"series":"EQ","isin":isin,"open":op,"high":hi,"low":lo,"close":cl,"volume":vol,"source_url":url,"source_archive_sha256":sha}
 return {"status":"VALID_DIRECT_NSE_EQ_OHLCV_ROW" if ok else "INVALID_DIRECT_NSE_ROW","row_count":1,"ohlc_valid":ohlc,"volume_valid":volume,"identity_status":identity,"source_url":url,"source_archive_sha256":sha,"raw_values_published":False,"_raw_row":raw}

def check(item):
 errors=[]
 for url in urls(item["date"]):
  for attempt in range(2):
   try:
    resp=requests.get(url,headers=HEADERS,timeout=45)
    if resp.status_code!=200:errors.append("HTTP_"+str(resp.status_code));break
    if not resp.content.startswith(b"PK"):errors.append("INVALID_ZIP_SIGNATURE");break
    return {**item,**parse_archive(resp.content,item,url)}
   except (requests.RequestException,zipfile.BadZipFile,ValueError,UnicodeError) as exc:errors.append(type(exc).__name__)
   if attempt==0:time.sleep(2)
 return {**item,"status":"DIRECT_NSE_ARCHIVE_UNAVAILABLE","row_count":0,"ohlc_valid":False,"volume_valid":False,"source_error_categories":sorted(set(errors))}

def main():
 p=argparse.ArgumentParser();p.add_argument("--root",default=".");p.add_argument("--run-id",default="");a=p.parse_args()
 results=[check(x) for x in TARGETS]
 raw_rows=[x.pop("_raw_row") for x in results if x.get("_raw_row")]
 good=sum(x["status"]=="VALID_DIRECT_NSE_EQ_OHLCV_ROW" for x in results)
 cache_written=False;cache_sha=None
 token=os.environ.get("HF_TOKEN","");cache_dir=os.environ.get("TEJHQ_ENCRYPTED_CACHE_DIR","")
 if raw_rows and token and cache_dir:
  cols=sorted({k for row in raw_rows for k in row})
  buf=io.StringIO();writer=csv.DictWriter(buf,fieldnames=cols);writer.writeheader();writer.writerows(raw_rows)
  encrypted=encrypt_cache(buf.getvalue().encode("utf-8"),token,b"bup01:nse-direct-special-sessions:v1")
  target=Path(cache_dir)/"direct_nse_special_sessions.csv.aesgcm";target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(encrypted)
  cache_written=True;cache_sha=hashlib.sha256(encrypted).hexdigest()
 now=datetime.now(timezone.utc).isoformat()
 report={"schema_version":2,"methodology_version":"bup01-c1-direct-nse-residuals-v2","updated_at_utc":now,"github_actions_run_id":a.run_id or None,"status":"PASS_ALL_SEVEN" if good==len(TARGETS) else "PARTIAL_DIRECT_ARCHIVE_COVERAGE","summary":{"residual_sessions":len(TARGETS),"valid_direct_nse_rows":good,"raw_prices_or_volume_published":False,"encrypted_supplemental_cache_written":cache_written,"encrypted_cache_sha256":cache_sha,"raw_feature_cache_integration":"PERSISTED_NOT_YET_MERGED"},"source":{"publisher":"National Stock Exchange of India","legacy_archive_pattern":"https://archives.nseindia.com/content/historical/EQUITIES/YYYY/MON/cmDDMONYYYYbhav.csv.zip","modern_archive_pattern":"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_YYYYMMDD_F_0000.csv.zip","independent_of_third_party_mirror":True},"results":results,"limitations":["Legacy CSV is checked by symbol/series/timestamp and ISIN when present.","Modern UDiFF CSV is checked by TckrSymb/SctySrs/TradDt and ISIN.","HTTP 404 is unavailable, not proof of no trade.","Raw rows are persisted only in AES-GCM encrypted Actions cache, not repository or artifacts.","Daily feature panel and corporate-action adjusted returns are separate gates."]}
 root=Path(a.root);out=root/"research/constituent_weekly/C1_DIRECT_NSE_SPECIAL_SESSION_AUDIT.json";md=root/"research/constituent_weekly/C1_DIRECT_NSE_SPECIAL_SESSION_AUDIT.md";out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 lines=["# C1 Direct NSE Residual-session Bhavcopy Audit","",f"Updated: {now}",f"Status: {report['status']}",f"Direct official NSE rows validated: {good}/{len(TARGETS)}.",f"Encrypted supplemental cache written: {cache_written}","", "| Date | Symbol | Session | Result | OHLC | Volume | Identity |","|---|---|---|---|---|---|---|"]
 for x in results:lines.append(f"| {x['date']} | {x['symbol']} | {x['session']} | {x['status']} | {'PASS' if x.get('ohlc_valid') else '—'} | {'PASS' if x.get('volume_valid') else '—'} | {x.get('identity_status','—')} |")
 lines += ["","## Method","", "Downloaded the exact official NSE cash-market archive for each residual date, selecting legacy CM ZIP/CSV before 8 July 2024 and UDiFF CM ZIP/CSV thereafter. Filtered exact point-in-time symbol, EQ series and trade date; validated unique row, OHLC ordering, nonnegative volume and ISIN. Raw rows are encrypted using the existing BUP01/HF_TOKEN-derived AES-GCM cache key; only metadata and archive hashes are published.","","## Limitations","",*["- "+x for x in report["limitations"]]]
 md.write_text("\n".join(lines)+"\n",encoding="utf-8")
 print(json.dumps(report["summary"],sort_keys=True))
if __name__=="__main__":main()
