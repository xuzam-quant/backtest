#%% func_order_intrabar

def func_order_intrabar(df_order, df_ohlcv, column_ohlc_adj=['high','low','close'], len_min_st=5, len_min_lt=30, second_valid=5, len_day_volumestats=15):
    import pandas as pd
    import numpy as np
    from datetime import timedelta
        
    df_order_intrabar = pd.DataFrame(columns=['ret_adj', 'amt_pov', 'bar_vol_st', 'bar_vol_lt', 'bar_trend_st', 'bar_trend_lt', 'side_order', 'amt_order', 'price_order', 'amt_mkt', 'volumeratio_mkt'])    
    
    bar_return = df_ohlcv.close/df_ohlcv.close.shift(1)-1
    trend_st = bar_return.rolling(len_min_st).mean()
    trend_lt = bar_return.rolling(len_min_lt).mean()
            
    trp = np.max([df_ohlcv.high-df_ohlcv.low, np.abs(df_ohlcv.high - df_ohlcv.shift(1).close), np.abs(df_ohlcv.low  - df_ohlcv.shift(1).close)],axis=0) / df_ohlcv.close
    atrp_st = trp.rolling(len_min_st).mean()
    atrp_lt = trp.rolling(len_min_lt).mean()    

    volume_stats = df_ohlcv.volume.rolling(str(int(len_day_volumestats))+'D').mean()
    
    # find orders within 1min and merge
    df_order['time_diff'] = df_order.index.to_series().diff()
    df_order['minute'] = df_order.index.minute
    pos_trade_1min_beg = np.where( ( (df_order.time_diff<=timedelta(minutes=1)) & (df_order.minute!=df_order.minute.shift(1)) ) \
                                  | ( (df_order.time_diff>timedelta(minutes=1)) &  (df_order.index.second<=second_valid) ) )[0] 
    time_beg = df_order.iloc[pos_trade_1min_beg].index.values.astype('datetime64[m]')
    time_end = time_beg + np.timedelta64(59,'s')
    for i in range(time_beg.shape[0]):
        if time_beg[i] in df_ohlcv.index:            
            if df_order[time_beg[i]:time_end[i]].index[-1].second<=60-second_valid and df_order.shift(-1).loc[time_beg[i]:time_end[i]].time_diff[-1]>timedelta(minutes=1):                
                continue
                        
            amt_order  = df_order[time_beg[i]:time_end[i]].amount.sum()
            side_order = np.sign(amt_order)
            price_order= np.sum(df_order[time_beg[i]:time_end[i]].amount * df_order[time_beg[i]:time_end[i]].price) / amt_order
            ret_adj    = -side_order*(price_order/df_ohlcv.loc[time_beg[i]][column_ohlc_adj].mean()-1)
            amt_mkt    = df_ohlcv.loc[time_beg[i]].volume
            if df_ohlcv.loc[time_beg[i]].volume==0:
                amt_pov=0
            else:
                amt_pov=side_order*amt_order/df_ohlcv.loc[time_beg[i]].volume
                        
            bar_vol_st = atrp_st.loc[time_beg[i]].copy()
            bar_vol_lt = atrp_lt.loc[time_beg[i]].copy()
            bar_trend_st = side_order*trend_st.loc[time_beg[i]].copy()
            bar_trend_lt = side_order*trend_lt.loc[time_beg[i]].copy()
            volumeratio_mkt = amt_mkt / volume_stats.loc[time_beg[i]]        
            
            df_order_intrabar.loc[time_beg[i]] = np.array([ret_adj, amt_pov, bar_vol_st, bar_vol_lt, bar_trend_st, bar_trend_lt, side_order, amt_order, price_order, amt_mkt, volumeratio_mkt])
            
    return df_order_intrabar


#%% func_order_time

def func_order_time(df_order, df_ohlcv):
    import pandas as pd
    import numpy as np
    from datetime import timedelta
            
    #df_order_time     = pd.DataFrame(columns=['minute', 'amt_order', 'amt_pov', 'amt_mkt', 'time_beg', 'time_end'])
    
    # find orders within 1min and merge
    df_order['time_diff'] = df_order.index.to_series().diff()
        
    pos_trade_beg  = np.where( (df_order.time_diff>timedelta(minutes=1)) & (1) )[0]
    pos_trade_end  = np.append(pos_trade_beg-1, df_order.shape[0]-1)
    pos_trade_beg  = np.append(0, pos_trade_beg)    
    time_order_beg = df_order.iloc[pos_trade_beg].index.values.astype('datetime64[m]')    
    time_order_end = df_order.iloc[pos_trade_end].index.values.astype('datetime64[m]')    
    period_exe     = df_order.iloc[pos_trade_end].index - df_order.iloc[pos_trade_beg].index 
    minute_exe     = period_exe.total_seconds()/60
    df_order_time  = pd.DataFrame({'minute':minute_exe,'time_beg':df_order.iloc[pos_trade_beg].index.copy(),'time_end':df_order.iloc[pos_trade_end].index.copy()},index=time_order_end)
        
    amt_order = np.zeros(len(pos_trade_beg))
    amt_pov   = np.zeros(len(pos_trade_beg))
    amt_mkt   = np.zeros(len(pos_trade_beg))
    
    for i in range(len(pos_trade_beg)):
        amt_order[i] = df_order.iloc[pos_trade_beg[i]:pos_trade_end[i]].amount.sum()
        amt_mkt[i]   = df_ohlcv[time_order_beg[i]:time_order_end[i]].volume.sum() 
        if time_order_beg[i] in df_ohlcv.index:
            amt_mkt[i] = amt_mkt[i] - df_ohlcv.loc[time_order_beg[i]].volume*df_order.iloc[pos_trade_beg[i]].name.second/60
        if time_order_end[i] in df_ohlcv.index:
            amt_mkt[i] = amt_mkt[i] - df_ohlcv.loc[time_order_end[i]].volume*(60-df_order.iloc[pos_trade_end[i]].name.second)/60
        if amt_mkt[i]==0:
            amt_pov[i] = np.nan
        else:
            amt_pov[i] = np.abs(amt_order[i]) / amt_mkt[i]
        
    df_order_time['amt_pov'] = amt_pov
    df_order_time['amt_order'] = amt_order
    df_order_time['amt_mkt'] = amt_mkt
        
    return df_order_time