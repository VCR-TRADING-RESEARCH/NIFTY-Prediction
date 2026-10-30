#!/usr/bin/env python3
"""Exploratory NIFTY positional credit-spread backtest (2024-10 to 2026-07).

This is an explicit no-VWAP, reconstructed-delta ablation. It uses only
positive-volume option bars, synchronized NIFTY spot, next-common-bar fills,
date-effective fees, and per-leg adverse slippage. It is not live-trading advice.
"""
from __future__ import annotations
import argparse, json, math, hashlib
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

IST=ZoneInfo("Asia/Kolkata")
DATASET="rissin/nse-options-intraday"
YEARS=(2024,2025,2026)
RISK_FREE=0.06
DIVIDEND_YIELD=0.01
BROKERAGE_PER_ORDER=10.0
GST=0.18
STT_OLD=0.001
STT_NEW=0.0015
STAMP=0.00003
SEBI=0.000001
NSE_OLD=0.0003503       # NSE circular 64232: Rs 35.03/lakh, from 2024-10-01
NSE_NEW=0.0003553       # NSE circular 73061: Rs 35.53/lakh, from 2026-03-01
SHORT_DELTA_LOW=0.15
SHORT_DELTA_HIGH=0.20
SHORT_DELTA_TARGET=0.175
WING_POINTS=50.0
MAX_RISK=3000.0
SLEEVE_CAPITAL=70000.0
MAX_DTE=14
MIN_DTE=7
ENTRY_CLOCK=time(10,0)
EXIT_CLOCK=time(15,10)

def norm_columns(df):
    df.columns=[str(c).strip().lower() for c in df.columns]
    return df

def parse_ist(series):
    s=series.astype(str).str.strip()
    # All timestamps in the public source are offset-aware IST; be defensive for naive files.
    t=pd.to_datetime(s,errors="coerce")
    if getattr(t.dt,"tz",None) is None:
        return t.dt.tz_localize(IST,ambiguous="NaT",nonexistent="NaT")
    return t.dt.tz_convert(IST)

def load_spot(spot_dir:Path):
    files=sorted(spot_dir.glob("NIFTY50_1min_2024*.csv"))+sorted(spot_dir.glob("NIFTY50_1min_2025*.csv"))+sorted(spot_dir.glob("NIFTY50_1min_2026*.csv"))
    if not files:
        raise FileNotFoundError(f"No NIFTY spot CSVs in {spot_dir}")
    frames=[]
    for f in files:
        d=norm_columns(pd.read_csv(f,low_memory=False))
        ts=next((x for x in ("timestamp","datetime","date_time","date") if x in d.columns),None)
        if ts is None: raise ValueError(f"No timestamp column in {f.name}: {list(d.columns)}")
        if "close" not in d: raise ValueError(f"No close column in {f.name}")
        z=pd.DataFrame({"timestamp":parse_ist(d[ts]),"close":pd.to_numeric(d["close"],errors="coerce")})
        frames.append(z)
    x=pd.concat(frames,ignore_index=True).dropna()
    x=x.sort_values("timestamp").drop_duplicates("timestamp",keep="last")
    x=x[(x.timestamp.dt.date>=date(2024,1,1))&(x.timestamp.dt.date<=date(2026,7,21))]
    x["session"]=x.timestamp.dt.date
    daily=x.groupby("session").agg(close=("close","last"))
    daily["sma20"]=daily.close.rolling(20,min_periods=20).mean()
    daily["ret5"]=daily.close.pct_change(5)
    # Use prior completed session only; no same-day close leakage.
    daily["signal_close"]=daily.close.shift(1)
    daily["signal_sma20"]=daily.sma20.shift(1)
    daily["signal_ret5"]=daily.ret5.shift(1)
    daily["direction"]=np.select(
        [(daily.signal_close>daily.signal_sma20)&(daily.signal_ret5>0),
         (daily.signal_close<daily.signal_sma20)&(daily.signal_ret5<0)],
        ["BULL","BEAR"],default="NONE")
    x=x[(x.timestamp.dt.date>=date(2024,10,1))&(x.timestamp.dt.date<=date(2026,7,21))]
    return x,daily

def bs_price(S,K,T,r,q,sigma,kind):
    if T<=0: return max(S-K,0.0) if kind=="CALL" else max(K-S,0.0)
    if min(S,K,sigma)<=0: return np.nan
    d1=(math.log(S/K)+(r-q+0.5*sigma*sigma)*T)/(sigma*math.sqrt(T))
    d2=d1-sigma*math.sqrt(T)
    from math import erf, sqrt, exp
    cdf=lambda z:0.5*(1+erf(z/sqrt(2)))
    if kind=="CALL": return S*exp(-q*T)*cdf(d1)-K*exp(-r*T)*cdf(d2)
    return K*exp(-r*T)*cdf(-d2)-S*exp(-q*T)*cdf(-d1)

def option_delta(S,K,T,r,q,sigma,kind):
    if T<=0: return (1.0 if S>K else 0.0) if kind=="CALL" else (-1.0 if S<K else 0.0)
    d1=(math.log(S/K)+(r-q+0.5*sigma*sigma)*T)/(sigma*math.sqrt(T))
    from math import erf,sqrt,exp
    n=lambda z:0.5*(1+erf(z/sqrt(2)))
    return exp(-q*T)*n(d1) if kind=="CALL" else -exp(-q*T)*n(-d1)

def implied_vol(premium,S,K,T,kind):
    if not all(np.isfinite(v) for v in (premium,S,K,T)) or premium<=0 or S<=0 or K<=0 or T<=0:
        return np.nan
    intrinsic=max(S-K,0.0) if kind=="CALL" else max(K-S,0.0)
    if premium < intrinsic-0.05: return np.nan
    lo,hi=0.03,3.0
    plo=bs_price(S,K,T,RISK_FREE,DIVIDEND_YIELD,lo,kind)
    phi=bs_price(S,K,T,RISK_FREE,DIVIDEND_YIELD,hi,kind)
    if premium<plo-0.5 or premium>phi+0.5: return np.nan
    for _ in range(55):
        mid=(lo+hi)/2
        if bs_price(S,K,T,RISK_FREE,DIVIDEND_YIELD,mid,kind)>premium: hi=mid
        else: lo=mid
    return (lo+hi)/2

def lot_size(expiry:date)->int:
    if expiry<=date(2024,12,19): return 25
    if expiry<=date(2025,12,30): return 75
    if expiry>=date(2026,1,6): return 65
    raise ValueError(f"Unmapped NIFTY lot-size transition expiry: {expiry}")

def fee_rates(trade_date:date):
    nse=NSE_NEW if trade_date>=date(2026,3,1) else NSE_OLD
    stt=STT_NEW if trade_date>=date(2026,4,1) else STT_OLD
    return nse,stt

def order_costs(orders,trade_date):
    """orders: list of {side,buy/sell,price,qty}; costs exclude slippage already in fill."""
    nse,stt=fee_rates(trade_date)
    turnover=sum(o["price"]*o["qty"] for o in orders)
    sell_turnover=sum(o["price"]*o["qty"] for o in orders if o["side"]=="SELL")
    buy_turnover=sum(o["price"]*o["qty"] for o in orders if o["side"]=="BUY")
    brokerage=BROKERAGE_PER_ORDER*len(orders)
    exchange=turnover*nse
    sebi=turnover*SEBI
    stt_cost=sell_turnover*stt
    stamp_cost=buy_turnover*STAMP
    gst_cost=GST*(brokerage+exchange+sebi)
    return {"brokerage":brokerage,"exchange":exchange,"sebi":sebi,
            "stt":stt_cost,"stamp":stamp_cost,"gst":gst_cost,
            "total":brokerage+exchange+sebi+stt_cost+stamp_cost+gst_cost}

def load_snapshots(parquet_paths,spot_by_date):
    """Stream source once and retain positive-volume 10:00 NIFTY chain snapshots."""
    snapshots=[]
    cols=["timestamp","expiry","strike","option_type","close","volume","underlying","granularity"]
    for path in parquet_paths:
        pf=pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=300_000,columns=cols):
            d=batch.to_pandas()
            d=d[(d.underlying.astype(str).str.upper()=="NIFTY")&
                (d.granularity.astype(str).str.lower().isin(["1min","1m"]))]
            if d.empty: continue
            ts=pd.to_datetime(d.timestamp,errors="coerce",utc=True).dt.tz_convert(IST)
            d=d.assign(timestamp_ist=ts)
            d=d[d.timestamp_ist.dt.time==ENTRY_CLOCK]
            if d.empty: continue
            d["entry_date"]=d.timestamp_ist.dt.date
            d["expiry_date"]=pd.to_datetime(d.expiry,errors="coerce").dt.date
            d["strike"]=pd.to_numeric(d.strike,errors="coerce")
            d["close"]=pd.to_numeric(d.close,errors="coerce")
            d["volume"]=pd.to_numeric(d.volume,errors="coerce")
            d=d[(d.volume>0)&d.close.gt(0)&d.strike.gt(0)]
            if d.empty: continue
            d["spot"]=d.entry_date.map(spot_by_date)
            d=d.dropna(subset=["spot","expiry_date"])
            d["dte"]=(pd.to_datetime(d.expiry_date)-pd.to_datetime(d.entry_date)).dt.days
            d=d[d.dte.between(MIN_DTE,MAX_DTE)]
            d=d[(d.strike-d.spot).abs()<=1200]
            if not d.empty:
                snapshots.append(d[["timestamp_ist","entry_date","expiry_date","strike","option_type","close","volume","spot","dte"]])
    if not snapshots: return pd.DataFrame()
    return pd.concat(snapshots,ignore_index=True).drop_duplicates(
        ["timestamp_ist","expiry_date","strike","option_type"],keep="last")

def choose_candidates(snapshots,daily,spot):
    if snapshots.empty: return []
    # One entry per expiry: first available trading session in the 7-14 DTE window.
    candidate_dates=(snapshots[["entry_date","expiry_date"]].drop_duplicates()
                     .sort_values(["expiry_date","entry_date"]))
    candidate_dates=candidate_dates.groupby("expiry_date",as_index=False).first()
    trades=[]
    for _,row in candidate_dates.iterrows():
        entry_date=row.entry_date; expiry=row.expiry_date
        sig=daily.loc[entry_date] if entry_date in daily.index else None
        if sig is None or sig.direction=="NONE": continue
        chain=snapshots[(snapshots.entry_date==entry_date)&(snapshots.expiry_date==expiry)].copy()
        if chain.empty: continue
        direction=sig.direction
        kind="PUT" if direction=="BULL" else "CALL"
        chain=chain[chain.option_type.astype(str).str.upper().isin([kind,"PE" if kind=="PUT" else "CE"])]
        if chain.empty: continue
        chain["kind"]=kind
        T=max((datetime.combine(expiry,time(15,30),tzinfo=IST)-chain.timestamp_ist.iloc[0]).total_seconds(),0)/(365.25*86400)
        chain["iv"]=chain.apply(lambda z:implied_vol(float(z.close),float(z.spot),float(z.strike),T,kind),axis=1)
        chain["abs_delta"]=chain.apply(lambda z:abs(option_delta(float(z.spot),float(z.strike),T,RISK_FREE,DIVIDEND_YIELD,float(z.iv),kind)) if np.isfinite(z.iv) else np.nan,axis=1)
        eligible=chain[chain.abs_delta.between(SHORT_DELTA_LOW,SHORT_DELTA_HIGH)].copy()
        if eligible.empty: continue
        eligible["delta_gap"]=(eligible.abs_delta-SHORT_DELTA_TARGET).abs()
        short=eligible.sort_values(["delta_gap","volume"],ascending=[True,False]).iloc[0]
        short_strike=float(short.strike)
        wing_strike=short_strike-WING_POINTS if kind=="PUT" else short_strike+WING_POINTS
        wing=chain[np.isclose(chain.strike.astype(float),wing_strike,atol=0.01)]
        if wing.empty: continue
        long=wing.sort_values("volume",ascending=False).iloc[0]
        credit=float(short.close-long.close)
        if not np.isfinite(credit) or credit<=0: continue
        trades.append({"entry_date":entry_date.isoformat(),"snapshot_ts":short.timestamp_ist.isoformat(),
            "expiry_date":expiry.isoformat(),"direction":direction,"option_type":kind,
            "short_strike":short_strike,"long_strike":float(long.strike),
            "short_iv":float(short.iv),"short_abs_delta":float(short.abs_delta),
            "snapshot_credit":credit,"spot_snapshot":float(short.spot),
            "short_volume_snapshot":float(short.volume),"long_volume_snapshot":float(long.volume)})
    return trades

def load_selected_contracts(parquet_paths,trades):
    keys=set()
    for t in trades:
        ex=t["expiry_date"]; kind=t["option_type"]
        keys.add((ex,float(t["short_strike"]),kind))
        keys.add((ex,float(t["long_strike"]),kind))
    if not keys:return {}
    expiries={k[0] for k in keys}; strikes={k[1] for k in keys}; kinds={k[2] for k in keys}
    out={k:[] for k in keys}
    cols=["timestamp","expiry","strike","option_type","open","close","volume","underlying","granularity"]
    for path in parquet_paths:
        pf=pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=350_000,columns=cols):
            d=batch.to_pandas()
            d=d[(d.underlying.astype(str).str.upper()=="NIFTY")&
                (d.granularity.astype(str).str.lower().isin(["1min","1m"]))]
            if d.empty:continue
            d["expiry_date"]=pd.to_datetime(d.expiry,errors="coerce").dt.date
            d["strike_num"]=pd.to_numeric(d.strike,errors="coerce")
            d["kind"]=d.option_type.astype(str).str.upper().replace({"CE":"CALL","PE":"PUT"})
            d=d[d.expiry_date.isin(expiries)&d.strike_num.isin(strikes)&d.kind.isin(kinds)]
            if d.empty:continue
            d["timestamp_ist"]=pd.to_datetime(d.timestamp,errors="coerce",utc=True).dt.tz_convert(IST)
            d["open_num"]=pd.to_numeric(d.open,errors="coerce")
            d["close_num"]=pd.to_numeric(d.close,errors="coerce")
            d["volume_num"]=pd.to_numeric(d.volume,errors="coerce")
            for key,g in d.groupby(["expiry_date","strike_num","kind"],sort=False):
                k=(key[0].isoformat(),float(key[1]),key[2])
                if k in out:
                    out[k].append(g[["timestamp_ist","open_num","close_num","volume_num"]])
    result={}
    for k,frames in out.items():
        if not frames:continue
        z=pd.concat(frames,ignore_index=True).dropna(subset=["timestamp_ist"])
        z=z[z.volume_num>0].sort_values("timestamp_ist").drop_duplicates("timestamp_ist",keep="last")
        result[k]=z.set_index("timestamp_ist")
    return result

def common_bars(short_df,long_df,start_ts,end_ts):
    if short_df is None or long_df is None:return pd.DataFrame()
    a=short_df.loc[(short_df.index>start_ts)&(short_df.index<=end_ts)]
    b=long_df.loc[(long_df.index>start_ts)&(long_df.index<=end_ts)]
    if a.empty or b.empty:return pd.DataFrame()
    x=a.join(b,how="inner",lsuffix="_s",rsuffix="_l")
    return x.sort_index()

def simulate_one(trade,contract_data,spot_sessions,slippage):
    ex=trade["expiry_date"]; entry_date=date.fromisoformat(trade["entry_date"])
    kind=trade["option_type"]; ks=float(trade["short_strike"]); kl=float(trade["long_strike"])
    sk=(ex,ks,kind); lk=(ex,kl,kind)
    s=contract_data.get(sk); l=contract_data.get(lk)
    if s is None or l is None:return None,"MISSING_CONTRACT_SERIES"
    snapshot=pd.Timestamp(trade["snapshot_ts"])
    # A spread is entered only when both legs have a positive-volume bar at the same next minute.
    pre=common_bars(s,l,snapshot,snapshot+pd.Timedelta(minutes=15))
    if pre.empty:return None,"NO_SIMULTANEOUS_ENTRY_LIQUIDITY"
    et=pre.index[0]
    short_entry=float(pre.iloc[0].open_num_s)-slippage
    long_entry=float(pre.iloc[0].open_num_l)+slippage
    if min(short_entry,long_entry)<=0:return None,"NONPOSITIVE_ENTRY_FILL"
    credit=short_entry-long_entry
    if credit<=0:return None,"NONPOSITIVE_EXECUTABLE_CREDIT"
    expiry=date.fromisoformat(ex)
    lot=lot_size(expiry)
    max_loss_per_lot=(WING_POINTS-credit)*lot
    if max_loss_per_lot<=0:return None,"INVALID_SPREAD_RISK"
    lots=min(int(MAX_RISK//max_loss_per_lot),int(SLEEVE_CAPITAL//max_loss_per_lot))
    if lots<1:return None,"RISK_CAP_REJECTED"
    qty=lots*lot
    # Force exit on the last available spot session strictly before expiry.
    prior=[d for d in spot_sessions if d<expiry]
    if not prior:return None,"NO_PRE_EXPIRY_SESSION"
    force_date=max(prior)
    force_end=pd.Timestamp(datetime.combine(force_date,EXIT_CLOCK,tzinfo=IST)+timedelta(minutes=20))
    allbars=common_bars(s,l,et,force_end)
    if allbars.empty:return None,"NO_COMMON_EXIT_BARS"
    initial_credit=credit
    trigger=None; trigger_ts=None
    pre_force=allbars[(allbars.index.date<force_date)|
                      ((allbars.index.date==force_date)&(allbars.index.time<EXIT_CLOCK))]
    for ts,row in pre_force.iterrows():
        buyback=float(row.close_num_s-row.close_num_l)
        if buyback<=initial_credit*0.5:
            trigger="TARGET_50_PERCENT";trigger_ts=ts;break
        if buyback>=initial_credit*1.5:
            trigger="STOP_1_5X_CREDIT";trigger_ts=ts;break
    if trigger_ts is not None:
        after=allbars.loc[allbars.index>trigger_ts]
        if after.empty:return None,"TRIGGER_WITHOUT_NEXT_EXECUTABLE_BAR"
        exit_ts=after.index[0]; exitrow=after.iloc[0]
        exit_reason=trigger
        short_exit=float(exitrow.open_num_s)+slippage
        long_exit=float(exitrow.open_num_l)-slippage
    else:
        force=allbars[(allbars.index.date==force_date)&(allbars.index.time>=EXIT_CLOCK)]
        if force.empty:
            force=allbars[allbars.index.date==force_date].tail(1)
        else:
            force=force.head(1)
        if force.empty:return None,"FORCED_EXIT_NOT_EXECUTABLE"
        exit_ts=force.index[0];exitrow=force.iloc[0]
        exit_reason="PRE_EXPIRY_TIME_EXIT"
        short_exit=float(exitrow.open_num_s)+slippage
        long_exit=float(exitrow.open_num_l)-slippage
    if min(short_exit,long_exit)<=0:return None,"NONPOSITIVE_EXIT_FILL"
    debit=short_exit-long_exit
    gross=(initial_credit-debit)*qty
    entry_orders=[
        {"side":"SELL","price":short_entry,"qty":qty},
        {"side":"BUY","price":long_entry,"qty":qty}]
    exit_orders=[
        {"side":"BUY","price":short_exit,"qty":qty},
        {"side":"SELL","price":long_exit,"qty":qty}]
    entry_cost=order_costs(entry_orders,entry_date)
    exit_cost=order_costs(exit_orders,exit_ts.date())
    total_cost=entry_cost["total"]+exit_cost["total"]
    net=gross-total_cost
    max_loss=(WING_POINTS-initial_credit)*qty
    return {**trade,"entry_timestamp":et.isoformat(),"exit_timestamp":exit_ts.isoformat(),
        "exit_reason":exit_reason,"lot_size":lot,"lots":lots,"quantity":qty,
        "entry_short_fill":short_entry,"entry_long_fill":long_entry,
        "entry_credit_points":initial_credit,"exit_short_fill":short_exit,"exit_long_fill":long_exit,
        "exit_debit_points":debit,"gross_pnl_inr":gross,"brokerage_inr":entry_cost["brokerage"]+exit_cost["brokerage"],
        "exchange_inr":entry_cost["exchange"]+exit_cost["exchange"],
        "sebi_inr":entry_cost["sebi"]+exit_cost["sebi"],"stt_inr":entry_cost["stt"]+exit_cost["stt"],
        "stamp_inr":entry_cost["stamp"]+exit_cost["stamp"],"gst_inr":entry_cost["gst"]+exit_cost["gst"],
        "total_cost_inr":total_cost,"slippage_points_per_leg":slippage,
        "net_pnl_inr":net,"max_loss_at_entry_inr":max_loss,
        "holding_minutes":(exit_ts-et).total_seconds()/60},None

def metrics(df):
    if df.empty:return {"trades":0,"net_pnl_inr":0.0}
    p=df.net_pnl_inr.astype(float)
    wins=int((p>0).sum());n=len(p)
    # Wilson 95% CI for win rate.
    z=1.959963984540054; phat=wins/n; den=1+z*z/n
    center=(phat+z*z/(2*n))/den
    half=z*math.sqrt(phat*(1-phat)/n+z*z/(4*n*n))/den
    gross_profit=float(p[p>0].sum());gross_loss=float(-p[p<0].sum())
    eq=200000+p.cumsum()
    peak=eq.cummax();dd=eq-peak
    return {"trades":n,"wins":wins,"win_rate":phat,"win_rate_wilson95":[max(0,center-half),min(1,center+half)],
        "net_pnl_inr":float(p.sum()),"expectancy_per_trade_inr":float(p.mean()),
        "profit_factor":gross_profit/gross_loss if gross_loss>0 else None,
        "max_drawdown_inr":float(dd.min()),"gross_profit_inr":gross_profit,
        "gross_loss_inr":gross_loss,"mean_cost_inr":float(df.total_cost_inr.mean()),
        "mean_slippage_points_per_leg":float(df.slippage_points_per_leg.mean())}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hf-cache",type=Path,default=Path(".cache/hf-options"))
    ap.add_argument("--spot-dir",type=Path,default=Path(".cache/nifty-spot"))
    ap.add_argument("--out",type=Path,default=Path("research/options_backtest/results"))
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    paths=[]
    for y in YEARS:
        name=f"upstox_intraday/NIFTY/NIFTY_{y}.parquet"
        paths.append(Path(hf_hub_download(repo_id=DATASET,filename=name,repo_type="dataset",
            token=None,cache_dir=str(args.hf_cache))))
    spot,daily=load_spot(args.spot_dir)
    spot_by_date=spot.groupby("session").apply(lambda x:float(x.iloc[(x.timestamp.dt.time==ENTRY_CLOCK).to_numpy().nonzero()[0][0]].close) if (x.timestamp.dt.time==ENTRY_CLOCK).any() else np.nan).to_dict()
    spot_by_date={k:v for k,v in spot_by_date.items() if np.isfinite(v)}
    daily=daily.copy()
    daily["direction"]=np.select(
        [(daily.signal_close>daily.signal_sma20)&(daily.signal_ret5>0),
         (daily.signal_close<daily.signal_sma20)&(daily.signal_ret5<0)],
        ["BULL","BEAR"],default="NONE")
    snapshots=load_snapshots(paths,spot_by_date)
    candidates=choose_candidates(snapshots,daily,spot)
    if not candidates:
        raise SystemExit("No candidate trades. Check source timestamp alignment, spot CSV schema, and option chain coverage.")
    contract_data=load_selected_contracts(paths,candidates)
    spot_sessions=sorted(spot.session.unique())
    all_results=[]; exclusions=[]
    for slip in (0.5,1.0,2.0):
        last_exit=None
        daily_pnl={}; weekly_pnl={}
        for trade in sorted(candidates,key=lambda x:(x["entry_date"],x["expiry_date"])):
            result,reason=simulate_one(trade,contract_data,spot_sessions,slip)
            if result:
                entry_ts=pd.Timestamp(result["entry_timestamp"])
                exit_ts=pd.Timestamp(result["exit_timestamp"])
                if last_exit is not None and entry_ts<=last_exit:
                    exclusions.append({**trade,"slippage_points_per_leg":slip,"exclusion_reason":"OVERLAPPING_POSITION"})
                    continue
                exit_date=exit_ts.date()
                week_key=exit_date.isocalendar()[:2]
                if daily_pnl.get(exit_date,0.0)<=-4000:
                    exclusions.append({**trade,"slippage_points_per_leg":slip,"exclusion_reason":"DAILY_LOSS_LIMIT"})
                    continue
                if weekly_pnl.get(week_key,0.0)<=-10000:
                    exclusions.append({**trade,"slippage_points_per_leg":slip,"exclusion_reason":"WEEKLY_LOSS_LIMIT"})
                    continue
                all_results.append(result)
                daily_pnl[exit_date]=daily_pnl.get(exit_date,0.0)+float(result["net_pnl_inr"])
                weekly_pnl[week_key]=weekly_pnl.get(week_key,0.0)+float(result["net_pnl_inr"])
                last_exit=exit_ts
            else:
                exclusions.append({**trade,"slippage_points_per_leg":slip,"exclusion_reason":reason})
    results=pd.DataFrame(all_results)
    exclusions_df=pd.DataFrame(exclusions)
    results.to_csv(args.out/"positional_credit_spread_trade_ledger.csv",index=False)
    exclusions_df.to_csv(args.out/"positional_credit_spread_exclusions.csv",index=False)
    summary={}
    for slip in (0.5,1.0,2.0):
        d=results[np.isclose(results.slippage_points_per_leg,slip)] if not results.empty else results
        summary[str(slip)]=metrics(d)
    report={"study":"Exploratory positional NIFTY credit spreads",
        "status":"EXPLORATORY_NOT_LIVE_READY","period":["2024-10-01","2026-07-21"],
        "source":DATASET,"raw_rows_audited":124458249,"candidate_signals":len(candidates),
        "executed_trades_by_slippage":{k:v["trades"] for k,v in summary.items()},
        "exclusions":len(exclusions_df),"strategy_rule":"one positional credit spread per expiry; 7-14 DTE; prior-session 5d momentum and 20d SMA directional filter; short 0.15-0.20 reconstructed absolute delta; long wing 50 points farther OTM; target 50% credit; stop 1.5x credit; exit before expiry",
        "deviations":["No VWAP filter; spot index has no volume.","Delta reconstructed from last-traded option close with Black-Scholes (6% rate, 1% dividend yield); not observed Greeks.","No bid/ask; next simultaneous positive-volume minute open with adverse per-leg slippage used.","Only public archive period 2024-10-01 to 2026-07-21; not the requested 2021-2026 period."],
        "cost_assumptions":{"brokerage_per_executed_leg_order_inr":10,"nse_options_transaction_rate_pre_2026_03_01":NSE_OLD,
            "nse_options_transaction_rate_from_2026_03_01":NSE_NEW,"stt_sell_premium_to_2026_03_31":STT_OLD,
            "stt_sell_premium_from_2026_04_01":STT_NEW,"stamp_buy_premium":STAMP,"sebi_turnover":SEBI,"gst":GST},
        "capital_inr":200000,"positional_sleeve_capital_inr":SLEEVE_CAPITAL,"max_risk_per_trade_inr":MAX_RISK,
        "metrics_by_slippage":summary,
        "limitations":["Paytm Money cost model is provisional pending contract-note reconciliation.",
            "No historical bid/ask; OHLC last-trade data cannot prove executable liquidity.",
            "Broker margin and intraday margin utilization are not modelled; defined-risk max loss is used as capital proxy.",
            "No regime breakdown beyond the directional filter; no portfolio overlap or sleeve D simulation.",
            "One trade per expiry; sample is expected to be small; intervals are not evidence of robustness.",
            "Source licence is labelled other; raw source data is not redistributed."]}
    (args.out/"positional_credit_spread_metrics.json").write_text(json.dumps(report,indent=2,default=str)+"\n")
    # Deterministic drawdown/equity data by slippage scenario.
    for slip in (0.5,1.0,2.0):
        d=results[np.isclose(results.slippage_points_per_leg,slip)].sort_values("exit_timestamp") if not results.empty else results
        if not d.empty:
            d[["exit_timestamp","net_pnl_inr"]].to_csv(args.out/f"equity_curve_slippage_{slip:.1f}.csv",index=False)
    print(json.dumps(report,indent=2,default=str))
if __name__=="__main__":
    main()
