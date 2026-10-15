# Indian Financial-Sector Risk and Macroeconomic Variables

A reproducible **observational research project** covering Indian bank-stock returns, RBI repo-rate relationships, RBI policy-effective-date event windows, broad-market co-movement, India VIX, USD/INR and sensitivity to the 2020 disruption.

## Complete research report

**[Read the integrated research manuscript](reports/RESEARCH_PAPER.md)** — covers **seven research questions** across the project's original and expanded analysis. The editable Word and PDF manuscript versions were also generated separately for final review.

**[Data dictionary and provenance](docs/DATA_DICTIONARY.md)** documents definitions, sample periods, source caveats and units.

## Research questions and analyses

| Question | Analysis and result location |
| --- | --- |
| RQ1: How do average stock returns and realized volatility differ across banks and NIFTY 50? | `reports/results/descriptive_statistics_2010_2025.csv`; `reports/figures/mean_monthly_returns.png`, `monthly_volatility_comparison.png` |
| RQ2: How closely do individual bank returns move with the broad market? | `reports/results/stock_return_correlations_2015_2025.csv`; NIFTY coefficients in `expanded_macro_regressions.csv` |
| RQ3: Do repo-rate level and monthly policy-rate changes show conditional associations with bank returns? | `reports/results/market_controlled_regressions.csv` (initial SBI/HDFC models); `expanded_macro_regressions.csv` (four banks) |
| RQ4: Do India VIX and USD/INR add explanatory information across banks? | `reports/results/bank_macro_correlations_2015_2025.csv`, `model_fit_comparison.csv`, `expanded_macro_regressions.csv` |
| RQ5: How sample-sensitive are the results, and what do lagged-factor checks show? | `reports/results/robustness_coefficient_comparison.csv`, `robustness_model_fit.csv`, `timing_sensitivity_results.csv` |
| RQ6: What did the original SBI/HDFC/NIFTY repo-only analysis show? | `reports/results/return_descriptive_statistics.csv`, `factor_correlations.csv`, `single_factor_regressions.csv`, `market_controlled_regressions.csv`, `timing_sensitivity_results.csv` |
| RQ7: How did returns behave around RBI repo-rate **effective dates**, including hikes versus cuts and comparisons with NIFTY 50? | `reports/results/effective_date_event_study.csv`, `policy_event_descriptive_tests.csv`, `policy_event_market_comparison.csv`, `policy_event_hikes_vs_cuts.csv`, `policy_event_date_diagnostic.csv` |

The original event-window plots (`01_average_event_window_returns.png`, `02_individual_event_day_returns.png`, `03_repo_change_vs_event_day_returns.png`, `04_market_comparison_*.png`) and the newer macro figures are under `reports/figures/`.

## Data and periods

- Bank equities: **SBI** (`SBIN.NS`), **HDFC Bank** (`HDFCBANK.NS`), **ICICI Bank** (`ICICIBANK.NS`), **Axis Bank** (`AXISBANK.NS`). Broad-market control: **NIFTY 50** (`^NSEI`).
- **Full stock-return description:** January 2010–December 2025, **192 instrument-month observations per series**, 960 total.
- **Monthly RBI and expanded macro regressions:** February 2015–December 2025, **131 complete months per series**. Do **not** use the 2010–2025 window for the macro regressions without obtaining validated pre-2015 factor histories.
- **Policy-effective-date event study:** **26 historical repo-rate changes** in 2015–2025 (18 cuts, eight hikes) with trading-day windows.
- **COVID-era sensitivity:** exclude March–December 2020 (ten months), leaving **121 complete months per bank**.
- Macro factors: RBI repo-rate level (%), change (percentage points); India VIX monthly mean and previous month's VIX close; USD/INR monthly percentage change and its lag. USD/INR uses **INR per USD**, so a rise signifies INR depreciation.
- **No CPI/inflation model has been estimated**. The research title's “macroeconomic variables” refers to the actually included variables only.

## Reproduce from the versioned historical snapshot

Using Python with `pandas`, `numpy`, `matplotlib`, `scipy`, `statsmodels` and `openpyxl` installed, run from the repository root:

```bash
python -m pytest tests/test_macro_factors.py -v
# Existing repo-only monthly research, normalized to legacy SBI/HDFC/NIFTY labels:
python src/run_financial_analysis.py
# Existing RBI policy effective-date analysis using committed event dates + validated daily closes:
python src/run_policy_event_study.py
python src/analyze_policy_event_study.py
python src/plot_policy_event_study.py
# Expanded 2015-2025 aligned macro-factor models:
python src/build_analysis_dataset.py
python src/run_expanded_macro_analysis.py
python src/generate_research_outputs.py
python src/run_robustness_checks.py
```

All required **monthly** factor CSVs and validated **daily** stock-price inputs are already committed. The RBI source workbooks are in `data/raw/rbi_repo_rate/`, while historical Yahoo macro daily CSVs are in `data/raw/yahoo_macro/`. You **do not need to rerun** `src/download_macro_factors.py` unless intentionally collecting a new vendor snapshot. Re-downloading may produce revisions, different prices or incomplete history.

See `docs/DATA_DICTIONARY.md` for transformations, provenance and limitations.

## Interpretation and research-integrity boundaries

- The project describes associations, not causal effects of policy. Same-month NIFTY, VIX and USD/INR measurements cannot be interpreted as data available before the month.
- **The lagged macro specification still includes same-month NIFTY returns.** It is a lagged-factor sensitivity check, not an out-of-sample forecasting strategy.
- RBI repo-rate **effective dates** need not equal monetary-policy **announcement dates**. Event-window raw price changes and bank-minus-index returns are not verified surprise-based or beta-adjusted abnormal returns.
- The paper reports unadjusted individual p-values from multiple comparisons, plus one COVID-era exclusion sensitivity analysis. Provider histories, corporate-action adjustments, announcement timestamps, CPI and future-period forecasting remain outside the completed scope.
- This repository is educational/research material, not investment advice.

## Layout

`src/` analytical scripts · `tests/` synthetic tests · `data/raw/` original sources · `data/processed/` validated and aligned datasets · `reports/results/` CSV outputs · `reports/figures/` figures · `reports/RESEARCH_PAPER.md` integrated manuscript.
