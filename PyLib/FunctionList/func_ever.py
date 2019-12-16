import numpy as np
import pandas as pd
    
#%% ever
def func_ever(t, o, h, l ,c, v, bspcut=[0.05, 0.5, 0.95], bspmethod='mean', lookback=12000):
    t2 = pd.to_datetime(t)
    ev = np.zeros(len(c)) * np.nan
    for i in range(1,len(c)):
        r = max(h[i],c[i-1]) - min(l[i],c[i-1])
        if r==0:
            ev[i] = 0
        else:
            ev[i] = (c[i]-c[i-1])/r * v[i]
    
    bpev = np.zeros(len(c)) * np.nan    
    spev = np.zeros(len(c)) * np.nan
    for i in range(lookback-1,len(c)):
        if t2[i].date()!=t2[i-1].date():
            bpev[i] = np.percentile(np.abs(ev[i-lookback+1:i+1]), bspcut[2]*100, interpolation='nearest')
            spev[i] = np.percentile(np.abs(ev[i-lookback+1:i+1]), bspcut[0]*100, interpolation='nearest')
        else:
            bpev[i] = bpev[i-1]
            spev[i] = spev[i-1]
            
    mpev = np.zeros(len(c)) * np.nan
    if bspmethod=='median':
        for i in range(lookback-1,len(c)):
            if t2[i].date()!=t2[i-1].date():
                mpev[i] = np.percentile(np.abs(ev[i-lookback+1:i+1]), bspcut[1]*100, interpolation='nearest')
            else:
                mpev[i] = mpev[i-1]
    else:
        for i in range(lookback-1,len(c)):
            if t2[i].date()!=t2[i-1].date():
                mpev[i] = np.mean(np.abs(ev[i-lookback+1:i+1]))
            else:
                mpev[i] = mpev[i-1]
    
    evb = np.zeros(len(c))
    evs = np.zeros(len(c))
    evbl = np.zeros(len(c)) * np.nan
    evsl = np.zeros(len(c)) * np.nan
    vl   = np.zeros(len(c)) * np.nan
    for i in range(lookback-1,len(c)):
        if np.abs(ev[i])>spev[i] and np.abs(ev[i])<=mpev[i]:
            evs[i] = ev[i]
        elif np.abs(ev[i])>mpev[i] and np.abs(ev[i])<=bpev[i]:
            evb[i] = ev[i]
        if i==lookback-1:
            evbl[i] = evb[i]
            evsl[i] = evs[i]
            vl[i] = v[i]
        else:
            evbl[i] = evbl[i-1] + evb[i]
            evsl[i] = evsl[i-1] + evs[i]
            vl[i] = vl[i-1] + v[i]        
    return evbl, evsl, vl


def func_ever_bs(t, o, h, l ,c, v, bspcut=[0.05, 0.5, 0.95], bspmethod='mean', lookback=12000):
    t2 = pd.to_datetime(t)
    ev = np.zeros(len(c)) * np.nan
    for i in range(1,len(c)):
        r = max(h[i],c[i-1]) - min(l[i],c[i-1])
        if r==0:
            ev[i] = 0
        else:
            ev[i] = (c[i]-c[i-1])/r * v[i]
    
    bpev_b = np.zeros(len(c)) * np.nan    
    bpev_s = np.zeros(len(c)) * np.nan    
    spev_b = np.zeros(len(c)) * np.nan
    spev_s = np.zeros(len(c)) * np.nan
    for i in range(lookback-1,len(c)):
        if t2[i].date()!=t2[i-1].date():
            data = ev[i-lookback+1:i+1].copy()
            bpev_b[i] = np.percentile(data[data>0], bspcut[2]*100, interpolation='nearest')
            spev_b[i] = np.percentile(data[data>0], bspcut[0]*100, interpolation='nearest')
            bpev_s[i] = np.percentile(np.abs(data[data<0]), bspcut[2]*100, interpolation='nearest')
            spev_s[i] = np.percentile(np.abs(data[data<0]), bspcut[0]*100, interpolation='nearest')
        else:
            bpev_b[i] = bpev_b[i-1]
            spev_b[i] = spev_b[i-1]
            bpev_s[i] = bpev_s[i-1]
            spev_s[i] = spev_s[i-1]
            
    mpev_b = np.zeros(len(c)) * np.nan
    mpev_s = np.zeros(len(c)) * np.nan
    if bspmethod=='median':
        for i in range(lookback-1,len(c)):
            if t2[i].date()!=t2[i-1].date():
                data = ev[i-lookback+1:i+1].copy()
                mpev_b[i] = np.percentile(data[data>0], bspcut[1]*100, interpolation='nearest')
                mpev_s[i] = np.percentile(np.abs(data[data<0]), bspcut[1]*100, interpolation='nearest')
            else:
                mpev_b[i] = mpev_b[i-1]
                mpev_s[i] = mpev_s[i-1]
    else:
        for i in range(lookback-1,len(c)):
            if t2[i].date()!=t2[i-1].date():
                data = ev[i-lookback+1:i+1].copy()
                mpev_b[i] = np.mean(data[data>0])
                mpev_s[i] = np.mean(np.abs(data[data<0]))
            else:
                mpev_b[i] = mpev_b[i-1]
                mpev_s[i] = mpev_s[i-1]
    
    evb = np.zeros(len(c))
    evs = np.zeros(len(c))
    evbl = np.zeros(len(c)) * np.nan
    evsl = np.zeros(len(c)) * np.nan
    vl   = np.zeros(len(c)) * np.nan
    for i in range(lookback-1,len(c)):
        if ev[i]>0:            
            if np.abs(ev[i])>spev_b[i] and np.abs(ev[i])<=mpev_b[i]:
                evs[i] = ev[i]
            elif np.abs(ev[i])>mpev_b[i] and np.abs(ev[i])<=bpev_b[i]:
                evb[i] = ev[i]
        else:
            if np.abs(ev[i])>spev_s[i] and np.abs(ev[i])<=mpev_s[i]:
                evs[i] = ev[i]
            elif np.abs(ev[i])>mpev_s[i] and np.abs(ev[i])<=bpev_s[i]:
                evb[i] = ev[i]
        if i==lookback-1:
            evbl[i] = evb[i]
            evsl[i] = evs[i]
            vl[i] = v[i]
        else:
            evbl[i] = evbl[i-1] + evb[i]
            evsl[i] = evsl[i-1] + evs[i]
            vl[i] = vl[i-1] + v[i]        
    return evbl, evsl, vl

#%% smooth value
def func_ever_ma(evbl, evsl, vl, win_size):    
    erbl = np.zeros(len(vl)) * np.nan
    ersl = np.zeros(len(vl)) * np.nan
    for i in range(win_size-1,len(vl)):
        erbl[i] = (evbl[i]-evbl[i-win_size+1])/(vl[i]-vl[i-win_size+1]) * 100
        ersl[i] = (evsl[i]-evsl[i-win_size+1])/(vl[i]-vl[i-win_size+1]) * 100    
    return erbl, ersl
    
#    
#def func_epv_filter():
#    
##%% pivot, highlow, bounce
#def func_epv_direction():
#    
#def func_epv_pivot():
#    
#def func_epv_bounce():
#    
#def func_epv_delta():
#    
#def func_epv_highlow_band():
#    
#def func_epv_highlow_compare():
#    
    