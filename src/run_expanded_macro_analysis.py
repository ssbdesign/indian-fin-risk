"""Compare existing repo-rate bank models against expanded macro-factor models.

Models use identical complete-case months for valid R-squared comparisons.
Same-month factors are explanatory associations, not forecasts.
"""
from pathlib import Path

import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "analysis_dataset.csv"
OUTPUT = ROOT / "reports" / "results" / "expanded_macro_regressions.csv"
BANKS = ("SBI", "HDFC")
BASE = ["repo_rate_pct", "repo_rate_change_pp", "nifty_return_pct"]
ADDITIONAL = ["india_vix_mean", "usd_inr_change_pct"]
LAGGED = ["india_vix_lag1", "usd_inr_change_pct_lag1"]
TARGET = "monthly_return_pct"


def estimate_models(df: pd.DataFrame) -> pd.DataFrame:
    required = {"ticker", "month_end_date", TARGET, *BASE[:2], *ADDITIONAL, *LAGGED}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing new macro factors: {sorted(missing)}. "
                         "Run download_macro_factors.py and build_analysis_dataset.py first.")
    df = df.copy()
    df["month"] = pd.to_datetime(df["month_end_date"]).dt.to_period("M")
    if df.duplicated(["ticker", "month"]).any():
        raise ValueError("Duplicate ticker-month keys in combined data")
    market = df.loc[df["ticker"].eq("NIFTY50"), ["month", TARGET]].rename(
        columns={TARGET: "nifty_return_pct"}
    )
    if market.empty:
        raise ValueError("NIFTY50 returns required for market-control models")
    output = []
    for ticker in BANKS:
        bank = df.loc[df["ticker"].eq(ticker)].merge(
            market, on="month", how="left", validate="one_to_one"
        ).sort_values("month")
        all_columns = [TARGET, *BASE, *ADDITIONAL, *LAGGED]
        bank[all_columns] = bank[all_columns].apply(pd.to_numeric, errors="coerce")
        bank = bank.dropna(subset=all_columns)
        if len(bank) < 36:
            raise ValueError(f"{ticker}: only {len(bank)} complete months; need at least 36")
        models = {
            "baseline_common_sample": BASE,
            "expanded_same_month": BASE + ADDITIONAL,
            "expanded_lagged": BASE + LAGGED,
        }
        for name, factors in models.items():
            y = bank[TARGET]
            x = sm.add_constant(bank[factors], has_constant="add")
            model = sm.OLS(y, x).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
            for factor in factors:
                interval = model.conf_int().loc[factor]
                output.append({
                    "ticker": ticker, "specification": name,
                    "factor": factor, "observations": int(model.nobs),
                    "coefficient": model.params[factor],
                    "hac_std_error": model.bse[factor],
                    "p_value": model.pvalues[factor],
                    "ci_lower": interval.iloc[0], "ci_upper": interval.iloc[1],
                    "r_squared": model.rsquared, "adjusted_r_squared": model.rsquared_adj,
                    "sample_start": str(bank["month"].iloc[0]),
                    "sample_end": str(bank["month"].iloc[-1]),
                })
    return pd.DataFrame(output)


def main():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)
    results = estimate_models(pd.read_csv(INPUT))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT, index=False)
    print(results.round(4).to_string(index=False))
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
