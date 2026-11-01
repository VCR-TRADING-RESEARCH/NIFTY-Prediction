from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ConstituentWeeklyPlanTests(unittest.TestCase):
    def test_plan_validator_passes(self):
        script = ROOT / "scripts" / "constituent_weekly" / "validate_plan.py"
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("C0 registration structure: PASS", result.stdout)

    def test_bottom_up_is_point_in_time_and_uses_out_of_fold_signals(self):
        plan = (ROOT / "research" / "constituent_weekly" / "RESEARCH_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("point-in-time tradable NIFTY 50 constituent membership", plan)
        self.assertIn("cross-stock dependence", plan)
        self.assertIn("Today's membership must never be applied", plan)
        self.assertIn("unweighted cross-sectional forecast-signal aggregator", plan)
        self.assertIn("strictly out of fold", plan)
        self.assertIn("valid_count / point-in-time tradable member count", plan)


    def test_versioned_expiry_proxy_amendment_matches_version_history(self):
        plan = (ROOT / "research" / "constituent_weekly" / "RESEARCH_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("**Plan version:** 1.3", plan)
        self.assertIn("- **v1.1 — 2026-11-01:**", plan)
        self.assertIn("- **v1.2 — 2026-11-01:**", plan)
        self.assertIn("- **v1.3 — 2026-11-01:**", plan)
        self.assertIn("No comparison needed", plan)
        self.assertIn("actual NIFTY 50 index return remains the observed target", plan)
        self.assertIn("15:00 through 15:14 IST", plan)
        self.assertIn("15:15 expiry proxy", plan)
        self.assertIn("official 15:30 close", plan)

    def test_plan_separates_prediction_and_trading_gates(self):
        plan = (ROOT / "research" / "constituent_weekly" / "RESEARCH_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("Forecast quality is not trading P&L", plan)
        self.assertIn("Paytm Money", plan)
        self.assertIn("Stop C1 if point-in-time membership/security identity", plan)
        self.assertIn("exploratory gate", plan)

    def test_equal_weight_diagnostics_are_not_called_nifty_return(self):
        plan = (ROOT / "research" / "constituent_weekly" / "RESEARCH_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("must never be called the NIFTY 50 index return", plan)
        self.assertIn("Every per-stock forecast that enters a cycle summary must be generated out of fold", plan)
        self.assertNotIn("w[i,t] * muhat[i,t]", plan)

if __name__ == "__main__":
    unittest.main()
