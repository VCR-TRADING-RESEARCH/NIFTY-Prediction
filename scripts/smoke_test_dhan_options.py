#!/usr/bin/env python3
"""Authenticated Dhan rolling-options smoke test; never prints prices or credentials."""
from __future__ import annotations
import os,sys
from datetime import date,timedelta
import requests

URL="https://api.dhan.co/v2/charts/rollingoption"
BASE=["open","high","low","close","volume"]
TEST_SETS=[
    ("base",BASE),
    ("iv",BASE+["iv"]),
    ("oi",BASE+["oi"]),
    ("strike",BASE+["strike"]),
    ("spot",BASE+["spot"]),
    ("all",BASE+["iv","oi","strike","spot"]),
]
def classify(message):
    m=str(message).lower()
    for key,label in [("expiry","EXPIRY_PARAMETER"),("required","REQUIRED_DATA_PARAMETER"),
        ("security","SECURITY_ID_OR_UNDERLYING"),("strike","STRIKE_PARAMETER"),
        ("instrument","INSTRUMENT_PARAMETER"),("date","DATE_RANGE_OR_FORMAT"),
        ("interval","INTERVAL_PARAMETER"),("token","TOKEN_OR_AUTH")]:
        if key in m:return label
    return "UNCLASSIFIED_API_REJECTION"

def main():
    token=os.getenv("DHAN_JOB_ACCESS_TOKEN","").strip()
    client=os.getenv("DHAN_CLIENT_ID","").strip()
    if not token or not client:
        raise SystemExit("DHAN_SMOKE_FAIL: missing authenticated job context")
    end=date.today(); start=end-timedelta(days=7)
    headers={"access-token":token,"client-id":client,"Content-Type":"application/json","Accept":"application/json"}
    session=requests.Session(); results=[]; all_ok=False
    for label,fields in TEST_SETS:
        payload={"exchangeSegment":"NSE_FNO","interval":"1","securityId":"13",
            "instrument":"OPTIDX","expiryFlag":"WEEK","expiryCode":0,"strike":"ATM",
            "drvOptionType":"CALL","requiredData":fields,
            "fromDate":start.isoformat(),"toDate":end.isoformat()}
        r=session.post(URL,headers=headers,json=payload,timeout=60)
        if not r.ok:
            try:
                b=r.json(); code=b.get("errorCode"); msg=b.get("errorMessage") or b.get("message") or ""
            except Exception: code=None; msg=""
            results.append({"test":label,"http":r.status_code,"error_code":str(code)[:24],"reason":classify(msg)})
            if r.status_code==401:
                break
            continue
        block=((r.json().get("data") or {}).get("ce") or {})
        rows=len(block.get("timestamp") or [])
        results.append({"test":label,"http":200,"rows":rows,"fields":sorted(block.keys())})
        if label=="all" and rows: all_ok=True
    print({"status":"PASS" if all_ok else "FAIL","window":[start.isoformat(),end.isoformat()],
           "all_required_fields_available":all_ok,"trials":results})
    return 0 if all_ok else 2

if __name__=="__main__":
    raise SystemExit(main())
