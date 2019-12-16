import numpy as np
import statsmodels.api as sm
from PyEMD import EMD
from pywt import wavedec, threshold, waverec

#%% HP filter
def func_filter_hp(x, win_size, filter_lambda):
    y = x.copy()
    for i in range(win_size-1,len(x)):
        cycle, trend = sm.tsa.filters.hpfilter(x[i-win_size+1:i+1], filter_lambda)
        y[i] = trend[-1]
    return y

#%% EMD filter
def wavelet(imf):
    N = len(imf)
    n = int(np.ceil(N/2))
    thr = 0.4
    new_imf = []
    for i in range(N):
        imf_temp = imf[i]
        if i<n:
            coeffs = wavedec(imf_temp,'db1',level=3)
            a3, d3, d2, d1 = coeffs
            ytsoftd1 = threshold(d1,thr,'soft')
            ytsoftd2 = threshold(d2,thr,'soft')
            ytsoftd3 = threshold(d3,thr,'soft')
            coeffs_new = [a3, ytsoftd3, ytsoftd2, ytsoftd1]
            imf_temp_new = waverec(coeffs_new,'db1')
        else:
            imf_temp_new = imf_temp
        new_imf.append(imf_temp_new)    
    y = new_imf[0].copy()
    for i in range(1,len(new_imf)):
        y = y + new_imf[i]
    return y

def func_filter_emd(x, win_size):
    y = x.copy()    
    emd_pyemd = EMD()
    for i in range(win_size-1,len(x)):
        imf = emd_pyemd(x[i-win_size+1:i+1])
        wave = wavelet(imf)
        y[i] = wave[-1]
    return y

    

