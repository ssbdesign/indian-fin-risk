"""Create research tables and figures from existing project CSVs; no downloads."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'processed' / 'analysis_dataset.csv'
REG = ROOT / 'reports' / 'results' / 'expanded_macro_regressions.csv'
RESULTS = ROOT / 'reports' / 'results'
FIGURES = ROOT / 'reports' / 'figures'
LABELS = {'SBIN.NS':'SBI', 'HDFCBANK.NS':'HDFC Bank', 'ICICIBANK.NS':'ICICI Bank', 'AXISBANK.NS':'Axis Bank', '^NSEI':'NIFTY 50'}
BANKS = list(LABELS)[:4]
MACRO = ['repo_rate_pct', 'repo_rate_change_pp', 'india_vix_mean', 'usd_inr_change_pct']

def savefig(name):
    plt.tight_layout()
    plt.savefig(FIGURES / name, dpi=220, bbox_inches='tight')
    plt.close()

def main():
    for path in (DATA, REG):
        if not path.exists():
            raise FileNotFoundError(f'Missing {path}; use your existing generated file')
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    reg = pd.read_csv(REG)
    needed = {'ticker','month_end_date','monthly_return_pct', *MACRO}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    df['month'] = pd.to_datetime(df['month_end_date']).dt.to_period('M')
    if df.duplicated(['ticker','month']).any():
        raise ValueError('Duplicate ticker-month entries')
    df = df[df.ticker.isin(LABELS)].copy()
    df['instrument'] = df.ticker.map(LABELS)
    df['monthly_return_pct'] = pd.to_numeric(df.monthly_return_pct, errors='coerce')
    for factor in MACRO:
        df[factor] = pd.to_numeric(df[factor], errors='coerce')
    df = df.sort_values(['ticker','month'])

    # Full available stock-return history; count is based on nonmissing returns.
    s = df.groupby('instrument')['monthly_return_pct'].agg(
        observations='count', mean_return_pct='mean', median_return_pct='median',
        volatility_pct='std', min_return_pct='min', max_return_pct='max'
    ).reindex(list(LABELS.values()))
    s['annualized_volatility_pct'] = s['volatility_pct'] * np.sqrt(12)
    s.round(4).to_csv(RESULTS/'descriptive_statistics_2010_2025.csv')

    # Same 131-month window as the saved regression output.
    reg_start = pd.Period(str(reg['sample_start'].iloc[0]), freq='M')
    reg_end = pd.Period(str(reg['sample_end'].iloc[0]), freq='M')
    if (reg['sample_start'] != str(reg_start)).any() or (reg['sample_end'] != str(reg_end)).any():
        raise ValueError('Regression sample periods differ; inspect results before charting')
    common = df[df['month'].between(reg_start,reg_end)].copy()
    ret = common.pivot(index='month',columns='instrument',values='monthly_return_pct')
    ordered = list(LABELS.values())
    ret = ret.reindex(columns=ordered)
    ret.corr().round(4).to_csv(RESULTS/'stock_return_correlations_2015_2025.csv')
    market = ret['NIFTY 50'].rename('nifty_return_pct')
    bank = common[common.ticker.isin(BANKS)].copy().join(market,on='month')
    factors = ['monthly_return_pct','nifty_return_pct',*MACRO]
    corr = pd.concat({LABELS[t]:g[factors].corr().loc['monthly_return_pct'] for t,g in bank.groupby('ticker')},axis=1).T
    corr.index.name = 'bank'
    corr.round(4).to_csv(RESULTS/'bank_macro_correlations_2015_2025.csv')

    plt.figure(figsize=(10,5))
    s['volatility_pct'].plot(kind='bar')
    plt.ylabel('Monthly return standard deviation (%)')
    plt.title('Monthly return volatility by instrument (2010–2025)')
    plt.xticks(rotation=20,ha='right')
    savefig('monthly_volatility_comparison.png')

    plt.figure(figsize=(10,5))
    s['mean_return_pct'].plot(kind='bar')
    plt.axhline(0,color='gray',linewidth=0.8)
    plt.ylabel('Average monthly return (%)')
    plt.title('Average monthly returns by instrument (2010–2025)')
    plt.xticks(rotation=20,ha='right')
    savefig('mean_monthly_returns.png')

    # Plot each macro series only once (same monthly value is repeated across tickers).
    macro = common[common.ticker.eq('^NSEI')].set_index('month').sort_index()
    if macro.empty:
        raise ValueError('NIFTY 50 data missing for macro timeline')
    dates = macro.index.to_timestamp()
    for col, title, ylabel, filename in [
        ('repo_rate_pct','RBI repo rate','Repo rate (%)','repo_rate_timeline.png'),
        ('india_vix_mean','India VIX monthly average','India VIX level','india_vix_timeline.png'),
        ('usd_inr_change_pct','Monthly USD/INR change','Monthly change (%)','usd_inr_changes.png'),
    ]:
        plt.figure(figsize=(10,4.5))
        plt.plot(dates,macro[col],linewidth=1.6)
        plt.axhline(0,color='gray',linewidth=.6)
        plt.title(f'{title} ({reg_start} to {reg_end})')
        plt.ylabel(ylabel)
        plt.xlabel('Month')
        savefig(filename)

    # A zero-centered coefficient chart; confidence intervals are HAC-based.
    sub = reg[(reg.specification=='expanded_same_month') & reg.factor.isin(['usd_inr_change_pct','india_vix_mean'])].copy()
    sub['bank'] = sub.ticker.map(LABELS)
    for factor, filename, title in [
        ('usd_inr_change_pct','usd_inr_regression_coefficients.png','USD/INR change'),
        ('india_vix_mean','india_vix_regression_coefficients.png','India VIX'),
    ]:
        t = sub[sub.factor.eq(factor)].set_index('bank').reindex([LABELS[x] for x in BANKS])
        if t[['coefficient','ci_lower','ci_upper']].isna().any().any():
            raise ValueError(f'Missing coefficient or interval for {factor}')
        x = t['coefficient'].to_numpy()
        low = x - t['ci_lower'].to_numpy()
        high = t['ci_upper'].to_numpy() - x
        plt.figure(figsize=(8,4.5))
        plt.errorbar(x,range(len(t)),xerr=[low,high],fmt='o',capsize=4)
        plt.yticks(range(len(t)),t.index)
        plt.axvline(0,color='gray',linestyle='--')
        plt.xlabel('Coefficient (95% HAC confidence interval)')
        plt.title(f'{title}: same-month regression coefficients')
        savefig(filename)

    # One row per bank and model (rather than repeated factor rows).
    fits = reg.drop_duplicates(['ticker','specification'])[
        ['ticker','specification','observations','r_squared','adjusted_r_squared','sample_start','sample_end']
    ].copy()
    fits['bank'] = fits.ticker.map(LABELS)
    fits.drop(columns='ticker').to_csv(RESULTS/'model_fit_comparison.csv',index=False)
    print('Done. Created 4 tables and 7 charts.')
    print('Tables:',RESULTS)
    print('Figures:',FIGURES)
    print(f'Regression comparison period: {reg_start} through {reg_end}')
    print('Full stock descriptive observations:',s['observations'].to_dict())

if __name__ == '__main__':
    main()
