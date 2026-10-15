"""Tests for macro factor processing with synthetic daily data (no API calls)."""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from download_macro_factors import monthly_factors


class MacroFactorTests(unittest.TestCase):
    @staticmethod
    def daily():
        months = pd.period_range("2014-12", "2025-12", freq="M")
        dates = [m.to_timestamp() for m in months]
        return pd.DataFrame({"date": dates, "close": [20.0 + i for i in range(len(dates))]})

    def test_vix_complete_period(self):
        result = monthly_factors(self.daily(), "india_vix")
        self.assertEqual(len(result), 132)
        self.assertEqual(result.iloc[0]["india_vix_lag1"], 20.0)

    def test_fx_returns(self):
        result = monthly_factors(self.daily(), "usd_inr")
        self.assertAlmostEqual(result.iloc[0]["usd_inr_change_pct"], 5.0)
        self.assertTrue(pd.isna(result.iloc[0]["usd_inr_change_pct_lag1"]))

    def test_missing_month_rejected(self):
        daily = self.daily()
        daily = daily.loc[daily["date"].dt.strftime("%Y-%m") != "2020-03"]
        with self.assertRaisesRegex(ValueError, "missing study months"):
            monthly_factors(daily, "india_vix")


if __name__ == "__main__":
    unittest.main()
