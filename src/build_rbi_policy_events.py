
from pathlib import Path

import pandas as pd

# Locate the project root and source workbook.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "rbi_repo_rate"
    / "major_monetary_policy_rates.xlsx"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Read the verified worksheet and columns.
raw = pd.read_excel(
    INPUT_FILE,
    sheet_name="Report 1",
    header=None,
)

# Column B contains effective dates; column D contains repo rates.
data = pd.DataFrame({
    "effective_date": pd.to_datetime(raw.iloc[:, 1], errors="coerce"),
    "repo_rate_pct": pd.to_numeric(
        raw.iloc[:, 3].replace("-", pd.NA),
        errors="coerce",
    ),
})

# Remove title/header rows and rows without dates.
data = data.dropna(subset=["effective_date"]).copy()

# Sort chronologically before carrying rates forward.
data = data.sort_values("effective_date").reset_index(drop=True)

# A dash means no new repo-rate value is reported on that row.
data["repo_rate_pct"] = data["repo_rate_pct"].ffill()

# Collapse duplicate dates, keeping the last reported value for each date.
data = (
    data.dropna(subset=["repo_rate_pct"])
    .drop_duplicates(subset=["effective_date"], keep="last")
    .sort_values("effective_date")
    .reset_index(drop=True)
)

# Calculate changes between successive effective-date records.
data["repo_rate_change_pp"] = data["repo_rate_pct"].diff()

# Keep only actual rate changes.
events = data.loc[
    data["repo_rate_change_pp"].notna()
    & data["repo_rate_change_pp"].ne(0)
].copy()

events.to_csv(
    OUTPUT_DIR / "rbi_policy_events.csv",
    index=False,
)
study_events = events.loc[
    events["effective_date"].between(
        "2015-01-01", "2025-12-31"
    )
].copy()

study_events.to_csv(
    OUTPUT_DIR / "rbi_policy_events_2015_2025.csv",
    index=False,
)

print("\nPolicy changes during the study period:")
print(f"Number of changes: {len(study_events)}")
print(study_events.to_string(index=False))
data.to_csv(
    OUTPUT_DIR / "repo_rate_effective_history.csv",
    index=False,
)

print(f"Historical records: {len(data)}")
print(f"Repo-rate changes found: {len(events)}")
print("\nFirst 10 changes:")
print(events.head(10).to_string(index=False))
print("\nLatest 10 changes:")
print(events.tail(10).to_string(index=False))
print(f"\nSaved files to: {OUTPUT_DIR}")


# Compare event dates with the existing monthly repo-rate data.
monthly_file = (
    PROJECT_ROOT / "data" / "processed" / "repo_rate_monthly.csv"
)

monthly = pd.read_csv(monthly_file, parse_dates=["date"])

study_start = pd.Timestamp("2015-01-01")
study_end = pd.Timestamp("2025-12-31")

monthly_study = monthly.loc[
    monthly["date"].between(study_start, study_end)
].copy()

print("\nMonthly repo-rate data during study period:")
print(f"Monthly rows: {len(monthly_study)}")
print(monthly_study.head(3).to_string(index=False))
print(monthly_study.tail(3).to_string(index=False))

print("\nPolicy-event dates during study period:")
print(study_events[
    ["effective_date", "repo_rate_pct", "repo_rate_change_pp"]
].to_string(index=False))