# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 17:06:24 2019

@author: XzzzX
"""

import numpy as np
import pandas as pd
from scipy.signal import hilbert
from .func_filter import *

#%% HL
def strategy_HL(df_bar, trade_param):
    win_size = trade_param['win_size']
    
    close_30 = df_bar.close.values    
    buy_sell_indicator_30 = np.zeros(len(close_30))
    filter_live_1_30 = np.zeros(len(close_30))
    filter_live_2_30 = np.zeros(len(close_30))    
    backtest_start = win_size
    backtest_end   = len(close_30)
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]        
        # hilbert
        signal_filtered = hilbert(close_30[t-win_size:t+1]-close_30[t-win_size:t+1].mean())
        filter_live_1_30[t] = np.imag(signal_filtered[-1])
        filter_live_2_30[t] = np.real(signal_filtered[-1])            
        # long
        if buy_sell_indicator_30[t]!=1 and filter_live_1_30[t]>0:
            buy_sell_indicator_30[t] = 1        
        # short
        if buy_sell_indicator_30[t]!=-1 and filter_live_1_30[t]<0:
            buy_sell_indicator_30[t] = -1
            
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)
    

#%% MR
def strategy_MR(df_bar, trade_param):
    win_size, filter_lambda, std_mul = trade_param['win_size'], trade_param['filter_lambda'], trade_param['std_mul']
    
    close_30 = df_bar.close.values    
    filter_live_30 = func_filter_hp(close_30, win_size, filter_lambda)
    upper_bound_30 = filter_live_30.copy()
    lower_bound_30 = filter_live_30.copy()
    for t in range(len(close_30)):
        std_error = np.std(close_30[t-win_size+1:t+1]-filter_live_30[t-win_size+1:t+1])
        upper_bound_30[t] = filter_live_30[t] + std_error * std_mul
        lower_bound_30[t] = filter_live_30[t] - std_error * std_mul
    buy_sell_indicator_30 = np.zeros(len(close_30))    
    backtest_start = max(win_size,200)
    backtest_end   = len(close_30)    
    big_trend_indicator = np.zeros(len(close_30))
    big_trend_slope   = np.zeros(len(close_30))
    big_trend_slope_2 = np.zeros(len(close_30))
    big_trend_cut_off = 0.3e-4
    big_trend_look_back = 10
    big_trend_look_back_2 = 200
    touch_indicator = np.zeros(len(close_30))
    touch_indicator[0] = 2
    idx_touch = 0    
    for t in range(backtest_start, backtest_end):
        buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]            
    #    a,b = func_linearmodel_coefficient(close_30[t-big_trend_look_back+1:t+1], np.arange(big_trend_look_back)+1)
    #    big_trend_slope = b / close_30[t]
    #    a,b = func_linearmodel_coefficient(close_30[t-big_trend_look_back_2+1:t+1], np.arange(big_trend_look_back_2)+1)
    #    big_trend_slope_2 = b / close_30[t]        
        if close_30[t]>upper_bound_30[t]:
            touch_indicator[t] = 1        
            idx_touch = t
        if close_30[t]<lower_bound_30[t]:
            touch_indicator[t] = -1
            idx_touch = t        
        # close long
        if buy_sell_indicator_30[t]==1 and close_30[t]>upper_bound_30[t]:
            buy_sell_indicator_30[t] = 0        
        # close short
        if buy_sell_indicator_30[t]==-1 and close_30[t]<lower_bound_30[t]:
            buy_sell_indicator_30[t] = 0
        # long
        if buy_sell_indicator_30[t]!=1 and close_30[t]<filter_live_30[t] and touch_indicator[idx_touch]==1:
            buy_sell_indicator_30[t] = 1        
        # short
        if buy_sell_indicator_30[t]!=-1 and close_30[t]>filter_live_30[t] and touch_indicator[idx_touch]==-1:
            buy_sell_indicator_30[t] = -1
            
    return pd.DataFrame({'buysell':buy_sell_indicator_30, 'price':df_bar.close.values}, index=df_bar.index)