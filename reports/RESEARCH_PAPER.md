# Monetary Policy, Market Risk, and Exchange-Rate Movements: Evidence from Four Indian Banking Stocks

**Integrated research-paper draft | Data end date: December 2025 | Prepared October 2026**

**Study scope.** Four NSE-listed banks (State Bank of India, HDFC Bank, ICICI Bank and Axis Bank) and the NIFTY 50. Descriptive sample: January 2010-December 2025 (192 observations per instrument). Multivariate sample: February 2015-December 2025 (131 observations per bank).

## Abstract
This study examines whether monthly returns of major Indian bank stocks are associated with broad equity-market performance, RBI repo-rate conditions, option-implied market volatility and USD/INR movements. Five instrument series provide 192 monthly return observations each for descriptive analysis; four bank-specific ordinary least-squares regressions are estimated using 131 aligned monthly observations from February 2015 through December 2025, with heteroskedasticity-and-autocorrelation-consistent (HAC) standard errors. In the expanded same-month regressions, the NIFTY 50 coefficient is positive and strongly significant for all four banks (range: 0.909-1.428). Positive repo-rate-change coefficients appear for SBI, ICICI and Axis, but only the SBI coefficient stays significant after excluding March-December 2020. HDFC's negative USD/INR coefficient persists under this exclusion, while ICICI's marginally significant VIX coefficient does not. Expanded models yield only modest gains in in-sample fit, and lagged macro coefficients do not reach 5% significance. The evidence indicates strong common-market co-movement alongside heterogeneous and sample-sensitive additional macro associations; it does not establish causality or predictive performance.

The study additionally incorporates the project's original three-instrument repo-rate correlations, single-factor and market-controlled models, the one-month policy-timing comparison, and an effective-date analysis of 26 RBI repo-rate changes (18 cuts and eight hikes). In that preliminary event study, SBI's mean t−1-to-t+1 close-to-close return is -1.107% (p=0.0288); the SBI-minus-NIFTY return difference is -0.804 percentage points (p=0.0272). These are nominal, multiple-test-unadjusted event-window associations, not verified policy-surprise effects.

**Keywords:** Indian banks; RBI repo rate; NIFTY 50; India VIX; USD/INR; event-window returns; HAC regression; sensitivity analysis.

## 1. Introduction and research questions
Indian bank returns can respond to systemic equity-market fluctuations, monetary-policy expectations, funding costs, economic conditions, currency changes and shifts in risk appetite. Simply comparing two variables can conceal these interrelationships. The central question is whether specific macro-financial variables have an identifiable *conditional association* with banks' monthly returns, after accounting for the broad market.

**RQ1.** How do the average monthly return and realized volatility of the four banks compare with NIFTY 50 during 2010-2025?

**RQ2.** How strongly are the four banks' monthly returns associated with contemporaneous NIFTY 50 returns during 2015-2025?

**RQ3.** Are RBI repo-rate level and monthly repo-rate changes associated with bank returns after controlling for market movements?

**RQ4.** Do India VIX and monthly USD/INR changes add explanatory information, and does that information differ across banks?

**RQ5.** Are the findings stable after excluding the turbulent March-December 2020 period? Do lagged macro measures demonstrate evidence of forecasting usefulness?

**RQ6.** What did the original SBI/HDFC/NIFTY 50 repo-only analysis find, and does the interpretation change when controlling for broad-market movements or lagging repo-rate changes?

**RQ7.** How did four banks and NIFTY 50 behave around the effective dates of recorded RBI policy-rate changes, including cuts versus hikes and market-relative returns?

The exercise is observational, not a causal natural experiment. It does not currently include CPI/inflation; questions about inflation cannot be answered by these models.

### Related literature and interpretive context

Research on common equity-return factors motivates adjusting bank-stock regressions for the broad market rather than reading raw policy correlations in isolation. Fama and French (1993) document shared risk-factor variation in stock and bond returns; the present project uses only a contemporaneous NIFTY 50 market control and does **not** estimate a Fama–French asset-pricing model. Newey and West (1987) motivate the HAC(3) standard errors used for monthly OLS inference, but HAC inference does not identify causality.

MacKinlay (1997) explains how classical event-study identification depends on the event timestamp and construction of expected versus abnormal returns. For India, Edwin Prabu A, Bhattacharyya and Ray (2016) report generally weak index-level reactions to observed monetary-policy announcements, while noting that surprise components may matter. Khuntia and Hiremath (2019) and Edwin Prabu A, Bhattacharyya and Ray (2020) examine the heterogeneous sectoral response to monetary-policy information. These studies motivate the bank-by-bank approach without implying that the reported effective-date raw returns are equivalent to announcement-surprise causal estimates.

**Micro versus macro definition.** This project's micro-level evidence refers to bank-specific stock-price return distributions, volatility, extremes, bank–market co-movement, and conditional coefficients that differ across SBI, HDFC, ICICI and Axis. It does **not** estimate any bank's loan portfolio, funding costs, capital adequacy, non-performing asset ratio or earnings. Macro-financial measures are RBI repo rates, market index returns, option-implied India VIX and USD/INR; CPI/inflation is not included.

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

Multiple individual tests are conducted. In a Benjamini–Hochberg sensitivity check of 16 nonmarket coefficients in the four expanded same-month models, only HDFC's USD/INR association survives 5% FDR control (q=0.0312). SBI's repo-change association has q=0.0517. Since interest-rate changes, macro shocks and stock-market outcomes can respond jointly to news, results are not policy treatment effects.

### Micro-level interpretation: four individual banking stocks

The 2010–2025 bank-specific stock characteristics and February 2015–December 2025 conditional macro responses are distinct analytical layers. These four summaries intentionally avoid inferring unmeasured bank balance-sheet fundamentals from observed share prices.

- **SBI:** Mean monthly return 1.3305%, volatility 9.7276% (highest among the banks), extreme months −35.0330% and +38.3020%. Correlation with NIFTY 50 is 0.6774. In the expanded same-month regression its market coefficient is +1.2388 (p<0.001), and its repo-change coefficient +7.1022 (p=0.0065) remains +7.4703 (p=0.0155) after excluding March–December 2020. VIX and USD/INR same-month coefficients are not significant at 5%.
- **HDFC Bank:** Mean monthly return 1.5449%, monthly volatility 6.1875% (lowest among four bank securities). NIFTY correlation is 0.7783 and the conditional same-month market coefficient is +0.9086 (p<0.001). HDFC's USD/INR coefficient is −0.7329 (p=0.0019), retaining sign and nominal significance at −0.7885 (p=0.0002) in the exclusion sample. The original prior-month repo-rate change yields −2.8635 (p=0.0117, n=130) in a *different* timing specification with same-month NIFTY controls; this is not a real-time forecast.
- **ICICI Bank:** Mean monthly return 1.5755% (highest bank monthly average), volatility 8.5378%, NIFTY correlation 0.7514. Same-month repo change +3.8362 (p=0.0263) and India VIX −0.1329 (p=0.0470) lose nominal significance after omitting the 2020 shock months (p=0.1405 and p=0.7062 respectively). The VIX result is statistically fragile.
- **Axis Bank:** Mean monthly return 1.4864%, volatility 9.4812%; the observed worst monthly return −45.6475% is the most negative in the five-instrument set. NIFTY correlation is 0.7569 and same-month market coefficient +1.4277 (p<0.001). Its positive repo-change coefficient +5.3289 (p=0.0292) decreases to +2.1736 (p=0.3960) after the 2020 exclusion.

Because these are individual equity outcomes, a higher mean return or lower price volatility does not necessarily indicate higher bank profitability, better liquidity, lower credit risk, or superior risk-adjusted performance. Those propositions would require bank financial statements, more controls and different models.

### Interpreting policy and currency coefficient units

A repo-change coefficient is denominated in **monthly stock-return percentage points per one percentage-point increase in the repo rate**. For example, SBI's estimated +7.1022 coefficient multiplied by a hypothetical +0.25 percentage-point repo movement gives +1.7756 percentage points as a linear *conditional association*; it is **not** a forecast or causal effect of a 25-basis-point hike. A +1% USD/INR monthly change indicates INR depreciation and corresponds to HDFC's estimated −0.7329-percentage-point conditional association. India VIX levels are index points, and the lagged VIX variable is last month's **close**, not last month's mean.

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

## 9. Original repo-rate analysis and policy-event study: RQ6-RQ7

This section integrates the *earlier* analyses already committed to the repository, which used SBI, HDFC and NIFTY 50 as the original three-instrument scope before adding ICICI and Axis to the macro regressions. Original repo-rate models were estimated on the February 2015-December 2025 window (131 monthly observations each), not the 2010-2025 descriptive sample. The script `src/run_financial_analysis.py` has been updated to normalize current ticker symbols and preserve the original 131-month analysis window, preventing the expanded dataset from silently changing the earlier research design.

### 9.1 Repo-rate correlations, single-factor and market-controlled regressions

| Instrument | Corr. with repo level | Corr. with repo change | Repo-change-only coefficient (p) |
|---|---:|---:|---:|
| SBI | -0.1138 | 0.2371 | 14.3778 (0.0819) |
| HDFC | -0.0122 | 0.1377 | 5.1444 (0.4162) |
| NIFTY 50 | -0.1147 | 0.1601 | 4.6042 (0.4081) |

The low absolute correlations with repo **levels** support the original finding that simple linear associations were small in this sample. The policy-change correlations are more positive but remain modest. None of the three *single-variable* repo-change OLS coefficients is significant at 5% with HAC(3) standard errors. The coefficient units are percentage points of monthly stock/index return for a **one-percentage-point** repo-rate change, which is considerably larger than a typical policy increment.

When repo level, repo change and same-month NIFTY return are included in SBI and HDFC bank models, the earlier market-controlled results are:

| Bank | Repo-level coefficient (p) | Repo-change coefficient (p) | NIFTY coefficient (p) | R² |
|---|---:|---:|---:|---:|
| SBI | -0.3587 (0.5323) | 8.0363 (0.0010) | 1.3746 (<0.001) | 0.4774 |
| HDFC | 0.4502 (0.0904) | 0.4620 (0.7725) | 1.0204 (<0.001) | 0.6119 |

Controlling for the market makes SBI's positive same-month repo-change coefficient nominally significant, even though the single-factor model did not pass 5%. This is consistent with joint market co-movement and overlapping macro information; it **does not** show that raising repo rates causes bank shares to gain. These SBI/HDFC baseline coefficients are consistent to rounding with the later expanded study's baseline models, providing useful continuity between the project's original and extended phases.

### 9.2 Original one-month timing comparison

The earlier script also compared the original same-month repo-change model against a model using the *previous month's* repo-rate change, alongside **current-month** repo level and NIFTY return. This is a timing sensitivity comparison, not a complete forecasting design.

| Bank | Same-month repo change coefficient (p), n=131 | Prior-month repo change coefficient (p), n=130 |
|---|---:|---:|
| SBI | 8.0363 (0.0010) | 3.0267 (0.5858) |
| HDFC | 0.4620 (0.7725) | -2.8635 (0.0117) |

The HDFC prior-month negative coefficient is significant at an unadjusted 5% level, but it differs in sign from the same-month estimate and is estimated on one fewer month. It needs further specification checks, especially with multiple testing and contemporaneous market controls. This finding **does not conflict** with the newer result that the added lagged **VIX and USD/INR variables** fail to achieve individual 5% significance: these are different regressors in different models.

### 9.3 Effective-date event-window returns

A separate daily-frequency event study uses 26 RBI **repo-rate effective dates** from 2015-2025: **18 cuts and eight hikes**. Every event date was present as a trading date for all five instruments in the project's event-date diagnostic. The event-day return is the change from the preceding close through the effective-date close; the shorter window is the close-to-close return from t−1 to t+1 (two daily return intervals), and the longer window is the close-to-close return from t−5 to t+5 (ten daily return intervals). Returns are raw price changes, not abnormal returns from a fitted market model.

| Instrument | Mean event-day return (%) | Mean t−1-to-t+1 return (%) | Mean t−5-to-t+5 return (%) | t−1-to-t+1 p-value against 0 |
|---|---:|---:|---:|---:|
| SBI | -0.4741 | -1.1074 | -1.2074 | 0.0288 |
| HDFC Bank | -0.3164 | -0.2026 | 0.7459 | 0.6675 |
| ICICI Bank | -0.4413 | -0.7831 | -0.1896 | 0.1486 |
| Axis Bank | -0.5301 | -0.3971 | 0.2834 | 0.5193 |
| NIFTY 50 | -0.2017 | -0.3039 | 0.3782 | 0.3519 |

Each cell averages 26 event windows. The SBI t−1-to-t+1 mean of -1.1074% differs from zero at nominal 5% (p=0.0288). Separately, SBI underperformed NIFTY by an average **-0.8036 percentage points** in the t−1-to-t+1 window (p=0.0272); HDFC, ICICI and Axis bank-minus-market t−1-to-t+1 results were not nominally significant. These differences are **raw bank-minus-index returns**, not formal abnormal returns adjusted for stock-specific market beta.

Hike-versus-cut comparisons are also available in `policy_event_hikes_vs_cuts.csv`. None of the 15 instrument/window comparisons passes an unadjusted 5% threshold. For example, SBI's average t−1-to-t+1 return was -0.0871% around the eight hikes versus -1.5609% around 18 cuts (difference +1.4738 percentage points, Welch p=0.0924). The smaller hike sample and simultaneous news constrain interpretation.

### 9.4 Limits particular to effective-date analysis

The effective date of an RBI repo-rate change may differ from the announcement date, and even same-day decisions can be anticipated by markets. Observed event-window returns combine contemporaneous market news, bank-specific events and policy information; overlapping windows and multiple hypotheses are not fully corrected. The analysis therefore answers **how returns behaved around recorded effective dates**, not how stocks responded causally to unexpected monetary-policy announcements. The two nominally significant SBI results do not survive Benjamini–Hochberg adjustment: q=0.4315 across 15 raw-return window tests and q=0.3261 across 12 bank-minus-market window tests.

**Source outputs:** `reports/results/factor_correlations.csv`, `single_factor_regressions.csv`, `market_controlled_regressions.csv`, `timing_sensitivity_results.csv`, `effective_date_event_study.csv`, `policy_event_descriptive_tests.csv`, `policy_event_market_comparison.csv`, `policy_event_hikes_vs_cuts.csv`, and `policy_event_date_diagnostic.csv`. The corresponding daily-window figures already live in `reports/figures/`.

## 10. Interpretation, limitations and extensions
The earlier RBI effective-date study further suggests negative SBI raw and bank-minus-market returns in the selected t−1-to-t+1 event window, but its nominal 5% findings require caution because they use effective rather than verified surprise dates and involve many tests. Across the broader monthly analyses, the most defensible synthesis is that the market-wide component is the dominant consistent association: positive NIFTY co-movement appears for every bank. Monetary-policy, implied-volatility and exchange-rate coefficients are heterogeneous, with some sensitive to a small set of turbulent months. The sample provides meaningful bank-specific hypotheses for further study, but not an investment trading rule.

**Limitations:** (i) event-study policy effective dates, rather than verified surprise announcements, and non-beta-adjusted event-window returns; (ii) observational simultaneity, policy endogeneity and omitted variables; (iii) monthly aggregation masks intra-month timing and policy announcements; (iv) possible price adjustments, dividends and provider differences have not undergone an independent source-by-source audit; (v) simultaneous repo-rate level and change can complicate interpretation; (vi) small event counts and excluded months affect inference; (vii) multiple comparisons, with exploratory false-discovery-rate sensitivity checks reported; (viii) lagged-factor analysis has same-month controls and no rolling/holdout out-of-sample evaluation; (ix) CPI inflation, bank financial statements, monetary-policy surprise data and cross-sectional confounders are not yet modeled.

**Future extensions:** verified NSE/RBI source reconciliation, inflation/CPI and liquidity factors, announcement-time event-window design, structural break tests and out-of-sample cross-validation. These are proposed work, not completed findings.

## 11. Conclusion
The combined project answers seven descriptive and associative research questions using four bank stocks and NIFTY 50, including the original repo-rate and effective-date studies. Compared with the diversified benchmark, the individual banking stocks show higher historical volatility and somewhat higher raw average monthly returns. Market returns correlate strongly with all bank returns, and this conditional relation survives adjustment for included macro measures. Positive repo-change relationships for selected banks and a negative USD/INR relationship for HDFC emerge in the original sample; only the SBI rate-change and HDFC exchange-rate associations among the highlighted findings retain conventional significance in the specified 2020-exclusion check. A nominally significant ICICI VIX association is particularly sample-sensitive. The principal contribution is a bank-by-bank, common-sample comparison with transparent robustness qualifications, rather than causal claims or forecasts.

## References
- Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3–56. https://doi.org/10.1016/0304-405X(93)90023-5
- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13–39. https://ideas.repec.org/a/aea/jeclit/v35y1997i1p13-39.html
- Edwin Prabu A, Bhattacharyya, I., & Ray, P. (2016). Is the stock market impervious to monetary policy announcements: Evidence from emerging India. *International Review of Economics & Finance*, 46, 166–179. https://doi.org/10.1016/j.iref.2016.09.007
- Khuntia, S., & Hiremath, G. S. (2019). Monetary Policy Announcements and Stock Returns: Some Further Evidence from India. *Journal of Quantitative Economics*, 17(4). https://ideas.repec.org/a/spr/jqecon/v17y2019i4d10.1007_s40953-019-00158-y.html
- Edwin Prabu A, Bhattacharyya, I., & Ray, P. (2020). Impact of monetary policy on the Indian stock market: Does the devil lie in the detail? *Indian Economic Review*, 55, 27–50. https://doi.org/10.1007/s41775-020-00078-2

[1] National Stock Exchange of India, **India VIX Index**: https://www.nseindia.com/static/products-services/indices-indiavix-index

[2] National Stock Exchange of India, **Nifty 50 Index**: https://www.nseindia.com/static/products-services/indices-nifty50-index

[3] Reserve Bank of India, **Historical data: key policy rates**: https://www.rbi.org.in/Scripts/bs_viewcontent.aspx?Id=624

[4] Newey, W. K., and West, K. D. (1987). **A Simple, Positive Semi-definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix.** *Econometrica*, 55(3), 703-708. https://doi.org/10.2307/1913610

[5] RBI, **Reference-rate archive** (independent verification resource): https://www.rbi.org.in/scripts/ReferenceRateArchive.aspx

**Reproducibility:** `src/run_financial_analysis.py` reproduces the original repo-rate-only study from the committed combined dataset; `src/build_rbi_policy_events.py` -> `src/run_policy_event_study.py` -> `src/analyze_policy_event_study.py` covers the policy effective-date analysis (the original RBI source workbook and validated daily prices are versioned). The expanded analysis is `src/build_analysis_dataset.py` -> `src/run_expanded_macro_analysis.py` -> `src/generate_research_outputs.py` -> `src/run_robustness_checks.py`. Key output paths are documented in `docs/DATA_DICTIONARY.md`.

*This is a ready-to-review research draft, not a peer-reviewed paper. Authorship, acknowledgments, institutional requirements, full bibliographic literature review and independent vendor-data reconciliation remain for final submission review.*
