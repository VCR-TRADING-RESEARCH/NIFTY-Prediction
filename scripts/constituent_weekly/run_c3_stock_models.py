from __future__ import annotations
import gzip, hashlib, json, os, traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from scipy.stats import spearmanr
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss, matthews_corrcoef, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'research/constituent_weekly'; MANIFEST=OUT/'C2_PANEL_BUILD.json'
PANEL_DIR=Path(os.getenv('BUP01_C3_PANEL_DIR','/tmp/bup01-c3-panel'))
FEATURES=['ret_1d','ret_5d','ret_10d','ret_20d','ret_60d','vol_5d','vol_20d','vol_60d','range_10d','range_20d','gap_1d','volume_z20','cs_rank_ret5','cs_rank_ret20']
MIN_PRIOR=104; HOLDOUT=206; REFIT=4; SEED=20261031; REPS=2000
def key(token):
    if not token: raise ValueError('HF_TOKEN missing for encrypted panel decryption')
    return hashlib.sha256(b'BUP01-TejHQ-EOD-cache-v1:'+token.strip().encode()).digest()
def decrypt(path,token,aad):
    b=path.read_bytes()
    if len(b)<13: raise ValueError('Encrypted panel truncated')
    return AESGCM(key(token)).decrypt(b[:12],b[12:],aad)
def encrypt(data,token,aad):
    n=os.urandom(12); return n+AESGCM(key(token)).encrypt(n,data,aad)
def load_panels():
    m=json.loads(MANIFEST.read_text()); assert m['status']=='COMPLETED' and m['methodology_version']=='bup01-c2-panel-v1'
    digest=m['input_manifest']['hash']; token=os.environ['HF_TOKEN']; frames=[]
    for name in ('stock','index'):
        meta=m['encrypted_panel_cache'][name]; path=PANEL_DIR/Path(meta['cache_relative_path']).name; raw=path.read_bytes()
        if len(raw)!=meta['ciphertext_bytes'] or hashlib.sha256(raw).hexdigest()!=meta['ciphertext_sha256']: raise ValueError(name+' ciphertext checksum mismatch')
        aad=f"bup01-c2-panel-v1|frozen_panel|{digest}|{name}".encode(); frames.append(pd.read_csv(gzip.decompress(decrypt(path,token,aad))))
    return frames[0],frames[1],m
def weights(ids):
    c=ids.value_counts(); w=ids.map(lambda x:1/c.loc[x]).to_numpy(float); return w/w.mean()
def score(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6); pred=(p>=.5).astype(int)
    return {'n':len(y),'accuracy':float(accuracy_score(y,pred)),'balanced_accuracy':float(balanced_accuracy_score(y,pred)),'mcc':float(matthews_corrcoef(y,pred)),'brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,p,labels=[0,1])),'roc_auc':float(roc_auc_score(y,p)) if len(np.unique(y))>1 else None,'positive_rate':float(y.mean())}
def symbol_frequency(train,test):
    g=train.groupby('symbol').stock_label.agg(['sum','count']); global_p=(train.stock_label.sum()+1)/(len(train)+2); out=[]
    for s in test.symbol:
        out.append((g.loc[s,'sum']+1)/(g.loc[s,'count']+2) if s in g.index else global_p)
    return np.asarray(out,float)
def boot_ci(diffs):
    x=np.asarray(diffs,float); n=len(x)
    if n<8:return {'n_cycles':n,'mean_difference':float(x.mean()) if n else None,'ci95':None}
    rng=np.random.default_rng(SEED); reps=np.empty(REPS)
    for b in range(REPS):
        ix=[]
        while len(ix)<n:
            s=int(rng.integers(n)); ix.extend([(s+j)%n for j in range(4)])
        reps[b]=x[ix[:n]].mean()
    return {'n_cycles':n,'mean_difference':float(x.mean()),'ci95':[float(np.quantile(reps,.025)),float(np.quantile(reps,.975))],'replicates':REPS,'block_cycles':4,'seed':SEED}
def models(seed):
    return {
      'logistic':Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler()),('model',LogisticRegression(C=.1,max_iter=2000,class_weight='balanced',random_state=seed))]),
      'extra_trees':Pipeline([('impute',SimpleImputer(strategy='median')),('model',ExtraTreesClassifier(n_estimators=300,max_depth=10,min_samples_leaf=25,max_features=.8,class_weight='balanced_subsample',random_state=seed,n_jobs=-1))]),
      'hist_gradient_boosting':Pipeline([('impute',SimpleImputer(strategy='median')),('model',HistGradientBoostingClassifier(max_iter=150,learning_rate=.05,max_leaf_nodes=15,l2_regularization=5,min_samples_leaf=40,random_state=seed))])}
def main():
    OUT.mkdir(parents=True,exist_ok=True); stock,index,manifest=load_panels()
    required={'cycle_idx','symbol','stock_label','stock_return','primary_flag',*FEATURES}
    if required-set(stock.columns): raise ValueError('Panel schema missing '+str(sorted(required-set(stock.columns))))
    if stock.duplicated(['cycle_idx','symbol']).any() or index.duplicated(['cycle_idx']).any(): raise ValueError('Duplicate C2 cycle keys')
    cycles=sorted(index.cycle_idx.astype(int).unique())
    if len(cycles)!=258 or HOLDOUT not in cycles: raise ValueError('C2 cycle or holdout boundary differs from frozen plan')
    primary=stock.primary_flag.astype(str).str.lower().isin(['true','1'])
    d=stock.loc[primary & stock.stock_label.notna()].copy(); d['cycle_idx']=d.cycle_idx.astype(int); d['stock_label']=d.stock_label.astype(int); d['stock_return']=pd.to_numeric(d.stock_return,errors='coerce'); d=d.dropna(subset=FEATURES+['stock_return'])
    if (d.groupby('cycle_idx').size().reindex(cycles,fill_value=0)<47).any(): raise ValueError('Complete-case C3 rows below 47 in an accepted cycle')
    forecast_cycles=cycles[MIN_PRIOR:]; blocks=[forecast_cycles[i:i+REFIT] for i in range(0,len(forecast_cycles),REFIT)]; out=[]
    for block in blocks:
        start=block[0]; tr=d[d.cycle_idx<start]; te=d[d.cycle_idx.isin(block)]
        if tr.cycle_idx.nunique()<MIN_PRIOR or tr.stock_label.nunique()<2: raise ValueError('Warm-up or class diversity gate failed at '+str(start))
        xtr=tr[FEATURES].to_numpy(float); xte=te[FEATURES].to_numpy(float); y=tr.stock_label.to_numpy(int); w=weights(tr.cycle_idx)
        row=te[['cycle_idx','anchor_date','expiry_date','symbol','stock_label','stock_return']].copy()
        row['momentum_p_up']=np.where(te.ret_5d.to_numpy(float)>0,.55,.45); row['symbol_frequency_p_up']=symbol_frequency(tr,te)
        for name,model in models(SEED+start).items():
            model.fit(xtr,y,model__sample_weight=w); row[name+'_p_up']=model.predict_proba(xte)[:,1]
        reg=Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler()),('model',Ridge(alpha=10))]); reg.fit(xtr,tr.stock_return.to_numpy(float),model__sample_weight=w)
        row['ridge_return_prediction']=reg.predict(xte); out.append(row)
    pred=pd.concat(out,ignore_index=True).sort_values(['cycle_idx','symbol'])
    if pred.duplicated(['cycle_idx','symbol']).any() or pred.cycle_idx.min()!=cycles[MIN_PRIOR] or pred.cycle_idx.max()!=cycles[-1]: raise ValueError('OOF coverage/uniqueness gate failed')
    result_metrics={}; cycle_detail={}; diffs=[]
    for split,sub in [('development',pred[pred.cycle_idx<HOLDOUT]),('untouched_holdout',pred[pred.cycle_idx>=HOLDOUT])]:
        result_metrics[split]={}; detail=[]
        for col in ['momentum_p_up','symbol_frequency_p_up','logistic_p_up','extra_trees_p_up','hist_gradient_boosting_p_up']: result_metrics[split][col.removesuffix('_p_up')]=score(sub.stock_label,sub[col])
        for cid,g in sub.groupby('cycle_idx'):
            r={'cycle_idx':int(cid),'anchor_date':str(g.anchor_date.iloc[0]),'expiry_date':str(g.expiry_date.iloc[0]),'n':len(g)}
            for col in ['momentum_p_up','symbol_frequency_p_up','logistic_p_up','extra_trees_p_up','hist_gradient_boosting_p_up']:
                r[col.replace('_p_up','_accuracy')]=float(accuracy_score(g.stock_label,(g[col]>=.5).astype(int))); r[col.replace('_p_up','_brier')]=float(brier_score_loss(g.stock_label,g[col]))
            rho=spearmanr(g.stock_return,g.ridge_return_prediction).statistic; r['ridge_return_rank_ic']=float(rho) if np.isfinite(rho) else None; detail.append(r)
        result_metrics[split]['cycle_macro']={'cycles':len(detail),'momentum_accuracy':float(np.mean([x['momentum_accuracy'] for x in detail])),'logistic_accuracy':float(np.mean([x['logistic_accuracy'] for x in detail])),'extra_trees_accuracy':float(np.mean([x['extra_trees_accuracy'] for x in detail])),'hist_gradient_boosting_accuracy':float(np.mean([x['hist_gradient_boosting_accuracy'] for x in detail])),'ridge_return_rank_ic':float(np.nanmean([x['ridge_return_rank_ic'] for x in detail if x['ridge_return_rank_ic'] is not None])) if any(x['ridge_return_rank_ic'] is not None for x in detail) else None}
        if split=='untouched_holdout':
            cycle_detail=detail
            for _,g in sub.groupby('cycle_idx'): diffs.append(accuracy_score(g.stock_label,(g.logistic_p_up>=.5).astype(int))-accuracy_score(g.stock_label,(g.momentum_p_up>=.5).astype(int)))
    token=os.environ['HF_TOKEN']; enc=encrypt(gzip.compress(pred.to_csv(index=False).encode()),token,b'BUP01-C3-STOCK-OOF-v1'); (OUT/'C3_STOCK_OOF_FORECASTS.csv.gz.aesgcm').write_bytes(enc)
    result={'track':'BUP-01-C3','status':'EXPLORATORY_COMPLETE_NOT_CONFIRMATORY','created_at_utc':datetime.now(timezone.utc).isoformat(),'methodology_version':'BUP01-C3-v1','input_c2_manifest_hash':manifest['input_manifest']['hash'],'data':{'eligible_cycles':len(cycles),'forecast_cycles':int(pred.cycle_idx.nunique()),'holdout_start_cycle_idx':HOLDOUT,'holdout_cycles':int((index.cycle_idx>=HOLDOUT).sum()),'stock_forecast_rows':len(pred),'unique_symbols':int(pred.symbol.nunique()),'minimum_prior_cycles':MIN_PRIOR,'refit_block_cycles':REFIT,'identity_flagged_rows_excluded':int(stock.identity_review_flag.sum()),'action_crossing_rows_excluded':int(stock.action_crossing_flag.sum()),'raw_prices_published':False,'per_stock_forecasts_encrypted':True},'metrics':result_metrics,'holdout_logistic_vs_momentum_cycle_accuracy_difference':boot_ci(diffs),'holdout_cycle_detail':cycle_detail,'limitations':['Exploratory only; not confirmation or trading approval.','Scores are uncalibrated; no holdout tuning or calibration.','Identity/action flags excluded; unresolved historical catalogue not certified.','Cycle dependence addressed using paired four-cycle moving-block bootstrap.','C4 NIFTY aggregation remains separate.','No options, FII/DII, global-market, VIX, news, costs, slippage or P&L analysis in C3.']}
    (OUT/'C3_RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    lines=['# BUP-01 C3 Stock Model Results','','**Status:** EXPLORATORY COMPLETE — NOT CONFIRMATORY','',f"- C2 manifest: `{result['input_c2_manifest_hash']}`",f"- Eligible cycles: {len(cycles)}; OOF forecast cycles: {pred.cycle_idx.nunique()}; holdout starts at cycle {HOLDOUT}.",f"- OOF stock rows: {len(pred)} across {pred.symbol.nunique()} symbols.",'- 104-cycle warm-up; model refit every four cycles; complete cycles remain indivisible.','- Per-stock OOF forecasts encrypted; raw prices and feature values not published.','','## Stock direction metrics','','| Split | Model | Rows | Accuracy | Balanced accuracy | MCC | ROC-AUC | Brier | Log loss |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for split,items in result_metrics.items():
        for name,m in items.items():
            if name=='cycle_macro': continue
            lines.append(f"| {split} | {name} | {m['n']} | {m['accuracy']:.4f} | {m['balanced_accuracy']:.4f} | {m['mcc']:.4f} | {m['roc_auc'] if m['roc_auc'] is not None else float('nan'):.4f} | {m['brier']:.4f} | {m['log_loss']:.4f} |")
    lines+=['','## Cycle-macro performance','','| Split | Cycles | Momentum accuracy | Logistic accuracy | ExtraTrees accuracy | HistGradientBoosting accuracy | Ridge return rank IC |','|---|---:|---:|---:|---:|---:|---:|']
    for split,items in result_metrics.items():
        m=items['cycle_macro']; lines.append(f"| {split} | {m['cycles']} | {m['momentum_accuracy']:.4f} | {m['logistic_accuracy']:.4f} | {m['extra_trees_accuracy']:.4f} | {m['hist_gradient_boosting_accuracy']:.4f} | {m['ridge_return_rank_ic'] if m['ridge_return_rank_ic'] is not None else float('nan'):.4f} |")
    u=result['holdout_logistic_vs_momentum_cycle_accuracy_difference']; lines+=['','## Paired holdout uncertainty','',f"- Logistic minus momentum mean cycle-accuracy difference: {u['mean_difference']}",f"- Four-cycle moving-block bootstrap 95% interval: {u['ci95']}",'- Replicates: 2,000; seed: 20261031.','','Stock-level results are exploratory. C4 must test whether OOF stock forecasts improve NIFTY direction on the same holdout. No trading profitability is inferred.']
    (OUT/'C3_RESULTS.md').write_text('\n'.join(lines)+'\n')
    (OUT/'C3_STATUS.md').write_text('# C3 Status\n\n- Status: EXPLORATORY COMPLETE — NOT CONFIRMATORY\n- C2: PASS; C3: exploratory stock modelling complete.\n- C4 NIFTY aggregation: NOT STARTED.\n- Trading: NOT VALIDATED.\n- Results: [C3_RESULTS.md](C3_RESULTS.md)\n')
    print('C3_COMPLETE',json.dumps({'rows':len(pred),'forecast_cycles':int(pred.cycle_idx.nunique()),'holdout_rows':int((pred.cycle_idx>=HOLDOUT).sum()),'metrics':{s:{k:v.get('accuracy') for k,v in x.items() if isinstance(v,dict) and 'accuracy' in v} for s,x in result_metrics.items()}},sort_keys=True))
if __name__=='__main__':
    try: main()
    except Exception as e:
        OUT.mkdir(parents=True,exist_ok=True); fail={'track':'BUP-01-C3','status':'BLOCKED_OR_FAILED','created_at_utc':datetime.now(timezone.utc).isoformat(),'error_type':type(e).__name__,'error_message':str(e)[:500],'traceback_tail':traceback.format_exc().splitlines()[-8:]}
        (OUT/'C3_RESULTS.json').write_text(json.dumps(fail,indent=2)+'\n'); (OUT/'C3_STATUS.md').write_text('# C3 Status\n\n- Status: BLOCKED_OR_FAILED; no model result is claimed.\n- Error: '+type(e).__name__+': '+str(e)[:500]+'\n'); raise