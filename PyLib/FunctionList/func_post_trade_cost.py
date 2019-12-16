#%% func_post_trade_cost

def func_post_trade_cost(df_buy_sell_model, df_ohlcv_1, df_ohlcv_cash_1, spread, alphadecay_minutes_list, \
                         column_ohlc_adj=['high','low','close'], delay_minutes=1, decay_minutes=5, exe_minutes=3, volume_minutes=1, pov_rate_limit=0.2, marketimpact_cost_1min=[0,0]):
    import pandas as pd
    import numpy as np
        
    df_buy_sell_1  = df_buy_sell_model.reindex(df_ohlcv_1.index, method='ffill')    
    df_return_1 = df_ohlcv_1[[]].copy()
    
    buy_sell_indicator = df_buy_sell_1.buy_sell_indicator.shift(1).fillna(0).copy()
    bar_future_return  = df_ohlcv_1.close/df_ohlcv_1.close.shift(1)-1
    bar_cash_return    = df_buy_sell_1.close/df_buy_sell_1.close.shift(1)-1
    bar_roll_return    = df_ohlcv_1.roll.copy()    
    
    bar_vwaphold_return   = df_ohlcv_1[column_ohlc_adj].mean(axis=1) / df_ohlcv_1.close - 1 #vwap price to last close    
    bar_future_return_pt  = bar_future_return.rolling(delay_minutes+exe_minutes).mean().shift(-delay_minutes-exe_minutes+1) # price trend
    bar_future_return_pt2 = bar_future_return.rolling(delay_minutes+exe_minutes*2).mean().shift(-delay_minutes-exe_minutes*2+1) # price trend, flip double
    bar_volume_completion = df_ohlcv_1.volume*pov_rate_limit/volume_minutes
    #bar_volume_completion[bar_volume_completion>2] = 2        
    bar_volume_completion[bar_volume_completion>1] = 1
    
    bar_marketimpact_return = pd.Series(np.ones(df_ohlcv_cash_1.shape[0])*marketimpact_cost_1min[0], index=df_ohlcv_cash_1.index )
    bar_marketimpact_return = bar_marketimpact_return.reindex(df_ohlcv_1.index)
    bar_marketimpact_return.fillna(marketimpact_cost_1min[1], inplace=True)
    
    bar_future_return_roll  = bar_future_return + bar_roll_return
    price_future_roll       = np.cumprod(bar_future_return_roll+1)
    price_future_roll_model = price_future_roll.reindex(df_buy_sell_model.index, method='ffill')
    bar_future_return_model = price_future_roll_model/price_future_roll_model.shift(1)-1
    bar_cash_return_model   = df_buy_sell_model.close/df_buy_sell_model.close.shift(1)-1
    bar_basis_return_model  = bar_future_return_model - bar_cash_return_model 
    pnl_basis_return_model  = np.cumprod(bar_basis_return_model+1)
    pnl_basis_return = pnl_basis_return_model.reindex(df_ohlcv_1.index,method='ffill')
    bar_basis_return = pnl_basis_return/pnl_basis_return.shift(1)-1
    
    df_return_1['buy_sell_indicator'] = buy_sell_indicator.copy()  # here return means hold in this bar
    df_return_1['bar_future_return']  = bar_future_return.copy()
    df_return_1['bar_cash_return']    = bar_cash_return.copy()
    df_return_1['bar_roll_return']    = bar_roll_return.copy()
    df_return_1['cash_return']        = bar_cash_return   * buy_sell_indicator
    df_return_1['future_return']      = bar_future_return * buy_sell_indicator
    df_return_1['roll_return']        = bar_roll_return   * buy_sell_indicator
    df_return_1['basis_return']       = bar_basis_return  * buy_sell_indicator
    df_return_1['spread_return']      = - spread/2 /df_ohlcv_1.close * np.abs((df_return_1.buy_sell_indicator-df_return_1.buy_sell_indicator.shift(1))) \
                                        - spread/df_ohlcv_1.close * (df_ohlcv_1.roll!=0)   # trade + roll
                                        
    df_return_1['decay_return']         = np.zeros(df_return_1.shape[0])
    df_return_1['delay_return']         = np.zeros(df_return_1.shape[0])    
    df_return_1['pricetrend_return']    = np.zeros(df_return_1.shape[0])
    df_return_1['timingrisk_return']    = np.zeros(df_return_1.shape[0]) 
    df_return_1['vwaphold_return']      = np.zeros(df_return_1.shape[0])    
    df_return_1['liquidityrisk_return'] = np.zeros(df_return_1.shape[0])
    df_return_1['opportunity_return']   = np.zeros(df_return_1.shape[0])
    df_return_1['marketimpact_return']  = np.zeros(df_return_1.shape[0]) # not calculate in this function
    
    df_return_1['barvolpt_return']      = np.zeros(df_return_1.shape[0]) 
    df_return_1['completion_missing']   = np.zeros(df_return_1.shape[0])
    df_return_1['bar_volume_completion']  = bar_volume_completion # not calculate in this function
    df_return_1['volume']  = df_ohlcv_1.volume.copy()
    
    #pos_trade_open_1 = np.where((df_return_1.buy_sell_indicator!=df_return_1.buy_sell_indicator.shift(1)) & (df_return_1.buy_sell_indicator!=0) )[0]
    pos_trade_open_1 = np.where((df_return_1.buy_sell_indicator!=df_return_1.buy_sell_indicator.shift(1)) & (1) )[0] #including trade close
    
    # decay_return, continuous position changing
    pos_trade_open_1 = pos_trade_open_1[(pos_trade_open_1+decay_minutes<df_return_1.shape[0]) & (pos_trade_open_1!=0)]
    position_flip_1  = df_return_1.buy_sell_indicator.diff().iloc[pos_trade_open_1].values
    for idx_minutes in range(decay_minutes):
        df_return_1.iloc[pos_trade_open_1+idx_minutes, df_return_1.columns.get_loc('decay_return')] = \
            bar_future_return[pos_trade_open_1+idx_minutes].values * (position_flip_1/decay_minutes*idx_minutes-position_flip_1)
    
    # delay_return
    pos_trade_open_1 = pos_trade_open_1[(pos_trade_open_1+delay_minutes<df_return_1.shape[0]) & (pos_trade_open_1!=0)]
    position_flip_1  = df_return_1.buy_sell_indicator.diff().iloc[pos_trade_open_1].values
    for idx_minutes in range(delay_minutes):
        df_return_1.iloc[pos_trade_open_1+idx_minutes, df_return_1.columns.get_loc('delay_return')] = \
            bar_future_return[pos_trade_open_1+idx_minutes].values * (-position_flip_1)
        df_return_1.iloc[pos_trade_open_1+idx_minutes, df_return_1.columns.get_loc('barvolpt_return')] = \
            df_return_1.iloc[pos_trade_open_1+idx_minutes-1, df_return_1.columns.get_loc('barvolpt_return')].values + bar_future_return[pos_trade_open_1+idx_minutes].values \
            - (np.abs(position_flip_1)==1) * bar_future_return_pt[pos_trade_open_1].values - (np.abs(position_flip_1)==2) * bar_future_return_pt2[pos_trade_open_1].values
            
    # pricetrend_return and timingrisk_return
    pos_trade_open_1 = pos_trade_open_1[(pos_trade_open_1+delay_minutes+exe_minutes*2<df_return_1.shape[0]) & (pos_trade_open_1!=0)]
    position_flip_1  = df_return_1.buy_sell_indicator.diff().iloc[pos_trade_open_1].values
    for idx_minutes in range(exe_minutes*2):
        volume_nohold_minutes  = np.sign(position_flip_1) * np.minimum(idx_minutes/exe_minutes-np.abs(position_flip_1), 0)
        execute_finish_ornot = (np.minimum(idx_minutes/exe_minutes-np.abs(position_flip_1),0)==0)  # 0:not_finish, 1:finished
        
        df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes, df_return_1.columns.get_loc('barvolpt_return')] = \
            df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes-1, df_return_1.columns.get_loc('barvolpt_return')].values + bar_future_return[pos_trade_open_1+delay_minutes+idx_minutes].values \
            - (np.abs(position_flip_1)==1) * bar_future_return_pt[pos_trade_open_1].values - (np.abs(position_flip_1)==2) * bar_future_return_pt2[pos_trade_open_1].values
        
        df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes, df_return_1.columns.get_loc('pricetrend_return')] = \
            ( (np.abs(position_flip_1)==1) * bar_future_return_pt[pos_trade_open_1].values + (np.abs(position_flip_1)==2) * bar_future_return_pt2[pos_trade_open_1].values ) \
            * volume_nohold_minutes
                        
        df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes, df_return_1.columns.get_loc('timingrisk_return')] = \
            ( df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes, df_return_1.columns.get_loc('barvolpt_return')].values \
              - df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes-1, df_return_1.columns.get_loc('barvolpt_return')].values ) \
            * volume_nohold_minutes
    
        df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes, df_return_1.columns.get_loc('vwaphold_return')] = \
            bar_vwaphold_return[pos_trade_open_1+delay_minutes+idx_minutes].values * 1/exe_minutes * np.sign(position_flip_1) \
            * (execute_finish_ornot==0)
        
        df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes, df_return_1.columns.get_loc('marketimpact_return')] = \
            bar_marketimpact_return[pos_trade_open_1+delay_minutes+idx_minutes].values * 1/exe_minutes \
            * (execute_finish_ornot==0)
        
        # deal with volume    
        if idx_minutes==0:
            df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes-1, df_return_1.columns.get_loc('completion_missing')] = 0 #-position_flip_1.copy()
        df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes, df_return_1.columns.get_loc('completion_missing')] = \
            ( df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes-1, df_return_1.columns.get_loc('completion_missing')].values \
              + 1/exe_minutes*np.sign(position_flip_1) * (bar_volume_completion[pos_trade_open_1+delay_minutes+idx_minutes].values-1) ) \
            * (execute_finish_ornot==0)
        
        df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes, df_return_1.columns.get_loc('liquidityrisk_return')] = \
            bar_future_return[pos_trade_open_1+delay_minutes+idx_minutes].values \
            * df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes-1, df_return_1.columns.get_loc('completion_missing')].values \
            * (execute_finish_ornot==0)
            
        df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes-1, df_return_1.columns.get_loc('completion_missing')] = \
            0 + (execute_finish_ornot==1) * df_return_1.iloc[pos_trade_open_1+delay_minutes+idx_minutes-1, df_return_1.columns.get_loc('completion_missing')].values            
    
    df_return_1['completion_missing'] = df_return_1['completion_missing'].shift(1)
    df_return_1['completion_missing'].replace(to_replace=0, value=np.nan, inplace=True)    
    df_return_1.iloc[pos_trade_open_1, df_return_1.columns.get_loc('completion_missing')] = 0
    df_return_1['completion_missing'].replace(to_replace=np.nan, inplace=True, method='ffill')
    df_return_1['completion_missing'] = df_return_1['completion_missing'] * (df_return_1['buy_sell_indicator'].diff()==0)
    df_return_1['opportunity_return'] = buy_sell_indicator * bar_future_return * df_return_1['completion_missing']    
    df_return_1.fillna(0,inplace=True)
    
        
    # alpha decay return and pnl
    df_return_alphadecay_1       = df_ohlcv_1[[]].copy()
    df_return_alphadecay_best_1  = df_ohlcv_1[[]].copy()
    df_return_alphadecay_worst_1 = df_ohlcv_1[[]].copy()
    for idx_minutes in alphadecay_minutes_list:
        df_return_alphadecay_1[str(idx_minutes)] = (df_return_1.bar_future_return+df_return_1.bar_roll_return) * df_return_1.buy_sell_indicator.shift(idx_minutes)
        bar_high_adj_return = df_ohlcv_1[column_ohlc_adj].mean(axis=1).rolling(np.abs(idx_minutes)+1).max().shift(-idx_minutes)/df_ohlcv_1.close-1
        bar_low_adj_return  = df_ohlcv_1[column_ohlc_adj].mean(axis=1).rolling(np.abs(idx_minutes)+1).min().shift(-idx_minutes)/df_ohlcv_1.close-1    
        df_return_alphadecay_best_1[str(idx_minutes)]  = (df_return_1.bar_future_return+df_return_1.bar_roll_return) * df_return_1.buy_sell_indicator + \
            df_return_1.buy_sell_indicator.diff().abs() * ( (df_return_1.buy_sell_indicator.diff()>0)*bar_low_adj_return.shift(1)*-1 + (df_return_1.buy_sell_indicator.diff()<0)*bar_high_adj_return.shift(1)*1 )
        df_return_alphadecay_worst_1[str(idx_minutes)] = (df_return_1.bar_future_return+df_return_1.bar_roll_return) * df_return_1.buy_sell_indicator + \
            df_return_1.buy_sell_indicator.diff().abs() * ( (df_return_1.buy_sell_indicator.diff()>0)*bar_high_adj_return.shift(1)*-1 + (df_return_1.buy_sell_indicator.diff()<0)*bar_low_adj_return.shift(1)*1 )
    df_return_alphadecay_1.fillna(0,inplace=True)    
    df_return_alphadecay_best_1.fillna(0,inplace=True)
    df_return_alphadecay_worst_1.fillna(0,inplace=True)
        
    return df_return_1, df_return_alphadecay_1, df_return_alphadecay_best_1, df_return_alphadecay_worst_1