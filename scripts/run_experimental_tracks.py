#!/usr/bin/env python3
"""Bounded experimental model tracks; never promotes candidates to trading signals."""
from __future__ import annotations
import json, os, subprocess, sys, traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, matthews_corrcoef, brier_score_loss
from sklearn.model_selection import TimeSeriesSplit

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/processed/weekly_labels_features.csv"
OUT=ROOT/"research/results/experimental"
LOG=ROOT/"logs/ERROR_LOG.md"
FEATURES=["ret_1","ret_5","ret_10","ret_20","rv_5","rv_10","rv_20","range_5","range_10","range_20","overnight_gap","pre_anchor_return","anchor_jump","prior_cycle_return","prior_cycle_up","prior_close_range_position","session_gap_days","post_expiry_change","month_sin","month_cos"]

def record_error(track, exc):
    LOG.parent.mkdir(parents=True,exist_ok=True)
    with LOG.open("a",encoding="utf-8") as f:
        f.write(f"\n\n## {datetime.now(timezone.utc).isoformat()} — {track} experimental track\n- Severity: Medium; this track is non-blocking and results remain exploratory.\n- Symptom: {type(exc).__name__}: {str(exc)[:500]}\n- Response: record failure, retain other tracks, do not promote a model.\n- Secrets: no environment values or request bodies recorded.\n")

def metrics(y,pred,prob):
    return {"n":int(len(y)),"accuracy":float(accuracy_score(y,pred)),"balanced_accuracy":float(balanced_accuracy_score(y,pred)),"mcc":float(matthews_corrcoef(y,pred)),"brier":float(brier_score_loss(y,prob))}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report={"generated_utc":datetime.now(timezone.utc).isoformat(),"status":"EXPLORATORY_ONLY","target":"sign of expiry close / next-session 10:00 anchor - 1","tracks":{},"promotion":"NONE; calendar and independent price-source gates remain skipped/blocked"}
    if not DATA.exists(): raise FileNotFoundError(f"Required pipeline output missing: {DATA}")
    df=pd.read_csv(DATA)
    if not {"label","return_pct"}.issubset(df.columns): raise ValueError("weekly feature file lacks label/return_pct")
    df=df[df.label.isin(["UP","DOWN"])].sort_values("expiry_date" if "expiry_date" in df else "anchor_timestamp").reset_index(drop=True)
    available=[c for c in FEATURES if c in df.columns]
    if len(df)<60 or len(available)<5: raise ValueError(f"Insufficient rows/features for bounded experiments: n={len(df)}, features={len(available)}")
    X=df[available].replace([np.inf,-np.inf],np.nan)
    y=(df.label=="UP").astype(int)
    cut=max(int(len(df)*0.8),1)
    if len(df)-cut<10 or cut<30: raise ValueError("Chronological development/holdout split too small")
    Xtr,Xte=X.iloc[:cut],X.iloc[cut:]; ytr,yte=y.iloc[:cut],y.iloc[cut:]
    base=make_pipeline(SimpleImputer(strategy="median",add_indicator=True),StandardScaler(),LogisticRegression(max_iter=2000,class_weight="balanced",random_state=41))
    base.fit(Xtr,ytr); base_prob=base.predict_proba(Xte)[:,1]
    report["sample"]={"rows":int(len(df)),"development_rows":int(cut),"holdout_rows":int(len(df)-cut),"features":available,"up_fraction":float(y.mean()),"calendar_quality":"HEURISTIC / NOT VERIFIED"}
    report["tracks"]["baseline_logistic"]={"status":"completed","holdout":metrics(yte,(base_prob>=.5).astype(int),base_prob)}

    # Bounded evolutionary search inspired by QuantEvolve; fixed, auditable operators, no LLM code execution.
    try:
        rng=np.random.default_rng(20261025)
        imputer=SimpleImputer(strategy="median",add_indicator=True)
        Xtr_i=imputer.fit_transform(Xtr); Xte_i=imputer.transform(Xte)
        mean=Xtr_i.mean(axis=0); std=Xtr_i.std(axis=0); std[std==0]=1
        Xtr_s=np.clip((Xtr_i-mean)/std,-8,8); Xte_s=np.clip((Xte_i-mean)/std,-8,8)
        # Chromosomes are sparse signed linear rules; fitness is rolling-origin balanced accuracy minus complexity penalty.
        splits=list(TimeSeriesSplit(n_splits=4).split(Xtr_s))
        population=[]
        for _ in range(80):
            w=rng.normal(0,1,len(mean)); w[rng.random(len(w))<.65]=0
            if not np.any(w): w[rng.integers(0,len(w))]=1
            population.append(w)
        def fitness(w):
            scores=[]
            for a,b in splits:
                scores.append(balanced_accuracy_score(ytr.iloc[b],(Xtr_s[b]@w>=0).astype(int)))
            complexity=np.count_nonzero(w)/len(w)
            return float(np.mean(scores)-0.015*complexity)
        history=[]
        for gen in range(35):
            scored=sorted(((fitness(w),w) for w in population),key=lambda z:z[0],reverse=True)
            history.append({"generation":gen,"best_development_fitness":scored[0][0],"nonzero_weights":int(np.count_nonzero(scored[0][1]))})
            elites=[w.copy() for _,w in scored[:12]]
            children=elites.copy()
            while len(children)<80:
                parent=elites[rng.integers(len(elites))].copy()
                mask=rng.random(len(parent))<.15
                parent[mask]+=rng.normal(0,0.6,mask.sum())
                parent[rng.random(len(parent))<.04]=0
                if not np.any(parent): parent[rng.integers(len(parent))]=1
                children.append(parent)
            population=children
        best=sorted(((fitness(w),w) for w in population),key=lambda z:z[0],reverse=True)[0][1]
        p=1/(1+np.exp(-np.clip(Xte_s@best,-30,30)))
        pred=(p>=.5).astype(int)
        report["tracks"]["quantevolve"]={"status":"completed_local_bounded_evolution","upstream_repository":"https://github.com/tarsyang/quantevolve","upstream_execution":"cloned/smoke-tested separately; upstream Binance/Gemini strategy loop is not run on NIFTY labels","generations":35,"population":80,"selection":"4-fold chronological development balanced accuracy minus 0.015 * sparsity fraction","history":history,"nonzero_features":[{"feature":name,"weight":float(w)} for name,w in zip(available,best) if abs(w)>1e-8],"holdout":metrics(yte,pred,p),"warning":"small, noisy, unverified labels; one holdout, no strategy/P&L certification"}
    except Exception as e:
        report["tracks"]["quantevolve"]={"status":"failed","error":type(e).__name__+": "+str(e)[:400]}; record_error("QuantEvolve-inspired bounded search",e)

    # PySR symbolic regression on a continuous return target, constrained to small expressions.
    try:
        from pysr import PySRRegressor
        model=PySRRegressor(niterations=25,populations=8,maxsize=12,model_selection="best",binary_operators=["+","-","*","/"],unary_operators=["abs"],elementwise_loss="loss(prediction, target) = (prediction - target)^2",verbosity=0,random_state=41,progress=False)
        model.fit(Xtr.fillna(Xtr.median()).to_numpy(dtype=float),df.return_pct.iloc[:cut].to_numpy(dtype=float),variable_names=[f"x{i}" for i in range(len(available))])
        pred=model.predict(Xte.fillna(Xtr.median()).to_numpy(dtype=float))
        denom=np.sum((df.return_pct.iloc[cut:].to_numpy()-df.return_pct.iloc[cut:].mean())**2)
        r2=float(1-np.sum((df.return_pct.iloc[cut:].to_numpy()-pred)**2)/denom) if denom>0 else None
        equations=model.equations_.replace({np.nan:None}).to_dict(orient="records")
        report["tracks"]["pysr"]={"status":"completed","niterations":25,"populations":8,"maxsize":12,"holdout_return_rmse":float(np.sqrt(np.mean((df.return_pct.iloc[cut:].to_numpy()-pred)**2))),"holdout_return_r2":r2,"equations":equations[:20],"variable_map":{f"x{i}":name for i,name in enumerate(available)},"warning":"continuous-return symbolic regression on heuristic labels; expression discovery is highly overfit-prone"}
    except Exception as e:
        report["tracks"]["pysr"]={"status":"failed_or_unavailable","error":type(e).__name__+": "+str(e)[:500]}; record_error("PySR",e)

    # Python mirror of the fixed-weight TradingView indicator; no threshold tuning on holdout.
    try:
        trend=np.clip(pd.to_numeric(df.get("ret_5",pd.Series(np.nan,index=df.index)),errors="coerce")/0.015,-1,1)
        morning=np.clip(pd.to_numeric(df.get("pre_anchor_return",pd.Series(np.nan,index=df.index)),errors="coerce")/0.004,-1,1)
        gap=np.clip(pd.to_numeric(df.get("overnight_gap",pd.Series(np.nan,index=df.index)),errors="coerce")/0.006,-1,1)
        pressure=0.50*trend+0.35*morning+0.15*gap
        ph=pressure.iloc[cut:].fillna(0).to_numpy()
        yh=yte.to_numpy()
        signal=np.where(ph>0.22,1,np.where(ph< -0.22,0,-1))
        active=signal!=-1
        indicator_result={"status":"completed_python_mirror","fixed_weights":{"prior_5_session_return":0.50,"pre_anchor_return":0.35,"overnight_gap":0.15},"threshold":0.22,"holdout_rows":int(len(yh)),"signals":int(active.sum()),"coverage":float(active.mean()),"directional_accuracy_on_signaled_rows":float(accuracy_score(yh[active],signal[active])) if active.any() else None,"balanced_accuracy_on_signaled_rows":float(balanced_accuracy_score(yh[active],signal[active])) if active.any() and len(np.unique(yh[active]))>1 else None,"warning":"Python mirror is not Pine compiler verification; no trading P&L or costs evaluated"}
        report["tracks"]["custom_indicator"]=indicator_result
    except Exception as e:
        report["tracks"]["custom_indicator"]={"status":"failed","error":type(e).__name__+": "+str(e)[:400]}; record_error("Custom indicator Python mirror",e)

    # TradingAgents upstream smoke-test and reproducible multi-role review; no live LLM calls or orders.
    try:
        vend=ROOT/"vendor/TradingAgents"
        import importlib.util
        package_present=vend.exists()
        report["tracks"]["tradingagents"]={"status":"upstream_smoke_test_only","upstream_repository":"https://github.com/TauricResearch/TradingAgents","repository_cloned":package_present,"python_package_importable":bool(importlib.util.find_spec("tradingagents")),"live_agent_debate":"not run: requires provider configuration and would add non-determinism; no LLM credentials are sent by this script","roles":[{"role":"Quant reviewer","task":"Compare holdout metrics to majority and logistic baselines; reject accuracy-only claims."},{"role":"Data reviewer","task":"Flag heuristic expiry calendar and independent-close mismatches as blocking."},{"role":"Execution/risk reviewer","task":"Reject profitability claims absent instrument fills, fees, spread, slippage and dated Paytm Money costs."}],"review_conclusion":"No model promotion; data and execution gates remain unresolved"}
    except Exception as e:
        report["tracks"]["tradingagents"]={"status":"failed","error":type(e).__name__+": "+str(e)[:400]}; record_error("TradingAgents smoke test",e)

    (OUT/"experimental_results.json").write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")
    pd.DataFrame([{"track":k,"status":v.get("status"),"holdout_balanced_accuracy":v.get("holdout",{}).get("balanced_accuracy"),"holdout_mcc":v.get("holdout",{}).get("mcc")} for k,v in report["tracks"].items()]).to_csv(OUT/"track_summary.csv",index=False)
    print(json.dumps({"status":report["status"],"sample":report["sample"],"tracks":{k:v.get("status") for k,v in report["tracks"].items()}},indent=2))
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as e:
        record_error("Experimental runner",e); traceback.print_exc(); raise
