from pathlib import Path
import pandas as pd

# =====================================================
# 1. PROJECT SETTINGS
# =====================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = ROOT / "data" / "processed" / "validated"
OUTPUT_DIR = ROOT / "data" / "processed"

OUTPUT_FILE = OUTPUT_DIR / "monthly_returns_all.csv"
QUALITY_FILE = OUTPUT_DIR / "monthly_returns_quality_report.txt"

START_MONTH = "2015-01"
END_MONTH = "2025-12"

FILES = {
    "SBI_daily.csv": "SBI",
    "HDFC_daily.csv": "HDFC",
    "NIFTY50_daily.csv": "NIFTY50",
}


# =====================================================
# 2. LOAD AND VALIDATE EACH INPUT
# =====================================================

def load_daily_data(filename, ticker):
    path = INPUT_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")

    df = pd.read_csv(path)

    required = {"date", "close", "ticker"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"{filename} is missing columns: {sorted(missing)}"
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    if df["date"].isna().any():
        raise ValueError(f"{filename} contains invalid dates.")

    if df["close"].isna().any():
        raise ValueError(f"{filename} contains missing closing prices.")

    if (df["close"] <= 0).any():
        raise ValueError(f"{filename} contains non-positive prices.")

    if df["date"].duplicated().any():
        raise ValueError(f"{filename} contains duplicate dates.")

    actual_tickers = df["ticker"].dropna().astype(str).unique()

    if len(actual_tickers) != 1 or actual_tickers[0] != ticker:
        raise ValueError(
            f"{filename}: expected ticker {ticker}, "
            f"found {actual_tickers.tolist()}"
        )

    df = df.sort_values("date").reset_index(drop=True)

    # Retain only the intended research period.
    # We will later download a December 2014 price if needed
    # to calculate January 2015's return.
    df = df[
        (df["date"] >= "2015-01-01")
        & (df["date"] < "2026-01-01")
    ].copy()

    if df.empty:
        raise ValueError(
            f"{filename} has no observations in the study period."
        )

    return df


# =====================================================
# 3. CALCULATE MONTHLY RETURNS
# =====================================================

def calculate_monthly_returns(df, ticker):
    df = df.copy()
    df["month_period"] = df["date"].dt.to_period("M")

    # Last observed trading-day close within each month.
    monthly = (
        df.groupby("month_period")
        .agg(
            month_end_date=("date", "max"),
            month_end_close=("close", "last"),
            trading_days=("date", "count"),
        )
        .reset_index()
        .sort_values("month_period")
        .reset_index(drop=True)
    )

    # Return is valid only when the preceding calendar month
    # is present. Do not calculate across a missing month.
    previous_month = monthly["month_period"].shift(1)

    consecutive_month = (
        monthly["month_period"].astype("int64")
        - previous_month.astype("int64")
        == 1
    )

    raw_return = monthly["month_end_close"].pct_change(
        fill_method=None
    )

    monthly["monthly_return"] = raw_return.where(
        consecutive_month
    )

    monthly["monthly_return_pct"] = (
        monthly["monthly_return"] * 100
    )

    monthly["ticker"] = ticker
    monthly["month"] = monthly["month_period"].astype(str)

    return monthly[
        [
            "month",
            "ticker",
            "month_end_date",
            "month_end_close",
            "trading_days",
            "monthly_return",
            "monthly_return_pct",
        ]
    ]


# =====================================================
# 4. CHECK COVERAGE AND DATA QUALITY
# =====================================================

def create_quality_report(combined):
    expected_months = pd.period_range(
        START_MONTH, END_MONTH, freq="M"
    ).astype(str)

    lines = [
        "MONTHLY MARKET RETURNS: DATA QUALITY REPORT",
        "=" * 55,
        f"Study period: {START_MONTH} to {END_MONTH}",
        f"Expected calendar months per instrument: {len(expected_months)}",
        "",
    ]

    for ticker in ["SBI", "HDFC", "NIFTY50"]:
        data = combined[combined["ticker"] == ticker].copy()

        present = set(data["month"])
        missing_months = [
            month for month in expected_months
            if month not in present
        ]

        missing_returns = int(
            data["monthly_return"].isna().sum()
        )

        valid_returns = data["monthly_return"].dropna()

        lines.extend([
            f"INSTRUMENT: {ticker}",
            f"Monthly rows: {len(data)}",
            f"Missing calendar months: {missing_months}",
            f"Missing monthly returns: {missing_returns}",
        ])

        if not valid_returns.empty:
            lines.extend([
                f"Mean return (%): {valid_returns.mean() * 100:.4f}",
                f"Median return (%): {valid_returns.median() * 100:.4f}",
                f"Standard deviation (%): {valid_returns.std() * 100:.4f}",
                f"Minimum return (%): {valid_returns.min() * 100:.4f}",
                f"Maximum return (%): {valid_returns.max() * 100:.4f}",
            ])

        # Review flags only; do not automatically delete observations.
        flagged = data.loc[
            data["monthly_return"].abs() > 0.25,
            ["month", "monthly_return_pct"],
        ]

        lines.append("Returns outside +/-25%:")

        if flagged.empty:
            lines.append("None")
        else:
            lines.append(flagged.to_string(index=False))

        lines.append("")

    # Check whether all instruments have matching month rows.
    counts = combined.groupby("ticker")["month"].apply(
        lambda values: set(values)
    )

    if len(counts) == 3:
        aligned = (
            counts["SBI"] == counts["HDFC"]
            and counts["SBI"] == counts["NIFTY50"]
        )
        lines.append(f"Instrument month coverage aligned: {aligned}")

    return "\n".join(lines)

print("\nChecking missing return months:")
# =====================================================
# 5. RUN THE PIPELINE

# =====================================================
# 5. RUN THE PIPELINE
# =====================================================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    monthly_results = []

    for filename, ticker in FILES.items():
        print(f"Processing {ticker}...")

        daily = load_daily_data(filename, ticker)
        monthly = calculate_monthly_returns(daily, ticker)

        print("Daily observations:", len(daily))
        print("Monthly rows:", len(monthly))

        monthly_results.append(monthly)

    # Combine SBI, HDFC, and NIFTY50 into one dataset.
    combined = pd.concat(monthly_results, ignore_index=True)

    combined = combined.sort_values(
        ["month", "ticker"]
    ).reset_index(drop=True)

    # Save the monthly dataset.
    combined.to_csv(OUTPUT_FILE, index=False)

    # Generate and save the quality report.
    report = create_quality_report(combined)
    QUALITY_FILE.write_text(report, encoding="utf-8")

    print("\n" + report)

    print("\nSaved monthly dataset:")
    print(OUTPUT_FILE)

    print("\nSaved quality report:")
    print(QUALITY_FILE)

    # Check missing monthly returns for EVERY instrument.
    print("\nCHECKING MISSING RETURN MONTHS")
    print("=" * 40)

    for ticker in ["SBI", "HDFC", "NIFTY50"]:
        rows = combined[
            (combined["ticker"] == ticker)
            & (combined["monthly_return"].isna())
        ]

        print(f"\n{ticker}:")

        if rows.empty:
            print("No missing monthly returns.")
        else:
            print(
                rows[
                    ["month", "month_end_date", "month_end_close"]
                ].to_string(index=False)
            

            )




if __name__ == "__main__":
    main()