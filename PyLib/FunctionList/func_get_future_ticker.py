def func_get_future_ticker(date_beg, date_end, contract_interval, contract_keyword, contract_asset='Index'):
    import numpy as np
    contract_month = np.array(['F','G','H','J','K','M','N','Q','U','V','X','Z'])
    future_ticker_list = np.array([])
    date_roll = np.arange(date_end, date_beg, -1, dtype='datetime64[M]')
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
            future_ticker_list=np.append(future_ticker_list, ticker_temp)
    
    return future_ticker_list            