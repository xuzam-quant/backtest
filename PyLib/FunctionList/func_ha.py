import numpy as np
import pandas as pd
from statsmodels.distributions.empirical_distribution import ECDF
    
#%% ha bar
def func_ha_bar(t, o, h, l ,c):
    ho,hh,hl,hc = o.copy(), h.copy(), l.copy(), c.copy()
    for i in range(1,len(t)):
        hc[i] = (o[i]+h[i]+l[i]+c[i])/4
        ho[i] = (ho[i-1]+hc[i-1])/2
        hh[i] = max(ho[i],hc[i],h[i])
        hl[i] = min(ho[i],hc[i],l[i])
    df_bar = pd.DataFrame({'open':ho,'high':hh,'low':hl,'close':hc}, index=t)        
    return df_bar

#%% ps
def func_ps_level(ha_open, ha_close, ha_bar_percent_level):    
    ha_bar_size = ha_close - ha_open
    idx_positive_bar = np.where(ha_bar_size>0)[0]
    idx_negative_bar = np.where(ha_bar_size<0)[0]
    ha_bar_positive_size = ha_bar_size[idx_positive_bar]
    ha_bar_negative_size = ha_bar_size[idx_negative_bar]            
    positive = ECDF(ha_bar_positive_size)
    negative = ECDF(-ha_bar_negative_size)
    ha_positive_size, ha_positive_cdf = positive.x, positive.y    
    ha_negative_size, ha_negative_cdf = negative.x, negative.y
        
    n_level = len(ha_bar_percent_level)
    ha_ps_positive_level = np.zeros(n_level)
    ha_ps_negative_level = np.zeros(n_level)
    for i in range(n_level):
        ha_ps_positive_level[i] = ha_positive_size[np.where(ha_positive_cdf<=ha_bar_percent_level[i])[0][-1]]
        ha_ps_negative_level[i] = -ha_negative_size[np.where(ha_negative_cdf<=ha_bar_percent_level[i])[0][-1]]
    return ha_ps_positive_level, ha_ps_negative_level
        
def func_ha_ps(t, ha_open, ha_close, len_ps, ha_bar_percent_level=[0,35,0.5,0.95,0.97]):
    n = len(ha_close)
    ps = np.zeros(n)    
    ha_range = ha_close - ha_open    
    for i in range(len_ps, n):
        ha_ps_positive_level, ha_ps_negative_level = func_ps_level(ha_open[i-len_ps:i], ha_close[i-len_ps:i], ha_bar_percent_level)
        if ha_range[i]>0:
            ha_ps_temp = np.where(ha_range[i]<=ha_ps_positive_level)[0]
            if len(ha_ps_temp)!=0:
                ps[i] = ha_ps_temp[0]
            else:
                ps[i] = len(ha_ps_positive_level)
        elif ha_range[i]<0:
            ha_ps_temp = np.where(ha_range[i]>=ha_ps_negative_level)[0]
            if len(ha_ps_temp)!=0:
                ps[i] = - ha_ps_temp[0]
            else:
                ps[i] = - len(ha_ps_positive_level)    
    df_barps = pd.DataFrame({'ps':ps}, index=t)
    return df_barps

#%% bar count
def func_ha_number(t, ha_open, ha_close, ps):
    n = len(ha_close)
    bar_idx_live = np.zeros(n)
    
    ha_sign = np.sign(ha_close-ha_open)
    idx_first = np.where(np.isnan(ps)==0)[0][0]
    bar_stats = np.zeros((n,3))
    
    bar_pass = 0
    bar_pass_cut = 2
    ps_pass_cut = 2
    idx = 0    
    for i in range(idx_first, n):
        if ha_sign[i]==1:
            if idx>=0:
                idx = idx + 1
                bar_stats[i,0] = idx
                bar_idx_live[i] = idx
                bar_pass = 0
            else:
                if ps[i]<ps_pass_cut and bar_pass<bar_pass_cut:
                    idx = idx - 1
                    bar_stats[i,0] = idx
                    bar_idx_live[i] = idx
                    bar_pass = bar_pass + 1*(ps[i]!=0)
                else:
                    bar_stats[i-bar_pass,1] = idx + bar_pass
                    idx = 1 + bar_pass
                    bar_stats[i,0] = idx
                    bar_idx_live[i] = idx
                    for k in range(1, bar_pass+1):
                        bar_stats[i-k,0] = bar_pass + 1 - k
                    bar_pass = 0            
        elif ha_sign[i]==-1:
            if idx<=0:
                idx = idx - 1
                bar_stats[i,0] = idx
                bar_idx_live[i] = idx
                bar_pass = 0
            else:
                if ps[i]>-ps_pass_cut and bar_pass<bar_pass_cut:
                    idx = idx + 1
                    bar_stats[i,0] = idx
                    bar_idx_live[i] = idx
                    bar_pass = bar_pass + 1*(ps[i]!=0)
                else:
                    bar_stats[i-bar_pass,1] = idx - bar_pass
                    idx = -1 - bar_pass
                    bar_stats[i,0] = idx
                    bar_idx_live[i] = idx
                    for k in range(1, bar_pass+1):
                        bar_stats[i-k,0] = -bar_pass - 1 + k
                    bar_pass = 0                    
    
    df_barnum = pd.DataFrame({'number':bar_idx_live}, index=t)
    return df_barnum