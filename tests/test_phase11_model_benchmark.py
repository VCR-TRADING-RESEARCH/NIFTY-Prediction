import json
import pandas as pd
from scripts.benchmark_model_families import FEATURES, MIN_HISTORY, run_benchmark

def test_benchmark_is_reproducible_and_reports_exploratory_status(tmp_path):
    rows=[]
    dates=pd.date_range("2023-01-01",periods=MIN_HISTORY+4,freq="7D")
    for i,date in enumerate(dates):
        row={"expiry_date":date.date().isoformat(),"label":"UP" if i%3 else "DOWN","source_gate_pass":True}
        row.update({f:((i+j)%11)/100 for j,f in enumerate(FEATURES)})
        rows.append(row)
    path=tmp_path/"input.csv"; pd.DataFrame(rows).to_csv(path,index=False); out=tmp_path/"out"
    run_benchmark(path,out); a=pd.read_csv(out/"predictions_expanding_window.csv")
    run_benchmark(path,out); b=pd.read_csv(out/"predictions_expanding_window.csv")
    pd.testing.assert_frame_equal(a,b)
    assert set(["logistic","extra_trees","random_forest","gradient_boosting","hist_gradient_boosting","rbf_svc"]).issubset(set(a.candidate))
    assert len(a[a.candidate=="logistic"])==4
    summary=json.loads((out/"summary.json").read_text())
    assert summary["status"]=="EXPLORATORY_ONLY_NOT_CONFIRMATORY"
    assert summary["trading_strategy_validated"] is False
    assert len(summary["paired_four_week_block_bootstrap"]) == 2
    assert all(item["status"] in {"COMPLETED", "UNDERPOWERED"} for item in summary["paired_four_week_block_bootstrap"])
