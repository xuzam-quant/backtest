# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 21:18:36 2019

@author: zhangxu
"""

import numpy as np
import pandas as pd
import pickle

#%%
def func_get_instrument_data(date_beg, date_end, instrument, minute_interval, tc, traxexcore, indicators, filepath, download_orload):
    if download_orload==1:
        symbol_list = func_get_future_ticker(date_beg, date_end, instrument)
        bar_list = func_get_future_data(date_beg, date_end, symbol_list, minute_interval, tc, traxexcore, indicators)
        with open(filepath+instrument['symbol']+'.pickle', 'wb') as f:
            pickle.dump(dict(bar_list=bar_list),f)
        if instrument['currency']!='USD':
            symbol_list_= np.array([instrument['currency']+'USD', 'USD'+instrument['currency']])
            bar_list_ = func_get_future_data(date_beg, date_end, symbol_list_, minute_interval, tc, traxexcore, indicators)    
            try:
                df_bar_ = bar_list_[0][1]
                with open(filepath+instrument['currency']+'USD.pickle', 'wb') as f:
                    pickle.dump(dict(bar_list=bar_list_),f)
            except:
                df_bar_ = 1/bar_list_[1][1]
                with open(filepath+'USD'+instrument['currency']+'.pickle', 'wb') as f:
                    pickle.dump(dict(bar_list=bar_list_),f)
        else:
            df_bar_ = pd.DataFrame({'open':1,'high':1,'low':1,'close':1,'volume':0},index=[date_beg])
    else:
        with open(filepath+instrument['symbol']+'.pickle', 'rb') as f:
            bar_list = pickle.load(f)['bar_list']
        symbol_list = func_get_future_ticker(date_beg, date_end, instrument)
        bar_list = func_get_future_data_load(date_beg, date_end, bar_list, symbol_list)
        if instrument['currency']!='USD':
            try:
                with open(filepath+instrument['currency']+'USD.pickle', 'rb') as f:
                    bar_list_ = pickle.load(f)['bar_list']
                    df_bar_ = func_get_future_data_load(date_beg, date_end, bar_list_)[0][1]
            except:
                with open(filepath+'USD'+instrument['currency']+'.pickle', 'rb') as f:
                    bar_list_ = pickle.load(f)['bar_list']
                    df_bar_ = 1/func_get_future_data_load(date_beg, date_end, bar_list_)[0][1]
        else:        
            df_bar_ = pd.DataFrame({'open':1,'high':1,'low':1,'close':1,'volume':0},index=[date_beg])
        
    return bar_list, df_bar_

#%%
def func_get_future_ticker(date_beg, date_end, instrument):
    contract_keyword  = instrument['symbol']
    contract_asset    = instrument['asset']
    contract_interval = instrument['contract_interval']
    
    contract_month = np.array(['F','G','H','J','K','M','N','Q','U','V','X','Z'])
    future_ticker_list=np.array([])        
    if contract_interval==0:
        future_ticker_list = np.append(future_ticker_list, contract_keyword)
        return future_ticker_list
        
    date_roll = np.arange(date_end, date_beg, -1, dtype='datetime64[M]')        
    #only deal with case that contract_interval=1,3,6
    for date_i in date_roll:
        year_num = np.mod(date_i.item().year,10)
        month_num = date_i.item().month        
        ticker_temp = contract_keyword + contract_month[month_num-1] + str(year_num) + ' '+contract_asset
        if contract_interval==3:
            if month_num%3==0:
                future_ticker_list=np.append(future_ticker_list, ticker_temp)
            elif date_i==date_roll[0]:
                ticker_temp2 = contract_keyword + contract_month[int(np.ceil(month_num/3)*3-1)] + str(year_num) + ' '+contract_asset
                future_ticker_list=np.append(future_ticker_list, ticker_temp2)            
        elif contract_interval==6:
            if month_num%6==0:
                future_ticker_list=np.append(future_ticker_list, ticker_temp)                
            elif date_i==date_roll[0]:
                ticker_temp2 = contract_keyword + contract_month[int(np.ceil(month_num/6)*6-1)] + str(year_num) + ' '+contract_asset
                future_ticker_list=np.append(future_ticker_list, ticker_temp2)            
        else:
            #if date_i==date_roll[0] and month_num!=12:
                #ticker_temp2 = contract_keyword + contract_month[month_num+1-1] + str(year_num) + ' Index'
                #future_ticker_list=np.append(future_ticker_list, ticker_temp2)
            future_ticker_list=np.append(future_ticker_list, ticker_temp)
    return future_ticker_list

#%%
def func_get_future_data(date_beg, date_end, symbol_list, minute_interval, tc, traxexcore, indicators):
    bar_list = []
    for symbol in symbol_list:
        try:
            print(symbol)
            sec = traxexcore.get_symbol(symbol)            
            params = 'DAYS_BACK:0,DAYS_BACKDATE:0,START_DATE:{0},END_DATE:{1},MINUTE_INTERVAL:{2},LIVE_DATA:0,SUBSCRIPTION:0'.format(date_beg, date_end, minute_interval)
            df_bar_temp = indicators.io.OHLCBar(tc,sec,params).P
            df_bar_temp['dt'] = df_bar_temp['dt'] + np.timedelta64(minute_interval,'m')
            df_bar_temp.set_index('dt',inplace=True)
            volume_d_temp = df_bar_temp.volume.resample('1D').sum()
            volume_d_temp = volume_d_temp[volume_d_temp>0]
            ADV_peak = volume_d_temp.nlargest(n=22).mean()
            bar_list.append([str(symbol), df_bar_temp, ADV_peak])
        except:
            bar_list.append([str(symbol), np.nan])
            print(symbol+' - data error!')                        
    return bar_list

def func_get_future_data_load(date_beg, date_end, bar_list, symbol_list=[]):
    idx_remain = []
    for i in range(len(bar_list)):
        try:
            symbol_temp = bar_list[i][0]
            if symbol_temp in symbol_list or len(symbol_list)==0:
                idx_remain.append(i)
                bar_temp = bar_list[i][1]
                bar_temp = bar_temp.truncate(before=date_beg, after=date_end)
                if bar_temp.empty:
                    bar_list[i][1] = np.nan
                else:
                    bar_list[i][1] = bar_temp                    
        except:
            hehe = 1
    return [bar_list[i] for i in idx_remain]

#%%
def func_convert_curncy(df_bar, df_curncy, instrument):
    if len(df_curncy)==1:
        return df_bar/df_curncy.close[0], instrument['tick']
    
    if instrument['asset']=='Curncy' and instrument['currency']!='USD' and instrument['symbol'][:3]=='USD':
        df_bar_out = df_bar.copy()
        df_bar_out['close'] = 1/df_bar_out['close']
        return df_bar_out, instrument['tick']*np.power(df_bar_out['close'].mean(),2)
    
    df_curncy_bar = df_curncy.reindex(df_bar.index, method='ffill')
    df_bar_out = df_bar.copy()
    df_bar_out['close'] = df_bar['close'] * df_curncy_bar['close']
    df_bar_out.dropna(axis=0, inplace=True)
    if df_bar.close[0]==1:
        df_bar_out['close'] = df_bar_out['close'] / df_bar_out.close[0]
    return df_bar_out, instrument['tick']
    

            
#%%
def symbol2expire(symbol, df_bar, month_actv):
    idx_empty = symbol.find(' ')
    try:
        if idx_empty!=-1:
            if (symbol[idx_empty-2] in month_actv) or (month_actv==['all']):
                dict_month = dict(F=1,G=2,H=3,J=4,K=5,M=6,N=7,Q=8,U=9,V=10,X=11,Z=12)
                end_year  = int(symbol[idx_empty-1])
                end_month = dict_month[symbol[idx_empty-2]]
                data_end = np.datetime64('2010') + np.timedelta64(end_year,'Y') + np.timedelta64(end_month+1,'M')
                return df_bar[:data_end]
            else:
                return pd.DataFrame([])
        else:
            return df_bar
    except:
        return df_bar
            
    
def func_get_future_rollover(bar_list, roll_option, instrument):
    df_bar = pd.DataFrame([])
    roll_info = []
    
    if roll_option['method']=='DBE':
        days_roll_before_expire = roll_option['days']
        month_actv = instrument['actv']
        hour_bod   = instrument['hourbod']
        for idx in range(len(bar_list)):
            try:
                symbol =  bar_list[idx][0]
                df_bar_temp = bar_list[idx][1]
                df_bar_temp = symbol2expire(symbol, df_bar_temp, month_actv)
                if df_bar_temp.empty:
                    print(symbol+' - not active!')
                    continue
                df_bar_temp = df_bar_temp.shift(-int(hour_bod),freq='h')
                if df_bar.empty==0:
                    time_roll_trigger = (df_bar_temp.index[-1] - np.timedelta64(days_roll_before_expire,'D')).date()
                    time_intersect = df_bar.index.intersection(df_bar_temp[time_roll_trigger:].index)                    
                    if time_intersect.empty:
                        time_roll = time_roll_trigger
                        time_roll_gap = df_bar[time_roll:].index[0]-df_bar_temp[:time_roll].index[-1]
                        print(symbol+' - no intersect - '+str(time_roll_gap))
                    else:
                        time_roll = time_intersect[0]
                        time_roll_gap = np.timedelta64(0,'s')
                    df_bar = df_bar.truncate(before=time_roll)
                    df_bar.iloc[0]['roll'] = -1*(df_bar.iloc[0]['close']/df_bar_temp[:time_roll]['close'][-1]-1)
                    new_rows = df_bar_temp[:time_roll-np.timedelta64(1,'s')].copy()
                    new_rows.insert(new_rows.shape[1],'roll',0)
                    df_bar = pd.concat([new_rows,df_bar])
                else:
                    time_roll_trigger = df_bar_temp.index[-1].date()
                    time_roll = time_roll_trigger
                    time_roll_gap = np.timedelta64(0,'s')
                    df_bar = df_bar_temp.copy()
                    df_bar['roll'] = np.zeros(df_bar_temp.shape[0])
                roll_info.append([symbol, time_roll_trigger, time_roll, time_roll_gap+np.timedelta64(int(hour_bod),'h'), df_bar_temp.index[-1]+np.timedelta64(int(hour_bod),'h'), \
                                  df_bar_temp.index[0]+np.timedelta64(int(hour_bod),'h'), df_bar_temp.volume.sum()])
            except:
                print(symbol+' - roll error!')
        df_bar = df_bar.shift(int(hour_bod),freq='h')
        roll_info = pd.DataFrame(roll_info,columns=['symbol','time_roll_trigger','time_roll_exact','time_roll_gap','time_expire', 'time_effective', 'volume_sum'])
#        roll_info[['time_roll_exact','time_expire','time_effective']] = \
#            roll_info[['time_roll_exact','time_expire','time_effective']].values + np.timedelta64(int(hour_bod),'h')
        
    elif roll_option['method']=='DV':
        days_roll_before_expire_limit = roll_option['days']
        month_actv = instrument['actv']
        hour_bod   = instrument['hourbod']
        for idx in range(len(bar_list)):
            try:
                symbol =  bar_list[idx][0]
                df_bar_temp = bar_list[idx][1]
                df_bar_temp = symbol2expire(symbol, df_bar_temp, month_actv)
                if df_bar_temp.empty:
                    continue
                df_bar_temp = df_bar_temp.shift(-int(hour_bod),freq='h')
                if df_bar.empty==0:
                    volume_d = df_bar.volume.resample('1D').sum()
                    volume_d = volume_d[volume_d!=0]
                    volume_d_temp = df_bar_temp.volume.resample('1D').sum()
                    volume_d_temp = volume_d_temp[volume_d_temp!=0]
                    volume_diff = volume_d.reindex(volume_d_temp.index) - volume_d_temp
                    idx_roll = np.where((volume_diff>0) \
                                        & ( (df_bar_temp.index[-1]-volume_diff.index).days<days_roll_before_expire_limit+30 ) \
                                        & ( (df_bar_temp.index[-1]-volume_diff.index).days>=days_roll_before_expire_limit ) )[0]                    
                    if len(idx_roll)<1:
                        days_roll_before_expire = days_roll_before_expire_limit                      
                    else:
                        days_roll_before_expire = (df_bar_temp.index[-1].date() - volume_diff.index[idx_roll[0]].date()).days - 1
                        days_roll_before_expire = days_roll_before_expire * (days_roll_before_expire>0) + days_roll_before_expire_limit * (days_roll_before_expire<=0)            
                    time_roll_trigger = (df_bar_temp.index[-1] - np.timedelta64(days_roll_before_expire,'D')).date()
                    time_intersect = df_bar.index.intersection(df_bar_temp[time_roll_trigger:].index)                    
                    if time_intersect.empty:
                        time_roll = time_roll_trigger
                        time_roll_gap = df_bar[time_roll:].index[0]-df_bar_temp[:time_roll].index[-1]
                        print(symbol+' - no intersect - '+str(df_bar[time_roll:].index[0]-df_bar_temp[:time_roll].index[-1]))                    
                    else:
                        time_roll = time_intersect[0]
                        time_roll_gap = np.timedelta64(0,'s')
                    df_bar = df_bar.truncate(before=time_roll)
                    df_bar.iloc[0]['roll'] = -1*(df_bar.iloc[0]['close']/df_bar_temp[:time_roll]['close'][-1]-1)
                    new_rows = df_bar_temp[:time_roll-np.timedelta64(1,'s')].copy()
                    new_rows.insert(new_rows.shape[1],'roll',0)
                    df_bar = pd.concat([new_rows,df_bar])
                else:
                    time_roll_trigger = df_bar_temp.index[-1].date()
                    time_roll = time_roll_trigger
                    time_roll_gap = np.timedelta64(0,'s')
                    df_bar = df_bar_temp.copy()
                    df_bar['roll'] = np.zeros(df_bar_temp.shape[0])
                roll_info.append([symbol, time_roll_trigger, time_roll+np.timedelta64(int(hour_bod),'h'), time_roll_gap, df_bar_temp.index[-1]+np.timedelta64(int(hour_bod),'h'), \
                                  df_bar_temp.index[0]+np.timedelta64(int(hour_bod),'h'), df_bar_temp.volume.sum()])
            except:
                print(symbol+' - roll error!')
        df_bar = df_bar.shift(int(hour_bod), freq='h')        
        roll_info = pd.DataFrame(roll_info, columns=['symbol','time_roll_trigger','time_roll_exact','time_roll_gap','time_expire', 'time_effective', 'volume_sum'])
#        roll_info[['time_roll_exact','time_expire','time_effective']] = \
#            roll_info[['time_roll_exact','time_expire','time_effective']].values + np.timedelta64(int(hour_bod),'h')
    
    df_bar.sort_index(ascending=True, inplace=True)     
    return df_bar, roll_info


#%%
def func_get_future_normalize(df_bar, method):    
    bar_return  = df_bar.close/df_bar.close.shift(1)-1
    bar_return.fillna(0,inplace=True)
    roll_return = df_bar.roll.copy()    
        
    if method=='raw':
        norm_return = bar_return + roll_return    
        df_bar_norm = np.cumprod(norm_return+1).rename('close').to_frame()
        df_bar_norm['volume'] = df_bar.volume.copy()
        df_bar_norm['close'] = df_bar_norm.close * (df_bar.close[-1]/df_bar_norm.close[-1])
    elif method=='unit':
        norm_return = bar_return + roll_return    
        df_bar_norm = np.cumprod(norm_return+1).rename('close').to_frame()
        df_bar_norm['volume'] = df_bar.volume.copy()
    elif method=='rawnoroll':
        df_bar_norm = df_bar[['close','volume']].copy()
    elif method=='unitnoroll':        
        df_bar_norm = df_bar[['close','volume']].copy()
        df_bar_norm['close'] = df_bar_norm.close / df_bar_norm.close[0]
        
    return df_bar_norm