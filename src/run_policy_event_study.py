
from pathlib import Path

import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
DAILY_DIR = DATA_DIR / "validated"
EVENT_FILE = DATA_DIR / "rbi_policy_events_2015_2025.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "results"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Load RBI repo-rate events
# --------------------------------------------------
events = pd.read_csv(EVENT_FILE, parse_dates=["effective_date"])

# Keep the analysis period explicit.
events = events.loc[
    events["effective_date"].between("2015-01-01", "2025-12-31")
].copy()

# --------------------------------------------------
# Load daily stock data
# --------------------------------------------------
def load_daily_stock(filename, ticker):
    path = DAILY_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Daily file not found: {path}")

    df = pd.read_csv(path, parse_dates=["date"])

    required_columns = {"date", "close"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"{filename} is missing columns: {missing}")

    df = df[["date", "close"]].copy()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["date", "close"])
    df = df.sort_values("date")
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.rename(columns={"close": f"{ticker}_close"})

    # Daily close-to-close percentage return.
    df[f"{ticker}_return_pct"] = df[f"{ticker}_close"].pct_change() * 100

    return df


sbi = load_daily_stock("SBI_daily.csv", "SBI")
hdfc = load_daily_stock("HDFC_daily.csv", "HDFC")
nifty = load_daily_stock("NIFTY50_daily.csv", "NIFTY50")

# --------------------------------------------------
# Inspect the event dates against available trading days
# --------------------------------------------------
daily_data = {
    "SBI": sbi,
    "HDFC": hdfc,
    "NIFTY50": nifty,
}

for name, df in daily_data.items():
    print(
        f"{name}: {df['date'].min().date()} to "
        f"{df['date'].max().date()}, {len(df)} daily rows"
    )

print(f"\nRBI effective-date events loaded: {len(events)}")
print(events[["effective_date", "repo_rate_pct", "repo_rate_change_pp"]]
      .to_string(index=False))

# Save a diagnostic copy. No event-window returns are calculated yet.
diagnostic = events[
    ["effective_date", "repo_rate_pct", "repo_rate_change_pp"]
].copy()

for name, df in daily_data.items():
    available_dates = pd.Index(df["date"])
    diagnostic[f"{name}_exact_trading_day"] = (
        diagnostic["effective_date"].isin(available_dates)
    )

diagnostic.to_csv(
    OUTPUT_DIR / "policy_event_date_diagnostic.csv",
    index=False,
)

print(
    "\nSaved event-date diagnostic to:",
    OUTPUT_DIR / "policy_event_date_diagnostic.csv",
)
print("\nExact trading-day matches:")
for name in daily_data:
    print(
        f"{name}: "
        f"{diagnostic[f'{name}_exact_trading_day'].sum()} / "
        f"{len(diagnostic)}"
    )

    # --------------------------------------------------
    # Effective-date event-window analysis
    # --------------------------------------------------

    # Merge all three daily datasets on trading date.
    daily = sbi.merge(hdfc, on="date", how="inner")
    daily = daily.merge(nifty, on="date", how="inner")
    daily = daily.sort_values("date").reset_index(drop=True)

    # Create trading-day indices for event-window calculations.
    daily["trading_index"] = range(len(daily))
    date_to_index = dict(zip(daily["date"], daily["trading_index"]))

    return_columns = {
        "SBI": "SBI_close",
        "HDFC": "HDFC_close",
        "NIFTY50": "NIFTY50_close",
    }

    event_results = []

    for _, event in events.iterrows():
        event_date = event["effective_date"]

        # Require the effective date to exist in the merged trading calendar.
        if event_date not in date_to_index:
            print(f"Skipping event without a common trading date: {event_date.date()}")
            continue

        event_idx = date_to_index[event_date]
        result = {
            "effective_date": event_date,
            "repo_rate_pct": event["repo_rate_pct"],
            "repo_rate_change_pp": event["repo_rate_change_pp"],
        }

        for ticker, close_col in return_columns.items():
            # Day 0: close-to-close daily return on the effective date.
            if event_idx >= 1:
                prev_close = daily.loc[event_idx - 1, close_col]
                event_close = daily.loc[event_idx, close_col]
                result[f"{ticker}_day0_return_pct"] = (
                    (event_close / prev_close - 1) * 100
                    if prev_close != 0 else float("nan")
                )
            else:
                result[f"{ticker}_day0_return_pct"] = float("nan")

            # Cumulative close-to-close return from t-1 close to t+1 close.
            if event_idx >= 1 and event_idx + 1 < len(daily):
                start_close = daily.loc[event_idx - 1, close_col]
                end_close = daily.loc[event_idx + 1, close_col]
                result[f"{ticker}_window_m1_p1_pct"] = (
                    (end_close / start_close - 1) * 100
                    if start_close != 0 else float("nan")
                )
            else:
                result[f"{ticker}_window_m1_p1_pct"] = float("nan")

            # Wider cumulative window: t-5 close to t+5 close.
            if event_idx >= 5 and event_idx + 5 < len(daily):
                start_close = daily.loc[event_idx - 5, close_col]
                end_close = daily.loc[event_idx + 5, close_col]
                result[f"{ticker}_window_m5_p5_pct"] = (
                    (end_close / start_close - 1) * 100
                    if start_close != 0 else float("nan")
                )
            else:
                result[f"{ticker}_window_m5_p5_pct"] = float("nan")

        event_results.append(result)

    event_study = pd.DataFrame(event_results)

    event_output = OUTPUT_DIR / "effective_date_event_study.csv"
    event_study.to_csv(event_output, index=False)

    print("\nEffective-date event study — first 10 events:")
    print(event_study.head(10).to_string(index=False))

    print("\nAverage event-window returns (%):")
    summary_columns = [
        col for col in event_study.columns
        if "return_pct" in col or "window_" in col
    ]
    print(event_study[summary_columns].mean().round(3).to_string())

    print(f"\nSaved event-study results to: {event_output}")