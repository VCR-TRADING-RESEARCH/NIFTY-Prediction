from __future__ import annotations
import gzip, hashlib, json, os, sys, time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, confusion_matrix, matthews_corrcoef, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from live_api.app import MASTER_URL, find_nifty50_security
from scripts.constituent_weekly import audit_c1_continuous_dhan_coverage as audit
from scripts.constituent_weekly.dhan_equity_preflight import acquire_access_token, apply_historical_security_aliases, resolve_ids

TRACK="BUP-01-C3X"; CACHE_SCHEMA=1; CACHE_FILE="panel.enc"; AAD=b"BUP01-C3X-PANEL-v1"
C1=ROOT/"research/constituent_weekly/C1_CONTINUOUS_COVERAGE.json"
MEM=ROOT/"data/constituent_weekly/nifty50_membership_intervals.csv"
EXP=ROOT/"data/reconciliation/expiry_verification.csv"
ACTIONS=ROOT/"data/constituent_weekly/security_corporate_action_events.csv"
OUT=ROOT/"research/constituent_weekly"
FEATURES=["ret_1","ret_5","ret_10","ret_20","rv_5","rv_10","rv_20","range_5","range_10","range_20","overnight_gap","pre_anchor_return","pre_anchor_range","volume_ratio_20"]
MIN_PRIOR=104; HOLDOUT=0.20; REFIT_BLOCK=4; REPS=2000; BLOCK=4; SEED=20261031

class ResearchBlocked(RuntimeError): pass

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def manifest():
    return {"membership":sha(MEM),"expiry_calendar":sha(EXP),"structural_actions":sha(ACTIONS),"c1_qa":sha(C1),"cache_schema":CACHE_SCHEMA}
def key_for(secret,client):
    return hashlib.sha256(f"BUP01-C3X|{secret}|{client}|{CACHE_SCHEMA}".encode()).digest()
def cache_read(path,key,source_manifest):
    if not path.exists(): return None
    raw=path.read_bytes()
    if len(raw)<29 or raw[:5]!=b"BUP1E": return None
    try:
        plain=AESGCM(key).decrypt(raw[5:17],raw[17:],AAD)
        obj=json.loads(gzip.decompress(plain).decode())
    except Exception: return None
    return obj if obj.get("input_manifest")==source_manifest else None
def cache_write(path,key,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    plain=gzip.compress(json.dumps(obj,separators=(",",":"),allow_nan=False).encode())
    nonce=os.urandom(12); encrypted=AESGCM(key).encrypt(nonce,plain,AAD)
    tmp=path.with_suffix(".tmp"); tmp.write_bytes(b"BUP1E"+nonce+encrypted); tmp.replace(path)

def to_frame(body,require_volume):
    arr,err=audit._payload_arrays(body)
    if arr is None or err: raise ResearchBlocked(f"Bad Dhan bar response: {err}")
    f=pd.DataFrame({"timestamp":pd.to_datetime(arr["timestamp"],unit="s",utc=True,errors="coerce"),
                    "open":pd.to_numeric(arr["open"],errors="coerce"),"high":pd.to_numeric(arr["high"],errors="coerce"),
                    "low":pd.to_numeric(arr["low"],errors="coerce"),"close":pd.to_numeric(arr["close"],errors="coerce")})
    if isinstance(arr.get("volume"),list): f["volume"]=pd.to_numeric(arr["volume"],errors="coerce")
    elif require_volume: raise ResearchBlocked("Stock response has no volume array")
    else: f["volume"]=0.0
    f=f.dropna(subset=["timestamp","open","high","low","close"])
    f["timestamp"]=f["timestamp"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    f=f.sort_values("timestamp").reset_index(drop=True)
    f["day"]=f["timestamp"].dt.strftime("%Y-%m-%d"); f["clock"]=f["timestamp"].dt.strftime("%H:%M")
    return f

def valid_rows(f):
    x=f[["open","high","low","close"]].to_numpy(float); lo=f["low"].to_numpy(float); hi=f["high"].to_numpy(float)
    op=f["open"].to_numpy(float); cl=f["close"].to_numpy(float); vol=f["volume"].to_numpy(float)
    ok=np.isfinite(x).all(axis=1)&(x>0).all(axis=1)&(lo<=np.minimum(op,cl))&(hi>=np.maximum(op,cl))&(hi>=lo)&np.isfinite(vol)&(vol>=0)
    return pd.Series(ok,index=f.index)

def target_prices(f,stamp):
    d=f[f.day.eq(stamp)]
    a=d[d.clock.between("10:00","10:03")]; e=d[d.clock.between("15:00","15:14")]
    if a.empty or e.empty: raise ValueError("Registered anchor or expiry-proxy bar missing")
    if a.timestamp.duplicated().any() or e.timestamp.duplicated().any(): raise ValueError("Duplicate target timestamp")
    if not valid_rows(a).all() or not valid_rows(e).all(): raise ValueError("Bad target OHLCV")
    return float(a.iloc[0].open),float(e.iloc[-1].close)

def daily_history(f):
    r=f[f.clock.between("09:15","15:14")].copy(); r=r[valid_rows(r)]
    out=[]
    for stamp,d in r.groupby("day",sort=True):
        if d.timestamp.duplicated().any(): continue
        op=d[d.clock.between("09:15","09:20")]; cl=d[d.clock.between("15:00","15:14")]
        if op.empty or cl.empty: continue
        out.append({"day":stamp,"open":float(op.iloc[0].open),"high":float(d.high.max()),"low":float(d.low.min()),
                    "close":float(cl.iloc[-1].close),"volume":float(d.volume.sum())})
    if not out: return pd.DataFrame()
    h=pd.DataFrame(out).sort_values("day").reset_index(drop=True)
    h["ret"]=h.close.pct_change(); h["range"]=(h.high-h.low)/h.close.shift(1)
    return h

def causal_features_from_history(f,h,stamp):
    p=h[h.day.lt(stamp)].tail(21); d=f[f.day.eq(stamp)]
    a=d[d.clock.between("10:00","10:03")]; before=d[d.clock.ge("09:15")&d.clock.lt("10:00")]
    if len(p)<21 or a.empty or before.empty: raise ValueError("Insufficient causal feature history")
    if a.timestamp.duplicated().any() or before.timestamp.duplicated().any(): raise ValueError("Duplicate pre-anchor timestamp")
    ret=p.ret.dropna(); rng=p["range"].dropna()
    if len(ret)<20 or len(rng)<20: raise ValueError("Insufficient prior returns/ranges")
    op=float(before.iloc[0].open); anchor=float(a.iloc[0].open); pc=float(p.iloc[-1].close)
    vm=float(p.volume.tail(20).mean())
    vals={"ret_1":p.close.iloc[-1]/p.close.iloc[-2]-1,"ret_5":p.close.iloc[-1]/p.close.iloc[-6]-1,
          "ret_10":p.close.iloc[-1]/p.close.iloc[-11]-1,"ret_20":p.close.iloc[-1]/p.close.iloc[-21]-1,
          "rv_5":ret.tail(5).std(ddof=1),"rv_10":ret.tail(10).std(ddof=1),"rv_20":ret.tail(20).std(ddof=1),
          "range_5":rng.tail(5).mean(),"range_10":rng.tail(10).mean(),"range_20":rng.tail(20).mean(),
          "overnight_gap":op/pc-1,"pre_anchor_return":anchor/op-1,
          "pre_anchor_range":(float(before.high.max())-float(before.low.min()))/op,
          "volume_ratio_20":float(p.volume.iloc[-1]/vm) if vm>0 else 1.0}
    if not np.isfinite(np.asarray(list(vals.values()),float)).all(): raise ValueError("Non-finite feature")
    return {k:float(v) for k,v in vals.items()}


def causal_features(f,stamp):
    return causal_features_from_history(f,daily_history(f),stamp)

def action_events():
    f=pd.read_csv(ACTIONS,keep_default_na=False); events=[]
    for x in f.to_dict("records"):
        ds=str(x.get("event_date",""))[:10]
        if len(ds)!=10: continue
        events.append((date.fromisoformat(ds),{s.strip().upper() for s in str(x.get("affected_symbols","")).split(";") if s.strip()}))
    return events
def action_excluded(symbol,anchor,expiry,events):
    lo=date.fromisoformat(anchor)-timedelta(days=40); hi=date.fromisoformat(expiry)
    return any(symbol.upper() in syms and lo<=d<=hi for d,syms in events)

def request_bars(sec,seg,inst,token,client,start,end,volume):
    body,attempts=audit.request_intraday_window(str(sec),seg,inst,token,client,start,end)
    return to_frame(body,volume),attempts

def build_panel(c1,token,client,source_manifest):
    if c1.get("target_coverage_status")!="PASS": raise ResearchBlocked("C1 target-coverage sub-gate is not PASS")
    cycles=[dict(x) for x in c1.get("cycle_results",[]) if x.get("cycle_accepted_for_coverage") and x.get("index_target_ok")]
    cycles.sort(key=lambda x:(x["anchor_date"],x["expiry_date"]))
    if len(cycles)<124: raise ResearchBlocked("Fewer than 124 validated target cycles")
    symcycles={}
    for i,c in enumerate(cycles):
        c["source_idx"]=i
        for s in c.get("valid_members",[]): symcycles.setdefault(str(s),[]).append(c)
    start=min(c["anchor_date"] for c in cycles); end=max(c["expiry_date"] for c in cycles)
    chunks=audit.make_chunks(start,end,90); cmap={}
    for ch in chunks:
        for d in pd.date_range(ch["from"],ch["to"],freq="D").strftime("%Y-%m-%d"): cmap[d]=ch
    master_resp=requests.get(MASTER_URL,timeout=60); master_resp.raise_for_status()
    master=pd.read_csv(pd.io.common.BytesIO(master_resp.content),low_memory=False)
    idx_id=find_nifty50_security(master)
    if not idx_id: raise ResearchBlocked("NIFTY 50 index security ID unresolved")
    symbols=sorted(symcycles); resolved=resolve_ids(master,symbols)
    aliases=resolve_ids(master,["TMPV"]); resolved=apply_historical_security_aliases(symbols,resolved,aliases)
    missing=sorted(set(symbols)-set(resolved))
    if missing: raise ResearchBlocked(f"Accepted-cycle security ID unresolved for {len(missing)} symbols")
    events=action_events(); stock_rows=[]; requests_made=0; excluded=0
    for sym in symbols:
        dates={d for c in symcycles[sym] for d in (c["anchor_date"],c["expiry_date"])}
        starts={cmap[d]["from"] for d in dates}
        # Include the preceding 90-day chunk so the first eligible anchor in a chunk has 20 prior sessions.
        ordered=[x["from"] for x in chunks]
        for c in symcycles[sym]:
            if c["anchor_date"] in cmap:
                j=ordered.index(cmap[c["anchor_date"]]["from"])
                if j>0: starts.add(ordered[j-1])
        frames=[]
        for cs in sorted(starts):
            ch=next(x for x in chunks if x["from"]==cs)
            f,n=request_bars(resolved[sym],"NSE_EQ","EQUITY",token,client,ch["from"],ch["to"],True)
            frames.append(f); requests_made+=n; time.sleep(0.5)
        combined=pd.concat(frames,ignore_index=True).sort_values("timestamp") if frames else pd.DataFrame()
        # Build each constituent's validated daily history once, then reuse it across weekly anchors.
        # The history is still sliced strictly before each anchor date inside the feature function.
        history=daily_history(combined)
        for c in symcycles[sym]:
            a,e=c["anchor_date"],c["expiry_date"]
            if action_excluded(sym,a,e,events): excluded+=1; continue
            try:
                ap,_=target_prices(combined,a); _,ep=target_prices(combined,e)
                feat=causal_features_from_history(combined,history,a); r=ep/ap-1
                if not np.isfinite(r) or r==0: continue
                stock_rows.append({"source_idx":c["source_idx"],"anchor_date":a,"expiry_date":e,
                                   "symbol":sym,"target_return":float(r),"target":int(r>0),**feat})
            except (ValueError,KeyError,IndexError,ZeroDivisionError): continue
        del combined,frames,history
    # The observed NIFTY 50 series supplies the index target. It is never a stock-model feature.
    index_targets={}
    index_dates=sorted({d for c in cycles for d in (c["anchor_date"],c["expiry_date"])})
    for ch in chunks:
        ds=[d for d in index_dates if ch["from"]<=d<=ch["to"]]
        if not ds: continue
        frame,n=request_bars(idx_id,"IDX_I","INDEX",token,client,ch["from"],ch["to"],False)
        requests_made+=n; time.sleep(0.5)
        for d in ds:
            try: index_targets[d]=target_prices(frame,d)
            except (ValueError,KeyError,IndexError): pass
    sf=pd.DataFrame(stock_rows)
    if sf.empty: raise ResearchBlocked("No constituent rows survived feature and action filters")
    cycle_rows=[]
    for c in cycles:
        i=c["source_idx"]; rows=sf[sf.source_idx.eq(i)]
        n=int(rows.symbol.nunique()); denom=int(c.get("member_count",0)); fraction=n/denom if denom else 0
        if n<47 or fraction<0.94: continue
        try:
            a=index_targets[c["anchor_date"]][0]; e=index_targets[c["expiry_date"]][1]
            ret=e/a-1
        except (KeyError,TypeError,ZeroDivisionError): continue
        if not np.isfinite(ret) or ret==0: continue
        cycle_rows.append({"source_idx":i,"anchor_date":c["anchor_date"],"expiry_date":c["expiry_date"],
                           "member_count":denom,"valid_member_count":n,"member_coverage":fraction,
                           "index_return":float(ret),"index_target":int(ret>0)})
    cycle_rows.sort(key=lambda x:x["source_idx"])
    if len(cycle_rows)<124: raise ResearchBlocked(f"Only {len(cycle_rows)} cycles survive action/feature/47-94 filters")
    mapping={r["source_idx"]:i for i,r in enumerate(cycle_rows)}
    stock_rows=[{**r,"cycle_index":mapping[r["source_idx"]]} for r in stock_rows if r["source_idx"] in mapping]
    for r in cycle_rows:r["cycle_index"]=mapping[r["source_idx"]]
    return {"input_manifest":source_manifest,"cycle_rows":cycle_rows,"stock_rows":stock_rows,
            "requests_made":requests_made,"source_coverage_cycles":len(cycles),
            "structural_action_events_considered":len(events),"structural_action_excluded_stock_rows":excluded}

def metrics(y,s):
    y=np.asarray(y,int); s=np.asarray(s,float); keep=np.isfinite(s); y=y[keep]; s=s[keep]
    if not len(y): return {"n":0}
    h=(s>=0.5).astype(int)
    return {"n":int(len(y)),"up_fraction":float(y.mean()),"accuracy":float(accuracy_score(y,h)),
            "balanced_accuracy":float(balanced_accuracy_score(y,h)),
            "mcc":float(matthews_corrcoef(y,h)) if len(np.unique(y))>1 else None,
            "brier_un_calibrated_score":float(brier_score_loss(y,s.clip(0,1))),
            "roc_auc":float(roc_auc_score(y,s)) if len(np.unique(y))>1 else None,
            "confusion_tn_fp_fn_tp":confusion_matrix(y,h,labels=[0,1]).ravel().astype(int).tolist()}

def bootstrap_diff(y,a,b):
    y=np.asarray(y,int); a=np.asarray(a,int); b=np.asarray(b,int); n=len(y)
    if n<BLOCK:return {"replicates":0,"ci95":None}
    rng=np.random.default_rng(SEED); starts=np.arange(0,n-BLOCK+1); values=[]
    for _ in range(REPS):
        ix=[]
        while len(ix)<n:
            s=int(rng.choice(starts)); ix.extend(range(s,min(s+BLOCK,n)))
        ix=np.asarray(ix[:n]); values.append(float(np.mean(a[ix]==y[ix])-np.mean(b[ix]==y[ix])))
    return {"replicates":REPS,"block_length_cycles":BLOCK,"mean_difference":float(np.mean(a==y)-np.mean(b==y)),
            "ci95":[float(np.quantile(values,.025)),float(np.quantile(values,.975))],"seed":SEED}

def fit_stock_oof(panel):
    stocks=pd.DataFrame(panel["stock_rows"]); cycles=pd.DataFrame(panel["cycle_rows"])
    hold=int(np.floor(len(cycles)*(1-HOLDOUT)))
    if hold<=MIN_PRIOR: raise ResearchBlocked("Holdout split does not leave 104 prior eligible cycles")
    preds=[]
    for start in range(MIN_PRIOR,len(cycles),REFIT_BLOCK):
        stop=min(start+REFIT_BLOCK,len(cycles))
        tr=stocks[stocks.cycle_index<start]; te=stocks[stocks.cycle_index.between(start,stop-1)]
        if tr.empty or te.empty or tr.target.nunique()<2: continue
        xt,yt=tr[FEATURES],tr.target.astype(int); xv=te[FEATURES]
        et=ExtraTreesClassifier(n_estimators=120,max_depth=10,min_samples_leaf=30,max_features=.8,
                                class_weight="balanced",random_state=SEED+start,n_jobs=-1).fit(xt,yt)
        ep=et.predict_proba(xv)[:,list(et.classes_).index(1)]
        lr=Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler()),
                     ("model",LogisticRegression(C=.10,max_iter=1200,class_weight="balanced"))]).fit(xt,yt)
        lp=lr.predict_proba(xv)[:,list(lr.classes_).index(1)]
        reg=ExtraTreesRegressor(n_estimators=100,max_depth=10,min_samples_leaf=30,max_features=.8,
                                random_state=SEED+start,n_jobs=-1).fit(xt,tr.target_return.astype(float))
        rp=reg.predict(xv)
        for j,(_,r) in enumerate(te.iterrows()):
            preds.append({"cycle_index":int(r.cycle_index),"anchor_date":r.anchor_date,"expiry_date":r.expiry_date,
                          "symbol":r.symbol,"actual":int(r.target),"et_score":float(ep[j]),"lr_score":float(lp[j]),
                          "et_return":float(rp[j]),"momentum_score":float(r.ret_5)})
    if not preds: raise ResearchBlocked("No strictly out-of-fold stock forecasts created")
    return pd.DataFrame(preds),cycles,hold

def aggregate_signals(pred,cycles):
    g=pred.groupby("cycle_index").agg(
        et_mean_score=("et_score","mean"),et_up_fraction=("et_score",lambda x:float((x>=.5).mean())),
        et_dispersion=("et_score","std"),lr_mean_score=("lr_score","mean"),
        mean_pred_return=("et_return","mean"),pred_return_dispersion=("et_return","std"),
        momentum_up_fraction=("momentum_score",lambda x:float((x>0).mean())),
        forecast_member_count=("symbol","nunique")).reset_index()
    s=cycles.merge(g,on="cycle_index",how="inner",validate="one_to_one").sort_values("cycle_index").reset_index(drop=True)
    s["forecast_coverage"]=s.forecast_member_count/s.member_count
    s["lagged_index_direction"]=s.index_target.shift(1)
    return s

def fit_meta_oof(s):
    feats=["et_mean_score","et_up_fraction","et_dispersion","lr_mean_score","mean_pred_return",
           "pred_return_dispersion","momentum_up_fraction","forecast_coverage"]
    rows=[]
    for _,r in s.iterrows():
        hist=s[s.cycle_index<r.cycle_index]
        if len(hist)<30 or hist.index_target.nunique()<2:continue
        m=Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler()),
                    ("model",LogisticRegression(C=.15,max_iter=1000,class_weight="balanced"))]).fit(hist[feats],hist.index_target.astype(int))
        score=float(m.predict_proba(r[feats].to_frame().T)[0,list(m.classes_).index(1)])
        lag=r.lagged_index_direction
        rows.append({"cycle_index":int(r.cycle_index),"anchor_date":r.anchor_date,"expiry_date":r.expiry_date,
                     "actual":int(r.index_target),"meta_score":score,"breadth_score":float(r.et_up_fraction),
                     "breadth_prediction":int(r.et_up_fraction>=.5),
                     "lag_prediction":int(lag) if pd.notna(lag) else None,
                     "mean_predicted_return":float(r.mean_pred_return),"forecast_coverage":float(r.forecast_coverage)})
    if not rows:raise ResearchBlocked("Insufficient OOF constituent cycle summaries for NIFTY meta-model")
    return pd.DataFrame(rows)

def main():
    t0=time.monotonic(); manifest_now=manifest()
    cdir=Path(os.getenv("BUP01_DHAN_CACHE_DIR","/tmp/bup01-dhan-exploratory")); cpath=cdir/CACHE_FILE
    secret=os.getenv("BUP01_CACHE_SECRET") or os.getenv("DHAN_TOTP_SECRET") or os.getenv("DHAN_ACCESS_TOKEN","")
    client=os.getenv("DHAN_CLIENT_ID","").strip()
    if not secret:raise ResearchBlocked("Missing cache encryption key material")
    key=key_for(secret,client); panel=cache_read(cpath,key,manifest_now); cache_hit=panel is not None
    if not cache_hit:
        token,client,auth_method,refresh,_=acquire_access_token()
        c1=json.loads(C1.read_text())
        panel=build_panel(c1,token,client,manifest_now)
        panel["auth_method"]=auth_method;panel["token_refresh_status"]=refresh
        cache_write(cpath,key,panel)
    pred,cycles,hold=fit_stock_oof(panel)
    test=pred[pred.cycle_index>=hold]
    if test.empty:raise ResearchBlocked("No stock holdout forecasts")
    stock_metrics={
        "ExtraTreesClassifier":metrics(test.actual,test.et_score),
        "LogisticRegression":metrics(test.actual,test.lr_score),
        "five_session_momentum_sign":metrics(test.actual,(test.momentum_score>0).astype(float))}
    summary=aggregate_signals(pred,cycles); meta=fit_meta_oof(summary)
    hi=meta[meta.cycle_index>=hold].copy()
    if len(hi)<20:raise ResearchBlocked(f"Only {len(hi)} NIFTY holdout cycles; need 20")
    mmetrics=metrics(hi.actual,hi.meta_score); bmetrics=metrics(hi.actual,hi.breadth_score)
    valid=hi.lag_prediction.notna()
    lmetrics=metrics(hi.loc[valid,"actual"],hi.loc[valid,"lag_prediction"].astype(float))
    boot=bootstrap_diff(hi.loc[valid,"actual"],(hi.loc[valid,"meta_score"]>=.5).astype(int),hi.loc[valid,"lag_prediction"].astype(int))
    hi["meta_prediction"]=(hi.meta_score>=.5).astype(int);hi["meta_correct"]=(hi.meta_prediction==hi.actual).astype(int)
    hold_date=cycles.loc[cycles.cycle_index.eq(hold),"anchor_date"].iloc[0]
    result={"track":TRACK,"status":"EXPLORATORY_COMPLETE_NOT_CONFIRMATORY","created_at_utc":datetime.now(timezone.utc).isoformat(),
            "plan_version":"1.4","cache_hit":cache_hit,"input_manifest":manifest_now,
            "data":{"c1_target_coverage_status":"PASS","c1_coverage_cycles":int(panel["source_coverage_cycles"]),
                    "eligible_model_cycles":int(len(cycles)),"stock_cycle_rows":int(len(panel["stock_rows"])),
                    "unique_member_symbols":int(pd.DataFrame(panel["stock_rows"]).symbol.nunique()),
                    "structural_action_events_considered":int(panel["structural_action_events_considered"]),
                    "structural_action_excluded_stock_rows":int(panel["structural_action_excluded_stock_rows"]),
                    "dhan_requests_this_run":int(panel.get("requests_made",0)),"holdout_start_cycle_index":int(hold),
                    "holdout_start_anchor_date":str(hold_date),"holdout_cycles":int(len(cycles)-hold),
                    "stock_holdout_rows":int(len(test)),"nifty_meta_holdout_cycles":int(len(hi)),
                    "minimum_prior_cycles":MIN_PRIOR,"model_refit_block_cycles":REFIT_BLOCK,
                    "raw_bars_published":False,"plaintext_stock_panel_published":False},
            "stock_holdout_metrics":stock_metrics,
            "nifty_holdout_metrics":{"oof_constituent_signal_logistic_meta":mmetrics,
                "constituent_breadth_baseline":bmetrics,"previous_eligible_cycle_direction":lmetrics,
                "meta_vs_lag_accuracy_block_bootstrap":boot},
            "limitations":["Exploratory only; C1 corporate-action review and C2 confirmatory panel gate remain incomplete.",
              "Only structural events in the checked-in action ledger were excluded; unresolved 711-event catalogue may still contaminate other windows.",
              "Model scores are uncalibrated; Brier score is a diagnostic only.",
              "NIFTY meta-model inputs are strictly OOF constituent summaries; cycle rows were kept together.",
              "This first run is price-only; no options, FII/DII, global markets, news or volatility derivatives.",
              "No trading P&L, fees, slippage, fills or profitability claims."],
            "runtime_seconds":round(time.monotonic()-t0,2)}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"EXPLORATORY_RESULTS.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    hi[["anchor_date","expiry_date","actual","meta_score","meta_prediction","breadth_prediction",
        "breadth_score","mean_predicted_return","forecast_coverage","meta_correct"]].to_csv(OUT/"EXPLORATORY_NIFTY_HOLDOUT.csv",index=False)
    lines=["# BUP-01 C3-X Exploratory Prediction Results","",
      "**Status:** EXPLORATORY COMPLETE — NOT CONFIRMATORY  ",
      f"**Generated:** {result['created_at_utc']}  ","**Plan:** v1.4","",
      "## Sample and safeguards","",
      f"- C1 target-coverage cycles: {result['data']['c1_coverage_cycles']}",
      f"- Cycles after features, available structural-event exclusions and registered 47/94% coverage: {len(cycles)}",
      f"- Stock-cycle rows: {len(panel['stock_rows'])}; member symbols: {result['data']['unique_member_symbols']}",
      f"- First holdout anchor: {hold_date}; holdout cycles: {result['data']['holdout_cycles']}",
      f"- Stock models use 104 prior eligible cycles and refit every {REFIT_BLOCK} cycles.",
      f"- Dhan requests this run: {result['data']['dhan_requests_this_run']}; encrypted cache hit: {cache_hit}.",
      "- Raw bars and plaintext constituent panel were not published.","",
      "## Stock models — chronological holdout","","| Model | Rows | Accuracy | Balanced accuracy | MCC | ROC-AUC | Brier (uncalibrated) |",
      "|---|---:|---:|---:|---:|---:|---:|"]
    for name,m in stock_metrics.items():
        lines.append(f"| {name} | {m.get('n',0)} | {m.get('accuracy',float('nan')):.4f} | {m.get('balanced_accuracy',float('nan')):.4f} | {m.get('mcc') if m.get('mcc') is not None else float('nan'):.4f} | {m.get('roc_auc') if m.get('roc_auc') is not None else float('nan'):.4f} | {m.get('brier_un_calibrated_score',float('nan')):.4f} |")
    lines += ["","## NIFTY direction from OOF constituent signals — chronological holdout","","| Model | Cycles | Accuracy | Balanced accuracy | MCC | ROC-AUC |","|---|---:|---:|---:|---:|---:|"]
    for name,k in [("OOF constituent-signal logistic meta-model","oof_constituent_signal_logistic_meta"),("Constituent breadth baseline","constituent_breadth_baseline"),("Previous eligible-cycle direction","previous_eligible_cycle_direction")]:
        m={"oof_constituent_signal_logistic_meta":mmetrics,"constituent_breadth_baseline":bmetrics,"previous_eligible_cycle_direction":lmetrics}[k]
        lines.append(f"| {name} | {m.get('n',0)} | {m.get('accuracy',float('nan')):.4f} | {m.get('balanced_accuracy',float('nan')):.4f} | {m.get('mcc') if m.get('mcc') is not None else float('nan'):.4f} | {m.get('roc_auc') if m.get('roc_auc') is not None else float('nan'):.4f} |")
    lines += ["","## Paired uncertainty","","- Meta minus lag-direction accuracy: "+str(boot.get("mean_difference")),
      "- Four-cycle moving-block bootstrap 95% interval: "+str(boot.get("ci95")),
      f"- Replicates: {boot.get('replicates')}; seed: {SEED}.","",
      "## Interpretation and limitations","",
      "These findings are exploratory only. They do not pass C1 corporate-action review, C2 confirmatory panel validation or C5 trading execution. The broad candidate event catalogue is not fully reconciled. Model scores are uncalibrated. Do not treat the forecasts as live trading signals or a profitability claim.","",
      "Machine-readable metrics: EXPLORATORY_RESULTS.json. Cycle-level NIFTY holdout predictions: EXPLORATORY_NIFTY_HOLDOUT.csv."]
    (OUT/"EXPLORATORY_REPORT.md").write_text("\n".join(lines)+"\n")
    (OUT/"EXPLORATORY_STATUS.md").write_text(
      "# C3-X Exploratory Prediction Status\n\n- Status: EXPLORATORY COMPLETE — NOT CONFIRMATORY\n"
      f"- Plan version: 1.4\n- Eligible cycles: {len(cycles)}\n- Holdout NIFTY cycles: {len(hi)}\n- Holdout anchor start: {hold_date}\n"
      "- C1: PARTIAL; corporate-action review remains open.\n- C2 confirmatory: LOCKED.\n"
      "- Trading: NOT VALIDATED; no execution/P&L test performed.\n- Results: [EXPLORATORY_REPORT.md](EXPLORATORY_REPORT.md)\n")
    print("C3X_COMPLETE",len(cycles),"cycles; holdout",len(hi))
    print("C3X_NIFTY_META",json.dumps(mmetrics,sort_keys=True))
    print("C3X_STOCK_ET",json.dumps(stock_metrics["ExtraTreesClassifier"],sort_keys=True))
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as exc:
        OUT.mkdir(parents=True,exist_ok=True)
        obj={"track":TRACK,"status":"BLOCKED_OR_FAILED","created_at_utc":datetime.now(timezone.utc).isoformat(),
             "error_type":type(exc).__name__,"error_message":str(exc)[:400]}
        (OUT/"EXPLORATORY_RESULTS.json").write_text(json.dumps(obj,indent=2)+"\n")
        (OUT/"EXPLORATORY_STATUS.md").write_text("# C3-X Exploratory Prediction Status\n\n- Status: BLOCKED_OR_FAILED; no prediction result is claimed.\n"
            f"- Error type: {type(exc).__name__}\n- Error: {str(exc)[:400]}\n")
        print("C3X_BLOCKED",type(exc).__name__,str(exc)[:300])
        raise
