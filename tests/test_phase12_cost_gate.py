import tempfile, unittest
from pathlib import Path
import pandas as pd
from scripts.phase12_cost_gate import build_report, REQUIRED

class CostGateTests(unittest.TestCase):
 def row(self):
  return {"trade_id":"T1","entry_date":"2025-01-01","exit_date":"2025-01-02","instrument_type":"FUTURE","side":"LONG","entry_mid":100,"exit_mid":110,"entry_spread_points":2,"exit_spread_points":2,"entry_slippage_points":1,"exit_slippage_points":1,"quantity":1,"lot_size":1,"brokerage":2,"exchange_txn_charge":1,"stt":1,"gst":1,"stamp_duty":1,"sebi_charge":1,"other_charges":0,"cost_schedule_source":"test source","price_source":"test source","fill_method":"test fill model"}
 def test_missing_file_blocks_without_pnl(self):
  with tempfile.TemporaryDirectory() as d: r=build_report(Path(d)/"none.csv")
  self.assertEqual(r["status"],"BLOCKED_MISSING_CONTRACT_LEVEL_DATA"); self.assertIsNone(r["net_pnl"])
 def test_missing_schema_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"x.csv"; pd.DataFrame([{"trade_id":"x"}]).to_csv(p,index=False); r=build_report(p)
  self.assertEqual(r["status"],"BLOCKED_SCHEMA_INVALID"); self.assertIsNone(r["net_pnl"])
 def test_long_fill_cost_arithmetic(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"x.csv"; pd.DataFrame([self.row()],columns=REQUIRED).to_csv(p,index=False); r=build_report(p)
  self.assertEqual(r["status"],"EVALUATED_EXPLORATORY"); self.assertAlmostEqual(r["net_pnl"],-1.0)
 def test_negative_fee_rejected(self):
  row=self.row(); row["brokerage"]=-2
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"x.csv"; pd.DataFrame([row],columns=REQUIRED).to_csv(p,index=False)
   with self.assertRaises(ValueError): build_report(p)
if __name__=="__main__": unittest.main()
