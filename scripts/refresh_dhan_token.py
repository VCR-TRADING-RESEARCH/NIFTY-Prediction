#!/usr/bin/env python3
"""Create or renew an ephemeral Dhan access token for this Actions job."""
from __future__ import annotations
import os, sys
import requests
import pyotp

def find_access_token(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).replace("_", "").replace("-", "").lower() == "accesstoken":
                if isinstance(item, str) and len(item) >= 20:
                    return item
        for item in value.values():
            found=find_access_token(item)
            if found: return found
    elif isinstance(value, list):
        for item in value:
            found=find_access_token(item)
            if found: return found
    return None

def export_token(token, path):
    with open(path,"a",encoding="utf-8") as f:
        f.write("DHAN_JOB_ACCESS_TOKEN="+token.replace("\n","")+"\n")

def main():
    client=os.getenv("DHAN_CLIENT_ID","").strip()
    pin=os.getenv("DHAN_PIN","").strip()
    secret=os.getenv("DHAN_TOTP_SECRET","").strip()
    existing=os.getenv("DHAN_ACCESS_TOKEN","").strip()
    envfile=os.getenv("GITHUB_ENV","")
    if not client or not envfile:
        print("DHAN_AUTH_ERROR: Client ID or GITHUB_ENV missing.",file=sys.stderr); return 2

    if existing:
        try:
            r=requests.get("https://api.dhan.co/v2/RenewToken",
                           headers={"access-token":existing,"dhanClientId":client},timeout=30)
            if r.ok:
                token=find_access_token(r.json())
                if token:
                    export_token(token,envfile)
                    print("DHAN_AUTH_RENEW_OK: Existing active token renewed; token withheld.")
                    return 0
        except Exception:
            pass

    if not pin or not secret:
        print("DHAN_AUTH_ERROR: No renewable token and PIN/TOTP credentials are incomplete.",file=sys.stderr)
        return 2
    try:
        if secret.lower().startswith("otpauth://"):
            secret=pyotp.parse_uri(secret).secret
        secret="".join(secret.split()).replace("-","").upper()
        code=pyotp.TOTP(secret).now()
        r=requests.post("https://auth.dhan.co/app/generateAccessToken",
                        params={"dhanClientId":client,"pin":pin,"totp":code},timeout=30)
        if not r.ok:
            print("DHAN_AUTH_ERROR: Token service returned HTTP",r.status_code,file=sys.stderr); return 2
        body=r.json()
        token=find_access_token(body)
        if not token:
            keys=sorted(str(k) for k in body.keys()) if isinstance(body,dict) else [type(body).__name__]
            status=body.get("status") if isinstance(body,dict) else None
            print("DHAN_AUTH_ERROR: No access token in response; keys=",",".join(keys),
                  "status=",str(status)[:32],file=sys.stderr); return 2
        export_token(token,envfile)
        print("DHAN_AUTH_OK: Fresh short-lived token generated; token withheld.")
        return 0
    except Exception as exc:
        print("DHAN_AUTH_ERROR:",type(exc).__name__,"Sensitive response contents withheld.",file=sys.stderr); return 2

if __name__=="__main__":
    raise SystemExit(main())
