#!/usr/bin/env python3
"""Bounded expanding-window benchmark across diverse NIFTY direction model families."""
from __future__ import annotations
import json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss, matthews_corrcoef, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"data/processed/phase10_dhan_weekly_labels_features.csv"
OUT=ROOT/"research/results/phase11"
FEATURES=["ret_1","ret_5","ret_10","ret_20","rv_5","range_5","rv_10","range_10","rv_20","range_20","overnight_gap","pre_anchor_return","anchor_jump","prior_cycle_return","prior_cycle_up","prior_close_range_position","session_gap_days","post_expiry_change","month_sin","month_cos","momentum_spread_5_20","rv_ratio_5_20","trend_efficiency_20","downside_semivol_20","upside_semivol_20","semivol_asymmetry_20"]
MIN_HISTORY=104
SEED=20261026
def candidates():
    return {
      "logistic": Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler()),("model",LogisticRegression(C=0.1,max_iter=2000,class_weight="balanced",random_state=SEED))]),
      "extra_trees": Pipeline([("impute",SimpleImputer(strategy="median")),("model",ExtraTreesClassifier(n_estimators=300,min_samples_leaf=5,max_features="sqrt",class_weight="balanced",random_state=SEED,n_jobs=1))]),
      "random_forest": Pipeline([("impute",SimpleImputer(strategy="median")),("model",RandomForestClassifier(n_estimators=300,min_samples_leaf=5,max_features="sqrt",class_weight="balanced",random_state=SEED,n_jobs=1))]),
      "gradient_boosting": Pipeline([("impute",SimpleImputer(strategy="median")),("model",GradientBoostingClassifier(n_estimators=75,learning_rate=0.03,max_depth=1,min_samples_leaf=8,random_state=SEED))]),
      "hist_gradient_boosting": Pipeline([("impute",SimpleImputer(strategy="median")),("model",HistGradientBoostingClassifier(max_iter=75,learning_rate=0.03,max_leaf_nodes=7,l2_regularization=1.0,random_state=SEED))]),
      "rbf_svc": Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler()),("model",SVC(C=0.5,kernel="rbf",probability=True,class_weight="balanced",random_state=SEED))])
    }
def _prob(model,x):
    p=model.predict_proba(x)[0]; classes=list(model.classes_)
    return float(p[classes.index(1)]) if 1 in classes else 0.5
def _metrics(frame):
    y=frame.actual.astype(int).to_numpy(); pred=frame.predicted.astype(int).to_numpy(); p=np.clip(frame.p_up.astype(float).to_numpy(),1e-6,1-1e-6)
    return {"n":int(len(frame)),"accuracy":float(accuracy_score(y,pred)),"balanced_accuracy":float(balanced_accuracy_score(y,pred)),"mcc":float(matthews_corrcoef(y,pred)),"brier":float(brier_score_loss(y,p)),"log_loss":float(log_loss(y,p,labels=[0,1])),"roc_auc":float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None}
def _paired_block_bootstrap(predictions, candidate_a, candidate_b, reps=2000, block=4, seed=SEED):
    """Descriptive paired moving-block bootstrap of balanced-accuracy difference A minus B."""
    a=predictions.loc[predictions.candidate==candidate_a].sort_values("expiry_date")
    b=predictions.loc[predictions.candidate==candidate_b].sort_values("expiry_date")
    pair=a[["expiry_date","actual","predicted"]].merge(b[["expiry_date","predicted"]],on="expiry_date",how="inner",suffixes=("_a","_b"),validate="one_to_one").sort_values("expiry_date")
    y=pair.actual.to_numpy(dtype=int); pa=pair.predicted_a.to_numpy(dtype=int); pb=pair.predicted_b.to_numpy(dtype=int)
    n=len(y)
    if n < max(12,block*3) or len(np.unique(y))<2:
        return {"candidate_a":candidate_a,"candidate_b":candidate_b,"status":"UNDERPOWERED","n":n,"block_length":block,"replicates_requested":reps}
    observed=float(balanced_accuracy_score(y,pa)-balanced_accuracy_score(y,pb))
    rng=np.random.default_rng(seed); diffs=[]; attempts=0
    while len(diffs)<reps and attempts<reps*20:
        attempts+=1; ix=[]
        while len(ix)<n:
            start=int(rng.integers(0,n-block+1)); ix.extend(range(start,min(start+block,n)))
        ix=np.asarray(ix[:n],dtype=int); yy=y[ix]
        if len(np.unique(yy))<2: continue
        diffs.append(float(balanced_accuracy_score(yy,pa[ix])-balanced_accuracy_score(yy,pb[ix])))
    if len(diffs)<max(200,reps//2):
        return {"candidate_a":candidate_a,"candidate_b":candidate_b,"status":"UNDERPOWERED","n":n,"block_length":block,"replicates_requested":reps,"replicates_valid":len(diffs),"observed_difference":observed}
    values=np.asarray(diffs)
    return {"candidate_a":candidate_a,"candidate_b":candidate_b,"status":"COMPLETED","n":n,"block_length":block,"replicates_requested":reps,"replicates_valid":len(values),"observed_difference":observed,"difference_ci_95_low":float(np.quantile(values,0.025)),"difference_ci_95_high":float(np.quantile(values,0.975))}

def run_benchmark(input_path=INPUT,out_dir=OUT):
    data=pd.read_csv(input_path)
    required={"expiry_date","label","source_gate_pass",*FEATURES}
    missing=required-set(data.columns)
    if missing: raise ValueError("Missing required dataset columns: "+", ".join(sorted(missing)))
    data["expiry_date"]=pd.to_datetime(data.expiry_date,errors="coerce")
    data=data.loc[data.source_gate_pass.astype(str).str.lower().isin(["true","1"]) & data.label.isin(["UP","DOWN"])].sort_values("expiry_date").dropna(subset=["expiry_date"]).reset_index(drop=True)
    if len(data)<=MIN_HISTORY: raise ValueError(f"Need more than {MIN_HISTORY} source-gated binary rows; got {len(data)}")
    y=(data.label=="UP").astype(int).to_numpy(); rows=[]
    for i in range(MIN_HISTORY,len(data)):
        x_train=data.loc[:i-1,FEATURES].replace([np.inf,-np.inf],np.nan); x_test=data.loc[[i],FEATURES].replace([np.inf,-np.inf],np.nan); yt=y[:i]
        if len(np.unique(yt))<2: continue
        actual=int(y[i]); prior=int(y[i-1])
        for name,p,pred in [("expanding_majority",float(np.mean(yt)),int(np.mean(yt)>=0.5)),("prior_cycle",float(prior),prior),("momentum_5d",float(float(data.loc[i,"ret_5"])>0),int(float(data.loc[i,"ret_5"])>0))]:
            rows.append({"expiry_date":data.loc[i,"expiry_date"].date().isoformat(),"candidate":name,"actual":actual,"p_up":p,"predicted":pred})
        for name,model in candidates().items():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore"); model.fit(x_train,yt); p=_prob(model,x_test)
            rows.append({"expiry_date":data.loc[i,"expiry_date"].date().isoformat(),"candidate":name,"actual":actual,"p_up":p,"predicted":int(p>=0.5)})
    predictions=pd.DataFrame(rows)
    if predictions.empty: raise ValueError("No predictions produced")
    out_dir.mkdir(parents=True,exist_ok=True); predictions.to_csv(out_dir/"predictions_expanding_window.csv",index=False)
    metrics=pd.DataFrame([{"candidate":name,**_metrics(g)} for name,g in predictions.groupby("candidate",sort=False)]).sort_values(["balanced_accuracy","brier"],ascending=[False,True])
    metrics.to_csv(out_dir/"metrics.csv",index=False)
    paired_bootstrap=[_paired_block_bootstrap(predictions,"extra_trees","expanding_majority"),_paired_block_bootstrap(predictions,"extra_trees","random_forest")]
    summary={"status":"EXPLORATORY_ONLY_NOT_CONFIRMATORY","dataset_rows":int(len(data)),"minimum_training_history":MIN_HISTORY,"evaluation_start_expiry":str(data.loc[MIN_HISTORY,"expiry_date"].date()),"evaluation_end_expiry":str(data.iloc[-1].expiry_date.date()),"evaluation_rows":int(len(predictions[predictions.candidate=="logistic"])),"candidates":metrics.to_dict(orient="records"),"paired_four_week_block_bootstrap":paired_bootstrap,"feature_columns":FEATURES,"seed":SEED,"important_caveat":"Phase 10 holdout was already examined. This benchmark is exploratory and cannot certify a new edge; no tuning is permitted on this output. Bootstrap intervals are descriptive and do not repair prior holdout reuse.","trading_strategy_validated":False,"trading_gate":"BLOCKED: no contract-level options/futures fills, date-effective Paytm Money costs, spreads and slippage stress."}
    (out_dir/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    fig,ax=plt.subplots(figsize=(10,5.5)); plot=metrics.sort_values("balanced_accuracy"); ax.barh(plot.candidate,plot.balanced_accuracy); ax.axvline(0.5,linestyle="--",linewidth=1); ax.set_xlim(0,1); ax.set_xlabel("Balanced accuracy"); ax.set_title("Phase 11 — exploratory expanding-window benchmark"); fig.tight_layout(); fig.savefig(out_dir/"balanced_accuracy.png",dpi=160); plt.close(fig)
    report=["# Phase 11 — Diverse Model-Family Benchmark","","- Status: **"+summary["status"]+"**","- Source-gated rows: "+str(len(data)),"- Expanding-window predictions per candidate: "+str(summary["evaluation_rows"]),"- Evaluation dates: "+summary["evaluation_start_expiry"]+" to "+summary["evaluation_end_expiry"],"- Candidates: expanding majority, prior-cycle direction, 5-session momentum, logistic regression, ExtraTrees, Random Forest, Gradient Boosting, Histogram Gradient Boosting, RBF SVC.","","## Results","","| Candidate | N | Accuracy | Balanced accuracy | MCC | Brier | Log loss | ROC AUC |","|---|---:|---:|---:|---:|---:|---:|---:|"]
    for _,r in metrics.iterrows(): report.append(f"| {r.candidate} | {int(r.n)} | {r.accuracy:.3f} | {r.balanced_accuracy:.3f} | {r.mcc:.3f} | {r.brier:.3f} | {r.log_loss:.3f} | {r.roc_auc:.3f} |")
    report += ["","## Interpretation","","This is exploratory screening, not confirmatory evidence. The Phase 10 holdout has already been inspected; these results must not be described as a fresh holdout or used for repeated tuning. A top rank does not establish significance or profitability.","","## Trading gate","",summary["trading_gate"],"","## Reproducibility","","See summary.json, metrics.csv, predictions_expanding_window.csv and balanced_accuracy.png. Preprocessing is fitted inside each expanding training fold."]
    report += ["","## Paired four-week moving-block bootstrap","","Descriptive balanced-accuracy differences use paired four-week blocks to preserve some local dependence. These intervals are not confirmatory because the Phase 10 sample/holdout has already been inspected.","","| Candidate A | Candidate B | Difference A−B | 95% interval | Status |","|---|---|---:|---:|---|"]
    for item in paired_bootstrap:
        ci=(str(round(item["difference_ci_95_low"],3))+" to "+str(round(item["difference_ci_95_high"],3))) if item.get("status")=="COMPLETED" else "n/a"
        diff=str(round(item["observed_difference"],3)) if item.get("observed_difference") is not None else "n/a"
        report.append("| "+item["candidate_a"]+" | "+item["candidate_b"]+" | "+diff+" | "+ci+" | "+item["status"]+" |")
    (out_dir/"report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps({"status":summary["status"],"rows":len(data),"metrics":len(metrics),"evaluation_rows":summary["evaluation_rows"],"top_candidate":metrics.iloc[0].candidate,"top_balanced_accuracy":float(metrics.iloc[0].balanced_accuracy)},indent=2))
if __name__=="__main__": run_benchmark()
