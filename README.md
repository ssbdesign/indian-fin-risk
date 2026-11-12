# Indian financial risk research

Four Indian banks and NIFTY 50, using the frozen 2010-2025 price history and 2015-2025 macro sample.

## Updated research results

The current manuscript is [the V2 paper](reports/v2/RESEARCH_PAPER.md). It separates contemporaneous associations from historical forecasts and corrects the legacy event-window endpoints.

- The 12 original models reproduce to the precision of the committed results.
- HDFC's negative FX coefficient survives both BH and Holm across 16 same-month macro tests; it does not survive Holm across the broader 40-test family.
- SBI repo change has raw p=0.00646 and BH q=0.05166 in the 16-test family.
- Correct inclusive three-day SBI bank-minus-index returns average -1.270 pp: adjusted p=0.0244 across 12 relative tests, 0.0550 across all 27 corrected event tests, and 0.0916 including legacy endpoints.
- Fully lagged macro forecasts underperform a historical mean for all four banks over 70 expanding-origin forecasts per bank.

These are exploratory observational results, not causal estimates or a validated trading system.

## Reproduce the update

Use Python 3.12 or 3.13. The version manifest records the environment actually used.

```bash
python -m pip install numpy pandas scipy statsmodels matplotlib yfinance pytest
python src/run_research_v2.py
python src/plot_research_v2.py
python -m pytest -q tests/test_macro_factors.py tests/test_research_v2.py
```

No new downloads are required. The update writes to `reports/v2/results` and `reports/v2/figures` without changing existing input datasets or legacy result tables. Calendar-aware HAC retains the distance between observations across exclusions. The forecast design lags all predictors by calendar month; 60 initial training targets lead to 70 forecasts from March 2020 to December 2025.

The new event calculation includes three daily returns using closes t-2 to t+1, or eleven using closes t-6 to t+5. The original `run_policy_event_study.py` and its outputs remain historical reproducibility material: their old three- and eleven-day labels contain two and ten return intervals respectively. Use the V2 corrected event outputs for the updated paper. `run_manifest.json` records all input hashes and package versions.

## Earlier project documentation

The following notes describe the original workflow. Numerical and interpretive updates above supersede earlier significance and forecast claims.

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
