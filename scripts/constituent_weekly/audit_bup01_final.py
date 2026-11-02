#!/usr/bin/env python3
"""Independent arithmetic and gate audit for the sanitised BUP-01 closeout."""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "research" / "constituent_weekly"

def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return math.isfinite(a) and abs(a - b) <= tol

def main() -> None:
    d = json.loads((R / "C6_RESULTS_SUMMARY.json").read_text())
    c2, c3, x = d["c2"], d["c3"], d["c3x"]

    assert c2["status"] == "SUCCESS"
    assert c2["cycles"] == c2["valid_index_targets"] == 258
    assert c2["constituent_cycle_rows"] == 12807
    assert c2["duplicate_stock_cycle_keys"] == c2["duplicate_index_cycle_keys"] == 0

    assert c3["status"] == "SUCCESS" and c3["attempt"] == 2
    assert c3["development_rows"] + c3["holdout_rows"] == c3["total_oof_rows"] == 7512
    assert c3["development_cycles"] + c3["holdout_cycles"] == c3["forecast_cycles"] == 154
    assert c3["holdout_cycles"] == 52
    assert c3["holdout_rows"] == 2583
    assert c3["models"]["logistic"]["accuracy"] < c3["models"]["momentum"]["accuracy"]
    assert c3["models"]["extra_trees"]["accuracy"] < c3["models"]["momentum"]["accuracy"]
    assert c3["models"]["hist_gradient_boosting"]["accuracy"] < c3["models"]["momentum"]["accuracy"]

    diff = c3["logistic_minus_momentum_cycle_accuracy"]
    cm = c3["cycle_macro"]["holdout"]
    recomputed = cm["logistic_accuracy"] - cm["momentum_accuracy"]
    assert close(recomputed, diff["mean"])
    assert diff["ci95"][0] < 0 < diff["ci95"][1]
    assert c3["development_positive_rate"] > c3["holdout_positive_rate"]

    assert x["nifty_meta_holdout_cycles"] == 51
    assert len(x["meta"]["confusion_tn_fp_fn_tp"]) == 4
    tn, fp, fn, tp = x["meta"]["confusion_tn_fp_fn_tp"]
    acc = (tn + tp) / (tn + fp + fn + tp)
    bal = ((tp / (tp + fn)) + (tn / (tn + fp))) / 2
    assert close(acc, x["meta"]["accuracy"])
    assert close(bal, x["meta"]["balanced_accuracy"])
    assert close((tn + tp) - 25, 1.0)  # exactly one additional correct cycle vs the 25/51 lag baseline
    assert close(x["meta_minus_lag_accuracy"]["mean"], 1 / 51)
    assert x["meta_minus_lag_accuracy"]["ci95"][0] < 0 < x["meta_minus_lag_accuracy"]["ci95"][1]
    assert x["meta"]["roc_auc"] < 0.5

    c5 = json.loads((R / "C5_STATUS.json").read_text())
    assert c5["status"] == "BLOCKED_NOT_RUN"
    assert c5["trading_strategy_accepted"] is False
    assert d["gates"]["c1"] == "PARTIAL"
    assert d["gates"]["c4_confirmatory"] == "GATED"
    assert d["gates"]["trading_strategy"] == "NOT_VALIDATED"

    print("C6_AUDIT_PASS_WITH_LIMITATIONS")
    print("C2 sample accounting, C3 sample split and paired-difference arithmetic passed.")
    print("C3-X NIFTY confusion-matrix accuracy/balanced-accuracy checks passed.")
    print("Both paired bootstrap intervals include zero; C1/C4/C5/trading gates remain correctly restricted.")

if __name__ == "__main__":
    main()
