# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 21:18:36 2019

@author: zhangxu
"""

import numpy as np
import pandas as pd
import pickle
import datetime

#%%
def bar_construct(instrument, bar_param, filepath, date_stats_beg, date_stats_end):
    # load 1min
    symbol = instrument['symbol']
    with open(filepath+symbol+'.pickle','rb') as f:
        raw_data = pickle.load(f)
    df_bar_1 = raw_data['df_bar_1'][date_stats_beg:date_stats_end]    
    interval = bar_param['interval']
    if bar_param['method']=='time':
        df_bar = time_bar(df_bar_1, instrument, interval, bar_param['execution'])
    else:
        df_bar = time_bar(df_bar_1, instrument, interval, bar_param['execution'])
    return df_bar

#%%    
def time_bar(df, instrument, intv, exe_option=dict(method='twap', st=5, lt=30)):
    if len(df)==0:
        return pd.DataFrame()        
    time_beg  = instrument['hourbod']
    time_zone = instrument['timezone']
    df_copy=df.copy()
    if time_zone!='Asia/Singapore':
        df_copy.index = df_copy.index.tz_localize('Asia/Singapore')
        df_copy.index = df_copy.index.tz_convert(time_zone)
    trade_time = trade_hour(instrument)    
    index_valid = trade_time_remain(df_copy.index.to_pydatetime(), [], trade_time)
    df_copy = df_copy.iloc[index_valid]
    hourshift = int(time_beg)
    minuteshift = int((time_beg-hourshift)*60)
    df_copy = df_copy.shift(-hourshift,'h').shift(-minuteshift,'Min')
    df_bar = df_copy.resample(str(intv)+'Min').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})
    df_bar.index = df_bar.index + np.timedelta64(intv,'m')
    df_bar.dropna(axis=0, subset=['close'], inplace=True)    
    df_bar = df_bar.shift(hourshift,'h').shift(minuteshift,'Min')
    if time_zone!='Asia/Singapore':
        df_bar.index = df_bar.index.tz_convert('Asia/Singapore').tz_localize(None)
#    idx_lastbar = df.index.shift(1,'Min').reindex(df_bar.index, method='ffill')[1]
#    df_bar.set_index(df.iloc[idx_lastbar].index.shift(1,'Min'), inplace=True)
    execution_price(df_bar, df, exe_option)
    return df_bar

    
def execution_price(df, df_base, exe_option=dict(method='twap', st=5, lt=30) ):
    df['exe_raw']   = df.close
    df['exe_open']  = df.open.shift(-1)
    df['exe_close'] = df.close.shift(-1)        
    st = exe_option['st']
    lt = exe_option['lt']
    df_exe = df_base.copy()
    df_exe.index = df_exe.index + np.timedelta64(1,'m')    
    if exe_option['method']=='twap':
        df_exe['px_st'] = df_exe.close.rolling(st).mean().shift(-st)
        df_exe['px_lt'] = df_exe.close.rolling(lt).mean().shift(-lt)
        df['exe_wapst'] = df_exe.px_st.reindex(df.index, method='bfill')
        df['exe_waplt'] = df_exe.px_lt.reindex(df.index, method='bfill')
    elif exe_option['method']=='vwap':
        df_exe['px_st'] = ((df_exe.close*df_exe.volume).rolling(st).sum()/df_exe.volume.rolling(st).sum()).shift(-st)
        df_exe['px_lt'] = ((df_exe.close*df_exe.volume).rolling(lt).sum()/df_exe.volume.rolling(lt).sum()).shift(-lt)
        df['exe_wapst'] = df_exe.px_st.reindex(df.index, method='bfill')
        df['exe_waplt'] = df_exe.px_lt.reindex(df.index, method='bfill')
    else:
        pass
        
def trade_time_remain(dt, trade_date, trade_time):
    trade_date_comp = trade_date.copy()
    if len(trade_date_comp)==0:
        trade_date_comp.append([dt[0].date(), dt[-1].date()])
    trade_time_comp = trade_time.copy()
    if len(trade_time_comp)==0:
        trade_time_comp.append([datetime.time(0), datetime.time(23,59,59)])
    index_valid = []
    for i in range(len(dt)):
        t=dt[i]
        status=0
        for trade_date_temp in trade_date_comp:
            if status==0 and t.date()>=trade_date_temp[0] and t.date()<trade_date_temp[-1]:
                for trade_time_temp in trade_time_comp:
                    if t.time()>=trade_time_temp[0] and t.time()<=trade_time_temp[-1]:
                        status=1
                        index_valid.append(i)
                        break
    return index_valid
    
def trade_hour(instrument):
    tradehour = instrument['tradehour']
    if tradehour=='China':
        trade_time = [[datetime.time(9,30), datetime.time(11,29)],
                      [datetime.time(13,00), datetime.time(14,59)]]
    elif tradehour=='HongKong':
        trade_time = [[datetime.time(9,30), datetime.time(11,59)],
                      [datetime.time(13,00), datetime.time(15,59)]]
    elif tradehour=='Japan':
        trade_time = [[datetime.time(8,00), datetime.time(10,29)],
                      [datetime.time(11,30), datetime.time(13,59)]]
    elif tradehour=='Australia':
        trade_time = [[datetime.time(8,00), datetime.time(13,59)]]
    elif tradehour=='India':
        trade_time = [[datetime.time(11,45), datetime.time(17,59)]]    
    elif tradehour=='Taiwan':
        trade_time = [[datetime.time(9,00), datetime.time(13,29)]]
        
    elif tradehour=='Germany':
        trade_time = [[datetime.time(8,00), datetime.time(16,29)]]
    elif tradehour=='France':
        trade_time = [[datetime.time(9,00), datetime.time(17,29)]]
    elif tradehour=='England':
        trade_time = [[datetime.time(8,00), datetime.time(16,29)]]
    elif tradehour=='America':
        trade_time = [[datetime.time(9,30), datetime.time(15,59)]]
    else:
        trade_time = []
    return trade_time
    
    
    