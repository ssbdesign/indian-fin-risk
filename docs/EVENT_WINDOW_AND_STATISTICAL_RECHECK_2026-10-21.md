# Event-window clarification and statistical recheck (21 October 2026)

**Important correction to manuscript terminology (without changing the existing estimates):**

The saved `src/run_policy_event_study.py` uses the common trading-calendar index t for each RBI repo-rate effective date.

- Event-day return: 100 × (close[t] / close[t-1] − 1). One close-to-close return.
- Saved `window_m1_p1_pct` (called “3-day” in older reports): 100 × (close[t+1] / close[t-1] − 1). **Two** close-to-close returns spanning three inclusive trading dates. Refer to this as the **t−1-to-t+1 close-to-close window**.
- Saved `window_m5_p5_pct` (called “11-day”): 100 × (close[t+5] / close[t-5] − 1). **Ten** close-to-close returns spanning eleven inclusive trading dates. Refer to this as the **t−5-to-t+5 close-to-close window**.

If instead calculating conventional cumulative event returns across all daily returns indexed −1 through +1, the start close would be t−2; for returns indexed −5 through +5, the start close would be t−6. **Do not claim the existing numbers measure those conventional event windows.** Existing numerical estimates are retained pending any deliberate recomputation.

## Direct calculation verification

The saved 26 event dates all appear in the 26-row event-study output (18 cuts, 8 hikes). Recalculated all **390** combinations of 26 dates × five securities × three windows from the five committed validated daily close series, using their shared trading calendar. The largest absolute discrepancy between recomputed and stored percentage returns was **0.000050715 percentage points**; all are within **0.0001 percentage points**, consistent with small price-series representation differences. Therefore the original endpoint formulas are confirmed to that tolerance. This does **not** independently validate the vendor's original daily closes or the RBI announcement timestamps.

## Multiple-comparison sensitivity

Benjamini–Hochberg adjusted p-values (q-values) computed from the committed regression and event-summary p-values. Families are exploratory and were defined for this audit:

| Family | Number of tests | Nominally significant result | Raw p | BH q | Survives 5% BH? |
|---|---:|---|---:|---:|---|
| Expanded same-month, all four nonmarket coefficients per bank | 16 | HDFC / USD-INR change | 0.001947 | **0.031159** | Yes |
| Same 16 tests | 16 | SBI / repo-rate change | 0.006457 | 0.051655 | No |
| Same 16 tests | 16 | ICICI / repo-rate change | 0.026259 | 0.116958 | No |
| Same 16 tests | 16 | Axis / repo-rate change | 0.029240 | 0.116958 | No |
| Same 16 tests | 16 | ICICI / India VIX mean | 0.047006 | 0.133066 | No |
| Same 16 tests | 16 | HDFC / repo-rate level | 0.049900 | 0.133066 | No |
| Event raw returns: five instruments × three windows | 15 | SBI / t−1-to-t+1 | 0.028770 | **0.431550** | No |
| Event bank-minus-NIFTY: four banks × three windows | 12 | SBI / t−1-to-t+1 | 0.027178 | **0.326132** | No |

**Interpretation:** The paper's SBI event-study findings are *nominal* and **do not survive** this multiple-testing check. Among nonmarket coefficients in the main expanded model, only HDFC's USD/INR association survives this specified 16-test BH correction. These calculations do not establish causality, forecast skill, or external data accuracy.

## Internal consistency checks

- 960 monthly return observations (five instruments × 192 distinct months), 131 common complete-case macro months each.
- Every return in the analysis panel agrees numerically with the separate monthly-return CSV (tolerance 1e−8).
- All RBI monthly levels and changes in the merged panel agree numerically with the repo-rate monthly source; minor textual differences reflect floating-point formatting.
- All 52 full-sample robustness coefficients and p-values agree with the expanded regression output (tolerance 1e−8).
- 26 policy-effective-date events in both the event file and event-study output.

## Outstanding before journal submission

Independent official-source reconciliation of historical prices and policy dates; residual/collinearity/influence diagnostics on the regression sample; checking manuscript tables and abstract for accurate updated event terminology; submission-format and journal-specific disclosure checks. **This audit is not a certification of full journal readiness.**
