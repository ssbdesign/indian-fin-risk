"""Extend the frozen research snapshot without downloading or changing inputs.

Run: python src/run_research_v2.py
Exploratory extensions selected after inspecting the original findings.
"""
from pathlib import Path
import hashlib
import json
import platform
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor
from run_expanded_macro_analysis import estimate_models
from run_robustness_checks import prepare, BANKS, DISPLAY, SPECS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/v2/results'
TARGET = 'monthly_return_pct'
FACTORS = SPECS['expanded_same_month']
MACRO = [x for x in FACTORS if x != 'nifty_return_pct']


def calendar_hac(frame, factors=FACTORS, lags=3):
    """OLS with Bartlett HAC scores spaced by calendar month, not retained rows.

    Zero scores for omitted months preserve actual distances across exclusions.
    No small-sample multiplier, matching statsmodels' original HAC convention.
    """
    frame = frame.sort_values('month')
    x = sm.add_constant(frame[factors], has_constant='add')
    model = sm.OLS(frame[TARGET], x).fit()
    score = x.to_numpy() * np.asarray(model.resid)[:, None]
    grid = pd.period_range(frame.month.min(), frame.month.max(), freq='M')
    scores = pd.DataFrame(score, index=pd.PeriodIndex(frame.month), columns=x.columns).reindex(grid, fill_value=0).to_numpy()
    meat = scores.T @ scores
    for lag in range(1, min(lags, len(scores)-1)+1):
        cross = scores[lag:].T @ scores[:-lag]
        meat += (1-lag/(lags+1)) * (cross+cross.T)
    bread = np.asarray(model.normalized_cov_params)
    cov = bread @ meat @ bread
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    p = 2 * stats.norm.sf(np.abs(np.asarray(model.params)/se))
    table = pd.DataFrame({'factor':x.columns, 'coefficient':model.params.to_numpy(), 'standard_error':se, 'p_value':p})
    table['ci_lower'] = table.coefficient - stats.norm.ppf(.975)*se
    table['ci_upper'] = table.coefficient + stats.norm.ppf(.975)*se
    return model, table, cov


def forecasts(bank, initial=60):
    """Expanding-origin forecasts using previous-calendar-month inputs only."""
    bank = bank.set_index('month').sort_index()
    bank = bank.reindex(pd.period_range(bank.index.min(), bank.index.max(), freq='M'))
    predictors = [TARGET, *FACTORS]
    lagged = bank[predictors].shift(1).add_prefix('lag_')
    data = bank[[TARGET]].join(lagged).dropna()
    base = ['lag_'+TARGET, 'lag_nifty_return_pct']
    expanded = ['lag_'+c for c in predictors]
    rows=[]
    for i in range(initial, len(data)):
        train, test = data.iloc[:i], data.iloc[i:i+1]
        row={'month':str(data.index[i]), 'last_training_month':str(data.index[i-1]), 'training_n':len(train), 'actual':test[TARGET].iloc[0], 'historical_mean':train[TARGET].mean()}
        for name, cols in [('lagged_returns',base),('lagged_macro',expanded)]:
            fit=sm.OLS(train[TARGET],sm.add_constant(train[cols],has_constant='add')).fit()
            row[name]=float(fit.predict(sm.add_constant(test[cols],has_constant='add')).iloc[0])
        rows.append(row)
    return pd.DataFrame(rows)


def compounded_window(closes, event_index, first_day, last_day):
    """Compound inclusive daily returns; first return needs the prior close."""
    start, end = event_index + first_day - 1, event_index + last_day
    if start < 0 or end >= len(closes):
        raise ValueError('Incomplete event window')
    return 100 * (closes.iloc[end] / closes.iloc[start] - 1)


def corrected_event_analysis():
    frames=[]
    for name in ['SBI','HDFC','ICICI','AXIS','NIFTY50']:
        frame=pd.read_csv(ROOT/f'data/processed/validated/{name}_daily.csv',parse_dates=['date'])
        frames.append(frame.set_index('date').close.rename(name))
    daily=pd.concat(frames,axis=1,join='inner').sort_index()
    events=pd.read_csv(ROOT/'data/processed/rbi_policy_events_2015_2025.csv',parse_dates=['effective_date'])
    positions=[daily.index.get_loc(d) for d in events.effective_date]
    detail=[]
    for pos,(_,event) in zip(positions,events.iterrows()):
        for name,lo,hi in [('Event day',0,0),('3 daily returns',-1,1),('11 daily returns',-5,5)]:
            values=compounded_window(daily,pos,lo,hi)
            for ticker,value in values.items():
                detail.append({'ticker':ticker,'window':name,'effective_date':str(event.effective_date.date()),'start_close_date':str(daily.index[pos+lo-1].date()),'end_close_date':str(daily.index[pos+hi].date()),'daily_return_count':hi-lo+1,'return_pct':value,'bank_minus_index_pp':value-values['NIFTY50'],'overlapping_event':any(p!=pos and abs(p-pos)<=hi-lo for p in positions)})
    detail=pd.DataFrame(detail);detail.to_csv(OUT/'corrected_event_detail.csv',index=False)
    rows=[]
    for (ticker,window),group in detail.groupby(['ticker','window']):
        for kind,column in [('raw','return_pct'),('bank_minus_index','bank_minus_index_pp')]:
            if ticker=='NIFTY50' and kind=='bank_minus_index':continue
            x=group[column];test=stats.ttest_1samp(x,0);ci=stats.t.interval(.95,len(x)-1,loc=x.mean(),scale=stats.sem(x))
            rows.append({'ticker':ticker,'window':window,'family':kind,'n':len(x),'mean_pp':x.mean(),'ci_lower':ci[0],'ci_upper':ci[1],'p_value':test.pvalue,'overlapping_events':int(group.overlapping_event.sum())})
    result=pd.DataFrame(rows)
    for _,idx in result.groupby('family').groups.items():
        result.loc[idx,'bh_q_within_family']=multipletests(result.loc[idx,'p_value'],method='fdr_bh')[1]
        result.loc[idx,'holm_p_within_family']=multipletests(result.loc[idx,'p_value'],method='holm')[1]
    result['bh_q_27']=multipletests(result.p_value,method='fdr_bh')[1]
    result['holm_p_27']=multipletests(result.p_value,method='holm')[1]
    legacy=pd.read_csv(OUT/'event_multiple_testing.csv')
    extra=legacy.loc[legacy.window.ne('Event day'),['ticker','window','family','p_value']].copy()
    extra['window']='legacy_'+extra.window
    broader=pd.concat([result[['ticker','window','family','p_value']],extra],ignore_index=True)
    broader['holm_p_45']=multipletests(broader.p_value,method='holm')[1]
    broader['bh_q_45']=multipletests(broader.p_value,method='fdr_bh')[1]
    result=result.merge(broader[['ticker','window','family','holm_p_45','bh_q_45']],on=['ticker','window','family'],how='left')
    result.to_csv(OUT/'corrected_event_tests.csv',index=False)
    broader.to_csv(OUT/'event_endpoint_sensitivity.csv',index=False)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(ROOT/'data/processed/analysis_dataset.csv')
    groups=prepare(raw)
    reproduced=estimate_models(raw)
    old=pd.read_csv(ROOT/'reports/results/expanded_macro_regressions.csv')
    keys=['ticker','specification','factor']
    match=reproduced.merge(old,on=keys,suffixes=('_new','_old'),validate='one_to_one')
    comparison=[]
    for col in ['coefficient','p_value','r_squared','hac_std_error']:
        error=float((match[col+'_new']-match[col+'_old']).abs().max())
        comparison.append({'quantity':col,'maximum_absolute_difference':error,'matches_to_4_decimals':error<.000051})
    assert len(match)==len(reproduced)==len(old)
    assert all(x['matches_to_4_decimals'] for x in comparison), comparison
    pd.DataFrame(comparison).to_csv(OUT/'reproduction.csv',index=False)
    reproduced.to_csv(OUT/'reproduced_models.csv',index=False)
    primary=reproduced.loc[reproduced.specification.eq('expanded_same_month') & reproduced.factor.isin(MACRO)].copy()
    primary['bh_q_16']=multipletests(primary.p_value,method='fdr_bh')[1]
    primary['holm_p_16']=multipletests(primary.p_value,method='holm')[1]
    all_macro=reproduced.loc[reproduced.factor.ne('nifty_return_pct')].copy()
    all_macro['bh_q_40']=multipletests(all_macro.p_value,method='fdr_bh')[1]
    all_macro['holm_p_40']=multipletests(all_macro.p_value,method='holm')[1]
    primary=primary.merge(all_macro[keys+['bh_q_40','holm_p_40']],on=keys)
    primary.to_csv(OUT/'macro_multiple_testing.csv',index=False)
    all_macro.to_csv(OUT/'all_model_multiple_testing.csv',index=False)
    sensitivity=[]; joint=[]; diagnostics=[]; predictions=[]; metrics=[]; breaks=[]
    for ticker,bank in groups.items():
        fit,_,cov=calendar_hac(bank)
        for lags in [0,1,3,6,12]:
            _, table,_=calendar_hac(bank,lags=lags)
            sensitivity.extend(table.assign(ticker=ticker,exercise='HAC_bandwidth',variant=str(lags),n=len(bank)).to_dict('records'))
        scenarios={'exclude_mar_dec_2020':bank.loc[~bank.month.between(pd.Period('2020-03'),pd.Period('2020-12'))]}
        scenarios.update({f'omit_{year}':bank.loc[bank.month.dt.year.ne(year)] for year in sorted(bank.month.dt.year.unique())})
        for name,subset in scenarios.items():
            _,table,_=calendar_hac(subset)
            sensitivity.extend(table.assign(ticker=ticker,exercise='calendar_exclusion',variant=name,n=len(subset)).to_dict('records'))
        for name,cols in [('without_repo_level',[x for x in FACTORS if x!='repo_rate_pct']),('vix_change',['repo_rate_pct','repo_rate_change_pp','nifty_return_pct','india_vix_change','usd_inr_change_pct'])]:
            _,table,_=calendar_hac(bank,cols)
            sensitivity.extend(table.assign(ticker=ticker,exercise='specification',variant=name,n=len(bank)).to_dict('records'))
        names=fit.params.index.tolist()
        ids=[names.index('india_vix_mean'),names.index('usd_inr_change_pct')]
        beta=np.asarray(fit.params)[ids]; variance=cov[np.ix_(ids,ids)]
        w=float(beta@np.linalg.pinv(variance)@beta)
        base=sm.OLS(bank[TARGET],sm.add_constant(bank[SPECS['baseline_common_sample']],has_constant='add')).fit()
        joint.append({'ticker':ticker,'wald_chi2':w,'df':2,'p_value':stats.chi2.sf(w,2),'incremental_r2':fit.rsquared-base.rsquared,'incremental_adjusted_r2':fit.rsquared_adj-base.rsquared_adj,'partial_r2':(fit.rsquared-base.rsquared)/(1-base.rsquared)})
        x=sm.add_constant(bank[FACTORS],has_constant='add')
        for i,col in enumerate(x.columns):
            if col!='const': diagnostics.append({'ticker':ticker,'factor':col,'vif':variance_inflation_factor(x.to_numpy(),i),'max_cooks_distance':fit.get_influence().cooks_distance[0].max(),'max_cooks_month':str(bank.month.iloc[np.argmax(fit.get_influence().cooks_distance[0])])})
        # Exploratory break at 2020-01: all slopes and intercept can change.
        interaction=bank.copy();interaction['post2020']=(bank.month>=pd.Period('2020-01')).astype(float)
        for col in FACTORS: interaction['post_'+col]=interaction.post2020*interaction[col]
        extended=FACTORS+['post2020']+['post_'+c for c in FACTORS]
        bf,_,bc=calendar_hac(interaction,extended)
        bid=[list(bf.params.index).index(c) for c in extended if c.startswith('post')]
        beta=np.asarray(bf.params)[bid];cv=bc[np.ix_(bid,bid)]
        w=float(beta@np.linalg.pinv(cv)@beta)
        breaks.append({'ticker':ticker,'break_month':'2020-01','wald_chi2':w,'df':len(bid),'p_value':stats.chi2.sf(w,len(bid)),'pre_n':int((interaction.post2020==0).sum()),'post_n':int(interaction.post2020.sum())})
        pred=forecasts(bank).assign(ticker=ticker);predictions.append(pred)
        mse_mean=np.mean((pred.actual-pred.historical_mean)**2)
        for name in ['historical_mean','lagged_returns','lagged_macro']:
            err=pred.actual-pred[name]
            metrics.append({'ticker':ticker,'model':name,'n':len(pred),'start':pred.month.min(),'end':pred.month.max(),'rmse_pp':np.sqrt(np.mean(err**2)),'mae_pp':np.mean(np.abs(err)),'oos_r2_vs_mean':1-np.mean(err**2)/mse_mean})
    for rows,name in [(joint,'joint_added_factors'),(breaks,'break_tests')]:
        df=pd.DataFrame(rows);df['holm_p_4']=multipletests(df.p_value,method='holm')[1];df.to_csv(OUT/(name+'.csv'),index=False)
    pd.DataFrame(sensitivity).to_csv(OUT/'sensitivity.csv',index=False)
    pd.DataFrame(diagnostics).to_csv(OUT/'diagnostics.csv',index=False)
    pd.concat(predictions).to_csv(OUT/'forecast_predictions.csv',index=False)
    pd.DataFrame(metrics).to_csv(OUT/'forecast_metrics.csv',index=False)
    events=[]
    for name,file in [('raw','policy_event_descriptive_tests.csv'),('bank_minus_index','policy_event_market_comparison.csv')]:
        df=pd.read_csv(ROOT/'reports/results'/file);df['family']=name
        df['bh_q_within_family']=multipletests(df.p_value,method='fdr_bh')[1]
        df['holm_p_within_family']=multipletests(df.p_value,method='holm')[1]
        events.append(df)
    events=pd.concat(events,ignore_index=True)
    events['bh_q_27']=multipletests(events.p_value,method='fdr_bh')[1]
    events['holm_p_27']=multipletests(events.p_value,method='holm')[1]
    events.to_csv(OUT/'event_multiple_testing.csv',index=False)
    corrected_event_analysis()
    files=['data/processed/analysis_dataset.csv','data/processed/monthly_returns_all.csv','reports/results/expanded_macro_regressions.csv','reports/results/policy_event_descriptive_tests.csv','reports/results/policy_event_market_comparison.csv']
    files += ['data/processed/rbi_policy_events_2015_2025.csv'] + [str(p.relative_to(ROOT)) for p in sorted((ROOT/'data/processed/validated').glob('*_daily.csv'))]
    manifest={'source_commit':'9ca8395a8783da44602ca3e9ee531d291321f7f0','run_date':'2026-11-12','versions':{'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'statsmodels':statsmodels.__version__,'scipy':scipy.__version__},'inputs':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},'raw_rows':len(raw),'independent_macro_months':len(next(iter(groups.values()))),'outputs':[p.name for p in sorted(OUT.glob('*.csv'))]}
    (OUT/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Reproduced original models; completed corrections, calendar HAC sensitivity, break tests and expanding forecasts.')
    print(primary[['ticker','factor','p_value','bh_q_16','holm_p_16']].round(5).to_string(index=False))
    print(pd.DataFrame(metrics).round(4).to_string(index=False))


if __name__=='__main__':
    main()
