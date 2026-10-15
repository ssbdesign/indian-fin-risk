"""Download and prepare monthly India VIX and USD/INR factors.

Run before build_analysis_dataset.py. Never forward-fill missing months.
Source: Yahoo Finance via yfinance; verify against NSE/RBI before publication.
"""
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "yahoo_macro"
PROCESSED = ROOT / "data" / "processed"
START = "2014-12-01"  # needed to calculate January 2015 changes and lags
END = "2026-01-01"  # yfinance end is exclusive
STUDY_MONTHS = pd.period_range("2015-01", "2025-12", freq="M")
SYMBOLS = {"india_vix": "^INDIAVIX", "usd_inr": "INR=X"}


def normalize_download(downloaded: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Return unique, sorted date/close rows despite yfinance column formats."""
    if downloaded is None or downloaded.empty:
        raise ValueError(f"{symbol}: Yahoo Finance returned no daily data")
    if isinstance(downloaded.columns, pd.MultiIndex):
        if "Close" not in downloaded.columns.get_level_values(0):
            raise ValueError(f"{symbol}: missing Close column")
        close = downloaded.xs("Close", axis=1, level=0).iloc[:, 0]
    else:
        if "Close" not in downloaded.columns:
            raise ValueError(f"{symbol}: missing Close column")
        close = downloaded["Close"]
    idx = pd.to_datetime(close.index, errors="coerce")
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    daily = pd.DataFrame({"date": idx, "close": pd.to_numeric(close.to_numpy(), errors="coerce")})
    if daily["date"].isna().any() or daily["close"].isna().any():
        raise ValueError(f"{symbol}: invalid dates or prices in Yahoo response")
    if (daily["close"] <= 0).any():
        raise ValueError(f"{symbol}: non-positive prices found")
    daily["date"] = daily["date"].dt.normalize()
    if daily["date"].duplicated().any():
        raise ValueError(f"{symbol}: duplicate trading dates")
    return daily.sort_values("date").reset_index(drop=True)


def monthly_factors(daily: pd.DataFrame, kind: str) -> pd.DataFrame:
    """Aggregate daily closes with consistent calendar-month keys."""
    if kind not in SYMBOLS:
        raise ValueError(f"Unknown macro factor {kind}")
    df = daily.copy()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
    grouped = df.groupby("month")["close"]
    monthly = pd.DataFrame({"close": grouped.last(), "mean": grouped.mean()}).sort_index()
    missing = STUDY_MONTHS.difference(monthly.index)
    if len(missing):
        raise ValueError(
            f"{kind}: {len(missing)} missing study months in downloaded data: "
            f"{[str(m) for m in missing[:12]]}. Do not fill gaps silently; "
            "use a verified source for missing months."
        )

    if kind == "india_vix":
        monthly["india_vix_close"] = monthly["close"]
        monthly["india_vix_mean"] = monthly["mean"]
        monthly["india_vix_change"] = monthly["close"].diff()
        monthly["india_vix_lag1"] = monthly["close"].shift(1)
        columns = ["india_vix_close", "india_vix_mean", "india_vix_change", "india_vix_lag1"]
    else:
        monthly["usd_inr_close"] = monthly["close"]
        monthly["usd_inr_change_pct"] = monthly["close"].pct_change(fill_method=None) * 100
        monthly["usd_inr_change_pct_lag1"] = monthly["usd_inr_change_pct"].shift(1)
        columns = ["usd_inr_close", "usd_inr_change_pct", "usd_inr_change_pct_lag1"]

    monthly = monthly.loc[STUDY_MONTHS, columns].copy()
    monthly.index.name = "month"
    monthly = monthly.reset_index()
    monthly.insert(0, "date", monthly["month"].dt.to_timestamp("M"))
    return monthly.drop(columns="month")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    for kind, symbol in SYMBOLS.items():
        print(f"Downloading {kind}: {symbol}, {START} to 2025-12-31")
        response = yf.download(
            symbol, start=START, end=END, interval="1d",
            auto_adjust=False, progress=False, threads=False,
        )
        daily = normalize_download(response, symbol)
        daily.to_csv(RAW / f"{kind}_daily.csv", index=False)
        factors = monthly_factors(daily, kind)
        destination = PROCESSED / f"{kind}_monthly.csv"
        factors.to_csv(destination, index=False)
        print(f"{kind}: {len(daily)} daily rows; {len(factors)} months; saved {destination}")
    print("Macro factor download complete. Next: python src/build_analysis_dataset.py")


if __name__ == "__main__":
    main()
