# Research validation audit — 21 October 2026

**Status: CONDITIONAL / NOT YET SUBMISSION-CLEARED.** This audit distinguishes confirmed checks against the committed data from methodological issues requiring correction or independent verification. The repository's passing GitHub Actions tests cover synthetic macro-factor transformations, **not** a complete empirical replication.

## Verified directly against committed CSVs and source code

| Check | Finding | Status |
|---|---|---|
| Equity monthly panel | Five instruments, each with 192 rows and 192 distinct months, January 2010–December 2025 | PASS |
| Expanded macro common sample | 131 complete macro months per instrument (February 2015–December 2025) | PASS |
| Stock return consistency | All 960 monthly-return values in `analysis_dataset.csv` agree with `monthly_returns_all.csv` to tolerance 1e-8 | PASS |
| RBI monthly factor merge | Repo level and monthly change agree with `repo_rate_monthly.csv` numerically; 20 string differences are harmless floating-point representation at about 1e-16 | PASS |
| Regression outputs | 52 coefficient rows, 131 observations per bank/specification, common February 2015–December 2025 period | PASS (structural) |
| Robustness full sample | All 52 original full-sample coefficients and p-values match `robustness_coefficient_comparison.csv` to 1e-8 | PASS |
| Event date alignment | 26 effective-date events, all 26 present in event-study output, comprising 18 cuts and 8 hikes | PASS |
| Automated unit tests | Three synthetic macro-processing tests exist; these do not validate empirical price histories, event timing or all statistical outputs | LIMITED |

**What has not been independently replicated here:** Running every Python estimator against a separately fetched historical source, rechecking corporate-action adjustments and dividends, reconciling each RBI effective date with the official policy announcement timestamp, checking each historical FX/VIX observation against an independent provider, or auditing every published table/figure against raw source data.

## Blocking methodological issue: event-window naming

`src/run_policy_event_study.py` computes:
- `day0_return_pct`: close at t-1 to close at t, correctly **one daily return interval**.
- `window_m1_p1_pct`: close at t-1 to close at t+1, which spans **two** close-to-close return intervals, despite being described as a “3-trading-day window” because the inclusive dates t-1, t and t+1 cover three trading dates.
- `window_m5_p5_pct`: close at t-5 to close at t+5, which spans **ten** close-to-close return intervals, despite being described as an “11-trading-day window” because the inclusive dates t-5 through t+5 cover eleven trading dates.

This is not necessarily an arithmetic bug if the intention is to measure returns between the first and last close **within** each calendar window. It **is** an interpretation ambiguity, and those estimates are **not** the cumulative returns over three and eleven daily returns in the usual event-study convention. The manuscript and figures should specify endpoints explicitly, or the event study should be recomputed using t-2 to t+1 for three daily returns and t-6 to t+5 for eleven daily returns. If the window is meant to cover event days -1 through +1 inclusive, the standard cumulative event return instead uses close t-2 through close t+1; for -5 through +5 it uses close t-6 through close t+5. **Changing these endpoints changes the numerical estimates and p-values, so do not relabel existing estimates as corrected results.**

The paper currently reports event-window values from the original calculation. Before journal submission, either relabel those values as *close-to-close returns from t-1 to t+1 and from t-5 to t+5*, with a clear methodology note, or recompute all affected results, tables, figures and prose.

## Other validation gaps / publication caveats

1. **Original research scope:** CPI/inflation is absent, and monthly bank volatility is only described, not used as a dependent variable in the macro regressions. The original broad question is therefore **not fully answered**. Either narrow the paper's stated scope or add CPI and volatility-outcome models with verified historical sources.
2. **Multiple testing:** Many bank, factor, window and specification comparisons are examined. Nominal p<0.05 must not be portrayed as multiplicity-adjusted evidence. Consider Benjamini–Hochberg false discovery rate sensitivity.
3. **Event identification:** The 26 events are repo-rate **effective dates**, not verified announcement timestamps. Raw returns and bank-minus-NIFTY return differences are not estimated abnormal returns or causal policy-surprise effects.
4. **Timing and prediction:** All expanded regressions include contemporaneous NIFTY returns. The lagged-factor specification is **not** a real-time prediction model; no holdout test was run.
5. **Vendor and price adjustments:** Verify the historical stock closes' split/dividend conventions and compare monthly FX/VIX and RBI policy histories against official sources. Current internal consistency alone does not establish external data accuracy.
6. **Model diagnostics:** Examine residual serial correlation, heteroskedasticity, influential months, collinearity, and model stability. HAC(3) does not fix omitted-variable bias or reverse causation.
7. **Submission requirements:** Verify the intended journal's rules for prior preprints, AI-assisted drafting, authorship and data availability; disclose assistance truthfully.

## Submission decision

**Not yet fully validated for journal submission.** The descriptive panel, common-sample joins and stored full-sample robustness output are internally consistent. The original event-window terminology needs correction or an explicit endpoint clarification, and external-source and manuscript-wide validation remain open. The project's regression findings can be presented as *exploratory observational associations*, not causal effects or verified forecasts.

## Next validation steps

1. Resolve the event-window endpoint convention; rerun the original event-study script and downstream tables if correcting the return intervals.
2. Reconcile RBI policy announcement/effective dates and verify representative stock/FX/VIX observations against primary providers.
3. Add formal statistical diagnostic and multiple-comparison checks.
4. Decide whether to add CPI and a volatility-outcome regression or formally restrict the research question.
5. Refresh abstract, manuscript, figures and references from the final validated outputs, then freeze the release and submit.
