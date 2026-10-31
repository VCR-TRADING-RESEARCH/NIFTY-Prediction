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

    def test_bottom_up_is_weighted_and_point_in_time(self):
        plan = (ROOT / "research" / "constituent_weekly" / "RESEARCH_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("point-in-time free-float weights", plan)
        self.assertIn("cross-stock dependence", plan)
        self.assertIn("Today's membership must never be applied", plan)
        self.assertIn("weighted breadth", plan)

    def test_plan_separates_prediction_and_trading_gates(self):
        plan = (ROOT / "research" / "constituent_weekly" / "RESEARCH_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("Forecast quality is not trading P&L", plan)
        self.assertIn("Paytm Money", plan)
        self.assertIn("Stop at C1", plan)

if __name__ == "__main__":
    unittest.main()
