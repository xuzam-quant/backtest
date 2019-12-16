# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 21:18:36 2019

@author: zhangxu
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#from matplotlib.finance import candlestick_ohlc

#%% buy sell indciator
def plot_buysell(df_bar, df_buysell, instrument, bar_param, trade_param):
    num_ticks = 50
    xticks = np.arange(df_buysell.index.shape[0])
    xlabel_ticks = np.arange(0,len(xticks),int(len(xticks)/num_ticks))
    
    plt.figure()
    plt.title(str(instrument)+'\n'+str(bar_param)+'\n'+str(trade_param))
#    candlestick_ohlc(ax, df_bar.index, df_bar.open, df_bar.close, df_bar.high, df_bar.close)
    plt.plot(df_bar.close.values, 'k-')
    plt.xticks(xticks[xlabel_ticks], df_buysell.index[xlabel_ticks].date, rotation=270, fontsize=8)
    buy_sell_indicator = df_buysell.buysell.values.copy()
    buy_sell_indicator[-1] = 0
    spread = df_bar.close.values.copy()
    yminval = df_bar.close.min()
    ymaxval = max(df_bar.close.max(),1)
    for t in range(len(buy_sell_indicator)):
        if buy_sell_indicator[t]!=1 and buy_sell_indicator[t-1]==1:
            a = np.where(buy_sell_indicator[:t]!=1)[0]
            if len(a)==0:
                a = 0
            else:
                a = a[-1] + 1
            plt.axvspan(xmin=a, xmax=t, ymin=0, ymax=ymaxval, facecolor='yellow')
            plt.plot(a, spread[a], 'r*')
            plt.plot(t, spread[t], 'r*')
        if buy_sell_indicator[t]!=-1 and buy_sell_indicator[t-1]==-1:
            a = np.where(buy_sell_indicator[:t]!=-1)[0]
            if len(a)==0:
                a = 0
            else:
                a = a[-1] + 1
            plt.axvspan(xmin=a, xmax=t, ymin=0, ymax=ymaxval, facecolor='green')
            plt.plot(a, spread[a], 'r*')
            plt.plot(t, spread[t], 'r*')


    