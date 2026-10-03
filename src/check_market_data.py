from pathlib import Path

import pandas as pd



ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "processed" / "validated"

FILES = {
    "SBI_daily.csv": "SBI",
    "HDFC_daily.csv": "HDFC",
    "NIFTY50_daily.csv": "NIFTY50",
}


def load_and_clean_csv(path, ticker):
    """
    Read yfinance CSVs with either a normal header or
    the multi-row Price/Ticker/Date header format.
    """

    # Read without assuming which row is the header.
    raw = pd.read_csv(path, header=None, dtype=str)

    if raw.empty:
        raise ValueError("CSV is empty.")

    # Find the row containing the price field names.
    header_row = None

    for i in range(min(5, len(raw))):
        values = raw.iloc[i].fillna("").str.strip().str.lower().tolist()

        if "close" in values and "open" in values:
            header_row = i
            break

    if header_row is None:
        raise ValueError(
            f"Could not identify the price header. "
            f"First rows:\n{raw.head(4)}"
        )

    # Get the column names from the identified header.
    headers = [
        str(value).strip().lower()
        for value in raw.iloc[header_row].tolist()
    ]

    # Data begins after any metadata rows, including Ticker and Date.
    data = raw.iloc[header_row + 1:].copy()
    data.columns = headers

    # Remove metadata rows and blank rows.
    first_col = data.columns[0]
    data[first_col] = data[first_col].astype(str).str.strip()

    data = data[
        ~data[first_col].str.lower().isin(["ticker", "date", "price", ""])
    ].copy()

    # The first column contains the trading dates.
    data = data.rename(columns={first_col: "date"})

    # Normalize expected column names.
    data.columns = [str(c).strip().lower() for c in data.columns]

    required = ["date", "open", "high", "low", "close"]
    missing = [c for c in required if c not in data.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. "
            f"Found: {data.columns.tolist()}"
        )

    if "volume" not in data.columns:
        data["volume"] = pd.NA

    # Convert fields to their proper types.
    data["date"] = pd.to_datetime(data["date"], errors="coerce")

    numeric_columns = ["open", "high", "low", "close", "volume"]

    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    # Remove rows that are metadata or have invalid dates.
    data = data.dropna(subset=["date"]).copy()

    # Invalid or missing prices must not pass validation.
    if data.empty:
        raise ValueError("No valid dated market rows were found.")

    if data[["open", "high", "low", "close"]].isna().any().any():
        raise ValueError("Some rows have missing or non-numeric prices.")

    if (data[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("Some prices are zero or negative.")

    # Sort and check dates.
    data = data.sort_values("date").reset_index(drop=True)

    if data["date"].duplicated().any():
        duplicates = data.loc[
            data["date"].duplicated(keep=False), "date"
        ].dt.strftime("%Y-%m-%d").tolist()

        raise ValueError(f"Duplicate dates found: {duplicates[:10]}")

    data["ticker"] = ticker

    columns = [
        "date", "open", "high", "low",
        "close", "volume", "ticker"
    ]

    return data[columns]


def main():
    if not RAW.exists():
        raise FileNotFoundError(
            f"Raw data folder not found: {RAW}"
        )

    CLEAN.mkdir(parents=True, exist_ok=True)

    print("Project:", ROOT)
    print("Reading raw files from:", RAW)
    print("Saving cleaned files to:", CLEAN)

    failed = []

    for filename, ticker in FILES.items():
        source = RAW / filename

        print(f"\nChecking {filename}...")

        if not source.exists():
            print("FAILED: File not found:", source)
            failed.append(filename)
            continue

        try:
            df = load_and_clean_csv(source, ticker)

            # Write the standardized copy, leaving the original untouched.
            output = CLEAN / filename
            df.to_csv(output, index=False, date_format="%Y-%m-%d")

            # Read back the output to verify its saved structure.
            check = pd.read_csv(output, parse_dates=["date"])

            expected = [
                "date", "open", "high", "low",
                "close", "volume", "ticker"
            ]

            if check.columns.tolist() != expected:
                raise ValueError(
                    f"Unexpected output columns: {check.columns.tolist()}"
                )

            print("PASSED")
            print("Rows:", len(check))
            print(
                "Date range:",
                check["date"].min().date(),
                "to",
                check["date"].max().date(),
            )
            print("Columns:", check.columns.tolist())
            print("Clean file:", output)

        except Exception as error:
            print("FAILED:", error)
            failed.append(filename)

    print("\n" + "=" * 55)

    if failed:
        print("VALIDATION FINISHED WITH ERRORS")
        print("Files needing attention:", failed)
    else:
        print("ok report")
        print("Cleaned CSVs are in data/processed/validated/")


if __name__ == "__main__":
    main()
