# Indian Financial-Sector Risk and Macroeconomic Variables

Research on RBI repo-rate changes, Indian bank returns and market conditions (2015–2025). This repository contains historical observational analysis, not causal identification or investment advice.

## Instruments and factors
- Stock/market returns: SBI, HDFC Bank, NIFTY 50 (monthly); extended RBI event-study scripts also use ICICI and Axis Bank.
- RBI policy: repo-rate level and changes, from `data/processed/repo_rate_monthly.csv`.
- New optional Yahoo Finance downloads: India VIX (`^INDIAVIX`) and USD/INR (`INR=X`).

## Reproduce the new factor analysis
Set up a Python environment and install the packages required by the scripts (including `pandas`, `yfinance`, and `statsmodels`), then run these commands from the repository root:

```bash
python -m unittest discover -s tests -v
python src/download_macro_factors.py
python src/build_analysis_dataset.py
python src/run_financial_analysis.py
python src/run_expanded_macro_analysis.py
```

The new downloader gets daily close data from Yahoo Finance for December 2014 through December 2025 and saves original download results in `data/raw/yahoo_macro/`. It aggregates monthly India VIX close/mean/change/lagged close and USD/INR close/percentage change/lagged percentage change into `data/processed/`. **If the provider cannot supply all 132 study months, the script stops and reports the missing months.** Validate coverage, adjustments, and market calendars against official NSE and RBI publications before using the results for research claims. Data-provider usage terms may apply.

`build_analysis_dataset.py` adds both monthly factor files to the existing ticker-month dataset. `run_expanded_macro_analysis.py` writes `reports/results/expanded_macro_regressions.csv` and compares baseline, contemporaneous, and lagged specifications on **the same complete-case months**. The pre-existing regression and event-study scripts are retained, and their outputs are not replaced in this branch.

## Interpretation cautions
- Monthly relationships, including same-month VIX and exchange-rate movements, are not forecasts; simultaneity and market-wide shocks matter.
- The lagged specification includes repo-rate and NIFTY same-month controls, so it is a *lagged-factor sensitivity analysis*, not a purely real-time forecasting model.
- RBI effective-date event studies are not equivalent to verified announcement-time surprise studies.
- Check specification stability, overlapping-event windows, omitted-variable bias, multiple-testing risk, and historical data adjustments before claiming a robust result.
- Do not commit credentials. Github account authentication is external to this research repository.

## Existing project layout
- `src/`: download, clean, combine, regress, and event-study scripts
- `data/raw/`, `data/processed/`: inputs and research-ready datasets
- `reports/results/`, `reports/figures/`: analysis outputs
- `tests/`: synthetic transformation tests
