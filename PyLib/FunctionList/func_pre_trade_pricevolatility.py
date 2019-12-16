import pandas as pd
import numpy as np
from datetime import timedelta
#from arch import arch_model

    
#%% func_pre_trade_pricevolatility_predict_ewma
def func_pre_trade_pricevolatility_predict_ewma(df_ohlcv_1, df_buy_sell_1, time_scale_minutes=10, len_ewma=10, lambda_ewma=0.7):
            
    bar_future_return  = df_ohlcv_1.close/df_ohlcv_1.close.shift(1)-1 + df_ohlcv_1.roll
    bar_future_std = bar_future_return.rolling(time_scale_minutes).std()
        
    buy_sell_indicator = df_buy_sell_1.buy_sell_indicator.shift(1).copy()
    pos_trade_open = np.where((buy_sell_indicator!=buy_sell_indicator.shift(1)) & (1) )[0] #including trade clocolumns
    pos_trade_open = pos_trade_open[pos_trade_open>time_scale_minutes*len_ewma]
    
    pricevolatility = bar_future_std.shift(-(time_scale_minutes-1))[pos_trade_open]
    pricevolatilitypredict = pd.Series.ewm(bar_future_std, com=lambda_ewma, min_periods=len_ewma).mean()[pos_trade_open]
        
    df_pricevolatility_1 = pd.DataFrame({'pricevolatility':pricevolatility, 'pricevolatilitypredict':pricevolatilitypredict})
    
    return df_pricevolatility_1

#%% func_pre_trade_pricevolatility_predict_garch        
def func_pre_trade_pricevolatility_predict_garch(df_ohlcv_1, df_buy_sell_1, time_scale_minutes=10, len_min_st=10, len_min_lt=60, \
                                      days_train_pricetrend=150, days_test_pricetrend=7, minutes_pricetrend_volatility=30, daybeghour=5, \
                                      num_feature=2, outlier_std_cut=3):
    return
            
#    df_ohlcv_1_daybeghour    = df_ohlcv_1.shift(-daybeghour,freq='H').copy()
#    df_buy_sell_1_daybeghour = df_buy_sell_1.shift(-daybeghour,freq='H').copy()
#    
#    df_pricetrend_1_daybeghour = func_pre_trade_pricetrend_factor(df_ohlcv_1_daybeghour, df_buy_sell_1_daybeghour, time_scale_minutes, len_min_st, len_min_lt)
#    df_pricetrend_1_daybeghour['pricetrendpredict'] = np.empty(df_pricetrend_1_daybeghour.shape[0])*np.nan
#    df_pricetrend_1_daybeghour['pricetrendmean']    = np.empty(df_pricetrend_1_daybeghour.shape[0])*np.nan
#    feature_list = ['trend_st','trend_lt','vol_st','vol_lt']
#    
#    # rolling build volume profile        
#    date_beg = df_ohlcv_1_daybeghour.index[0].date()
#    date_end = df_ohlcv_1_daybeghour.index[-1].date()    
#    for date_update in np.arange(date_beg+timedelta(days=days_train_pricetrend), date_end, timedelta(days=days_test_pricetrend)):
#        df_pricetrend_1_train = df_pricetrend_1_daybeghour.truncate(before=date_update-np.timedelta64(days_train_pricetrend-1,'D'), after=date_update)
#        df_pricetrend_1_test  = df_pricetrend_1_daybeghour.truncate(before=date_update, after=date_update+np.timedelta64(days_test_pricetrend,'D'))        
#        if df_pricetrend_1_test.empty:
#            continue
#        
#        # train
#        x = df_pricetrend_1_train[feature_list].values.copy()
#        y = df_pricetrend_1_train['pricetrend'].values.copy()        
#        idx_filter = np.where( ( np.abs(x[:,3]) > 0.7 * np.median(np.abs((x[:,3]))) ) & ( np.abs(x[:,2]) > 0.7 * np.median(np.abs((x[:,2]))) ) & ( 1 ) \
#                             )[0]
#        # & ( np.abs(y-np.mean(y)) / np.std(y) < outlier_std_cut  )  \
#        # & ( np.abs(x[:,0]-np.mean(x[:,0])) / np.std(x[:,0]) < outlier_std_cut  )  \        
#        feature_select = func_linearmodel_featureselection(y[idx_filter], x[idx_filter,:], num_feature)
#        # print('Selected Features: %s' % (feature_select))
#        feature_coef, est_fit = func_linearmodel_linearregression(y[idx_filter], x[idx_filter,:], feature_select)
#        
#        # predict
#        x_test = df_pricetrend_1_test[feature_list].values.copy()
#        y_test_mean = np.ones(x_test.shape[0]) * np.mean(y)
#        y_test_predict = np.sum(x_test*feature_coef[:-1], axis=1) + feature_coef[-1]        
#        df_pricetrend_1_daybeghour.loc[df_pricetrend_1_test.index, 'pricetrendpredict']  = y_test_predict.copy()
#        df_pricetrend_1_daybeghour.loc[df_pricetrend_1_test.index, 'pricetrendmean']     = y_test_mean.copy()
#        
#    df_pricetrendpredict_1 = df_pricetrend_1_daybeghour.shift(daybeghour,freq='H').copy()
        
#    return df_pricetrendpredict_1