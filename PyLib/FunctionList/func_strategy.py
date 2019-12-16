# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 00:42:27 2019

@author: xuzha
"""

import pandas as pd
import numpy as np
from .func_strategy_bar import *
from .func_strategy_trfilter import *
from .func_strategy_trswing import *

def trade_strategy(df_bar, trade_param):
    if trade_param['strategy']=='BS':
        df_buysell = strategy_BS(df_bar, trade_param)
    elif trade_param['strategy']=='BT':
        df_buysell = strategy_BT(df_bar, trade_param)
    elif trade_param['strategy']=='SL':
        df_buysell = strategy_SL(df_bar, trade_param)
    elif trade_param['strategy']=='SN':
        df_buysell = strategy_SN(df_bar, trade_param)
    elif trade_param['strategy']=='GT':
        df_buysell = strategy_GT(df_bar, trade_param)
        
    elif trade_param['strategy']=='FS':
        df_buysell = strategy_FS(df_bar, trade_param)
    elif trade_param['strategy']=='EMD':
        df_buysell = strategy_EMD(df_bar, trade_param)
    elif trade_param['strategy']=='MO':
        df_buysell = strategy_MO(df_bar, trade_param)
    elif trade_param['strategy']=='MOL':
        df_buysell = strategy_MOL(df_bar, trade_param)
    elif trade_param['strategy']=='HN':
        df_buysell = strategy_HN(df_bar, trade_param)
        
    elif trade_param['strategy']=='MR':
        df_buysell = strategy_MR(df_bar, trade_param)
    elif trade_param['strategy']=='HL':
        df_buysell = strategy_HL(df_bar, trade_param)
    else:
        return pd.DataFrame({'buysell':np.zeros(len(df_bar))}, index=df_bar.index)        
    return df_buysell