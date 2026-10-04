from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "data" / "processed" / "validated"
OUTPUT_DIR = ROOT / "data" / "processed"

OUTPUT_FILE = OUTPUT_DIR / "monthly_returns_all.csv"
QUALITY_FILE = OUTPUT_DIR / "monthly_returns_quality_report.txt"

START_MONTH = "2010-01"
END_MONTH = "2025-12"

FILES = {
    "SBI_daily.csv": "SBIN.NS",
    "HDFC_daily.csv": "HDFCBANK.NS",
    "ICICI_daily.csv": "ICICIBANK.NS",
    "AXIS_daily.csv": "AXISBANK.NS",
    "NIFTY50_daily.csv": "^NSEI",
}

START_DATE = pd.Timestamp("2010-01-01")
END_DATE = pd.Timestamp("2026-01-01")


def load_daily_data(filename, ticker):
    path = INPUT_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing validated file: {path}\n"
            "Download the new instruments and validate them first."
        )

    df = pd.read_csv(path)

    required = {"date", "close", "ticker"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{filename} is missing columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    if df["date"].isna().any():
        raise ValueError(f"{filename} contains invalid dates.")
    if df["close"].isna().any() or (df["close"] <= 0).any():
        raise ValueError(f"{filename} contains invalid closing prices.")
    if df["date"].duplicated().any():
        raise ValueError(f"{filename} contains duplicate dates.")

    actual = df["ticker"].dropna().astype(str).unique()
    if len(actual) != 1 or actual[0] != ticker:
        raise ValueError(
            f"{filename}: expected ticker label {ticker}, "
            f"found {actual.tolist()}"
        )

    df = df.sort_values("date").reset_index(drop=True)

    # Keep December 2009 as a possible baseline for January 2010.
    df = df[
        (df["date"] >= pd.Timestamp("2009-12-01"))
        & (df["date"] < END_DATE)
    ].copy()

    if df.empty:
        raise ValueError(f"{filename} has no data in the required date range.")

    return df


def calculate_monthly_returns(df, ticker):
    df = df.copy()
    df["month_period"] = df["date"].dt.to_period("M")

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

    previous_month = monthly["month_period"].shift(1)
    consecutive = (
        monthly["month_period"].astype("int64")
        - previous_month.astype("int64")
        == 1
    )

    monthly["monthly_return"] = monthly[
        "month_end_close"
    ].pct_change(fill_method=None).where(consecutive)

    monthly["monthly_return_pct"] = monthly["monthly_return"] * 100
    monthly["ticker"] = ticker
    monthly["month"] = monthly["month_period"].astype(str)

    monthly = monthly[
        (monthly["month"] >= START_MONTH)
        & (monthly["month"] <= END_MONTH)
    ]

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
    ].copy()


def create_quality_report(combined):
    expected = set(
        pd.period_range(START_MONTH, END_MONTH, freq="M").astype(str)
    )

    lines = [
        "MONTHLY MARKET RETURNS: DATA QUALITY REPORT",
        "=" * 60,
        f"Study period: {START_MONTH} to {END_MONTH}",
        f"Expected months per instrument: {len(expected)}",
        "",
    ]

    for ticker in FILES.values():
        data = combined[combined["ticker"] == ticker].copy()
        present = set(data["month"])
        missing = sorted(expected - present)
        missing_returns = int(data["monthly_return"].isna().sum())
        valid = data["monthly_return"].dropna()

        lines.extend([
            f"INSTRUMENT: {ticker}",
            f"Monthly rows: {len(data)}",
            f"Missing calendar months: {missing}",
            f"Missing monthly returns: {missing_returns}",
        ])

        if not valid.empty:
            lines.extend([
                f"Mean return (%): {valid.mean() * 100:.4f}",
                f"Median return (%): {valid.median() * 100:.4f}",
                f"Standard deviation (%): {valid.std() * 100:.4f}",
                f"Minimum return (%): {valid.min() * 100:.4f}",
                f"Maximum return (%): {valid.max() * 100:.4f}",
            ])

        flagged = data.loc[
            data["monthly_return"].abs() > 0.25,
            ["month", "monthly_return_pct"],
        ]

        lines.append("Returns outside +/-25%:")
        lines.append("None" if flagged.empty else flagged.to_string(index=False))
        lines.append("")

    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    monthly_results = []

    for filename, ticker in FILES.items():
        print(f"Processing {ticker}...")
        daily = load_daily_data(filename, ticker)
        monthly = calculate_monthly_returns(daily, ticker)

        print(f"Daily rows in loaded range: {len(daily)}")
        print(f"Monthly rows in study period: {len(monthly)}")
        monthly_results.append(monthly)

    combined = pd.concat(monthly_results, ignore_index=True)
    combined = combined.sort_values(["month", "ticker"]).reset_index(drop=True)

    combined.to_csv(OUTPUT_FILE, index=False)
    report = create_quality_report(combined)
    QUALITY_FILE.write_text(report, encoding="utf-8")

    print("\n" + report)
    print(f"\nSaved monthly dataset: {OUTPUT_FILE}")
    print(f"Saved quality report: {QUALITY_FILE}")


if __name__ == "__main__":
    main()