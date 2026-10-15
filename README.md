# Indian Financial-Sector Risk & Monetary Policy

**Empirical research | India, 2010–2025 | Four listed banks + NIFTY 50**

A reproducible Python research project examining **bank-specific equity risk (micro-level outcomes)** and their relationships with **market-wide and macro-financial conditions**: RBI repo-rate decisions, India VIX, USD/INR and NIFTY 50. The study also investigates stock-price behavior around RBI policy **effective dates** and checks whether selected regression findings survive removal of the March–December 2020 observations.

> **Research status:** Completed historical data processing, descriptive analyses, RBI effective-date window comparisons, matched-sample OLS/HAC regressions, and COVID-window sensitivity checks. These are **observational associations**, not causal effects, policy-surprise estimates or validated return forecasts. Source-data adjustment audits, inflation/CPI modeling, and independent replication are prospective work.

## Read the research

| Start here | What it contains |
| :--- | :--- |
| **[Integrated manuscript](reports/RESEARCH_PAPER.md)** | Complete project: original repo-rate work, daily event windows, four-bank macro models and robustness qualifications |
| **[Data dictionary & source notes](docs/DATA_DICTIONARY.md)** | Definitions, units, transformations, vendor/source notes and identification limits |
| **[Research tables](reports/results/)** | Statistics, correlations, model fit, coefficient estimates, event tests, timing and robustness |
| **[Research charts](reports/figures/)** | Return/volatility comparisons, repo-rate views, bank-factor coefficient comparisons and RBI event-window plots |
| **[Code and tests](src/)** | Processing, event-study, estimation and figure generation scripts |

## Research questions

1. **Bank-level risk:** How do monthly return distributions, extreme observations and volatility compare across SBI, HDFC Bank, ICICI Bank, Axis Bank and NIFTY 50?
2. **Common-market component:** How strongly do monthly bank returns co-move with the broad Indian equity market?
3. **Monetary policy:** Are RBI repo-rate **levels** and **monthly changes** associated with individual bank returns after adjusting for NIFTY 50?
4. **Added macro factors:** Are India VIX and USD/INR changes associated with bank returns, and do their estimated relationships differ among banks?
5. **Stability and timing:** Does dropping March–December 2020 change the results? What do the earlier one-month repo-rate lag and the new lagged macro-factor specifications indicate?
6. **Original repo-only study:** What did the initial SBI/HDFC/NIFTY 50 correlations, single-factor OLS and market-controlled OLS models find?
7. **RBI events:** How did the five instruments behave around 26 recorded repo-rate **effective dates**, and what do hikes/cuts and bank-minus-index window comparisons show?

**Scope note:** “Micro” means the *instrument-level* risk/return and heterogeneous bank equity responses studied here. We do **not** estimate bank balance-sheet fundamentals, firm-level capital ratios, non-performing assets or loan-growth determinants; no such data have been modeled.

## Data coverage and design

| Segment | Coverage | Units / notes |
| :--- | :--- | :--- |
| Bank and NIFTY 50 monthly returns | **January 2010–December 2025** | 192 monthly observations per series; 960 combined rows |
| Original monthly repo-rate study | **February 2015–December 2025** | SBI, HDFC and NIFTY 50; 131 aligned months |
| Four-bank expanded macro OLS | **February 2015–December 2025** | 131 matched monthly observations per bank, common-sample model comparisons |
| RBI repo-rate effective-date event windows | **2015–2025** | 26 policy-rate changes: 18 cuts, 8 hikes |
| Exclusion sensitivity | **2015–2025, excluding Mar–Dec 2020** | 121 monthly observations per bank after excluding 10 months |

**Symbols:** `SBIN.NS`, `HDFCBANK.NS`, `ICICIBANK.NS`, `AXISBANK.NS`, and `^NSEI` (NIFTY 50). Legacy SBI/HDFC/NIFTY50 labels are normalized for the original analysis script.

**Measured variables:** monthly simple close-to-close return in percent; sample standard deviation of monthly returns; repo rate in percent and its change in **percentage points**; India VIX **mean daily closing level** within each month; USD/INR monthly percent change (positive = **rupee depreciation**); NIFTY 50 monthly return as same-month market control. The lagged VIX variable is the **prior month's closing VIX level**, not a lag of the monthly mean.

### Results at a glance

| Indicator | Supported result |
| :--- | :--- |
| Full-period average monthly return | ICICI highest among bank series (1.5755%); SBI 1.3305%, HDFC 1.5449%, Axis 1.4864%; NIFTY 50 0.9560% |
| Full-period monthly volatility | SBI 9.7276%, Axis 9.4812%, ICICI 8.5378%, HDFC 6.1875%; NIFTY 50 4.7107% |
| Market co-movement | Bank/NIFTY monthly correlations between **0.6774 and 0.7783** over the macro sample |
| Same-month expanded OLS | NIFTY coefficient **positive** and significant in all four bank models (HAC p < 0.001) |
| Selected macro effects | SBI repo-rate change +7.1022 (p=0.0065); HDFC USD/INR change −0.7329 (p=0.0019); conditional effects vary across banks |
| COVID-exclusion sensitivity | SBI repo-rate-change and HDFC USD/INR coefficients retain nominal significance; ICICI VIX and selected other repo-change findings do not |
| RBI effective-date windows | SBI mean raw 3-day return −1.1074% (p=0.0288), bank-minus-index difference −0.8036 pp (p=0.0272); **not verified monetary-policy surprises** |

*Regression coefficients are in percentage points of monthly stock return per one **unit** of the named regressor. Individual p-values are unadjusted for multiple hypotheses.*

## Repository map

```text
data/
  raw/                         # source daily equities, RBI spreadsheets, downloaded macro prices
  processed/
    validated/                  # validated bank/index daily prices
    monthly_returns_all.csv     # 5 instruments x 192 monthly records
    repo_rate_monthly.csv       # 2015–2025 RBI policy series
    india_vix_monthly.csv       # monthly India VIX
    usd_inr_monthly.csv         # monthly FX
    analysis_dataset.csv        # common ticker/month research dataset
src/
  check_market_data.py         # price-source validation
  calc_monthly.py              # monthly price and return calculation
  run_financial_analysis.py    # original SBI/HDFC/NIFTY monthly repo regressions
  build_rbi_policy_events.py   # repo effective-date changes
  run_policy_event_study.py    # daily raw event windows
  analyze_policy_event_study.py# descriptive tests, hike/cut, relative comparisons
  download_macro_factors.py    # optional Yahoo VIX/FX snapshot downloader
  build_analysis_dataset.py    # monthly macro factor merge
  run_expanded_macro_analysis.py# 4-bank HAC(3) model comparisons
  generate_research_outputs.py # research tables and macro figures
  run_robustness_checks.py     # compare full and COVID-window exclusion samples
reports/
  RESEARCH_PAPER.md            # full integrated manuscript
  results/                     # all reproducible CSV tables
  figures/                     # bank, macro and event figures
docs/DATA_DICTIONARY.md
tests/test_macro_factors.py
.github/workflows/macro-tests.yml
```

## Reproducing the analysis

From the repository root, create a virtual environment with your preferred tool and install compatible versions of `pandas`, `numpy`, `scipy`, `matplotlib`, `statsmodels`, `openpyxl`, `yfinance` (optional downloader) and `pytest`. The historical monthly inputs, RBI workbooks, macro factor snapshots and validated daily stock files are **already versioned**; don't re-download unless intentionally updating the data vintage.

```bash
python -m pytest tests/test_macro_factors.py -v

# Original study: existing 2015–2025 data and saved effective-date data
python src/run_financial_analysis.py
python src/run_policy_event_study.py
python src/analyze_policy_event_study.py
python src/plot_policy_event_study.py

# Expanded macro study: existing versioned monthly input files
python src/build_analysis_dataset.py
python src/run_expanded_macro_analysis.py
python src/generate_research_outputs.py
python src/run_robustness_checks.py
```

Reproduction scripts write to `reports/results/` and `reports/figures/`. Running scripts may modify tracked outputs; review diffs before committing. `src/download_macro_factors.py` obtains a **new** Yahoo Finance history and should not be rerun when reproducing the fixed 2025-vintage results. `src/build_rbi_policy_events.py` can rebuild the effective-date dataset from the saved RBI workbook; do so only when auditing that earlier preprocessing.

**Model comparison:** OLS with an intercept and heteroskedasticity/autocorrelation-consistent **Newey–West HAC(3)** standard errors; baseline controls are repo level, repo change and *contemporaneous* NIFTY return, and expanded versions add *contemporaneous* VIX/FX or their lagged measurements. Since contemporaneous controls remain present, the lagged analysis is **not a pure ex-ante forecast**. Reported R² values measure **in-sample** fit.

## Methods, provenance & reproducibility limits

- **RBI effective dates ≠ announcement timestamps.** The 26-event exercise tabulates raw price returns on and around *effective dates*. “Bank minus NIFTY” is a simple return difference, not a beta-adjusted abnormal return. The event results cannot isolate unexpected RBI monetary-policy news.
- **Market-wide co-movement can generate spurious causal narratives.** Repo changes may respond to the macroeconomy, and equity/FX/volatility may move jointly with common news. The analysis estimates conditional associations, not intervention effects.
- **Corporate actions and providers:** historical close adjustment, split/dividend conventions, VIX/FX provider differences and policy-rate monthly timing require independent data-provider verification before formal publication.
- **Samples differ intentionally.** Do not combine 2010–2025 descriptive statistics with the 2015–2025 macro model as if they were estimated on the same period; do not silently fill missing pre-2015 macro data.
- **Multiple testing:** p-values are conventional, not corrected for multiple comparisons. One COVID-period exclusion is not a comprehensive structural robustness evaluation.
- **Outside scope:** CPI/inflation estimates, bank balance-sheet fundamentals, announcement-surprise identification, adjusted abnormal returns, out-of-sample forecasting, investment signals and causal effects.

## Data source and literature pointers

- [Reserve Bank of India](https://www.rbi.org.in/) — historical policy-rate workbooks, archives and official time series.
- [NSE — India VIX](https://www.nseindia.com/static/products-services/indices-indiavix-index) and [NSE — NIFTY 50](https://www.nseindia.com/static/products-services/indices-nifty50-index) — official index definitions.
- [Newey & West (1987)](https://ideas.repec.org/a/ecm/emetrp/v55y1987i3p703-08.html) — HAC covariance estimation.
- [MacKinlay (1997)](https://ideas.repec.org/a/aea/jeclit/v35y1997i1p13-39.html) — event-study methodology.

## Use and citation

This repository is a transparent independent research workflow, not financial advice and not a claim of peer review. If using the results, cite the integrated manuscript, document the observation window and identify whether a figure derives from price returns, effective-date windows, or common-sample regressions. See `docs/DATA_DICTIONARY.md` for precise definitions.
