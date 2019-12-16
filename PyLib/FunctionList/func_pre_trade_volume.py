import pandas as pd
import numpy as np
from datetime import timedelta
    
#%% func_pre_trade_volume_profile
def func_pre_trade_volume_profile(df_ohlcv_1, time_scale_minutes=30, daybeghour=5):
        
    df_ohlcv_bar = df_ohlcv_1['volume'].resample(str(int(time_scale_minutes))+'Min').mean()
    df_ohlcv_bar.fillna(0, inplace=True)
    time_intraday_bar = df_ohlcv_bar.index.time
    time_intraday     = np.unique(time_intraday_bar)
    volume_intraday   = np.array([df_ohlcv_bar[time_intraday_bar==i].mean() for i in time_intraday])
    volume_intraday   = [0 if np.isnan(i) else i for i in volume_intraday]    
    
    volume_1_daybeghour = df_ohlcv_1['volume'].shift(-daybeghour,freq='H').copy()    
    volume_d = volume_1_daybeghour.resample('1D').sum()    
    volume_d = volume_d[volume_d>0]
    volume_d = volume_d.shift(daybeghour,freq='H')
    df_ohlcv_1_ratio = df_ohlcv_1['volume'] / volume_d.reindex(df_ohlcv_1.index, method='ffill')
    df_ohlcv_bar_ratio = df_ohlcv_1_ratio.resample(str(int(time_scale_minutes))+'Min').mean()
    df_ohlcv_bar_ratio.fillna(0, inplace=True)
    time_intraday_bar_ratio = df_ohlcv_bar_ratio.index.time
    volume_intraday_ratio   = np.array([df_ohlcv_bar_ratio[time_intraday_bar_ratio==i].mean() for i in time_intraday])
    volume_intraday_ratio   = [0 if np.isnan(i) else i for i in volume_intraday_ratio]    
    
    df_volume_profile = pd.DataFrame({'volumemean':volume_intraday,'volumeratio':volume_intraday_ratio}, index=time_intraday)
    return df_volume_profile

#%% func_pre_trade_volume_profile        
def func_pre_trade_volume_predict(df_ohlcv_1, time_scale_minutes=30, daybeghour=5, days_train_volume=10, days_test_volume=1, \
                                  days_filter_volume=90, percent_filter_volume=0.9, days_latest_volume=1, minutes_volume_volatility=30):

    df_ohlcv_1_daybeghour = df_ohlcv_1.shift(-daybeghour,freq='H').copy()
    df_volumepredict_1 = df_ohlcv_1_daybeghour.volume.copy().to_frame()
    df_volumepredict_1['volumeratio'] = np.empty(df_volumepredict_1.shape[0])*np.nan
    df_volumepredict_1['volumemean'] = np.empty(df_volumepredict_1.shape[0])*np.nan
    volume_d = df_ohlcv_1_daybeghour['volume'].resample('1D').sum()
    volume_d = volume_d[volume_d>0]
    volume_d = volume_d.rolling(days_latest_volume).mean()
    volume_d_1 = volume_d.shift(1).reindex(df_volumepredict_1.index,method='ffill')
    
    # rolling build volume profile        
    date_beg = df_ohlcv_1_daybeghour.index[0].date()
    date_end = df_ohlcv_1_daybeghour.index[-1].date()    
    #for date_update in np.arange(date_beg+timedelta(days=days_train_volume), date_end, timedelta(days=days_test_volume)):
    for date_update in np.arange(date_beg+timedelta(days=days_filter_volume), date_end, timedelta(days=days_test_volume)):
        #df_ohlcv_1_train = df_ohlcv_1_daybeghour.truncate(before=date_update-np.timedelta64(days_train_volume-1,'D'), after=date_update)        
        # remove big volume days, and find only days_train_volume valid days to build model
        df_ohlcv_1_train = df_ohlcv_1_daybeghour.truncate(before=date_update-np.timedelta64(days_filter_volume-1,'D'), after=date_update)        
        volume_d_train = volume_d.truncate(before=date_update-np.timedelta64(days_filter_volume-1,'D'), after=date_update)
        volume_d_cut   = volume_d_train.quantile(percent_filter_volume, interpolation='nearest')
        idx_d_select_train = np.where(volume_d_train<=volume_d_cut)[0]
        df_ohlcv_1_train['date'] = df_ohlcv_1_train.index.date
        df_ohlcv_1_train = df_ohlcv_1_train.loc[df_ohlcv_1_train.date.isin(volume_d_train.iloc[idx_d_select_train[-1-days_train_volume+1:-1]].index.date)]
        
        df_volume_profile_train = func_pre_trade_volume_profile(df_ohlcv_1_train, time_scale_minutes, daybeghour=0)
        
        df_ohlcv_1_test  = df_ohlcv_1_daybeghour.truncate(before=date_update, after=date_update+np.timedelta64(days_test_volume,'D'))        
        df_volume_test_1 = df_volume_profile_train.reindex(df_ohlcv_1_test.index.time,method='ffill')        
        df_volume_test_1.set_index(df_ohlcv_1_test.index, inplace=True)
        df_volume_test_1['volumeratio'] = df_volume_test_1['volumeratio'] * volume_d_1.loc[df_volume_test_1.index]
        df_volumepredict_1.loc[df_ohlcv_1_test.index, 'volumeratio']   = df_volume_test_1['volumeratio'].values.copy()
        df_volumepredict_1.loc[df_ohlcv_1_test.index, 'volumemean']    = df_volume_test_1['volumemean'].values.copy()
            
    df_volumepredict_1 = df_volumepredict_1.shift(daybeghour,freq='H')    
    df_volumepredict_1['volumeratio_vol'] = (df_volumepredict_1.volumeratio-df_volumepredict_1.volume).rolling(minutes_volume_volatility).std()
    df_volumepredict_1['volumemean_vol']  = (df_volumepredict_1.volumemean -df_volumepredict_1.volume).rolling(minutes_volume_volatility).std()
    return df_volumepredict_1