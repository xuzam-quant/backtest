import numpy as np
import pandas as pd
import pickle
import os
import sys
import matplotlib.pyplot as plt
from datetime import datetime

sys.path.append('..\\..\\PyLib')
from FunctionList import *

strategy = 'SP'
symbol   = 'XAUUSD'
minute_interval = 60

start_date = np.datetime64('2011-01-01')
end_date   = np.datetime64('2019-04-01')

dict_win_size = dict(default=500)
dict_filter_lambda = dict(default=10000)
dict_std_mul  = dict(default=1.8)

filepath = '..\\..\\Data\\market\\forex\\'
#%% ohlcv
with open(filepath+symbol+'.pickle','rb') as f:
    raw_data = pickle.load(f)
df_bar_1 = raw_data['df_bar_1']


df_bar_30 = df_bar_1.resample(str(int(minute_interval))+'Min').agg({'open':'first','high':'max','low':'min','close':'last'})
df_bar_30['volume'] = df_bar_1['volume'].resample(str(int(minute_interval))+'Min').sum()
df_bar_30.dropna(axis=0, inplace=True)
df_bar_30.set_index(df_bar_30.index+np.timedelta64(int(minute_interval),'m'),inplace=True)
df_bar_30 = df_bar_30.truncate(before=start_date, after=end_date)

time_30 = df_bar_30.index.values.copy()
open_30 = df_bar_30.open.values.copy()
high_30 = df_bar_30.high.values.copy()
low_30 = df_bar_30.low.values.copy()
close_30 = df_bar_30.close.values.copy()
volume_30 = df_bar_30.volume.values.copy()

#%% indicator
if symbol in dict_win_size.keys():
    win_size = dict_win_size[symbol]    
    filter_lambda = dict_filter_lambda[symbol]    
    std_mul  = dict_std_mul[symbol]    
else:
    win_size = dict_win_size['default'] 
    filter_lambda = dict_filter_lambda['default']    
    std_mul  = dict_std_mul['default'] 
    
filter_live_30 = func_filter_hp(close_30, win_size, filter_lambda)
upper_bound_30 = filter_live_30.copy()
lower_bound_30 = filter_live_30.copy()
for t in range(len(time_30)):
    std_error = np.std(close_30[t-win_size+1:t+1]-filter_live_30[t-win_size+1:t+1])
    upper_bound_30[t] = filter_live_30[t] + std_error * std_mul
    lower_bound_30[t] = filter_live_30[t] - std_error * std_mul
    
time_30_hour = df_bar_30.index.hour.values
    
#%% strategy
buy_sell_indicator_30 = np.zeros(len(time_30))

backtest_start = 500
backtest_end   = len(time_30)

change_indicator = np.zeros(len(time_30))
idx_change_pos = 0
idx_change_neg = 0
block_time = 3

for t in range(backtest_start, backtest_end):
    buy_sell_indicator_30[t] = buy_sell_indicator_30[t-1]
            
    if filter_live_30[t]>filter_live_30[t-1] and filter_live_30[t-1]<filter_live_30[t-2]:
        change_indicator[t] = 1        
        idx_change_pos = t
    if filter_live_30[t]<filter_live_30[t-1] and filter_live_30[t-1]>filter_live_30[t-2]:
        change_indicator[t] = -1
        idx_change_neg = t
    
    # close long
    if buy_sell_indicator_30[t]==1 and close_30[t]>filter_live_30[t] and time_30_hour[t]!=4 and time_30_hour[t]!=5:
        buy_sell_indicator_30[t] = 0
    
    # close short
    if buy_sell_indicator_30[t]==-1 and close_30[t]<filter_live_30[t] and time_30_hour[t]!=4 and time_30_hour[t]!=5:
        buy_sell_indicator_30[t] = 0
    
    # long
    if buy_sell_indicator_30[t]!=1 and close_30[t]<lower_bound_30[t] and ( filter_live_30[t]>filter_live_30[t-1] or t-idx_change_neg>block_time ) \
    and time_30_hour[t]!=4 and time_30_hour[t]!=5:
        buy_sell_indicator_30[t] = 1
    
    # short
    if buy_sell_indicator_30[t]!=-1 and close_30[t]>upper_bound_30[t] and ( filter_live_30[t]<filter_live_30[t-1] or t-idx_change_pos>block_time ) \
    and time_30_hour[t]!=4 and time_30_hour[t]!=5:
        buy_sell_indicator_30[t] = -1
    
df_buy_sell_30 = pd.DataFrame({'close':close_30,'buy_sell_indicator':buy_sell_indicator_30}, index=time_30)    
#%% stats        
bar_return_mkt = df_buy_sell_30.close/df_buy_sell_30.close.shift(1)-1
bar_return_model = bar_return_mkt * df_buy_sell_30.buy_sell_indicator.shift(1)
pnl_mkt = np.cumprod(1+bar_return_mkt) - 1
pnl_model = np.cumprod(1+bar_return_model) - 1

plt.figure()
plt.title(strategy+' - '+symbol)
plt.plot(pnl_mkt, 'k.-')
plt.plot(pnl_model, 'r.-')


df_buy_sell_model = pd.DataFrame({'close':close_30, 'buy_sell_indicator':buy_sell_indicator_30}, index=time_30)
bar_return = (df_buy_sell_model.close/df_buy_sell_model.close.shift(1)-1) * df_buy_sell_model.buy_sell_indicator.shift(1)
pnl = np.cumprod(bar_return+1)  
params = 'MINUTE_INTERVAL:{0},WIN_SIZE:{1}'.format(minute_interval, win_size)
buy_sell_model_temp = [symbol, df_buy_sell_model, pnl, params]

