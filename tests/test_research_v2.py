"""Guard calendar covariance and the information boundary of new forecasts."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from run_research_v2 import calendar_hac, forecasts, FACTORS, TARGET, compounded_window


def sample():
    rng=np.random.default_rng(17)
    d=pd.DataFrame(rng.normal(size=(95,len(FACTORS))),columns=FACTORS)
    d['month']=pd.period_range('2015-01',periods=len(d),freq='M')
    d[TARGET]=1+d[FACTORS].to_numpy()@np.arange(1,len(FACTORS)+1)+rng.normal(size=len(d))
    return d


def test_calendar_hac_matches_contiguous_reference():
    d=sample();_,_,cov=calendar_hac(d)
    ref=sm.OLS(d[TARGET],sm.add_constant(d[FACTORS])).fit(cov_type='HAC',cov_kwds={'maxlags':3})
    np.testing.assert_allclose(cov,ref.cov_params(),atol=1e-12)


def test_omitted_months_do_not_become_neighbors():
    d=sample().drop(index=range(30,40))
    _,_,cov=calendar_hac(d)
    ref=sm.OLS(d[TARGET],sm.add_constant(d[FACTORS])).fit(cov_type='HAC',cov_kwds={'maxlags':3})
    assert not np.allclose(cov,ref.cov_params())


def test_forecasts_do_not_see_present_or_future_values():
    d=sample();before=forecasts(d)
    boundary=before.month.iloc[0]
    d.loc[d.month>=pd.Period(boundary),FACTORS+[TARGET]]=9999
    after=forecasts(d)
    np.testing.assert_allclose(before[['historical_mean','lagged_returns','lagged_macro']].iloc[0],after[['historical_mean','lagged_returns','lagged_macro']].iloc[0])
    assert (pd.PeriodIndex(before.last_training_month,freq='M')<pd.PeriodIndex(before.month,freq='M')).all()


def test_inclusive_event_windows_count_all_returns():
    closes=pd.Series(100*1.01**np.arange(25))
    for lo,hi in [(0,0),(-1,1),(-5,5)]:
        np.testing.assert_allclose(compounded_window(closes,12,lo,hi),100*(1.01**(hi-lo+1)-1),atol=1e-12)
