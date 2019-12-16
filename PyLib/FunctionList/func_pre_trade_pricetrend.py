import pandas as pd
import numpy as np
from datetime import timedelta

from .func_linearmodel import func_linearmodel_featureselection
from .func_linearmodel import func_linearmodel_linearregression
    
#%% func_pre_trade_pricetrend_factor
def func_pre_trade_pricetrend_factor(df_ohlcv_1, df_buy_sell_1, time_scale_minutes=10, len_min_st=10, len_min_lt=60):
            
    buy_sell_indicator = df_buy_sell_1.buy_sell_indicator.shift(1).copy()
    bar_future_return  = df_ohlcv_1.close/df_ohlcv_1.close.shift(1)-1 + df_ohlcv_1.roll
    bar_future_pricetrend = bar_future_return.rolling(time_scale_minutes).mean().shift(-(time_scale_minutes-1))
    
    pos_trade_open = np.where((buy_sell_indicator!=buy_sell_indicator.shift(1)) & (1) )[0] #including trade clocolumns
    pos_trade_open = pos_trade_open[pos_trade_open>1]
    position_flip  = buy_sell_indicator.diff(1)[pos_trade_open]
    
    #pricetrend = (bar_future_pricetrend * -np.sign(position_flip)).iloc[pos_trade_open]
    pricetrend = bar_future_pricetrend[pos_trade_open].copy()
    trend_st = bar_future_return.rolling(len_min_st).mean().shift(1)[pos_trade_open]
    trend_lt = bar_future_return.rolling(len_min_lt).mean().shift(1)[pos_trade_open]
    trp = np.max([df_ohlcv_1.high-df_ohlcv_1.low, np.abs(df_ohlcv_1.high - df_ohlcv_1.shift(1).close), np.abs(df_ohlcv_1.low  - df_ohlcv_1.shift(1).close)],axis=0) / df_ohlcv_1.close
    atrp_st = trp.rolling(len_min_st).mean().shift(1)[pos_trade_open]
    atrp_lt = trp.rolling(len_min_lt).mean().shift(1)[pos_trade_open]
    
    df_pricetrend_1 = pd.DataFrame({'pricetrend':pricetrend, 'trend_st':trend_st, 'trend_lt':trend_lt, 'vol_st':atrp_st, 'vol_lt':atrp_lt})
    
    return df_pricetrend_1

#%% func_pre_trade_pricetrend_predict        
def func_pre_trade_pricetrend_predict(df_ohlcv_1, df_buy_sell_1, time_scale_minutes=10, len_min_st=10, len_min_lt=60, \
                                      days_train_pricetrend=150, days_test_pricetrend=7, minutes_pricetrend_volatility=30, daybeghour=5, \
                                      num_feature=2, outlier_std_cut=3):
            
    df_ohlcv_1_daybeghour    = df_ohlcv_1.shift(-daybeghour,freq='H').copy()
    df_buy_sell_1_daybeghour = df_buy_sell_1.shift(-daybeghour,freq='H').copy()
    
    df_pricetrend_1_daybeghour = func_pre_trade_pricetrend_factor(df_ohlcv_1_daybeghour, df_buy_sell_1_daybeghour, time_scale_minutes, len_min_st, len_min_lt)
    df_pricetrend_1_daybeghour['pricetrendpredict'] = np.empty(df_pricetrend_1_daybeghour.shape[0])*np.nan
    df_pricetrend_1_daybeghour['pricetrendmean']    = np.empty(df_pricetrend_1_daybeghour.shape[0])*np.nan
    feature_list = ['trend_st','trend_lt','vol_st','vol_lt']
    
    # rolling build volume profile        
    date_beg = df_ohlcv_1_daybeghour.index[0].date()
    date_end = df_ohlcv_1_daybeghour.index[-1].date()    
    for date_update in np.arange(date_beg+timedelta(days=days_train_pricetrend), date_end, timedelta(days=days_test_pricetrend)):
        df_pricetrend_1_train = df_pricetrend_1_daybeghour.truncate(before=date_update-np.timedelta64(days_train_pricetrend-1,'D'), after=date_update)
        df_pricetrend_1_test  = df_pricetrend_1_daybeghour.truncate(before=date_update, after=date_update+np.timedelta64(days_test_pricetrend,'D'))        
        if df_pricetrend_1_test.empty:
            continue
        
        # train
        x = df_pricetrend_1_train[feature_list].values.copy()
        y = df_pricetrend_1_train['pricetrend'].values.copy()        
        idx_filter = np.where( ( np.abs(x[:,3]) > 0.7 * np.median(np.abs((x[:,3]))) ) & ( np.abs(x[:,2]) > 0.7 * np.median(np.abs((x[:,2]))) ) & ( 1 ) \
                             )[0]
        # & ( np.abs(y-np.mean(y)) / np.std(y) < outlier_std_cut  )  \
        # & ( np.abs(x[:,0]-np.mean(x[:,0])) / np.std(x[:,0]) < outlier_std_cut  )  \        
        feature_select = func_linearmodel_featureselection(y[idx_filter], x[idx_filter,:], num_feature)
        # print('Selected Features: %s' % (feature_select))
        feature_coef, est_fit = func_linearmodel_linearregression(y[idx_filter], x[idx_filter,:], feature_select)
        
        # predict
        x_test = df_pricetrend_1_test[feature_list].values.copy()
        y_test_mean = np.ones(x_test.shape[0]) * np.mean(y)
        y_test_predict = np.sum(x_test*feature_coef[:-1], axis=1) + feature_coef[-1]        
        df_pricetrend_1_daybeghour.loc[df_pricetrend_1_test.index, 'pricetrendpredict']  = y_test_predict.copy()
        df_pricetrend_1_daybeghour.loc[df_pricetrend_1_test.index, 'pricetrendmean']     = y_test_mean.copy()
        
    df_pricetrendpredict_1 = df_pricetrend_1_daybeghour.shift(daybeghour,freq='H').copy()
        
    return df_pricetrendpredict_1