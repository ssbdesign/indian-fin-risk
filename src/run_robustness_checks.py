"""COVID-era exclusion sensitivity test for existing expanded macro regressions.

Run: python src/run_robustness_checks.py
Uses the same HAC(3) OLS specifications and common-case filtering as the
primary analysis. Writes separate files, without overwriting its results.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from run_expanded_macro_analysis import INPUT, ROOT, BANKS, estimate_models

OUT = ROOT / "reports" / "results"
FIG = ROOT / "reports" / "figures"
EXCLUSION_START, EXCLUSION_END = "2020-03", "2020-12"
LABELS = {"SBIN.NS": "SBI", "HDFCBANK.NS": "HDFC Bank",
          "ICICIBANK.NS": "ICICI Bank", "AXISBANK.NS": "Axis Bank"}
KEY = ("repo_rate_change_pp", "india_vix_mean", "usd_inr_change_pct")


def calculate(raw):
    dates = pd.to_datetime(raw["month_end_date"]).dt.to_period("M")
    outside = ~dates.between(pd.Period(EXCLUSION_START), pd.Period(EXCLUSION_END))
    pairs = [
        ("full_sample", raw),
        ("exclude_mar_dec_2020", raw.loc[outside].copy()),
    ]
    parts = []
    for sample, frame in pairs:
        result = estimate_models(frame)
        result.insert(0, "sample", sample)
        result.insert(0, "bank", result["ticker"].map(LABELS))
        parts.append(result)
    all_coefs = pd.concat(parts, ignore_index=True)
    fit_cols = ["bank", "ticker", "sample", "specification", "observations",
                "sample_start", "sample_end", "r_squared", "adjusted_r_squared"]
    fits = all_coefs[fit_cols].drop_duplicates().reset_index(drop=True)
    return all_coefs, fits


def save_plot(coefs):
    focus = coefs.loc[(coefs["specification"] == "expanded_same_month")
                      & coefs["factor"].isin(KEY)]
    fig, axes = plt.subplots(3, 1, figsize=(10, 11), sharex=False)
    for ax, factor in zip(axes, KEY):
        for sample, offset, marker, label in [
            ("full_sample", -0.11, "o", "All months"),
            ("exclude_mar_dec_2020", 0.11, "s", "Excluding Mar-Dec 2020"),
        ]:
            tmp = focus[(focus["factor"] == factor) &
                        (focus["sample"] == sample)].set_index("ticker").reindex(BANKS)
            vals = tmp["coefficient"].to_numpy(dtype=float)
            lo = tmp["ci_lower"].to_numpy(dtype=float)
            hi = tmp["ci_upper"].to_numpy(dtype=float)
            y = np.arange(len(BANKS)) + offset
            ax.errorbar(vals, y, xerr=np.vstack([vals-lo, hi-vals]),
                        fmt=marker, capsize=3, label=label)
        ax.axvline(0, color="gray", linestyle="--", linewidth=0.8)
        ax.set_yticks(range(len(BANKS)), [LABELS[b] for b in BANKS])
        ax.set_title(factor)
        ax.set_xlabel("Coefficient and 95% HAC(3) confidence interval")
        ax.grid(axis="x", alpha=0.2)
    axes[0].legend(fontsize=8)
    fig.suptitle("Sensitivity to excluding March-December 2020")
    fig.tight_layout()
    FIG.mkdir(parents=True, exist_ok=True)
    path = FIG / "robustness_macro_coefficients.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing existing combined data: {INPUT}")
    coefs, fits = calculate(pd.read_csv(INPUT))
    OUT.mkdir(parents=True, exist_ok=True)
    coefs.to_csv(OUT / "robustness_coefficient_comparison.csv", index=False)
    fits.to_csv(OUT / "robustness_model_fit.csv", index=False)
    chart = save_plot(coefs)
    key = coefs[(coefs.specification == "expanded_same_month") &
                coefs.factor.isin(KEY)]
    print(key[["bank", "sample", "factor", "observations",
               "coefficient", "p_value"]].round(4).to_string(index=False))
    print("Saved robustness comparisons and figure:", chart)


if __name__ == "__main__":
    main()
