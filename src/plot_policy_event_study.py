
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# --------------------------------------------------
# 1. PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "effective_date_event_study.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD EXISTING RESULTS
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("\nLoaded event-study results.")
print(f"Rows: {len(df)}")
print("\nAvailable columns:")
print(df.columns.tolist())


# Match column names without depending on capitalisation
# or spaces. Supports common naming variations.

def find_column(candidates, required=True):
    normalised = {
        str(col).lower().replace(" ", "").replace("-", "_"): col
        for col in df.columns
    }

    for candidate in candidates:
        key = candidate.lower().replace(" ", "").replace("-", "_")
        if key in normalised:
            return normalised[key]

    if required:
        raise ValueError(
            f"\nCould not find a column matching: {candidates}\n"
            f"Available columns: {df.columns.tolist()}\n"
            "Check the column names in effective_date_event_study.csv."
        )

    return None


date_col = find_column(
    ["event_date", "effective_date", "date"]
)

rate_change_col = find_column(
    [
        "repo_rate_change_pp",
        "repo_rate_change",
        "change_pp",
        "change",
    ],
    required=False,
)

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.dropna(subset=[date_col]).sort_values(date_col)


# --------------------------------------------------
# 3. IDENTIFY RETURN COLUMNS
# --------------------------------------------------

def return_column(ticker, window):
    """
    Find a return column for a ticker and event window.

    Expected concepts:
      day0       = event-day return
      m1_p1      = cumulative return from t-1 to t+1
      m5_p5      = cumulative return from t-5 to t+5
    """

    ticker_aliases = {
        "SBI": ["sbi"],
        "HDFC": ["hdfc"],
        "NIFTY50": ["nifty50", "nifty_50", "nifty"],
    }

    window_aliases = {
        "day0": [
            "day0_return_pct",
            "day0_pct",
            "event_day_return_pct",
            "event_day_pct",
        ],
        "m1_p1": [
            "window_m1_p1_pct",
            "m1_p1_return_pct",
            "m1_p1_pct",
        ],
        "m5_p5": [
            "window_m5_p5_pct",
            "m5_p5_return_pct",
            "m5_p5_pct",
        ],
    }

    for col in df.columns:
        key = str(col).lower().replace(" ", "").replace("-", "_")

        ticker_matches = any(
            alias in key for alias in ticker_aliases[ticker]
        )
        window_matches = any(
            alias in key for alias in window_aliases[window]
        )

        if ticker_matches and window_matches:
            return col

    return None


tickers = ["SBI", "HDFC", "NIFTY50"]
windows = ["day0", "m1_p1", "m5_p5"]

return_cols = {}

for ticker in tickers:
    for window in windows:
        col = return_column(ticker, window)
        if col is not None:
            return_cols[(ticker, window)] = col

if not return_cols:
    raise ValueError(
        "\nNo return columns were recognised.\n"
        "Review the printed column names and adjust return_column()."
    )

print("\nRecognised return columns:")
for key, col in return_cols.items():
    print(f"{key}: {col}")


# --------------------------------------------------
# 4. CONVERT RETURN COLUMNS TO NUMBERS
# --------------------------------------------------

for col in return_cols.values():
    df[col] = pd.to_numeric(df[col], errors="coerce")


# --------------------------------------------------
# 5. GRAPH 1: AVERAGE RETURNS BY EVENT WINDOW
# --------------------------------------------------

available_windows = [
    window
    for window in windows
    if any((ticker, window) in return_cols for ticker in tickers)
]

mean_data = {}

for ticker in tickers:
    mean_data[ticker] = []

    for window in available_windows:
        col = return_cols.get((ticker, window))
        mean_data[ticker].append(
            df[col].mean() if col is not None else np.nan
        )

x = np.arange(len(available_windows))
bar_width = 0.25

fig, ax = plt.subplots(figsize=(11, 6))

for i, ticker in enumerate(tickers):
    values = mean_data[ticker]

    ax.bar(
        x + (i - 1) * bar_width,
        values,
        bar_width,
        label=ticker,
    )

ax.axhline(0, linewidth=1, linestyle="--")
ax.set_xticks(x)
ax.set_xticklabels(
    {
        "day0": "Event day (day 0)",
        "m1_p1": "3-day window (-1 to +1)",
        "m5_p5": "11-day window (-5 to +5)",
    }[window]
    for window in available_windows
)
ax.set_ylabel("Mean return (%)")
ax.set_title("Average Returns Around RBI Repo-Rate Effective Dates")
ax.legend()
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "01_average_event_window_returns.png",
    dpi=300,
)
plt.close(fig)


# --------------------------------------------------
# 6. GRAPH 2: INDIVIDUAL EVENT-DAY RETURNS
# --------------------------------------------------

day0_tickers = [
    ticker for ticker in tickers
    if (ticker, "day0") in return_cols
]

if day0_tickers:
    plot_df = df.sort_values(date_col).copy()
    labels = plot_df[date_col].dt.strftime("%Y-%m-%d")

    fig, ax = plt.subplots(
        figsize=(15, 7)
    )

    x = np.arange(len(plot_df))
    width = 0.8 / len(day0_tickers)

    for i, ticker in enumerate(day0_tickers):
        col = return_cols[(ticker, "day0")]

        ax.bar(
            x + (i - (len(day0_tickers) - 1) / 2) * width,
            plot_df[col],
            width,
            label=ticker,
        )

    ax.axhline(0, linewidth=1, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=70, ha="right")
    ax.set_ylabel("Event-day return (%)")
    ax.set_title("Stock and Market Returns on RBI Effective Dates")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "02_individual_event_day_returns.png",
        dpi=300,
    )
    plt.close(fig)


# --------------------------------------------------
# 7. GRAPH 3: REPO-RATE CHANGE VS EVENT-DAY RETURNS
# --------------------------------------------------

if rate_change_col is not None and day0_tickers:
    df[rate_change_col] = pd.to_numeric(
        df[rate_change_col],
        errors="coerce",
    )

    fig, ax = plt.subplots(figsize=(9, 6))

    for ticker in day0_tickers:
        col = return_cols[(ticker, "day0")]

        valid = df[[rate_change_col, col]].dropna()

        ax.scatter(
            valid[rate_change_col],
            valid[col],
            label=ticker,
            alpha=0.75,
        )

    ax.axhline(0, linewidth=1, linestyle="--")
    ax.axvline(0, linewidth=1, linestyle="--")
    ax.set_xlabel("Repo-rate change (percentage points)")
    ax.set_ylabel("Event-day return (%)")
    ax.set_title("Repo-Rate Changes vs Event-Day Returns")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "03_repo_change_vs_event_day_returns.png",
        dpi=300,
    )
    plt.close(fig)
else:
    print(
        "\nGraph 3 skipped: a repo-rate-change column "
        "or event-day return columns were not found."
    )


# --------------------------------------------------
# 8. GRAPH 4: STOCK RETURNS RELATIVE TO NIFTY 50
# --------------------------------------------------

for window in available_windows:
    nifty_col = return_cols.get(("NIFTY50", window))

    if nifty_col is None:
        continue

    fig, ax = plt.subplots(figsize=(11, 6))

    for ticker in ["SBI", "HDFC"]:
        stock_col = return_cols.get((ticker, window))

        if stock_col is None:
            continue

        # Difference in cumulative returns, in percentage points.
        # This is a descriptive market comparison, not a causal estimate.
        difference = df[stock_col] - df[nifty_col]

        ax.plot(
            df[date_col],
            difference,
            marker="o",
            markersize=4,
            linewidth=1.2,
            label=f"{ticker} minus NIFTY 50",
        )

    ax.axhline(0, linewidth=1, linestyle="--")
    ax.set_xlabel("RBI effective date")
    ax.set_ylabel("Return difference (percentage points)")
    ax.set_title(
        f"Stock Returns Relative to NIFTY 50: {window}"
    )
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / f"04_market_comparison_{window}.png",
        dpi=300,
    )
    plt.close(fig)


# --------------------------------------------------
# 9. FINISHED
# --------------------------------------------------

print("\nGraph generation finished.")
print(f"Figures saved in:\n{OUTPUT_DIR}")

for path in sorted(OUTPUT_DIR.glob("*.png")):
    print(f" - {path.name}")