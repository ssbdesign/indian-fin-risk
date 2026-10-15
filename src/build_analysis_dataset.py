from pathlib import Path
import pandas as pd
# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RETURNS_PATH = PROCESSED_DIR / "monthly_returns_all.csv"

OUTPUT_PATH = PROCESSED_DIR / "analysis_dataset.csv"


# ============================================================
# MACROECONOMIC DATA CONFIGURATION
#
# To add a new factor later, add one entry to this list.
# Each file must contain one observation per month.
# ============================================================

MACRO_DATASETS = [
    {
        "name": "repo_rate",
        "path": PROCESSED_DIR / "repo_rate_monthly.csv",
        "date_column": "date",
        "columns": [
            "repo_rate_pct",
            "repo_rate_change_pp",
            "rate_changed",
        ],
    },

    {
        "name": "india_vix",
        "path": PROCESSED_DIR / "india_vix_monthly.csv",
        "date_column": "date",
        "columns": [
            "india_vix_close", "india_vix_mean",
            "india_vix_change", "india_vix_lag1",
        ],
    },
    {
        "name": "usd_inr",
        "path": PROCESSED_DIR / "usd_inr_monthly.csv",
        "date_column": "date",
        "columns": [
            "usd_inr_close", "usd_inr_change_pct",
            "usd_inr_change_pct_lag1",
        ],
    },

    # Future example — uncomment and edit when ready:
    #
    # {
    #     "name": "cpi",
    #     "path": PROCESSED_DIR / "cpi_monthly.csv",
    #     "date_column": "date",
    #     "columns": ["cpi_inflation_pct"],
    # },
]


# ============================================================
# HELPER: STANDARDISE MONTHLY DATES
# ============================================================

def make_month_key(date_series, dataset_name):
    dates = pd.to_datetime(date_series, errors="coerce")

    if dates.isna().any():
        raise ValueError(
            f"{dataset_name}: missing or invalid dates found."
        )

    return dates.dt.to_period("M")


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    print("BUILDING INTEGRATED ANALYSIS DATASET")
    print("=" * 45)

    # 1. Load existing monthly stock returns
    returns = pd.read_csv(RETURNS_PATH)

    required_return_columns = {
        "month",
        "ticker",
        "month_end_date",
        "month_end_close",
        "trading_days",
        "monthly_return",
        "monthly_return_pct",
    }

    missing_columns = required_return_columns - set(returns.columns)

    if missing_columns:
        raise ValueError(
            f"Stock returns file is missing columns: "
            f"{sorted(missing_columns)}"
        )

    returns["_month_key"] = make_month_key(
        returns["month_end_date"],
        "Stock returns",
    )

    if returns.duplicated(["ticker", "_month_key"]).any():
        raise ValueError(
            "Duplicate ticker-month observations found in stock returns."
        )

    print(f"Stock return rows: {len(returns)}")
    print(f"Tickers: {sorted(returns['ticker'].unique())}")

    # 2. Merge each configured macroeconomic dataset
    combined = returns.copy()

    for dataset in MACRO_DATASETS:
        name = dataset["name"]
        path = dataset["path"]
        date_column = dataset["date_column"]
        columns = dataset["columns"]

        print(f"\nLoading factor: {name}")

        if not path.exists():
            raise FileNotFoundError(
                f"Could not find {name} dataset: {path}"
            )

        macro = pd.read_csv(path)

        required_columns = {date_column, *columns}
        missing = required_columns - set(macro.columns)

        if missing:
            raise ValueError(
                f"{name} file is missing columns: {sorted(missing)}"
            )

        macro["_month_key"] = make_month_key(
            macro[date_column],
            name,
        )

        # A macro dataset must have no more than one row per month.
        if macro["_month_key"].duplicated().any():
            duplicate_months = (
                macro.loc[
                    macro["_month_key"].duplicated(keep=False),
                    "_month_key",
                ]
                .astype(str)
                .unique()
                .tolist()
            )

            raise ValueError(
                f"{name} has duplicate monthly observations: "
                f"{duplicate_months[:10]}"
            )

        # Keep only the month key and requested variables.
        macro = macro[["_month_key", *columns]]

        # Prevent accidental overwriting of existing columns.
        overlapping = set(columns) & set(combined.columns)

        if overlapping:
            raise ValueError(
                f"{name} would overwrite existing columns: "
                f"{sorted(overlapping)}"
            )

        # many stock rows can match one monthly macro observation.
        combined = combined.merge(
            macro,
            on="_month_key",
            how="left",
            validate="many_to_one",
            indicator="_merge_status",
        )

        unmatched_rows = (combined["_merge_status"] == "left_only").sum()

        print(f"Unmatched stock-return rows: {unmatched_rows}")

        combined = combined.drop(columns="_merge_status")

    # 3. Remove the temporary matching key
    combined = combined.drop(columns="_month_key")

    # 4. Sort for easy inspection
    combined = combined.sort_values(
        ["ticker", "month_end_date"]
    ).reset_index(drop=True)

    # 5. Validate the integrated dataset
    print("\nINTEGRATION VALIDATION")
    print("-" * 45)

    print(f"Rows in final dataset: {len(combined)}")
    print(f"Columns in final dataset: {len(combined.columns)}")
    print(
        "Duplicate ticker-month rows:",
        combined.duplicated(["ticker", "month_end_date"]).sum(),
    )

    macro_columns = [
        column
        for dataset in MACRO_DATASETS
        for column in dataset["columns"]
    ]

    print("\nMissing values in macro variables:")

    for column in macro_columns:
        print(f"  {column}: {combined[column].isna().sum()}")

    # 6. Save the integrated dataset
    combined.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved integrated dataset to:\n{OUTPUT_PATH}")

    print("\nPreview:")
    print(combined.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
