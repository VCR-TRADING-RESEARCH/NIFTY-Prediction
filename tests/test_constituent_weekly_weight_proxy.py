import math
import unittest

from scripts.constituent_weekly.weight_proxy import (
    compare_weight_vectors,
    drift_weights,
    normalize_equity_weights,
)


class WeightProxyTests(unittest.TestCase):
    def test_equity_normalization(self):
        # Cash is excluded by caller; these are the two equity rows only.
        result = normalize_equity_weights({"AAA": 49.96, "BBB": 49.96})
        self.assertAlmostEqual(sum(result.values()), 1.0)
        self.assertAlmostEqual(result["AAA"], 0.5)

    def test_fixed_share_price_drift(self):
        result = drift_weights({"AAA": 0.6, "BBB": 0.4}, {"AAA": 1.1, "BBB": 0.9})
        self.assertAlmostEqual(result["AAA"], 0.66 / 1.02)
        self.assertAlmostEqual(result["BBB"], 0.36 / 1.02)
        self.assertAlmostEqual(sum(result.values()), 1.0)

    def test_common_price_scale_does_not_change_weights(self):
        a = drift_weights({"AAA": 0.7, "BBB": 0.3}, {"AAA": 1.2, "BBB": 0.8})
        b = drift_weights({"AAA": 0.7, "BBB": 0.3}, {"AAA": 12.0, "BBB": 8.0})
        self.assertAlmostEqual(a["AAA"], b["AAA"])

    def test_identical_vectors_have_zero_error(self):
        x = {"AAA": 60.0, "BBB": 40.0}
        result = compare_weight_vectors(x, x)
        self.assertEqual(result["n"], 2)
        self.assertAlmostEqual(result["mae_fraction"], 0.0)
        self.assertAlmostEqual(result["rmse_fraction"], 0.0)
        self.assertAlmostEqual(result["pearson_r"], 1.0)

    def test_symbol_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            drift_weights({"AAA": 0.6, "BBB": 0.4}, {"AAA": 1.0, "CCC": 1.0})

    def test_non_positive_price_relative_rejected(self):
        with self.assertRaises(ValueError):
            drift_weights({"AAA": 1.0}, {"AAA": 0.0})

    def test_negative_and_non_finite_weights_rejected(self):
        for bad in (-1.0, float("nan"), float("inf")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                normalize_equity_weights({"AAA": bad})

    def test_zero_weight_total_rejected(self):
        with self.assertRaises(ValueError):
            normalize_equity_weights({"AAA": 0.0, "BBB": 0.0})


if __name__ == "__main__":
    unittest.main()
