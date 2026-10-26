#!/usr/bin/env python3
"""Fail-closed, transaction-cost-aware audit. Never invent historical fills."""
import argparse, json
from pathlib import Path
import pandas as pd

REQUIRED = ["trade_id","entry_date","exit_date","instrument_type","side","entry_mid","exit_mid","entry_spread_points","exit_spread_points","entry_slippage_points","exit_slippage_points","quantity","lot_size","brokerage","exchange_txn_charge","stt","gst","stamp_duty","sebi_charge","other_charges","cost_schedule_source","price_source","fill_method"]
COSTS = ["brokerage","exchange_txn_charge","stt","gst","stamp_duty","sebi_charge","other_charges"]
NONNEG = ["entry_spread_points","exit_spread_points","entry_slippage_points","exit_slippage_points","quantity","lot_size",*COSTS]

def build_report(path: Path) -> dict:
    if not path.exists():
        return {"status":"BLOCKED_MISSING_CONTRACT_LEVEL_DATA","input_path":str(path),"required_columns":REQUIRED,"trade_count":0,"net_pnl":None,"message":"No contract-level fills input. No P&L was estimated. Source-register historical contracts, prices, date-effective Paytm Money costs, spread and slippage before evaluating profitability."}
    df=pd.read_csv(path)
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing:
        return {"status":"BLOCKED_SCHEMA_INVALID","input_path":str(path),"missing_columns":missing,"trade_count":int(len(df)),"net_pnl":None,"message":"Required trade, fill, source, or cost fields are missing."}
    if df.empty:
        return {"status":"BLOCKED_EMPTY_DATA","input_path":str(path),"trade_count":0,"net_pnl":None,"message":"Trade file exists but contains no trades."}
    for c in ["entry_date","exit_date"]:
        df[c]=pd.to_datetime(df[c],errors="coerce")
    if df[["entry_date","exit_date"]].isna().any().any(): raise ValueError("Invalid entry_date or exit_date.")
    if (df.exit_date < df.entry_date).any(): raise ValueError("exit_date precedes entry_date.")
    numeric=["entry_mid","exit_mid","entry_spread_points","exit_spread_points","entry_slippage_points","exit_slippage_points","quantity","lot_size",*COSTS]
    for c in numeric: df[c]=pd.to_numeric(df[c],errors="coerce")
    if df[numeric].isna().any().any(): raise ValueError("Numeric input contains missing or invalid values.")
    if (df[NONNEG] < 0).any().any(): raise ValueError("Spread, slippage, quantity, lot size and charges must be nonnegative.")
    if (df[["quantity","lot_size"]] <= 0).any().any(): raise ValueError("quantity and lot_size must be positive.")
    if not df.side.isin(["LONG","SHORT"]).all(): raise ValueError("side must be LONG or SHORT.")
    if not df.instrument_type.isin(["FUTURE","OPTION"]).all(): raise ValueError("instrument_type must be FUTURE or OPTION.")
    for c in ["cost_schedule_source","price_source","fill_method"]:
        if df[c].astype(str).str.strip().eq("").any(): raise ValueError(f"{c} must identify provenance.")
    df=df.sort_values(["exit_date","trade_id"]).reset_index(drop=True)
    sign=df.side.map({"LONG":1.0,"SHORT":-1.0})
    entry_cost=df.entry_spread_points/2+df.entry_slippage_points
    exit_cost=df.exit_spread_points/2+df.exit_slippage_points
    entry_fill=df.entry_mid+sign*entry_cost
    exit_fill=df.exit_mid-sign*exit_cost
    multiplier=df.quantity*df.lot_size
    df["gross_before_execution"]=(df.exit_mid-df.entry_mid)*sign*multiplier
    df["execution_cost"]=(entry_cost+exit_cost)*multiplier
    df["gross_after_execution"]=(exit_fill-entry_fill)*sign*multiplier
    df["charges"]=df[COSTS].sum(axis=1)
    df["net_pnl"]=df.gross_after_execution-df.charges
    curve=df.net_pnl.cumsum()
    return {"status":"EVALUATED_EXPLORATORY","input_path":str(path),"trade_count":int(len(df)),"date_min":df.entry_date.min().date().isoformat(),"date_max":df.exit_date.max().date().isoformat(),"gross_pnl_before_execution_costs":float(df.gross_before_execution.sum()),"execution_cost_points_value":float(df.execution_cost.sum()),"explicit_charges":float(df.charges.sum()),"net_pnl":float(df.net_pnl.sum()),"profitable_trade_fraction":float((df.net_pnl>0).mean()),"max_drawdown_on_trade_sequence":float((curve-curve.cummax()).min()),"assumptions":["Prices and charges must use consistent units documented in the source manifest.","Spread and adverse slippage are charged at entry and exit.","Paytm Money charges must be date-effective and source-registered.","Results remain exploratory until contract mapping, settlement and out-of-sample design pass independent review."]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="research/data/phase12_contract_fills.csv")
    p.add_argument("--output",default="research/results/phase12/cost_gate_report.json")
    a=p.parse_args(); report=build_report(Path(a.input))
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
