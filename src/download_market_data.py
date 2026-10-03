import yfinance as yf
from pathlib import Path


# The three instruments in our project
TICKERS = {
    "SBI": "SBIN.NS",
    "HDFC": "HDFCBANK.NS",
    "NIFTY50": "^NSEI",
}

# Our initial research period
START_DATE = "2015-01-01"
END_DATE = "2026-01-01"


def download_market_data():
    # Project root / data / raw
    output_folder = Path(__file__).resolve().parent.parent / "data" / "raw"
    output_folder.mkdir(parents=True, exist_ok=True)

    for name, ticker in TICKERS.items():

        print(f"Downloading {name} ({ticker})...")

        data = yf.download(
            ticker,
            start=START_DATE,
            end=END_DATE,
            auto_adjust=True,
            progress=False,
        )

        if data.empty:
            print(f"ERROR: No data found for {name}")
            continue

        output_file = output_folder / f"{name}_daily.csv"

        data.to_csv(output_file)

        print(f"Saved {len(data):,} observations to:")
        print(output_file)
        print()


if __name__ == "__main__":
    download_market_data()