
from pathlib import Path

import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "rbi_repo_rate"
    / "RBIB Table No. 01 _ Select Economic Indicators.xlsx"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "repo_rate_monthly.csv"

START_DATE = "2015-01-01"
END_DATE = "2025-12-31"

if not RAW_FILE.exists():
    raise FileNotFoundError(
        f"Excel file not found: {RAW_FILE}\n"
        "Check the filename and folder location."
    )
df = pd.read_excel(
    RAW_FILE,
    sheet_name="Monthly",
    header=None,
    usecols="B,Q",
    skiprows=10,
    names=["date", "repo_rate_pct"],
)

# Remove rows without a monthly date, including year headings.
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"]).copy()

# Convert rates to numeric; RBI may use ".." for unavailable values.
df["repo_rate_pct"] = pd.to_numeric(
    df["repo_rate_pct"], errors="coerce"
)

# Keep the study period and sort chronologically.
df = df[
    df["date"].between(START_DATE, END_DATE)
].sort_values("date")

# Validate monthly dates and duplicate observations.
if df["date"].duplicated().any():
    duplicates = df.loc[df["date"].duplicated(False), "date"]
    raise ValueError(f"Duplicate dates found:\n{duplicates}")

expected_months = pd.period_range(
    "2015-01", "2025-12", freq="M"
)
actual_months = pd.PeriodIndex(df["date"], freq="M")
missing_months = expected_months.difference(actual_months)

# Calculate changes in percentage points.
df["repo_rate_change_pp"] = df["repo_rate_pct"].diff()

# Flag months with a recorded change.
df["rate_changed"] = (
    df["repo_rate_change_pp"]
    .ne(0)
    .astype("boolean")
)

df.loc[
    df["repo_rate_change_pp"].isna(),
    "rate_changed"
] = pd.NA

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False, date_format="%Y-%m-%d")

print("\nREPO RATE DATA VALIDATION")
print("=" * 35)
print(f"Study period: {START_DATE[:7]} to {END_DATE[:7]}")
print(f"Monthly observations: {len(df)}")
print(f"Missing repo-rate values: {df['repo_rate_pct'].isna().sum()}")
print(f"Duplicate dates: {df['date'].duplicated().sum()}")
print(f"Missing calendar months: {len(missing_months)}")

if len(missing_months):
    print("Missing months:", list(map(str, missing_months)))

print("\nFirst observations:")
print(df.head(5).to_string(index=False))

print("\nLast observations:")
print(df.tail(5).to_string(index=False))

print(f"\nSaved dataset: {OUTPUT_FILE}")