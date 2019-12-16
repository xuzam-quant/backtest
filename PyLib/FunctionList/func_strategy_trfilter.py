# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 17:06:24 2019

@author: XzzzX
"""

import numpy as np
import pandas as pd
from scipy import stats
from .func_ha import *
from .func_filter import *

#%% FS
def strategy_FS(df_bar, trade_param):
    win_size, filter_lambda_st, filter_lambda_lt = trade_param['win_size'], trade_param['filter_lambda_st'], trade_param['filter_lambda_lt']
    
    close_30 = df_bar.close.values    
    filter_live_st_30 = func_filter_hp(close_30, win_size, filter_lambda_st)
    filter_live_lt_30 = func_filter_hp(close_30, win_size, filter_lambda_lt)        
    buy_sell_indicator_30 = np.zeros(len(close_30))    
    backtest_start = win_size
    backtest_end   = len(close_30)    
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]                                
        # long
        if buy_sell_indicator_30[t]!=1 and close_30[t]>filter_live_st_30[t]:
            buy_sell_indicator_30[t] = 1    
        # short
        if buy_sell_indicator_30[t]!=-1 and close_30[t]<filter_live_st_30[t] and filter_live_st_30[t]<filter_live_lt_30[t]:
            buy_sell_indicator_30[t] = -1
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)
        
#%% EMD
def strategy_EMD(df_bar, trade_param):
    win_size = trade_param['win_size']
    
    close_30 = df_bar.close.values    
    close_norm = close_30/close_30[0]
    close_norm_emd = func_filter_emd(close_norm, win_size)    
    win_size_hp = 200
    filter_lambda_hp = 1e4
    close_norm_emd_hp = func_filter_hp(close_norm_emd, win_size_hp, filter_lambda_hp)        
    buy_sell_indicator_30 = np.zeros(len(close_30))    
    backtest_start = max(win_size, win_size_hp)
    backtest_end   = len(close_30)    
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]            
        # long
        if buy_sell_indicator_30[t]!=1 and close_norm_emd_hp[t]<close_norm[t]:
            buy_sell_indicator_30[t] = 1        
        # short
        if buy_sell_indicator_30[t]!=-1 and close_norm_emd_hp[t]>close_norm[t]:
            buy_sell_indicator_30[t] = -1            
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)

#%% MO
def strategy_MO(df_bar, trade_param):
    filter_length = trade_param['win_size']
    
    close_30 = df_bar.close.values        
    buy_sell_indicator_30 = np.zeros(len(close_30))
    sm_1_30 = np.zeros(len(close_30))
    sm_2_30 = np.zeros(len(close_30))    
    backtest_start = filter_length+1
    backtest_end   = len(close_30)        
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]        
        # return
        return_series_30 = close_30[t-filter_length:t+1]/close_30[t-filter_length-1:t] - 1
        sm_1_30[t] = stats.moment(return_series_30,moment=3)
        sm_2_30[t] = sm_1_30[t-filter_length:t+1].mean()            
        # long
        if buy_sell_indicator_30[t]!=1 and sm_1_30[t]>0:
            buy_sell_indicator_30[t] = 1
        # short
        if buy_sell_indicator_30[t]!=-1 and sm_1_30[t]<0:
            buy_sell_indicator_30[t] = -1
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)

#%% MOL            
def strategy_MOL(df_bar, trade_param):
    filter_length = trade_param['win_size']
    
    close_30 = df_bar.close.values        
    buy_sell_indicator_30 = np.zeros(len(close_30))
    sm_1_30 = np.zeros(len(close_30))
    sm_2_30 = np.zeros(len(close_30))    
    backtest_start = filter_length+1
    backtest_end   = len(close_30)    
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]        
        # return
        return_series_30 = close_30[t-filter_length:t+1]/close_30[t-filter_length-1:t] - 1
        sm_1_30[t] = np.sum(np.sqrt(np.abs(return_series_30))*np.sign(return_series_30))
        sm_2_30[t] = sm_1_30[t-filter_length:t+1].mean()            
        # long
        if buy_sell_indicator_30[t]!=1 and sm_1_30[t]>0:
            buy_sell_indicator_30[t] = 1        
        # short
        if buy_sell_indicator_30[t]!=-1 and sm_1_30[t]<0:
            buy_sell_indicator_30[t] = -1
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)

#%% HN
def strategy_HN(df_bar, trade_param):
    hourbod, timezone, cut_return, cut_ha_num = trade_param['hourbod'], trade_param['timezone'], trade_param['cut_return'], trade_param['cut_hanum']
    
    time_30, open_30, high_30, low_30 ,close_30 = df_bar.index.values, df_bar.open.values, df_bar.high.values, df_bar.low.values, df_bar.close.values        
    df_copy=df_bar.copy()
    if timezone!='Asia/Singapore':
        df_copy.index = df_copy.index.tz_localize('Asia/Singapore')
        df_copy.index = df_copy.index.tz_convert(timezone)
    hourshift = int(hourbod)
    minuteshift = int((hourbod-hourshift)*60)
    df_copy = df_copy.shift(-hourshift,'h').shift(-minuteshift,'Min')
    df_bar_d = df_copy.resample('1D').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})
    df_bar_d.index = df_bar_d.index + np.timedelta64(1440,'m')
    df_bar_d.dropna(axis=0, subset=['close'], inplace=True)    
    df_bar_d = df_bar_d.shift(hourshift,'h').shift(minuteshift,'Min')
    if timezone!='Asia/Singapore':
        df_bar_d.index = df_bar_d.index.tz_convert('Asia/Singapore').tz_localize(None)   
    idx_lastbar = df_bar.index.reindex(df_bar_d.index, method='ffill')[1]
    df_bar_d.set_index(df_bar.iloc[idx_lastbar].index, inplace=True)            
    # ha
    df_habar_30 = func_ha_bar(time_30, open_30, high_30, low_30 ,close_30)
    df_habar_d = func_ha_bar(df_bar_d.index, df_bar_d.open, df_bar_d.high, df_bar_d.low ,df_bar_d.close)
    df_haps_d  = func_ha_ps(df_habar_d.index, df_habar_d.open, df_habar_d.close, 50)
    df_hanum_d = func_ha_number(df_habar_d.index, df_habar_d.open, df_habar_d.close, df_haps_d.ps)    
    #
    ha_close_d = df_habar_d.close.values.copy()
    ha_open_d = df_habar_d.open.values.copy()
    bar_count_d = df_hanum_d.number.values.copy()
    ha_close_30 = df_habar_30.close.values.copy()
    ha_open_30 = df_habar_30.open.values.copy()
    ha_high_30 = df_habar_30.high.values.copy()
    ha_low_30 = df_habar_30.low.values.copy()
    last_d_30 = df_bar_d.index.reindex(df_bar.index, method='ffill')[1]
    last_30_d = df_bar.index.reindex(df_bar_d.index, method='ffill')[1]
        
    buy_sell_indicator_30 = np.zeros(len(time_30), dtype=int)
    trade_start_idx_30 = np.zeros(len(time_30), dtype=int)    
    backtest_start = 50
    backtest_end   = len(time_30)    
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]
        trade_start_idx_30[t] = trade_start_idx_30[t-1]
            
        # close long
        if buy_sell_indicator_30[t]==1 \
        and close_30[t]/max(close_30[trade_start_idx_30[t]:t+1])-1<-cut_return \
        and (ha_close_30[t]<ha_close_30[t-1] or ha_high_30[t]<ha_high_30[t-1]):
            buy_sell_indicator_30[t] = 0
            
        # close short
        if buy_sell_indicator_30[t]==-1 \
        and close_30[t]/min(close_30[trade_start_idx_30[t]:t+1])-1>cut_return \
        and (ha_close_30[t]>ha_close_30[t-1] or ha_low_30[t]>ha_low_30[t-1]):
            buy_sell_indicator_30[t] = 0
            
        # open long
        if buy_sell_indicator_30[t]!=1 \
        and ha_close_d[last_d_30[t]]>ha_open_d[last_d_30[t]] \
        and bar_count_d[last_d_30[t]]>-cut_ha_num \
        and all(buy_sell_indicator_30[last_30_d[last_d_30[t]]:t+1]!=1) \
        and (ha_close_30[t]>ha_close_30[t-1] or ha_low_30[t]>ha_low_30[t-1]):
            buy_sell_indicator_30[t] = 1
            trade_start_idx_30[t] = t
            
        # open short
        if buy_sell_indicator_30[t]!=-1 \
        and ha_close_d[last_d_30[t]]<ha_open_d[last_d_30[t]] \
        and bar_count_d[last_d_30[t]]<cut_ha_num \
        and all(buy_sell_indicator_30[last_30_d[last_d_30[t]]:t+1]!=-1) \
        and (ha_close_30[t]<ha_close_30[t-1] or ha_high_30[t]<ha_high_30[t-1]):
            buy_sell_indicator_30[t] = -1
            trade_start_idx_30[t] = t

    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)            