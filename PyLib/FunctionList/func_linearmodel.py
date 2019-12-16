import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm

#%% linear regression coefficient
def func_linearmodel_coefficient(y, x):
    beta  = np.sum( (x-np.mean(x)) * (y-np.mean(y)) ) / np.sum( (x-np.mean(x))*(x-np.mean(x)) )
    alpha = np.mean(y) - np.mean(x) * beta
    return alpha, beta
    

#%% feature selection
def func_linearmodel_featureselection(y, x, num_feature=2):
#    # 1. variance-based selection
#    percent_concentration_max = 0.8
#    x_uniform = (x - np.min(x,axis=0)) / (np.max(x,axis=0)-np.min(x,axis=0))
#    sel = VarianceThreshold(threshold=percent_concentration_max*(1-percent_concentration_max))
#    x_uniform_sel = sel.fit_transform(x_uniform)
    
#    # 2. fisher score-based selection
#    
#    # 3. recussive k best linear
#    model = LinearRegression()
#    rfe = RFE(model, num_feature)
#    fit = rfe.fit(x, y)

    # 4. select k-best - regression
    test = SelectKBest(score_func=mutual_info_regression, k=num_feature)
    fit = test.fit(x, y)
    feature_select = fit.get_support()    
    return feature_select

#%% linearregression
def func_linearmodel_linearregression(y, x, feature_select):
    x_select = x[:, feature_select]
    feature_coef = np.zeros(x.shape[1]+1)
    
    #statsmodels
    x_select = sm.add_constant(x_select)
    est_fit = sm.OLS(y, x_select).fit()
    feature_coef[np.where(feature_select!=0)[0]] = est_fit.params[1:]
    feature_coef[-1] = est_fit.params[0]
    return feature_coef
    
