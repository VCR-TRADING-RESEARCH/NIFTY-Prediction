#!/usr/bin/env python3
"""Small authenticated Dhan API smoke test; never prints market prices or credentials."""
from __future__ import annotations
import os, sys
from datetime import date, timedelta
import requests

URL="https://api.dhan.co/v2/charts/rollingoption"
FIELDS=["open","high","low","close","iv","volume","strike","oi","spot"]

def classify(message):
    m=str(message).lower()
    for key, label in [
        ("expiry date", "EXPIRY_DATE_INVALID"),
        ("expiry flag", "EXPIRY_FLAG_INVALID"),
        ("expiry code", "EXPIRY_CODE_INVALID"),
        ("weekly", "WEEKLY_EXPIRY_UNSUPPORTED"),
        ("security", "SECURITY_ID_OR_UNDERLYING"),
        ("date", "DATE_RANGE_OR_FORMAT"),
        ("strike", "STRIKE_PARAMETER"),
        ("instrument", "INSTRUMENT_PARAMETER"),
        ("required", "REQUIRED_DATA_PARAMETER"),
        ("interval", "INTERVAL_PARAMETER"),
        ("token", "TOKEN_OR_AUTH"),
        ("subscription", "DATA_API_SUBSCRIPTION"),
    ]:
        if key in m:
            return label
    return "UNCLASSIFIED_API_REJECTION"

def main():
    token=os.getenv("DHAN_JOB_ACCESS_TOKEN","").strip()
    client=os.getenv("DHAN_CLIENT_ID","").strip()
    if not token or not client:
        raise SystemExit("DHAN_SMOKE_FAIL: missing authenticated job context")
    end=date.today()
    start=end-timedelta(days=7)
    headers={"access-token":token,"client-id":client,"Content-Type":"application/json","Accept":"application/json"}
    session=requests.Session()
    results=[]
    successful=None
    for expiry_flag in ("WEEK","MONTH"):
        for expiry_code in (0,1,2):
            payload={"exchangeSegment":"NSE_FNO","interval":"1","securityId":"13",
                     "instrument":"OPTIDX","expiryFlag":expiry_flag,"expiryCode":expiry_code,
                     "strike":"ATM","drvOptionType":"CALL","requiredData":FIELDS,
                     "fromDate":start.isoformat(),"toDate":end.isoformat()}
            response=session.post(URL,headers=headers,json=payload,timeout=60)
            if not response.ok:
                try:
                    body=response.json()
                    code=body.get("errorCode") if isinstance(body,dict) else None
                    message=body.get("errorMessage") or body.get("message") or body.get("remarks") if isinstance(body,dict) else ""
                except Exception:
                    code=None; message=""
                results.append({"flag":expiry_flag,"code":expiry_code,"http":response.status_code,
                                "error_code":str(code)[:24],"reason":classify(message)})
                continue
            body=response.json()
            side=((body.get("data") or {}).get("ce") or {})
            rows=len(side.get("timestamp") or [])
            results.append({"flag":expiry_flag,"code":expiry_code,"http":200,"call_rows":rows})
            if rows and successful is None:
                successful=(expiry_flag,expiry_code)
    if successful:
        expiry_flag,expiry_code=successful
        payload={"exchangeSegment":"NSE_FNO","interval":"1","securityId":"13",
                 "instrument":"OPTIDX","expiryFlag":expiry_flag,"expiryCode":expiry_code,
                 "strike":"ATM","drvOptionType":"PUT","requiredData":FIELDS,
                 "fromDate":start.isoformat(),"toDate":end.isoformat()}
        response=session.post(URL,headers=headers,json=payload,timeout=60)
        put_rows=0
        if response.ok:
            put_rows=len((((response.json().get("data") or {}).get("pe") or {}).get("timestamp")) or [])
        print({"status":"PASS" if put_rows else "CALL_ONLY_OR_PUT_MISSING",
               "window":[start.isoformat(),end.isoformat()],
               "selected_expiry_flag":expiry_flag,"selected_expiry_code":expiry_code,
               "put_rows":put_rows,"parameter_trials":results})
        return 0 if put_rows else 2
    print({"status":"FAIL","parameter_trials":results},file=sys.stderr)
    return 2
if __name__=="__main__":
    raise SystemExit(main())
