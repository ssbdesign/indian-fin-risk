from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "reports" / "results" / "effective_date_event_study.csv"
OUTPUT_DIR = ROOT / "reports" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TICKERS = ["SBI", "HDFC", "ICICI", "AXIS", "NIFTY50"]
BANKS = ["SBI", "HDFC", "ICICI", "AXIS"]

WINDOWS = {
    "day0": "Event day (day 0)",
    "m1_p1": "3-day window (-1 to +1)",
    "m5_p5": "11-day window (-5 to +5)",
}


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Run run_policy_event_study.py first: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE, parse_dates=["effective_date"])
    df = df.sort_values("effective_date").reset_index(drop=True)

    if df.empty:
        raise ValueError("Event-study results contain no rows.")

    def col(ticker, window):
        suffix = {
            "day0": "day0_return_pct",
            "m1_p1": "window_m1_p1_pct",
            "m5_p5": "window_m5_p5_pct",
        }[window]
        name = f"{ticker}_{suffix}"
        return name if name in df.columns else None

    available_windows = [
        window for window in WINDOWS
        if any(col(ticker, window) for ticker in TICKERS)
    ]

    # Graph 1: mean raw returns across event windows.
    x = np.arange(len(available_windows))
    width = 0.8 / len(TICKERS)

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, ticker in enumerate(TICKERS):
        values = [
            df[col(ticker, window)].mean()
            if col(ticker, window) else np.nan
            for window in available_windows
        ]
        ax.bar(
            x + (i - (len(TICKERS) - 1) / 2) * width,
            values,
            width,
            label=ticker,
        )

    ax.axhline(0, linewidth=1, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([WINDOWS[w] for w in available_windows])
    ax.set_ylabel("Mean raw return (%)")
    ax.set_title("Returns Around RBI Repo-Rate Effective Dates")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "01_average_event_window_returns.png", dpi=300)
    plt.close(fig)

    # Graph 2: individual event-day returns.
    day0_tickers = [t for t in TICKERS if col(t, "day0")]

    if day0_tickers:
        fig, ax = plt.subplots(figsize=(16, 7))
        x = np.arange(len(df))
        width = 0.8 / len(day0_tickers)

        for i, ticker in enumerate(day0_tickers):
            ax.bar(
                x + (i - (len(day0_tickers) - 1) / 2) * width,
                df[col(ticker, "day0")],
                width,
                label=ticker,
            )

        ax.axhline(0, linewidth=1, linestyle="--")
        ax.set_xticks(x)
        ax.set_xticklabels(
            df["effective_date"].dt.strftime("%Y-%m-%d"),
            rotation=70,
            ha="right",
        )
        ax.set_ylabel("Event-day return (%)")
        ax.set_title("Returns on RBI Repo-Rate Effective Dates")
        ax.legend(ncol=3)
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "02_individual_event_day_returns.png", dpi=300)
        plt.close(fig)

    # Graph 3: rate change against event-day returns.
    if "repo_rate_change_pp" in df.columns and day0_tickers:
        fig, ax = plt.subplots(figsize=(9, 6))

        for ticker in day0_tickers:
            valid = df[["repo_rate_change_pp", col(ticker, "day0")]].dropna()
            ax.scatter(
                valid["repo_rate_change_pp"],
                valid[col(ticker, "day0")],
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

    # Graph 4: bank returns minus NIFTY 50 returns.
    for window in available_windows:
        nifty_col = col("NIFTY50", window)
        if not nifty_col:
            continue

        fig, ax = plt.subplots(figsize=(12, 6))

        for ticker in BANKS:
            stock_col = col(ticker, window)
            if not stock_col:
                continue

            difference = df[stock_col] - df[nifty_col]
            ax.plot(
                df["effective_date"],
                difference,
                marker="o",
                markersize=3,
                linewidth=1.1,
                label=f"{ticker} minus NIFTY 50",
            )

        ax.axhline(0, linewidth=1, linestyle="--")
        ax.set_xlabel("RBI effective date")
        ax.set_ylabel("Return difference (percentage points)")
        ax.set_title(f"Bank vs NIFTY 50: {WINDOWS[window]}")
        ax.legend()
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(
            OUTPUT_DIR / f"04_market_comparison_{window}.png",
            dpi=300,
        )
        plt.close(fig)

    print("\nPlot generation complete.")
    print(f"Figures saved to: {OUTPUT_DIR}")
    for path in sorted(OUTPUT_DIR.glob("*.png")):
        print(f" - {path.name}")


if __name__ == "__main__":
    main()