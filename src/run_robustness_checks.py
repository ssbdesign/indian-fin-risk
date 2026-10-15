"""Robustness: compare original HAC regressions with/without the 2020 shock months.

Run from project root: python src/run_robustness_checks.py
Inputs: data/processed/analysis_dataset.csv
Outputs: reports/results/robustness_coefficient_comparison.csv,
         reports/results/robustness_model_fit.csv,
         reports/figures/robustness_macro_coefficients.png
Does not overwrite original regression outputs or source datasets.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'processed' / 'analysis_dataset.csv'
RESULTS = ROOT / 'reports' / 'results'
FIGURES = ROOT / 'reports' / 'figures'
BANKS = ('SBIN.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS')
DISPLAY = {'SBIN.NS': 'SBI', 'HDFCBANK.NS': 'HDFC Bank',
           'ICICIBANK.NS': 'ICICI Bank', 'AXISBANK.NS': 'Axis Bank'}
TARGET = 'monthly_return_pct'
BASE = ['repo_rate_pct', 'repo_rate_change_pp', 'nifty_return_pct']
SPECS = {
    'baseline_common_sample': BASE,
    'expanded_same_month': BASE + ['india_vix_mean', 'usd_inr_change_pct'],
    'expanded_lagged': BASE + ['india_vix_lag1', 'usd_inr_change_pct_lag1'],
}
ALL_FACTORS = list(dict.fromkeys(f for fs in SPECS.values() for f in fs))
EXCLUDE_START = pd.Period('2020-03', freq='M')
EXCLUDE_END = pd.Period('2020-12', freq='M')


def prepare(raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    required = {'ticker', 'month_end_date', TARGET, *[f for f in ALL_FACTORS if f != 'nifty_return_pct']}
    missing = required - set(raw)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    df = raw.copy()
    df['month'] = pd.to_datetime(df['month_end_date'], errors='raise').dt.to_period('M')
    if df.duplicated(['ticker', 'month']).any():
        raise ValueError('Duplicate ticker-month rows; stop and inspect source data')
    nifty = df.loc[df['ticker'].eq('^NSEI'), ['month', TARGET]].rename(
        columns={TARGET: 'nifty_return_pct'}
    )
    if nifty.empty:
        raise ValueError('Missing ^NSEI observations for market control')
    groups = {}
    for ticker in BANKS:
        bank = df.loc[df['ticker'].eq(ticker)].merge(
            nifty, on='month', how='left', validate='one_to_one'
        ).sort_values('month')
        cols = [TARGET, *ALL_FACTORS]
        bank[cols] = bank[cols].apply(pd.to_numeric, errors='coerce')
        bank = bank.dropna(subset=cols).copy()
        if len(bank) < 36:
            raise ValueError(f'{ticker}: only {len(bank)} complete months')
        groups[ticker] = bank
    return groups


def estimate(groups: dict[str, pd.DataFrame]):
    coef_rows, model_rows = [], []
    for ticker, complete in groups.items():
        for label, bank in (
            ('full_sample', complete),
            ('exclude_mar_dec_2020', complete.loc[~complete['month'].between(EXCLUDE_START, EXCLUDE_END)]),
        ):
            if len(bank) < 36:
                raise ValueError(f'{ticker}, {label}: insufficient complete observations')
            for spec, factors in SPECS.items():
                x = sm.add_constant(bank[factors], has_constant='add')
                fitted = sm.OLS(bank[TARGET], x).fit(cov_type='HAC', cov_kwds={'maxlags': 3})
                common = {'bank': DISPLAY[ticker], 'ticker': ticker, 'sample': label,
                          'specification': spec, 'observations': int(fitted.nobs),
                          'sample_start': str(bank['month'].iloc[0]),
                          'sample_end': str(bank['month'].iloc[-1])}
                model_rows.append({**common, 'r_squared': fitted.rsquared,
                                   'adjusted_r_squared': fitted.rsquared_adj})
                ci = fitted.conf_int()
                for factor in factors:
                    coef_rows.append({**common, 'factor': factor,
                                      'coefficient': fitted.params[factor],
                                      'hac_std_error': fitted.bse[factor],
                                      'p_value': fitted.pvalues[factor],
                                      'ci_lower': ci.loc[factor].iloc[0],
                                      'ci_upper': ci.loc[factor].iloc[1]})
    return pd.DataFrame(coef_rows), pd.DataFrame(model_rows)


def plot(coefs: pd.DataFrame):
    subset = coefs.loc[coefs['specification'].eq('expanded_same_month') &
                       coefs['factor'].isin(['repo_rate_change_pp', 'india_vix_mean', 'usd_inr_change_pct'])]
    labels = {'repo_rate_change_pp': 'Repo-rate change (pp)',
              'india_vix_mean': 'India VIX monthly mean',
              'usd_inr_change_pct': 'USD/INR monthly change (%)'}
    fig, axs = plt.subplots(3, 1, figsize=(11, 11), sharex=True)
    for ax, (factor, title) in zip(axs, labels.items()):
        series = subset[subset['factor'].eq(factor)]
        ypos = np.arange(len(BANKS))
        for sample, offset, marker in [('full_sample', -0.12, 'o'), ('exclude_mar_dec_2020', 0.12, 's')]:
            temp = series[series['sample'].eq(sample)].set_index('bank').reindex([DISPLAY[b] for b in BANKS])
            vals = temp['coefficient'].to_numpy(dtype=float)
            low = temp['ci_lower'].to_numpy(dtype=float)
            high = temp['ci_upper'].to_numpy(dtype=float)
            ax.errorbar(vals, ypos + offset, xerr=np.vstack([vals-low, high-vals]),
                        fmt=marker, capsize=3, label='Full sample' if sample == 'full_sample' else 'Exclude Mar–Dec 2020')
        ax.axvline(0, color='grey', linestyle='--', linewidth=1)
        ax.set_yticks(ypos, [DISPLAY[b] for b in BANKS])
        ax.set_title(title)
        ax.grid(axis='x', alpha=0.2)
    axs[0].legend(loc='best')
    axs[-1].set_xlabel('OLS coefficient, 95% HAC confidence interval')
    fig.suptitle('Sensitivity to excluding March–December 2020 (same-month model)')
    fig.tight_layout()
    path = FIGURES / 'robustness_macro_coefficients.png'
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return path


def main():
    if not INPUT.is_file():
        raise FileNotFoundError(f'Missing {INPUT}; do not recreate or download data yet')
    groups = prepare(pd.read_csv(INPUT))
    coefficients, fits = estimate(groups)
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    coeff_path = RESULTS / 'robustness_coefficient_comparison.csv'
    fit_path = RESULTS / 'robustness_model_fit.csv'
    coefficients.to_csv(coeff_path, index=False)
    fits.to_csv(fit_path, index=False)
    fig_path = plot(coefficients)
    print('Robustness analysis completed. Original results were not modified.')
    print('Comparison: full 2015-02–2025-12 vs excluding 2020-03–2020-12')
    for ticker, data in groups.items():
        kept = ~data['month'].between(EXCLUDE_START, EXCLUDE_END)
        print(f'{DISPLAY[ticker]}: full={len(data)} months, excluded={int((~kept).sum())}, remaining={int(kept.sum())}')
    print('\nExpanded same-month coefficients (full vs exclusion):')
    key = coefficients[coefficients['specification'].eq('expanded_same_month') &
                       coefficients['factor'].isin(['repo_rate_change_pp', 'india_vix_mean', 'usd_inr_change_pct'])]
    print(key[['bank','sample','factor','coefficient','p_value']].round(4).to_string(index=False))
    print(f'\nSaved {coeff_path}\nSaved {fit_path}\nSaved {fig_path}')


if __name__ == '__main__':
    main()
