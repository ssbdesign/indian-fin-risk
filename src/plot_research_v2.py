"""Render final research figures from the generated CSVs."""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run_robustness_checks import BANKS, DISPLAY
ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'reports/v2/results'
FIG=ROOT/'reports/v2/figures'


def main():
    FIG.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#333333','figure.facecolor':'white'})
    d=pd.read_csv(RESULTS/'macro_multiple_testing.csv')
    fig,axs=plt.subplots(1,2,figsize=(10,3.3))
    for ax,factor,title,scale in [(axs[0],'repo_rate_change_pp','Repo change of 0.25 percentage points',.25),(axs[1],'usd_inr_change_pct','USD/INR increase of 1 percent',1)]:
        z=d[d.factor.eq(factor)].set_index('ticker').reindex(BANKS)
        y=np.arange(4)
        for i,(_,r) in enumerate(z.iterrows()):
            ax.errorbar(r.coefficient*scale,i,xerr=np.array([[r.coefficient-r.ci_lower],[r.ci_upper-r.coefficient]])*scale,fmt='o',capsize=3,color='#1a6774' if r.holm_p_16<.05 else '#5b6470')
        ax.axvline(0,color='#999999',linewidth=.8);ax.set_yticks(y,[DISPLAY[b] for b in BANKS]);ax.invert_yaxis();ax.set_title(title,fontsize=10);ax.set_xlabel('Conditional monthly return difference (pp)');ax.grid(axis='x',alpha=.15)
    fig.tight_layout();fig.savefig(FIG/'conditional_associations.png',dpi=190);plt.close(fig)
    d=pd.read_csv(RESULTS/'forecast_metrics.csv')
    fig,ax=plt.subplots(figsize=(9,3.0));y=np.arange(4)
    for off,model,label,color in [(-.23,'historical_mean','Historical mean','#aab0b7'),(0,'lagged_returns','Lagged returns','#597386'),(.23,'lagged_macro','Lagged macro model','#1a6774')]:
        z=d[d.model.eq(model)].set_index('ticker').reindex(BANKS);ax.barh(y+off,z.rmse_pp,height=.21,label=label,color=color)
    ax.set_yticks(y,[DISPLAY[b] for b in BANKS]);ax.invert_yaxis();ax.set_xlabel('Forecast RMSE (percentage points, lower is better)');ax.legend(loc='upper left',bbox_to_anchor=(0,1.17),ncol=3,frameon=False);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    fig.tight_layout();fig.savefig(FIG/'forecast_rmse.png',dpi=190);plt.close(fig)
    print('Rendered two figures')


if __name__=='__main__':main()
