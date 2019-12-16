# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 18:14:40 2019

@author: XzzzX
"""

import numpy as np
import pandas as pd
import datetime
import os
import sys
import pickle
import matplotlib.pyplot as plt


#-----------------------------------------------------------
strategy_name   = 'ChinaHK Vol Trading'
strategy_list   = ['FBV', 'FBF']
instrument_list = ['A50', 'Hsi', 'Hscei']


#-----------------------------------------------------------
strategy_name   = 'Global Index Trend Swing Trading'
strategy_list   = ['FRE', 'MR', 'HL']
instrument_list = ['A50', 'Hsi', 'Hscei', 'Nifty']

#strategy_list   = ['FRE']
#instrument_list = ['Hsi', 'Hscei']
#strategy_list   = ['MR']
#instrument_list = ['A50', 'Hsi', 'Hscei', 'Nifty']
#strategy_list   = ['HL']
#instrument_list = ['A50', 'Hsi', 'Nifty']


#-----------------------------------------------------------
strategy_name   = 'Global Index Trend Filter Trading'
strategy_list   = ['MO', 'MOL', 'EMD', 'FS', 'HN']
instrument_list = ['A50', 'Nifty', 'Nikkei','Nifty','Dow','Nasdaq','Sp500']

#strategy_list   = ['FS']
#instrument_list = ['Nikkei','Nifty','Dow','Nasdaq','Sp500','Russell2000','MidCap400']
#strategy_list   = ['HN']
#instrument_list = ['Nikkei','Nifty','Dow','Nasdaq','Sp500']
#strategy_list   = ['MO']
#instrument_list = ['A50', 'Nifty']
#strategy_list   = ['MOL']
#instrument_list = ['A50', 'Nifty']
#strategy_list   = ['EMD']
#instrument_list = ['A50', 'Nifty']


#-----------------------------------------------------------
#strategy_name   = 'Global Index Bar Pattern Trading'
#strategy_list   = ['SL', 'SN', 'BS', 'GT']
#instrument_list = ['Hsi', 'Hscei', 'Nifty', 
#                   'Dax', 'Cac', 'Euro50', 
#                   'Dow','Nasdaq','Sp500','Russell2000','MidCap400']

#strategy_list   = ['SL']
#instrument_list = ['Hsi', 'Hscei', 'Nifty']
#strategy_list   = ['SN']
#instrument_list = ['Dax', 'Cac', 'Euro50']
#strategy_list   = ['BS']
#instrument_list = ['Dax', 'Cac', 'Euro50']
#strategy_list   = ['GT']
#instrument_list = ['Dow','Nasdaq','Sp500','Russell2000','MidCap400']

#-----------------------------------------------------------
#strategy_name   = 'Global Index Trading Portfolio'
#strategy_list   = ['FBV', 'FBF', 
#                   'FRE', 'MR', 'HL',
#                   'MO', 'MOL', 'EMD', 'FS', 'HN',
#                   'SL', 'SN', 'BS', 'GT']
#instrument_list = ['A50', 'Hsi', 'Hscei','CSI300','CSI500', 'Dow','Nasdaq','Sp500','Russell2000','MidCap400',
#                   'Euro50','Dax','Cac','Ftse','Swiss','Spain', 'Nifty','Nikkei','Topix','Aus','TW']
#instrument_list = ['Dow','Nasdaq','Sp500','Russell2000','MidCap400']


#-----------------------------------------------------------
strategy_name   = 'China Personal Trading'
strategy_list   = ['FS', 'GT', 'HN', 'MOL']
#strategy_list   = ['MR']
instrument_list = ['Hscei']


exe_type = 'exe_raw'
cost_pertrade = 0.0000
start_date = np.datetime64('2014-01-01')
end_date   = np.datetime64('2019-09-30')

#start_date = np.datetime64('2016-10-01')
#end_date   = np.datetime64('2018-03-01')
#end_date   = np.datetime64('2018-06-01')
#end_date   = np.datetime64('2018-07-01')

#start_date = np.datetime64('2018-03-01')
#start_date = np.datetime64('2018-06-01')
#end_date   = np.datetime64('2018-10-01')
#end_date   = np.datetime64('2019-02-01')


filename_strategy = 'strategy_book_index.csv'
filepath = '.\\Data\\'
#%% 
date_stats_day = np.arange(start_date,end_date,np.timedelta64(1,'D'))
date_stats_day = date_stats_day[np.is_busday(date_stats_day,weekmask='1111100')]
df_portfolio_model_return = pd.DataFrame(index=date_stats_day)
df_portfolio_mkt_return   = pd.DataFrame(index=date_stats_day)
column_name = []
trade_num = []
hold_length = []
pnl_stats = []
strategy_book = pd.read_csv(filename_strategy)
for strategy in strategy_list:
    print('------------------------')
    print(strategy)
    with open(filepath+strategy+'.pickle','rb') as f:
        strategy_infor = pickle.load(f)
    for instrument in instrument_list:
        print(instrument)
        idx_strategy_instrument = np.where((strategy_book.strategy==strategy) & (strategy_book.instrument==instrument))[0]
#        idx_strategy_instrument = np.where((strategy_book.strategy==strategy) & (strategy_book.instrument==instrument) & (strategy_book.onoff==1) )[0]
        if len(idx_strategy_instrument)==0:
            print('No Data!')
            continue        
        idx_strategy_infor = [i for i in range(len(strategy_infor['buy_sell_model'])) if strategy_infor['buy_sell_model'][i][0]==strategy_book.symbol[idx_strategy_instrument[0]]]
        if len(idx_strategy_infor)==0:
            print('No Data!')
            continue        
        df_buy_sell_temp = strategy_infor['buy_sell_model'][idx_strategy_infor[0]][1][start_date:end_date]                
#        return_model_temp = (df_buy_sell_temp.close/df_buy_sell_temp.close.shift(1)-1) * df_buy_sell_temp.buy_sell_indicator.shift(1)
        return_model_temp = (df_buy_sell_temp[exe_type]/df_buy_sell_temp[exe_type].shift(1)-1) * df_buy_sell_temp.buy_sell_indicator.shift(1) \
            + -cost_pertrade/2*(df_buy_sell_temp.buy_sell_indicator!=df_buy_sell_temp.buy_sell_indicator.shift(1))
        pnl_model_temp = np.cumprod(1+return_model_temp)
        plt.figure()
        plt.title(strategy+':'+instrument)
        plt.plot(pnl_model_temp-1)
        pnl_model_temp_d = pnl_model_temp.reindex(df_portfolio_model_return.index, method='ffill')
        pnl_mkt_temp_d = df_buy_sell_temp.close.reindex(df_portfolio_model_return.index, method='ffill')
        return_model_temp_d = (pnl_model_temp_d/pnl_model_temp_d.shift(1)-1).fillna(0)        
        return_mkt_temp_d  = (pnl_mkt_temp_d/pnl_mkt_temp_d.shift(1)-1).fillna(0)        
#        return_model_temp_d = (pnl_model_temp_d/pnl_model_temp_d.shift(1)-1)
#        return_mkt_temp_d  = (pnl_mkt_temp_d/pnl_mkt_temp_d.shift(1)-1)
        column_name_temp = strategy+'_'+instrument
        df_portfolio_model_return[column_name_temp] = return_model_temp_d
        df_portfolio_mkt_return[column_name_temp]   = return_mkt_temp_d
        column_name = column_name + [column_name_temp]
        
        idx_trade_open  = np.where((df_buy_sell_temp.buy_sell_indicator!=df_buy_sell_temp.buy_sell_indicator.shift(1)) & (df_buy_sell_temp.buy_sell_indicator!=0))[0]
        idx_trade_close = np.where((df_buy_sell_temp.buy_sell_indicator!=df_buy_sell_temp.buy_sell_indicator.shift(1)) & (df_buy_sell_temp.buy_sell_indicator.shift(1)!=0))[0]
        idx_trade_close=idx_trade_close[idx_trade_close!=0]
        if len(idx_trade_close)<len(idx_trade_open):
            idx_trade_close = np.append(idx_trade_close,[len(df_buy_sell_temp)-1])
        trade_num_temp = len(idx_trade_open)
        hold_length_temp = df_buy_sell_temp.index[idx_trade_close] - df_buy_sell_temp.index[idx_trade_open]
        hold_length_temp = np.mean(hold_length_temp).astype('timedelta64[h]') / np.timedelta64(1,'h') / 24
        trade_num = trade_num + [trade_num_temp]
        hold_length = hold_length + [hold_length_temp]
        pnl_stats.append([strategy, instrument, pnl_model_temp[-1]-1])

df_portfolio_model_return['ret_portfolio'] = df_portfolio_model_return.mean(axis=1).fillna(0)
df_portfolio_mkt_return['ret_portfolio'] = df_portfolio_mkt_return.mean(axis=1).fillna(0)
df_portfolio_model_return['pnl_portfolio'] = np.cumprod(df_portfolio_model_return['ret_portfolio']+1) - 1
df_portfolio_mkt_return['pnl_portfolio'] = np.cumprod(df_portfolio_mkt_return['ret_portfolio']+1) - 1

def func_pnl_stats(ret_d):
    pnl = np.cumprod(1+ret_d) - 1
    ret_cum = pnl[-1]
    ret_ann = np.mean(ret_d) * 260
    vol_ann = np.std(ret_d) * np.sqrt(260)
    sharpe  = ret_ann / vol_ann
    max_dd  = np.max(np.maximum.accumulate(pnl)-pnl)
    calmar  = ret_ann / max_dd
    kelly_ratio = ret_ann / vol_ann / vol_ann    
    return pnl, ret_cum, ret_ann, vol_ann, sharpe, max_dd, calmar
pnl_mkt, ret_cum_mkt, ret_ann_mkt, vol_ann_mkt, sharpe_mkt, max_dd_mkt, calmar_mkt = func_pnl_stats(df_portfolio_mkt_return.ret_portfolio)
pnl, ret_cum, ret_ann, vol_ann, sharpe, max_dd, calmar = func_pnl_stats(df_portfolio_model_return.ret_portfolio)
ret_pt = ret_cum / np.mean(trade_num)
days_hold = np.mean(hold_length)


plt.figure()
plt.title(strategy_name+'\n'+str(strategy_list)+'\n'+str(instrument_list)+'\nDate Period: '+str(date_stats_day[0])+'~'+str(date_stats_day[-1]))
plt.plot(df_portfolio_model_return.pnl_portfolio,'r-')
plt.plot(df_portfolio_mkt_return.pnl_portfolio,'k-')
plt.legend(['-- model --'+'\nret_ann  : '+str(round(ret_ann,3))+'\nsharpe   : '+str(round(sharpe,3))+'\nmax_dd : '+str(round(max_dd,3)) \
            +'\nret_pt    : '+str(round(ret_pt,4))+'\ndays_hold: '+str(round(days_hold,1))+' days',
            '\n-- market --'+'\nret_ann  : '+str(round(ret_ann_mkt,3))+'\nsharpe   : '+str(round(sharpe_mkt,2))+'\nmax_dd : '+str(round(max_dd_mkt,3))])