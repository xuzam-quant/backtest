# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 16:32:28 2019

@author: XzzzX
"""

import numpy as np
import pandas as pd
from .func_ha import *

#%% BS
def strategy_BS(df_bar, trade_param):
    count_bar_threshold, roll_bar_threshold = trade_param['win_size'], trade_param['win_size_fast']
    
    open_30, close_30 = df_bar.open.values, df_bar.close.values
    buy_sell_indicator_30 = np.zeros(len(open_30))
    backtest_start = max(count_bar_threshold,roll_bar_threshold)
    backtest_end   = len(open_30)
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]
        bar_mean = (close_30[t-count_bar_threshold:t+1] - open_30[t-count_bar_threshold:t+1]).mean()
        bar_std = (close_30[t-count_bar_threshold:t+1] - open_30[t-count_bar_threshold:t+1]).std()
        # close long
        if buy_sell_indicator_30[t]==1 and (close_30[t-roll_bar_threshold:t]-open_30[t-roll_bar_threshold:t]).sum()<=bar_mean*roll_bar_threshold+0*bar_std:
            buy_sell_indicator_30[t] = 0
        # close short
        if buy_sell_indicator_30[t]==-1 and (close_30[t-roll_bar_threshold:t]-open_30[t-roll_bar_threshold:t]).sum()>=bar_mean*roll_bar_threshold+0*bar_std:
            buy_sell_indicator_30[t] = 0
        # long
        if buy_sell_indicator_30[t]!=1 and (close_30[t-roll_bar_threshold:t]-open_30[t-roll_bar_threshold:t]).sum()>bar_mean*roll_bar_threshold+4*bar_std:
            buy_sell_indicator_30[t] = 1
        # short
        if buy_sell_indicator_30[t]!=-1 and (close_30[t-roll_bar_threshold:t]-open_30[t-roll_bar_threshold:t]).sum()<bar_mean*roll_bar_threshold-4*bar_std:
            buy_sell_indicator_30[t] = -1    
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)


#%% BT
def strategy_BT(df_bar, trade_param):
    win_size, std_mul = trade_param['win_size'], trade_param['std_mul']
    
    open_30, close_30 = df_bar.open.values, df_bar.close.values    
    df_bar_30 = pd.DataFrame({'open':open_30, 'close':close_30})
    mean_bar_size_30 = (df_bar_30.close-df_bar_30.open).abs().rolling(win_size).mean().values
    std_bar_size_30  = (df_bar_30.close-df_bar_30.open).abs().rolling(win_size).std().values    
    buy_sell_indicator_30 = np.zeros(len(open_30))
    backtest_start = win_size
    backtest_end   = len(open_30)    
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]            
        # long
        if close_30[t]-open_30[t]<-mean_bar_size_30[t]-std_bar_size_30[t]*std_mul:
            buy_sell_indicator_30[t] = 1        
        # short
        if close_30[t]-open_30[t]>mean_bar_size_30[t]+std_bar_size_30[t]*std_mul:
            buy_sell_indicator_30[t] = -1
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)

#%% SL
def strategy_SL(df_bar, trade_param):
    win_size, std_mul = trade_param['win_size'], trade_param['std_mul']
    
    open_30, close_30, high_30, low_30 = df_bar.open.values, df_bar.close.values, df_bar.high.values, df_bar.low.values
    buy_sell_indicator_30 = np.zeros(len(close_30))
    backtest_start = win_size
    backtest_end   = len(close_30)    
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]            
        # long
        if high_30[t]-max(open_30[t],close_30[t])>min(open_30[t],close_30[t])-low_30[t] + np.mean(np.abs(close_30[t-win_size:t+1]-open_30[t-win_size:t+1]))*std_mul:
            buy_sell_indicator_30[t] = 1        
        # short
        if high_30[t]-max(open_30[t],close_30[t])<min(open_30[t],close_30[t])-low_30[t] - np.mean(np.abs(close_30[t-win_size:t+1]-open_30[t-win_size:t+1]))*std_mul:
            buy_sell_indicator_30[t] = -1
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)

#%% SN
def strategy_SN(df_bar, trade_param):
    win_size = trade_param['win_size']
    
    close_30 = df_bar.close.values
    skewness_30 = df_bar.close.rolling(win_size+1).skew().values
    quantile_30 = df_bar.close.rolling(win_size+1).quantile(0.5, interpolation='lower').values    
    buy_sell_indicator_30 = np.zeros(len(close_30))    
    backtest_start = win_size
    backtest_end   = len(close_30)    
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]        
        # long
        if skewness_30[t]<0 and close_30[t]<quantile_30[t]:
            buy_sell_indicator_30[t] = 1        
        # short
        if skewness_30[t]>0 and close_30[t]>quantile_30[t]:
            buy_sell_indicator_30[t] = -1
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)
    
#%% GT
def strategy_GT(df_bar, trade_param):
    hourbod, timezone, cut_return = trade_param['hourbod'], trade_param['timezone'], trade_param['cut_return']
    
    time_30, open_30, high_30, low_30 ,close_30 = df_bar.index.values, df_bar.open.values, df_bar.high.values, df_bar.low.values, df_bar.close.values        
    # ha bar
    df_habar_30 = func_ha_bar(time_30, open_30, high_30, low_30 ,close_30)            
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
    close_d = df_bar_d.close.values
    ha_close_30, ha_high_30, ha_low_30 = df_habar_30.close.values, df_habar_30.high.values, df_habar_30.low.values    
    last_d_30 = df_bar_d.index.reindex(df_bar.index, method='ffill')[1]

    buy_sell_indicator_30 = np.zeros(len(time_30), dtype=int)
    trade_start_idx_30    = np.zeros(len(time_30), dtype=int)    
    backtest_start = 20
    backtest_end   = len(time_30)    
    status_short_keep = 0
    idx_day_end = 0    
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]
        trade_start_idx_30[t] = trade_start_idx_30[t-1]
            
        if buy_sell_indicator_30[t]==1 \
        and last_d_30[t]==last_d_30[t-1] \
        and (ha_close_30[t]<ha_close_30[t-1] or ha_high_30[t]<ha_high_30[t-1]):
            buy_sell_indicator_30[t] = 0
            
        if buy_sell_indicator_30[t]==0 \
        and last_d_30[t]!=last_d_30[t-1]:
            buy_sell_indicator_30[t] = 1
            trade_start_idx_30[t] = t
            
        if close_30[t]/max(close_d[last_d_30[t]],open_30[idx_day_end+1])-1<-cut_return \
        and close_30[t]/max(close_d[last_d_30[t]],open_30[idx_day_end+1])-1>-2*cut_return \
        and last_d_30[t]==last_d_30[t-1] \
        and (ha_close_30[t]<ha_close_30[t-1] or ha_high_30[t]<ha_high_30[t-1]):
            status_short_keep = 1
        if last_d_30[t]==last_d_30[t-1] and last_d_30[t-1]!=last_d_30[t-2]:
            status_short_keep = 0
            
        if buy_sell_indicator_30[t]==-1 \
        and last_d_30[t]!=last_d_30[t-1]:
            buy_sell_indicator_30[t] = 0
            
        if buy_sell_indicator_30[t]==-1 \
        and last_d_30[t]==last_d_30[t-1] \
        and close_30[t]/min(close_30[trade_start_idx_30[t]:t+1])-1>cut_return \
        and close_30[t]/open_30[idx_day_end+1]-1>cut_return/2 \
        and (ha_close_30[t]>ha_close_30[t-1] or ha_low_30[t]>ha_low_30[t-1]):
            buy_sell_indicator_30[t] = 0        
            
        if buy_sell_indicator_30[t]!=-1 \
        and last_d_30[t]==last_d_30[t-1] \
        and close_30[t]/max(close_d[last_d_30[t]],open_30[idx_day_end+1])-1<-cut_return \
        and close_30[t]/max(close_d[last_d_30[t]],open_30[idx_day_end+1])-1>-2*cut_return \
        and all(buy_sell_indicator_30[idx_day_end:t+1]!=-1) \
        and (ha_close_30[t]<ha_close_30[t-1] or ha_high_30[t]<ha_high_30[t-1]):
            buy_sell_indicator_30[t] = -1
            trade_start_idx_30[t] = t
            
        if last_d_30[t]!=last_d_30[t-1]:
            idx_day_end = t            
            
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)            
            
            
            
            