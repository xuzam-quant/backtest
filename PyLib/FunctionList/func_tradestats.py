import numpy as np

#%% 
def func_pnl_stats(ret_d):
    pnl = np.cumprod(1+ret_d) - 1
    ret_cum = pnl[-1]
    ret_ann = np.mean(ret_d) * 312
    vol_ann = np.std(ret_d) * np.sqrt(312)
    sharpe  = ret_ann / vol_ann
    max_dd  = np.max(np.maximum.accumulate(pnl)-pnl)
    calmar  = ret_ann / max_dd
    kelly_ratio = ret_ann / vol_ann / vol_ann
    
    return pnl, ret_cum, ret_ann, vol_ann, sharpe, max_dd, calmar

