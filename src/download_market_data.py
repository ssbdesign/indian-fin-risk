from pathlib import Path

import yfinance as yf

TICKERS = {
    "SBI": "SBIN.NS",
    "HDFC": "HDFCBANK.NS",
    "ICICI": "ICICIBANK.NS",
    "AXIS": "AXISBANK.NS",
    "NIFTY50": "^NSEI",
}

START_DATE = "2009-12-01"
END_DATE = "2026-01-01"


def main():
    root = Path(__file__).resolve().parent.parent
    output_dir = root / "data" / "processed"/"validated"
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, symbol in TICKERS.items():
        print(f"\nDownloading {name} ({symbol})...")

        data = yf.download(
            symbol,
            start=START_DATE,
            end=END_DATE,
            auto_adjust=True,
            progress=False,
        )

        if data.empty:
            print(f"ERROR: No data returned for {name}")
            continue

        # Handle yfinance's MultiIndex columns consistently.
        if hasattr(data.columns, "nlevels") and data.columns.nlevels > 1:
            data.columns = data.columns.get_level_values(0)

        data = data.reset_index()
        data.columns = [str(col).lower() for col in data.columns]
        data = data.rename(columns={"datetime": "date"})

        data["date"] = data["date"].astype(str).str[:10]
        data["ticker"] = symbol

        output_file = output_dir / f"{name}_daily.csv"
        data.to_csv(output_file, index=False)

        print(f"Saved {len(data):,} rows to {output_file}")


if __name__ == "__main__":
    main()