# Independent OLS and essential diagnostics recheck — 21 October 2026

This check independently rebuilt the four **expanded same-month** OLS models from the committed `data/processed/analysis_dataset.csv` using matrix least squares (not the repository's statsmodels regression routine). Each bank has 131 complete monthly observations. Recomputed coefficients and R-squared agree with the saved regression output at reported precision.

| Bank | Recomputed R² | Repo-change coefficient | FX-change coefficient | Durbin–Watson | Residual lag-1 correlation |
|---|---:|---:|---:|---:|---:|
| SBI | 0.492458 | 7.102188 | -0.584173 | 2.232 | -0.116 |
| HDFC | 0.632961 | 1.456397 | -0.732907 | 2.255 | -0.133 |
| ICICI | 0.582139 | 3.836242 | -0.181674 | 2.364 | -0.190 |
| Axis | 0.598209 | 5.328894 | 0.424862 | 2.375 | -0.189 |

The same regressors are used for each bank, so variance inflation factors (VIF) are identical: repo level **1.277**, repo change **1.105**, NIFTY return **1.495**, India VIX mean **1.362**, USD/INR change **1.433**. These are all below the common VIF threshold of five, so severe *linear* multicollinearity is not evident in the selected specification.

Durbin–Watson statistics around 2.23–2.38 and modest negative lag-1 residual correlations do not suggest a strong *positive* first-order residual persistence problem. They are descriptive diagnostics, **not** a substitute for formal Breusch–Godfrey tests, higher-lag checks, heteroskedasticity diagnostics or influence analysis. HAC(3) standard errors are already used in the original stored models; their independent recomputation was not performed in this audit.

**Multiple-testing findings and independent event arithmetic** are recorded in `docs/EVENT_WINDOW_AND_STATISTICAL_RECHECK_2026-10-21.md`.

**Publication caution:** This is an internal reproducibility and diagnostics recheck, not a full external audit. The manuscript `reports/RESEARCH_PAPER.md` still uses the old abbreviated “3-day” and “11-day” event labels; the exact t−1-to-t+1 and t−5-to-t+5 endpoint definitions in the correction memo should be applied before submitting the manuscript. The revised abstract file already uses the corrected description.

**Readiness:** Conditional. Further formal residual tests, price-source verification and final manuscript consistency review are outstanding.
