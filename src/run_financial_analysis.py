from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm


# ============================================================
# PROJECT PATHS AND CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "reports" / "results"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

DATA_PATH = PROCESSED_DIR / "analysis_dataset.csv"

TARGET = "monthly_return_pct"

FACTORS = [
    "repo_rate_pct",
    "repo_rate_change_pp",
]

TICKERS = ["SBI", "HDFC", "NIFTY50"]
BANK_TICKERS = ["SBI", "HDFC"]


# ============================================================
# LOAD EXISTING COMBINED DATASET
# ============================================================

def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Combined dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    df["month_end_date"] = pd.to_datetime(
        df["month_end_date"], errors="coerce"
    )

    required = {
        "ticker",
        "month_end_date",
        TARGET,
        *FACTORS,
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    for column in [TARGET, *FACTORS]:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    return df.sort_values(
        ["ticker", "month_end_date"]
    ).copy()


# ============================================================
# 1. DESCRIPTIVE STATISTICS
# ============================================================

def descriptive_statistics(df):
    stats = (
        df.groupby("ticker")[TARGET]
        .agg(
            observations="count",
            mean_return_pct="mean",
            median_return_pct="median",
            volatility_pct="std",
            best_month_pct="max",
            worst_month_pct="min",
        )
        .reset_index()
    )

    stats.to_csv(
        RESULTS_DIR / "return_descriptive_statistics.csv",
        index=False,
    )

    print("\nMONTHLY RETURN STATISTICS")
    print(stats.round(4).to_string(index=False))


# ============================================================
# 2. CORRELATIONS AND SCATTER PLOTS
# ============================================================

def factor_relationships(df):
    correlations = []

    for ticker in TICKERS:
        group = df[df["ticker"] == ticker]

        for factor in FACTORS:
            sample = group[[TARGET, factor]].dropna()

            if len(sample) < 3:
                continue

            correlations.append({
                "ticker": ticker,
                "factor": factor,
                "observations": len(sample),
                "pearson_correlation": sample[TARGET].corr(
                    sample[factor]
                ),
            })

            fig, ax = plt.subplots(figsize=(7, 5))

            ax.scatter(
                sample[factor],
                sample[TARGET],
                alpha=0.7,
            )

            ax.axhline(0, linewidth=0.8)
            ax.set_xlabel(factor)
            ax.set_ylabel("Monthly return (%)")
            ax.set_title(f"{ticker}: return vs {factor}")
            ax.grid(alpha=0.25)

            fig.tight_layout()

            fig.savefig(
                FIGURES_DIR
                / f"{ticker}_vs_{factor}.png",
                dpi=300,
            )

            plt.close(fig)

    corr_df = pd.DataFrame(correlations)

    corr_df.to_csv(
        RESULTS_DIR / "factor_correlations.csv",
        index=False,
    )

    print("\nFACTOR CORRELATIONS")

    if corr_df.empty:
        print("No correlations could be calculated.")
    else:
        print(corr_df.round(4).to_string(index=False))


# ============================================================
# 3. SINGLE-FACTOR REGRESSIONS
# ============================================================

def run_regressions(df):
    results = []

    for ticker in TICKERS:
        group = df[df["ticker"] == ticker]

        for factor in FACTORS:
            sample = group[[TARGET, factor]].dropna()

            if len(sample) < 24:
                print(
                    f"Skipping {ticker} / {factor}: "
                    "fewer than 24 observations."
                )
                continue

            y = sample[TARGET]

            X = sm.add_constant(
                sample[[factor]]
            )

            model = sm.OLS(y, X).fit(
                cov_type="HAC",
                cov_kwds={"maxlags": 3},
            )

            ci = model.conf_int().loc[factor]

            results.append({
                "ticker": ticker,
                "factor": factor,
                "observations": int(model.nobs),
                "coefficient": model.params[factor],
                "hac_std_error": model.bse[factor],
                "p_value": model.pvalues[factor],
                "ci_lower": ci.iloc[0],
                "ci_upper": ci.iloc[1],
                "r_squared": model.rsquared,
            })

    result_df = pd.DataFrame(results)

    result_df.to_csv(
        RESULTS_DIR / "single_factor_regressions.csv",
        index=False,
    )

    print("\nSINGLE-FACTOR REGRESSION RESULTS")

    if result_df.empty:
        print("No single-factor regressions could be estimated.")
    else:
        print(result_df.round(4).to_string(index=False))


# ============================================================
# 4. MARKET-CONTROLLED REGRESSIONS
#
# Dependent variable:
#   Bank monthly return
#
# Explanatory variables:
#   Repo-rate level
#   Monthly repo-rate change
#   NIFTY 50 monthly return
#
# NIFTY 50 is used as a control for bank regressions only.
# ============================================================

def run_market_controlled_regressions(df):
    results = []

    # Keep one NIFTY 50 return per calendar month.
    market = (
        df.loc[
            df["ticker"] == "NIFTY50",
            ["month_end_date", TARGET],
        ]
        .rename(
            columns={
                TARGET: "nifty_return_pct",
            }
        )
    )

    # Match on calendar month, not the exact trading date.
    market["month_key"] = (
        market["month_end_date"].dt.to_period("M")
    )

    market = market[
        ["month_key", "nifty_return_pct"]
    ]

    for ticker in BANK_TICKERS:
        bank = df[df["ticker"] == ticker].copy()

        bank["month_key"] = (
            bank["month_end_date"].dt.to_period("M")
        )

        sample = bank.merge(
            market,
            on="month_key",
            how="left",
            validate="one_to_one",
        )

        required_columns = [
            TARGET,
            "repo_rate_pct",
            "repo_rate_change_pp",
            "nifty_return_pct",
        ]

        for column in required_columns:
            sample[column] = pd.to_numeric(
                sample[column], errors="coerce"
            )

        sample = sample.dropna(
            subset=required_columns
        )

        if len(sample) < 24:
            print(
                f"Skipping controlled regression for {ticker}: "
                "fewer than 24 complete observations."
            )
            continue

        y = sample[TARGET]

        X = sample[
            [
                "repo_rate_pct",
                "repo_rate_change_pp",
                "nifty_return_pct",
            ]
        ]

        X = sm.add_constant(X)

        model = sm.OLS(y, X).fit(
            cov_type="HAC",
            cov_kwds={"maxlags": 3},
        )

        print(
            f"\n{ticker}: MARKET-CONTROLLED REGRESSION"
        )
        print(model.summary())

        # Save coefficient-level results.
        for factor in [
            "repo_rate_pct",
            "repo_rate_change_pp",
            "nifty_return_pct",
        ]:
            ci = model.conf_int().loc[factor]

            results.append({
                "ticker": ticker,
                "factor": factor,
                "observations": int(model.nobs),
                "coefficient": model.params[factor],
                "hac_std_error": model.bse[factor],
                "p_value": model.pvalues[factor],
                "ci_lower": ci.iloc[0],
                "ci_upper": ci.iloc[1],
                "r_squared": model.rsquared,
            })

    result_df = pd.DataFrame(results)

    output_path = (
        RESULTS_DIR / "market_controlled_regressions.csv"
    )

    result_df.to_csv(output_path, index=False)

    print("\nMARKET-CONTROLLED REGRESSION RESULTS")

    if result_df.empty:
        print("No controlled regressions could be estimated.")
    else:
        print(result_df.round(4).to_string(index=False))

    print(f"\nSaved controlled results to:\n{output_path}")
def run_timing_sensitivity_analysis(df):
    """Compare same-month and one-month-lagged repo-rate changes."""

    results = []
    bank_tickers = ["SBI", "HDFC"]
    target = "monthly_return_pct"

    # Prepare NIFTY 50 returns as the market control.
    market = df.loc[
        df["ticker"] == "NIFTY50",
        ["month_end_date", target],
    ].copy()

    market["month_key"] = (
        pd.to_datetime(market["month_end_date"])
        .dt.to_period("M")
    )

    market = market[
        ["month_key", target]
    ].rename(columns={target: "nifty_return_pct"})

    for ticker in bank_tickers:
        bank = df.loc[df["ticker"] == ticker].copy()

        bank["month_key"] = (
            pd.to_datetime(bank["month_end_date"])
            .dt.to_period("M")
        )

        bank = bank.sort_values("month_key")

        # Shift the rate-change variable by one calendar month.
        bank["repo_rate_change_lag1"] = (
            bank["repo_rate_change_pp"].shift(1)
        )

        sample = bank.merge(
            market,
            on="month_key",
            how="left",
            validate="one_to_one",
        )

        specifications = {
            "same_month": "repo_rate_change_pp",
            "one_month_lag": "repo_rate_change_lag1",
        }

        for timing, change_column in specifications.items():
            required = [
                target,
                "repo_rate_pct",
                change_column,
                "nifty_return_pct",
            ]

            model_data = sample[required].apply(
                pd.to_numeric,
                errors="coerce",
            ).dropna()

            if len(model_data) < 24:
                print(
                    f"Skipping {ticker} {timing}: "
                    "not enough observations."
                )
                continue

            y = model_data[target]

            X = model_data[
                ["repo_rate_pct", change_column, "nifty_return_pct"]
            ].copy()

            X = X.rename(
                columns={change_column: "repo_rate_change"}
            )

            X = sm.add_constant(X)

            model = sm.OLS(y, X).fit(
                cov_type="HAC",
                cov_kwds={"maxlags": 3},
            )

            for factor in [
                "repo_rate_pct",
                "repo_rate_change",
                "nifty_return_pct",
            ]:
                results.append({
                    "ticker": ticker,
                    "timing": timing,
                    "factor": factor,
                    "observations": int(model.nobs),
                    "coefficient": model.params[factor],
                    "hac_std_error": model.bse[factor],
                    "p_value": model.pvalues[factor],
                    "ci_lower": model.conf_int().loc[factor, 0],
                    "ci_upper": model.conf_int().loc[factor, 1],
                    "r_squared": model.rsquared,
                })

            print(f"\n{ticker}: {timing.upper()} MODEL")
            print(model.summary())

    output = pd.DataFrame(results)

    output_path = RESULTS_DIR / "timing_sensitivity_results.csv"
    output.to_csv(output_path, index=False)

    print("\nTIMING SENSITIVITY RESULTS")
    print(output.to_string(index=False))
    print(f"\nSaved to: {output_path}")
# ============================================================
# MAIN
# ============================================================

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()

    print("FINANCIAL ANALYSIS")
    print("=" * 60)
    print(f"Rows loaded: {len(df)}")
    print(f"Tickers: {sorted(df['ticker'].dropna().unique())}")

    descriptive_statistics(df)
    factor_relationships(df)
    run_regressions(df)
    run_market_controlled_regressions(df)
    run_timing_sensitivity_analysis(df)
    print("\nAnalysis complete.")
    print(f"Results saved to: {RESULTS_DIR}")
    print(f"Figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()