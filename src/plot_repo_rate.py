from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "repo_rate_monthly.csv"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"
FIGURE_PATH = FIGURE_DIR / "repo_rate_over_time.png"


def main():
    # Load the existing processed dataset
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df = df.sort_values("date")

    # Create the output directory if needed
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    # Plot the monthly repo-rate series
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.step(
        df["date"],
        df["repo_rate_pct"],
        where="post",
        linewidth=2,
    )

    ax.set_title(
        "RBI Policy Repo Rate, India (2015–2025)",
        fontsize=14,
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Repo rate (%)")

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=300, bbox_inches="tight")

    # Plot monthly changes in the repo rate
    changes = df.dropna(subset=["repo_rate_change_pp"])

    fig2, ax2 = plt.subplots(figsize=(12, 5))

    ax2.bar(
        changes["date"],
        changes["repo_rate_change_pp"],
        width=20,
    )

    ax2.axhline(0, linewidth=1)
    ax2.set_title("Monthly Changes in RBI Policy Repo Rate (2015–2025)")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Change (percentage points)")

    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax2.grid(axis="y", alpha=0.3)

    fig2.tight_layout()

    change_figure_path = FIGURE_DIR / "repo_rate_changes.png"
    fig2.savefig(change_figure_path, dpi=300, bbox_inches="tight")

    # Print summary of repo-rate movements
    print("\nREPO RATE CHANGE SUMMARY")
    print("------------------------")
    print("Rate increases:", (changes["repo_rate_change_pp"] > 0).sum())
    print("Rate decreases:", (changes["repo_rate_change_pp"] < 0).sum())
    print("No change:", (df["repo_rate_change_pp"] == 0).sum())

    print(f"\nLevel chart saved to: {FIGURE_PATH}")
    print(f"Change chart saved to: {change_figure_path}")

    plt.show()
    plt.close("all")
    print(f"Observations plotted: {len(df)}")
    print(f"Figure saved to: {FIGURE_PATH}")


if __name__ == "__main__":
    main()
