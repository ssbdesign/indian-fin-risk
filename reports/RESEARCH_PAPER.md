# Monetary Policy, Market Risk, and Exchange-Rate Movements: Evidence from Four Indian Banking Stocks

**Research-paper draft | Data end date: December 2025 | Prepared October 2026**

**Study scope.** Four NSE-listed banks (State Bank of India, HDFC Bank, ICICI Bank and Axis Bank) and the NIFTY 50. Descriptive sample: January 2010-December 2025 (192 observations per instrument). Multivariate sample: February 2015-December 2025 (131 observations per bank).

## Abstract
This study examines whether monthly returns of major Indian bank stocks are associated with broad equity-market performance, RBI repo-rate conditions, option-implied market volatility and USD/INR movements. Five instrument series provide 192 monthly return observations each for descriptive analysis; four bank-specific ordinary least-squares regressions are estimated using 131 aligned monthly observations from February 2015 through December 2025, with heteroskedasticity-and-autocorrelation-consistent (HAC) standard errors. In the expanded same-month regressions, the NIFTY 50 coefficient is positive and strongly significant for all four banks (range: 0.909-1.428). Positive repo-rate-change coefficients appear for SBI, ICICI and Axis, but only the SBI coefficient stays significant after excluding March-December 2020. HDFC's negative USD/INR coefficient persists under this exclusion, while ICICI's marginally significant VIX coefficient does not. Expanded models yield only modest gains in in-sample fit, and lagged macro coefficients do not reach 5% significance. The evidence indicates strong common-market co-movement alongside heterogeneous and sample-sensitive additional macro associations; it does not establish causality or predictive performance.

**Keywords:** Indian banks; RBI repo rate; NIFTY 50; India VIX; USD/INR; HAC regression; sensitivity analysis.

## 1. Introduction and research questions
Indian bank returns can respond to systemic equity-market fluctuations, monetary-policy expectations, funding costs, economic conditions, currency changes and shifts in risk appetite. Simply comparing two variables can conceal these interrelationships. The central question is whether specific macro-financial variables have an identifiable *conditional association* with banks' monthly returns, after accounting for the broad market.

**RQ1.** How do the average monthly return and realized volatility of the four banks compare with NIFTY 50 during 2010-2025?

**RQ2.** How strongly are the four banks' monthly returns associated with contemporaneous NIFTY 50 returns during 2015-2025?

**RQ3.** Are RBI repo-rate level and monthly repo-rate changes associated with bank returns after controlling for market movements?

**RQ4.** Do India VIX and monthly USD/INR changes add explanatory information, and does that information differ across banks?

**RQ5.** Are the findings stable after excluding the turbulent March-December 2020 period? Do lagged macro measures demonstrate evidence of forecasting usefulness?

The exercise is observational, not a causal natural experiment. It does not currently include CPI/inflation; questions about inflation cannot be answered by these models.

## 2. Data and variable design
The project uses daily historical closes, consolidated into monthly closes and simple percentage returns. Four securities are identified by Yahoo-style tickers `SBIN.NS`, `HDFCBANK.NS`, `ICICIBANK.NS`, `AXISBANK.NS`; the NIFTY 50 benchmark is `^NSEI`. All five have 192 nonmissing monthly returns in the compiled 2010-2025 dataset. For a price close P, the monthly simple return (percentage units) equals 100(P_t/P_(t-1)-1).

The RBI repo-rate series is held in percent, and `repo_rate_change_pp` is the difference in **percentage points** from the prior month. India VIX is represented by the monthly average of observed daily closes; the lagged variable instead uses the **previous month's ending VIX level**, a distinction that matters for interpreting the model. For exchange rates, a positive monthly percentage change in INR per US dollar indicates *rupee depreciation*. NIFTY 50 monthly return is the common-market control. This is not a total-return or macro-announcement-surprise study.

The available RBI and Yahoo-derived macro series start in January 2015. Because models require nonmissing changes and lags, the common complete-case regression window is **February 2015-December 2025 (n = 131 per bank)**. Earlier stock months are retained only for descriptive comparisons; missing macro history in 2010-2014 has not been filled in. The reproducible pipeline and data lineage appear in `docs/DATA_DICTIONARY.md`.

Official definitions: NSE describes India VIX as an options-based indicator of expected near-term volatility, approximately over the following 30 calendar days [1]. NIFTY 50 is a diversified benchmark using free-float market capitalization weighting [2]. RBI identifies its database of historical policy rates [3]. These official documents define the concepts but have **not** independently verified every vendor-derived observation in the project.

## 3. Empirical strategy
Three specifications are fitted separately for each bank. The baseline is:

`bank_return_t = alpha + b1(repo_rate_pct_t) + b2(repo_rate_change_pp_t) + b3(nifty_return_pct_t) + error_t`.

The **expanded same-month model** adds `india_vix_mean_t` and `usd_inr_change_pct_t`. The **expanded lagged model** instead adds `india_vix_lag1_t` and `usd_inr_change_pct_lag1_t` alongside all three baseline controls. Because it retains contemporaneous NIFTY returns, the lagged model must **not** be presented as a genuine advance forecasting model.

Ordinary least squares is used with an intercept and Newey-West/HAC standard errors (three monthly lags) to mitigate heteroskedasticity and short-run autocorrelation in coefficient inference [4]. The three specifications use identical 131-month samples so in-sample R-squared measures are directly comparable. Individual coefficients are interpreted as conditional associations, not interventions. Sensitivity analysis re-estimates the specifications after removing the 10 months March-December 2020, leaving 121 observations per bank.

## 4. Descriptive results: RQ1

| Instrument | Monthly mean (%) | Monthly volatility / SD (%) | Lowest month (%) | Highest month (%) |
|---|---:|---:|---:|---:|
| SBI | 1.3305 | 9.7276 | -35.0330 | 38.3020 |
| HDFC Bank | 1.5449 | 6.1875 | -26.8119 | 21.7397 |
| ICICI Bank | 1.5755 | 8.5378 | -34.8919 | 31.7680 |
| Axis Bank | 1.4864 | 9.4812 | -45.6475 | 33.0343 |
| NIFTY 50 | 0.9560 | 4.7107 | -23.2464 | 14.6800 |

Each descriptive row has 192 monthly observations (2010-2025). Among these series ICICI displays the highest average monthly return, SBI the highest monthly standard deviation, and NIFTY 50 the lowest volatility. These averages are not risk-adjusted performance metrics and do not account for transaction costs.

## 5. Co-movement: RQ2
Pairwise bank-return correlations with NIFTY 50 range from **0.6774 (SBI)** to **0.7783 (HDFC)**. The other two are 0.7514 (ICICI) and 0.7569 (Axis). In the expanded same-month regressions, NIFTY 50 coefficients are SBI **1.2388**, HDFC **0.9086**, ICICI **1.2004**, and Axis **1.4277**; each has p < 0.001. Thus, broad-market co-movement is consistently present, though it does not establish a structural sensitivity invariant across time.

## 6. Conditional macro findings: RQ3-RQ4

| Bank | Repo-rate change coefficient (p) | India VIX coefficient (p) | USD/INR change coefficient (p) | Expanded R² |
|---|---:|---:|---:|---:|
| SBI | 7.1022 (0.0065) | -0.1836 (0.2607) | -0.5842 (0.2136) | 0.4925 |
| HDFC Bank | 1.4564 (0.3518) | 0.0520 (0.2004) | -0.7329 (0.0019) | 0.6330 |
| ICICI Bank | 3.8362 (0.0263) | -0.1329 (0.0470) | -0.1817 (0.6689) | 0.5821 |
| Axis Bank | 5.3289 (0.0292) | -0.1228 (0.1110) | 0.4249 (0.3276) | 0.5982 |

Table entries are HAC(3) estimates from same-month expanded regressions, n=131 each. A **one percentage-point** repo-rate change corresponds to the tabulated coefficient in percentage points of monthly return; actual policy moves are typically much smaller, so coefficients must be scaled accordingly. A one-percent USD/INR rise is associated with around **0.73 percentage-point lower** HDFC monthly return conditional on included controls, but no causal interpretation is warranted. For ICICI, the negative VIX association reaches only marginal nominal 5% significance (p=0.0470) and should not be overstated. Repo-rate *levels* are generally not reliably associated, with HDFC's same-month p=0.0499 borderline. Simple raw exchange-rate correlations are negative for all four banks, whereas their conditional regression coefficients are more heterogeneous.

Multiple individual tests are conducted; reported significance is unadjusted for multiple testing. Since interest-rate changes, macro shocks and stock-market outcomes can respond jointly to news, results are not policy treatment effects.

## 7. Model comparison and lagged specification: RQ4-RQ5

| Bank | Baseline R² | Expanded same-month R² | Expanded lagged R² | Baseline adjusted R² | Expanded same-month adjusted R² |
|---|---:|---:|---:|---:|---:|
| SBI | 0.4774 | 0.4925 | 0.5029 | 0.4650 | 0.4722 |
| HDFC | 0.6119 | 0.6330 | 0.6175 | 0.6027 | 0.6183 |
| ICICI | 0.5739 | 0.5821 | 0.5793 | 0.5638 | 0.5654 |
| Axis | 0.5905 | 0.5982 | 0.5929 | 0.5808 | 0.5821 |

Expanded same-month models raise in-sample R² modestly. However, larger R² alone is not proof of economic relevance or forecasting quality; adjusted R² increases are relatively modest. In the lagged regressions none of the VIX-close or exchange-rate-change lag coefficients has p < 0.05 for any bank. This does not establish that they have *no* predictive effect under alternative lag definitions, controls, or genuine out-of-sample evaluation.

## 8. COVID-era exclusion sensitivity: RQ5

| Bank / factor | Full coefficient (p) | Excluding Mar-Dec 2020 (p) | Interpretation |
|---|---:|---:|---|
| SBI / repo-rate change | 7.1022 (0.0065) | 7.4703 (0.0155) | Sign and nominal significance retained |
| HDFC / USD-INR change | -0.7329 (0.0019) | -0.7885 (0.0002) | Sign and nominal significance retained |
| ICICI / repo-rate change | 3.8362 (0.0263) | 2.6086 (0.1405) | No longer nominally significant |
| ICICI / India VIX | -0.1329 (0.0470) | -0.0473 (0.7062) | Association considerably attenuated |
| Axis / repo-rate change | 5.3289 (0.0292) | 2.1736 (0.3960) | No longer nominally significant |

Sensitivity figures were transcribed to four decimals from a successful local robustness run; see `reports/results/robustness_key_results.csv`. Both subsamples use the same HAC(3) estimator and model controls, with n=131 and n=121 respectively. Excluding ten months lowers statistical power and may change covariate distributions; changes in p-values by themselves do not establish differences in structural coefficients. The exclusion window is an analytical diagnostic, not a definitive separation of the pandemic's economic effects.

## 9. Interpretation, limitations and extensions
The most defensible synthesis is that the market-wide component is the dominant consistent association: positive NIFTY co-movement appears for every bank. Monetary-policy, implied-volatility and exchange-rate coefficients are heterogeneous, with some sensitive to a small set of turbulent months. The sample provides meaningful bank-specific hypotheses for further study, but not an investment trading rule.

**Limitations:** (i) observational simultaneity, policy endogeneity and omitted variables; (ii) monthly aggregation masks intra-month timing and policy announcements; (iii) possible price adjustments, dividends and provider differences have not undergone an independent source-by-source audit; (iv) simultaneous repo-rate level and change can complicate interpretation; (v) small event counts and excluded months affect inference; (vi) multiple comparisons and no correction for false discovery; (vii) lagged-factor analysis has same-month controls and no rolling/holdout out-of-sample evaluation; (viii) CPI inflation, bank financial statements, monetary-policy surprise data and cross-sectional confounders are not yet modeled.

**Future extensions:** verified NSE/RBI source reconciliation, inflation/CPI and liquidity factors, announcement-time event-window design, structural break tests and out-of-sample cross-validation. These are proposed work, not completed findings.

## 10. Conclusion
The analysis answers five descriptive and associative research questions using four bank stocks and NIFTY 50. Compared with the diversified benchmark, the individual banking stocks show higher historical volatility and somewhat higher raw average monthly returns. Market returns correlate strongly with all bank returns, and this conditional relation survives adjustment for included macro measures. Positive repo-change relationships for selected banks and a negative USD/INR relationship for HDFC emerge in the original sample; only the SBI rate-change and HDFC exchange-rate associations among the highlighted findings retain conventional significance in the specified 2020-exclusion check. A nominally significant ICICI VIX association is particularly sample-sensitive. The principal contribution is a bank-by-bank, common-sample comparison with transparent robustness qualifications, rather than causal claims or forecasts.

## References
[1] National Stock Exchange of India, **India VIX Index**: https://www.nseindia.com/static/products-services/indices-indiavix-index

[2] National Stock Exchange of India, **Nifty 50 Index**: https://www.nseindia.com/static/products-services/indices-nifty50-index

[3] Reserve Bank of India, **Historical data: key policy rates**: https://www.rbi.org.in/Scripts/bs_viewcontent.aspx?Id=624

[4] Newey, W. K., and West, K. D. (1987). **A Simple, Positive Semi-definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix.** *Econometrica*, 55(3), 703-708. https://doi.org/10.2307/1913610

[5] RBI, **Reference-rate archive** (independent verification resource): https://www.rbi.org.in/scripts/ReferenceRateArchive.aspx

**Reproducibility:** `src/build_analysis_dataset.py` -> `src/run_expanded_macro_analysis.py` -> `src/generate_research_outputs.py` -> `src/run_robustness_checks.py`. Key output paths are documented in `docs/DATA_DICTIONARY.md`.

*This is a ready-to-review research draft, not a peer-reviewed paper. Authorship, acknowledgments, institutional requirements, full bibliographic literature review and independent vendor-data reconciliation remain for final submission review.*
