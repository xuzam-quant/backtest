import numpy as np
import pandas as pd
import sys
import datetime
import matplotlib.pyplot as plt
sys.path.append('..\\PyLib')
from FunctionList import *

#instrument  = dict(symbol='TXIN9I Index',   hourbod=9.5, timezone='Asia/Singapore', tradehour='China')
#instrument  = dict(symbol='THSI Index',     hourbod=9.5, timezone='Asia/Singapore', tradehour='HongKong')
#instrument  = dict(symbol='THSCEI Index',   hourbod=9.5, timezone='Asia/Singapore', tradehour='HongKong')
#instrument  = dict(symbol='SHSZ300 Index',  hourbod=9.5, timezone='Asia/Singapore', tradehour='China')
instrument  = dict(symbol='SH000905 Index', hourbod=9.5, timezone='Asia/Singapore', tradehour='China')
#instrument  = dict(symbol='XIN9I Index',   hourbod=9.5, timezone='Asia/Singapore', tradehour='China')
#instrument  = dict(symbol='HSI Index',     hourbod=9.5, timezone='Asia/Singapore', tradehour='HongKong')
#instrument  = dict(symbol='HSCEI Index',   hourbod=9.5, timezone='Asia/Singapore', tradehour='HongKong')

#instrument  = dict(symbol='INDU Index',     hourbod=9.5, timezone='America/New_York',  tradehour='America')
#instrument  = dict(symbol='NDX Index',      hourbod=9.5, timezone='America/New_York',  tradehour='America')
#instrument  = dict(symbol='SPX Index',      hourbod=9.5, timezone='America/New_York',  tradehour='America')
#instrument  = dict(symbol='MID Index',      hourbod=9.5, timezone='America/New_York',  tradehour='America')
#instrument  = dict(symbol='RTY Index',      hourbod=9.5, timezone='America/New_York',  tradehour='America')
#instrument  = dict(symbol='DIA US',         hourbod=9.5, timezone='America/New_York',  tradehour='America')
#instrument  = dict(symbol='QQQ US',         hourbod=9.5, timezone='America/New_York',  tradehour='America')
#instrument  = dict(symbol='SPY US',         hourbod=9.5, timezone='America/New_York',  tradehour='America')
#instrument  = dict(symbol='MDY US',         hourbod=9.5, timezone='America/New_York',  tradehour='America')
#instrument  = dict(symbol='IWM US',         hourbod=9.5, timezone='America/New_York',  tradehour='America')

#instrument  = dict(symbol='NKY Index',      hourbod=8,   timezone='Asia/Singapore',  tradehour='Japan')
#instrument  = dict(symbol='TPX Index',      hourbod=8,   timezone='Asia/Singapore',  tradehour='Japan')
#instrument  = dict(symbol='NIFTY Index',    hourbod=11.5, timezone='Asia/Singapore',  tradehour='India')
#instrument  = dict(symbol='AS51 Index',     hourbod=8,   timezone='Asia/Singapore',  tradehour='Australia')
#instrument  = dict(symbol='TNKY Index',     hourbod=8,   timezone='Asia/Singapore',  tradehour='Japan')
#instrument  = dict(symbol='TTPX Index',     hourbod=8,   timezone='Asia/Singapore',  tradehour='Japan')
#instrument  = dict(symbol='NZ1 Index',      hourbod=11.5, timezone='Asia/Singapore',  tradehour='India')

#instrument  = dict(symbol='DAX Index',      hourbod=8,   timezone='Europe/Berlin',  tradehour='Germany')
#instrument  = dict(symbol='CAC Index',      hourbod=9,   timezone='Europe/Paris',   tradehour='France')
#instrument  = dict(symbol='UKX Index',      hourbod=8,   timezone='Europe/London',  tradehour='England')
#instrument  = dict(symbol='SX5E Index',     hourbod=8,   timezone='Europe/Berlin',  tradehour='Germany')
#instrument  = dict(symbol='TDAX Index',     hourbod=8,   timezone='Europe/Berlin',  tradehour='Germany')
#instrument  = dict(symbol='TCAC Index',     hourbod=9,   timezone='Europe/Paris',   tradehour='France')
#instrument  = dict(symbol='TUKX Index',     hourbod=8,   timezone='Europe/London',  tradehour='England')


#trade_param = dict(strategy='BS',   win_size=100,    win_size_fast=30)
#trade_param = dict(strategy='BT',   win_size=100,    std_mul=3)
#trade_param = dict(strategy='SL',   win_size=470,    std_mul=2.75)
#trade_param = dict(strategy='SN',   win_size=500)
#trade_param = dict(strategy='GT',   cut_return=0.005, hourbod=instrument['hourbod'], timezone=instrument['timezone'])

trade_param = dict(strategy='FS',   win_size=500,    filter_lambda_st=1e4, filter_lambda_lt=1e8)
#trade_param = dict(strategy='EMD',  win_size=500)
#trade_param = dict(strategy='MO',   win_size=20)
#trade_param = dict(strategy='MOL',  win_size=20)
#trade_param = dict(strategy='HN',   cut_return=0.01, cut_hanum=5,   hourbod=instrument['hourbod'], timezone=instrument['timezone'])

#trade_param = dict(strategy='MR',   win_size=500,    filter_lambda=5e3, std_mul=2)
#trade_param = dict(strategy='HL',   win_size=55)

bar_param   = dict(method='time',   interval=30,    execution=dict(method='twap', st=2, lt=5))

#instrument['hourbod'] = 0
#instrument['timezone'] = 'Asia/Singapore'
#instrument['tradehour'] = ''


exe_type = 'exe_waplt'
cost_pertrade = 0.0004
date_stats_beg = np.datetime64('2018-09-01')
date_stats_end = np.datetime64('2019-12-31')

filepath = 'D:\\Quant\\Project\\Quant\\Data\\market\\index\\'
#filepath = 'Z:\\ZhangXu\\RELTDL\\data\\temp\\m\\i\\'
#%% ohlcv
df_bar     = bar_construct(instrument, bar_param, filepath, date_stats_beg, date_stats_end)
df_buysell = trade_strategy(df_bar, trade_param)
plot_buysell(df_bar, df_buysell, instrument, bar_param, trade_param)

#%% stats        
bar_return_mkt = df_bar.close/df_bar.close.shift(1)-1
bar_return_exe = df_bar[exe_type]/df_bar[exe_type].shift(1)-1
bar_return_model = bar_return_exe*df_buysell.buysell.shift(1) - (cost_pertrade/2)*(df_buysell.buysell!=df_buysell.buysell.shift(1))
pnl_mkt = np.cumprod(1+bar_return_mkt) - 1
pnl_model = np.cumprod(1+bar_return_model) - 1

plt.figure()
plt.title(trade_param['strategy']+' - '+instrument['symbol'])
plt.plot(pnl_mkt, 'k.-')
plt.plot(pnl_model, 'r.-')


df_buy_sell_model = pd.DataFrame({'close':df_bar.close, 'buy_sell_indicator':df_buysell.buysell}, index=df_bar.index)
bar_return = (df_buy_sell_model.close/df_buy_sell_model.close.shift(1)-1) * df_buy_sell_model.buy_sell_indicator.shift(1)
pnl = np.cumprod(bar_return+1)  
params = ''
buy_sell_model_temp = [instrument['symbol'], df_buy_sell_model, pnl, params]

print(np.unique(df_bar.index.time))