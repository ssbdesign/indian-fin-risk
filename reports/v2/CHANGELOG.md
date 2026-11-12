# Research update on 12 November 2026

## Preserved

The frozen monthly and daily input datasets, original model definitions and legacy result tables are retained. Original 12-model estimates reproduce to four-decimal precision. Previously established monthly coverage and macro processing were not independently re-audited.

## Added

1. Full-precision 16- and 40-test macro corrections, with both BH and Holm results.
2. Joint VIX/FX tests, calendar-aware HAC sensitivity, leave-one-year-out estimates, two alternative specifications, collinearity and influence diagnostics, and exploratory 2020 break tests.
3. Fully lagged expanding-origin forecasts against historical mean and lagged-return benchmarks.
4. Corrected inclusive daily event endpoints, all event-level calculations and 27-/45-test endpoint families.
5. Revised manuscript, figures, documentation, version/input-hash manifest, and seven targeted macro/numerical tests.

## Changes in interpretation

HDFC FX is the strongest same-month macro association under the 16-test family, but fails broader Holm correction and one year-exclusion nominal threshold. SBI repo-change evidence is suggestive after multiplicity. Corrected SBI relative event evidence is stronger than the legacy result but sensitive to family definition. The tested macro forecasts are worse than a historical mean. All sensitivity analysis is exploratory and performed after seeing original results.

## Remaining limits

No independent vendor reconciliation, complete announcement-time policy calendar, surprise instrument, causal identification, inflation/fundamentals extension, or pristine live forecasting trial has been completed. Code records the intended auto-adjustment setting without presenting it as independent audit evidence.
