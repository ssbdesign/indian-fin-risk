from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"
DAILY_DIR = DATA_DIR / "validated"
EVENT_FILE = DATA_DIR / "rbi_policy_events_2015_2025.csv"
OUTPUT_DIR = ROOT / "reports" / "results"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TICKERS = ["SBI", "HDFC", "ICICI", "AXIS", "NIFTY50"]
EVENT_START = "2015-01-01"
EVENT_END = "2025-12-31"


def load_daily_stock(ticker):
    path = DAILY_DIR / f"{ticker}_daily.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Missing validated daily file: {path}"
        )

    df = pd.read_csv(path, parse_dates=["date"])

    required = {"date", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path.name} is missing columns: {missing}")

    df = df[["date", "close"]].copy()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["date", "close"])
    df = df.sort_values("date")

    if df["date"].duplicated().any():
        raise ValueError(f"{path.name} contains duplicate dates.")

    df = df.rename(columns={"close": f"{ticker}_close"})
    df[f"{ticker}_return_pct"] = (
        df[f"{ticker}_close"].pct_change(fill_method=None) * 100
    )

    return df


def main():
    if not EVENT_FILE.exists():
        raise FileNotFoundError(f"Missing RBI event file: {EVENT_FILE}")

    events = pd.read_csv(EVENT_FILE, parse_dates=["effective_date"])
    events = events.loc[
        events["effective_date"].between(EVENT_START, EVENT_END)
    ].copy()

    required_event_cols = {
        "effective_date",
        "repo_rate_pct",
        "repo_rate_change_pp",
    }
    missing = required_event_cols - set(events.columns)
    if missing:
        raise ValueError(f"RBI event file is missing columns: {missing}")

    daily_data = {ticker: load_daily_stock(ticker) for ticker in TICKERS}

    for ticker, df in daily_data.items():
        print(
            f"{ticker}: {df['date'].min().date()} to "
            f"{df['date'].max().date()}, {len(df)} rows"
        )

    print(f"\nRBI effective-date events: {len(events)}")

    # Diagnostics: is each effective date a trading day?
    diagnostic = events[
        ["effective_date", "repo_rate_pct", "repo_rate_change_pp"]
    ].copy()

    for ticker, df in daily_data.items():
        diagnostic[f"{ticker}_exact_trading_day"] = diagnostic[
            "effective_date"
        ].isin(pd.Index(df["date"]))

    diagnostic.to_csv(
        OUTPUT_DIR / "policy_event_date_diagnostic.csv",
        index=False,
    )

    print("\nExact event-date trading-day matches:")
    for ticker in TICKERS:
        column = f"{ticker}_exact_trading_day"
        print(f"{ticker}: {diagnostic[column].sum()} / {len(diagnostic)}")

    # Inner join to a shared trading calendar.
    daily = daily_data[TICKERS[0]]
    for ticker in TICKERS[1:]:
        daily = daily.merge(daily_data[ticker], on="date", how="inner")

    daily = daily.sort_values("date").reset_index(drop=True)
    daily["trading_index"] = range(len(daily))
    date_to_index = dict(zip(daily["date"], daily["trading_index"]))

    results = []

    for _, event in events.iterrows():
        event_date = event["effective_date"]

        if event_date not in date_to_index:
            print(f"Skipping non-common trading date: {event_date.date()}")
            continue

        idx = date_to_index[event_date]
        result = {
            "effective_date": event_date,
            "repo_rate_pct": event["repo_rate_pct"],
            "repo_rate_change_pp": event["repo_rate_change_pp"],
        }

        for ticker in TICKERS:
            close_col = f"{ticker}_close"

            # Day 0: previous close to effective-date close.
            if idx >= 1:
                start = daily.loc[idx - 1, close_col]
                end = daily.loc[idx, close_col]
                result[f"{ticker}_day0_return_pct"] = (
                    (end / start - 1) * 100 if start else float("nan")
                )
            else:
                result[f"{ticker}_day0_return_pct"] = float("nan")

            # Inclusive 3-trading-DATE span: close t-1 to close t+1.
            # This compounds TWO close-to-close daily return intervals, not three.
            if idx >= 1 and idx + 1 < len(daily):
                start = daily.loc[idx - 1, close_col]
                end = daily.loc[idx + 1, close_col]
                result[f"{ticker}_window_m1_p1_pct"] = (
                    (end / start - 1) * 100 if start else float("nan")
                )
            else:
                result[f"{ticker}_window_m1_p1_pct"] = float("nan")

            # Inclusive 11-trading-DATE span: close t-5 to close t+5.
            # This compounds TEN close-to-close daily return intervals, not eleven.
            if idx >= 5 and idx + 5 < len(daily):
                start = daily.loc[idx - 5, close_col]
                end = daily.loc[idx + 5, close_col]
                result[f"{ticker}_window_m5_p5_pct"] = (
                    (end / start - 1) * 100 if start else float("nan")
                )
            else:
                result[f"{ticker}_window_m5_p5_pct"] = float("nan")

        results.append(result)

    event_study = pd.DataFrame(results)
    output_file = OUTPUT_DIR / "effective_date_event_study.csv"
    event_study.to_csv(output_file, index=False)

    print("\nMean raw returns around effective dates (%):")
    return_cols = [
        col for col in event_study.columns
        if "return_pct" in col or "window_" in col
    ]
    print(event_study[return_cols].mean().round(3).to_string())

    print(f"\nSaved: {output_file}")
    print(f"Saved: {OUTPUT_DIR / 'policy_event_date_diagnostic.csv'}")


if __name__ == "__main__":
    main()