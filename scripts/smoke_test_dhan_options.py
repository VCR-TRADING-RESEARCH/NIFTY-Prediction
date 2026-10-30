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
        ("security", "SECURITY_ID_OR_UNDERLYING"),
        ("expiry", "EXPIRY_PARAMETER"),
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
    summary=[]
    for opt in ("CALL","PUT"):
        payload={"exchangeSegment":"NSE_FNO","interval":"1","securityId":"13",
                 "instrument":"OPTIDX","expiryFlag":"WEEK","expiryCode":0,
                 "strike":"ATM","drvOptionType":opt,"requiredData":FIELDS,
                 "fromDate":start.isoformat(),"toDate":end.isoformat()}
        response=session.post(URL,headers=headers,json=payload,timeout=60)
        if not response.ok:
            try:
                body=response.json()
                keys=sorted(str(k) for k in body.keys()) if isinstance(body,dict) else [type(body).__name__]
                status=body.get("status") if isinstance(body,dict) else None
                code=body.get("errorCode") or body.get("error_code") if isinstance(body,dict) else None
                message=body.get("message") or body.get("remarks") if isinstance(body,dict) else ""
            except Exception:
                keys=["non_json_response"]; status=None; code=None; message=""
            print({"status":"FAIL","http_status":response.status_code,"keys":keys,
                   "api_status":str(status)[:32],"error_code":str(code)[:32],
                   "reason":classify(message)},file=sys.stderr)
            return 2
        body=response.json()
        data=body.get("data") or {}
        side=data.get("ce" if opt=="CALL" else "pe") or {}
        stamps=side.get("timestamp") or []
        summary.append({"option_type":opt,"rows":len(stamps),"fields":sorted(side.keys())})
    print({"status":"PASS" if sum(x["rows"] for x in summary)>0 else "NO_DATA",
           "window":[start.isoformat(),end.isoformat()],"responses":summary})
    if sum(x["rows"] for x in summary)==0:
        return 2
    return 0
if __name__=="__main__":
    raise SystemExit(main())
