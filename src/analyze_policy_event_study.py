from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "reports" / "results" / "effective_date_event_study.csv"
OUTPUT_DIR = ROOT / "reports" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALPHA = 0.05
BANKS = ["SBI", "HDFC", "ICICI", "AXIS"]
TICKERS = BANKS + ["NIFTY50"]

WINDOWS = {
    "Event day": "day0_return_pct",
    "3-day window": "window_m1_p1_pct",
    "11-day window": "window_m5_p5_pct",
}


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Run run_policy_event_study.py first: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    required = [
        "effective_date",
        "repo_rate_pct",
        "repo_rate_change_pp",
    ]

    for ticker in TICKERS:
        for suffix in WINDOWS.values():
            required.append(f"{ticker}_{suffix}")

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in event-study data: {missing}")

    df["effective_date"] = pd.to_datetime(
        df["effective_date"], errors="coerce"
    )

    for column in required:
        if column != "effective_date":
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df = (
        df.dropna(subset=["effective_date"])
        .sort_values("effective_date")
        .reset_index(drop=True)
    )

    df["policy_direction"] = np.select(
        [
            df["repo_rate_change_pp"] > 0,
            df["repo_rate_change_pp"] < 0,
        ],
        ["Hike", "Cut"],
        default="No change",
    )

    print("=" * 65)
    print("RBI REPO-RATE EFFECTIVE-DATE EVENT STUDY")
    print("=" * 65)
    print(f"Events: {len(df)}")
    if not df.empty:
        print(
            f"Period: {df['effective_date'].min().date()} to "
            f"{df['effective_date'].max().date()}"
        )
    print("\nPolicy directions:")
    print(df["policy_direction"].value_counts())

    # 1. Descriptive statistics and tests against zero.
    summary_rows = []

    for ticker in TICKERS:
        for window_name, suffix in WINDOWS.items():
            column = f"{ticker}_{suffix}"
            values = df[column].dropna()

            if len(values) < 2:
                continue

            test = stats.ttest_1samp(values, popmean=0)

            summary_rows.append({
                "ticker": ticker,
                "window": window_name,
                "n": len(values),
                "mean_pct": values.mean(),
                "median_pct": values.median(),
                "std_pct": values.std(ddof=1),
                "min_pct": values.min(),
                "max_pct": values.max(),
                "t_statistic": test.statistic,
                "p_value": test.pvalue,
            })

    summary = pd.DataFrame(summary_rows)
    if not summary.empty:
        summary["significant_at_5pct"] = summary["p_value"] < ALPHA

    summary.to_csv(
        OUTPUT_DIR / "policy_event_descriptive_tests.csv", index=False
    )

    print("\nMean returns and tests against zero:")
    if not summary.empty:
        print(summary.round(4).to_string(index=False))

    # 2. Bank return minus NIFTY 50 return.
    relative_rows = []

    for ticker in BANKS:
        for window_name, suffix in WINDOWS.items():
            stock_col = f"{ticker}_{suffix}"
            market_col = f"NIFTY50_{suffix}"

            pair = df[[stock_col, market_col]].dropna()
            difference = pair[stock_col] - pair[market_col]

            if len(difference) < 2:
                continue

            test = stats.ttest_1samp(difference, popmean=0)

            relative_rows.append({
                "ticker": ticker,
                "window": window_name,
                "n": len(difference),
                "mean_relative_return_pp": difference.mean(),
                "median_relative_return_pp": difference.median(),
                "std_relative_return_pp": difference.std(ddof=1),
                "t_statistic": test.statistic,
                "p_value": test.pvalue,
            })

    relative = pd.DataFrame(relative_rows)
    if not relative.empty:
        relative["significant_at_5pct"] = relative["p_value"] < ALPHA

    relative.to_csv(
        OUTPUT_DIR / "policy_event_market_comparison.csv", index=False
    )

    print("\nBank returns minus NIFTY 50:")
    if not relative.empty:
        print(relative.round(4).to_string(index=False))

    # 3. Rate hikes versus cuts.
    direction_rows = []

    for ticker in TICKERS:
        for window_name, suffix in WINDOWS.items():
            column = f"{ticker}_{suffix}"

            hikes = df.loc[df["policy_direction"] == "Hike", column].dropna()
            cuts = df.loc[df["policy_direction"] == "Cut", column].dropna()

            if len(hikes) < 2 or len(cuts) < 2:
                continue

            test = stats.ttest_ind(hikes, cuts, equal_var=False)

            direction_rows.append({
                "ticker": ticker,
                "window": window_name,
                "n_hikes": len(hikes),
                "n_cuts": len(cuts),
                "mean_hike_return_pct": hikes.mean(),
                "mean_cut_return_pct": cuts.mean(),
                "hike_minus_cut_pp": hikes.mean() - cuts.mean(),
                "welch_t_statistic": test.statistic,
                "p_value": test.pvalue,
            })

    direction = pd.DataFrame(direction_rows)
    if not direction.empty:
        direction["significant_at_5pct"] = direction["p_value"] < ALPHA

    direction.to_csv(
        OUTPUT_DIR / "policy_event_hikes_vs_cuts.csv", index=False
    )

    print("\nHikes versus cuts:")
    if not direction.empty:
        print(direction.round(4).to_string(index=False))

    # 4. Largest and smallest observed event-window returns.
    extreme_rows = []

    for ticker in TICKERS:
        for window_name, suffix in WINDOWS.items():
            column = f"{ticker}_{suffix}"
            valid = df[["effective_date", column]].dropna()

            if valid.empty:
                continue

            for label, idx in [
                ("Largest return", valid[column].idxmax()),
                ("Smallest return", valid[column].idxmin()),
            ]:
                row = df.loc[idx]

                extreme_rows.append({
                    "ticker": ticker,
                    "window": window_name,
                    "extreme": label,
                    "effective_date": row["effective_date"].date(),
                    "return_pct": row[column],
                    "repo_rate_change_pp": row["repo_rate_change_pp"],
                    "policy_direction": row["policy_direction"],
                })

    extremes = pd.DataFrame(extreme_rows)
    extremes.to_csv(
        OUTPUT_DIR / "policy_event_extreme_events.csv", index=False
    )

    # 5. Event-level bank-minus-market comparison table.
    event_output = df.copy()

    for ticker in BANKS:
        for suffix in WINDOWS.values():
            stock_col = f"{ticker}_{suffix}"
            market_col = f"NIFTY50_{suffix}"

            event_output[f"{ticker}_minus_NIFTY50_{suffix}"] = (
                event_output[stock_col] - event_output[market_col]
            )

    event_output.to_csv(
        OUTPUT_DIR / "policy_event_analysis_table.csv", index=False
    )

    print("\nAnalysis complete. Results saved in:")
    for name in [
        "policy_event_descriptive_tests.csv",
        "policy_event_market_comparison.csv",
        "policy_event_hikes_vs_cuts.csv",
        "policy_event_extreme_events.csv",
        "policy_event_analysis_table.csv",
    ]:
        print(f" - {OUTPUT_DIR / name}")

    print(
        "\nCaution: these are raw-return analyses around effective dates, "
        "not verified announcement-date abnormal returns. Results do not "
        "establish causation. Multiple tests also increase the chance "
        "of false-positive findings."
    )


if __name__ == "__main__":
    main()