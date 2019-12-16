import pandas as pd
import numpy as np
from datetime import timedelta

from .func_order_intrabar import func_order_intrabar
from .func_linearmodel import func_linearmodel_featureselection
from .func_linearmodel import func_linearmodel_linearregression

#%% func_pre_trade_marketimpact_factor
def func_pre_trade_marketimpact_factor(df_order, ohlcv_1_list, pov_range=[0.05, 0.9], column_ohlc_adj=['high','low','close'], len_min_st=5, len_min_lt=60, second_valid=5):
        
    # order stats 
    df_order_intrabar = pd.DataFrame([])
    instrument_list_order = df_order.symbol.unique()
    instrument_list_match = [i[0] for i in ohlcv_1_list]
    for instrument_order in instrument_list_order:
        idx_instrument = [i for i,ltr in enumerate(instrument_list_match) if ltr==instrument_order]
        if len(idx_instrument)>0:
            df_order_temp = df_order[df_order.symbol.str.contains(instrument_order)][['amount','price']].copy()
            df_ohlcv_temp = ohlcv_1_list[idx_instrument[0]][1]
            df_order_intrabar_temp = func_order_intrabar(df_order_temp, df_ohlcv_temp, column_ohlc_adj, len_min_st, len_min_lt, second_valid)
            df_order_intrabar = df_order_intrabar.append(df_order_intrabar_temp)            
    df_order_intrabar.dropna(axis=0, inplace=True)
    df_order_intrabar.sort_index(ascending=True, inplace=True)
    
    df_order_intrabar.rename(columns={"ret_adj":"marketimpact", "bar_vol_st":"vol_st", "bar_vol_lt":"vol_lt", "bar_trend_st":"trend_st","bar_trend_lt":"trend_lt"}, inplace=True)
    df_order_intrabar = df_order_intrabar[~df_order_intrabar.index.duplicated(keep='first')]    
    df_order_intrabar = df_order_intrabar[(df_order_intrabar.amt_pov>=pov_range[0]) & (df_order_intrabar.amt_pov<=pov_range[1])]
    df_order_intrabar['trend_st'] = df_order_intrabar['trend_st'] * df_order_intrabar['side_order']
    df_order_intrabar['trend_lt'] = df_order_intrabar['trend_lt'] * df_order_intrabar['side_order']
    
    
    return df_order_intrabar

#%% func_pre_trade_marketimpact_predict        
def func_pre_trade_marketimpact_predict(df_order, ohlcv_1_list, pov_range=[0.05, 0.9], column_ohlc_adj=['high','low','close'], len_min_st=5, len_min_lt=60, second_valid=5, \
                                      days_train_marketimpact=150, days_test_marketimpact=7, daybeghour=5, \
                                      num_feature=2, outlier_std_cut=3):
            
        
    df_marketimpact_1  = func_pre_trade_marketimpact_factor(df_order, ohlcv_1_list, pov_range, column_ohlc_adj, len_min_st, len_min_lt, second_valid)    
    df_marketimpact_1_daybeghour = df_marketimpact_1.shift(-daybeghour,freq='H').copy()    
        
    df_marketimpact_1_daybeghour['marketimpactpredict'] = np.empty(df_marketimpact_1_daybeghour.shape[0])*np.nan
    df_marketimpact_1_daybeghour['marketimpactmean']    = np.empty(df_marketimpact_1_daybeghour.shape[0])*np.nan
    feature_list = ['trend_st','trend_lt','vol_st','vol_lt','amt_pov','volumeratio_mkt']
    
    # rolling build volume profile        
    date_beg = df_marketimpact_1_daybeghour.index[0].date()
    date_end = df_marketimpact_1_daybeghour.index[-1].date()    
    for date_update in np.arange(date_beg+timedelta(days=days_train_marketimpact), date_end, timedelta(days=days_test_marketimpact)):
        #df_marketimpact_1_train = df_marketimpact_1_daybeghour.truncate(before=date_update-np.timedelta64(days_train_marketimpact-1,'D'), after=date_update)
        df_marketimpact_1_train = df_marketimpact_1_daybeghour.truncate(after=date_update)
        df_marketimpact_1_test  = df_marketimpact_1_daybeghour.truncate(before=date_update, after=date_update+np.timedelta64(days_test_marketimpact,'D'))
        if df_marketimpact_1_test.empty:
            continue
        
        # train
        x = df_marketimpact_1_train[feature_list].values.copy()
        y = df_marketimpact_1_train['marketimpact'].values.copy()        
        idx_filter = np.where( ( np.abs(x[:,3]) > 0.7 * np.median(np.abs((x[:,3]))) ) & ( np.abs(x[:,2]) > 0.7 * np.median(np.abs((x[:,2]))) ) & ( 1 ) \
                             )[0]
        # & ( np.abs(y-np.mean(y)) / np.std(y) < outlier_std_cut  )  \
        # & ( np.abs(x[:,0]-np.mean(x[:,0])) / np.std(x[:,0]) < outlier_std_cut  )  \        
        feature_select = func_linearmodel_featureselection(y[idx_filter], x[idx_filter,:], num_feature)
        # print('Selected Features: %s' % (feature_select))
        feature_coef, est_fit = func_linearmodel_linearregression(y[idx_filter], x[idx_filter,:], feature_select)
        
        # predict
        x_test = df_marketimpact_1_test[feature_list].values.copy()
        y_test_mean = np.ones(x_test.shape[0]) * np.mean(y)
        y_test_predict = np.sum(x_test*feature_coef[:-1], axis=1) + feature_coef[-1]        
        df_marketimpact_1_daybeghour.loc[df_marketimpact_1_test.index, 'marketimpactpredict']  = y_test_predict.copy()
        df_marketimpact_1_daybeghour.loc[df_marketimpact_1_test.index, 'marketimpactmean']     = y_test_mean.copy()
        
    df_marketimpactpredict_1 = df_marketimpact_1_daybeghour.shift(daybeghour,freq='H').copy()
        
    return df_marketimpactpredict_1