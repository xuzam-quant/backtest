import numpy as np
import scipy.stats as ssta
import scipy.optimize as sopt

#%% equal weight
def func_portfolio_ew(x, cov):
    weights = np.ones(x.shape[1]) / x.shape[1]
    return weights

#%% equal volatility
def func_portfolio_ev(x, cov):
    weights = 1/np.std(x,axis=0) / np.sum(1/np.std(x,axis=0))
    return weights

#%% global mean-variance
def portfolio_ret_vol(weights, mean_returns, cov_matrix):
    ret = np.sum(mean_returns*weights)
    vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix,weights)))
    return ret, vol

def portfolio_volatility(weights, mean_returns, cov_matrix):
    return portfolio_ret_vol(weights, mean_returns, cov_matrix)[1]
            
def func_portfolio_gmv(x, cov):
    mean_returns = np.mean(x,axis=0)
    num_assets = len(mean_returns)
    args = (mean_returns, cov)
    constraints = ({'type':'eq','fun':lambda x:np.sum(x)-1})
    bound = (0, 1)
    bounds = tuple(bound for asset in range(num_assets))
    
    weights = sopt.minimize(portfolio_volatility, num_assets*[1./num_assets,], \
                            args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    return weights['x']

#%% maximum diversification
def portfolio_diversification_ratio(weights, mean_returns, std_returns, cov_matrix):
    return -np.sum(weights*std_returns) / portfolio_ret_vol(weights,mean_returns,cov_matrix)[1]

def func_portfolio_mdp(x, cov):
    mean_returns = np.mean(x,axis=0)
    std_returns = np.std(x,axis=0)
    num_assets = len(mean_returns)
    args = (mean_returns, std_returns, cov)
    constraints = ({'type':'eq','fun':lambda x:np.sum(x)-1})
    bound = (0, 1)
    bounds = tuple(bound for asset in range(num_assets))
    
    weights = sopt.minimize(portfolio_diversification_ratio, num_assets*[1./num_assets,], \
                            args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    return weights['x']

#%% risk parity
def portfolio_risk_parity_imbalance(weights, mean_returns, std_returns, cov_matrix):
    risk_budget = np.ones(len(weights)) * portfolio_ret_vol(weights,mean_returns,cov_matrix)[1] / len(weights)
    risk_contribution = weights * np.matmul(cov_matrix,weights) / risk_budget[0] / len(weights)
    risk_parity_imbalance = np.sum(np.square(risk_contribution-risk_budget))
    return risk_parity_imbalance

def func_portfolio_rp(x, cov):
    mean_returns = np.mean(x,axis=0)
    std_returns = np.std(x,axis=0)
    num_assets = len(mean_returns)
    args = (mean_returns, std_returns, cov)
    constraints = ({'type':'eq','fun':lambda x:np.sum(x)-1})
    bound = (0, 1)
    bounds = tuple(bound for asset in range(num_assets))
    ftol = portfolio_risk_parity_imbalance(np.array(num_assets*[1./num_assets,]), mean_returns, std_returns, cov) / 1e8
    options = ({'maxiter':100,'ftol':ftol})
    
    weights = sopt.minimize(portfolio_risk_parity_imbalance, num_assets*[1./num_assets,], \
                            args=args, method='SLSQP', bounds=bounds, constraints=constraints, options=options)
    return weights['x']
    
#%% pca risk parity
def portfolio_risk_parity_pca_imbalance(weights, mean_returns, std_returns, cov_matrix, pca_matrix):
    weights_pca = np.matmul(pca_matrix, weights)
    risk_budget = np.ones(len(weights_pca)) * portfolio_ret_vol(weights_pca,mean_returns,cov_matrix)[1] / len(weights_pca)
    risk_contribution = weights_pca * np.matmul(cov_matrix,weights_pca) / risk_budget[0] / len(weights_pca)
    risk_parity_imbalance = np.sum(np.square(risk_contribution-risk_budget))
    return risk_parity_imbalance

def func_portfolio_rp_pca(x, cov, pca_matrix):
    mean_returns = np.mean(x,axis=0)
    std_returns = np.std(x,axis=0)
    num_assets = len(mean_returns)
    args = (mean_returns, std_returns, cov, pca_matrix)
    constraints = ({'type':'eq','fun':lambda x:np.sum(x)-1})
    bound = (0, 1)
    bounds = tuple(bound for asset in range(num_assets))
    ftol = portfolio_risk_parity_pca_imbalance(np.array(num_assets*[1./num_assets,]), mean_returns, std_returns, cov, pca_matrix) / 1e8
    options = ({'maxiter':100,'ftol':ftol})
    
    weights = sopt.minimize(portfolio_risk_parity_pca_imbalance, num_assets*[1./num_assets,], \
                            args=args, method='SLSQP', bounds=bounds, constraints=constraints, options=options)
    return weights['x']

#%% tail risk parity
def tail_risk_measure(ret, vol, tail_type='es', percentile=0.05):
    if tail_type=='var':
        tail_risk = ret + vol * ssta.norm.ppf(percentile)
    else:
        tail_risk = -ret + vol * ssta.norm.pdf(ssta.norm.ppf(percentile)) / percentile
    return tail_risk

def tail_risk_contribution(weights, mean_returns, cov_matrix, tail_type='es', percentile=0.05):
    ret_portfolio, vol_portfolio = portfolio_ret_vol(weights, mean_returns, cov_matrix)
    vol_single = weights * np.matmul(cov_matrix, weights) / vol_portfolio
    ret_single = mean_returns
    tail_risk_single = tail_risk_measure(ret_single, vol_single, tail_type, percentile)
    tail_risk_portfolio = tail_risk_measure(ret_portfolio, vol_portfolio, tail_type, percentile)
    return tail_risk_single, tail_risk_portfolio

def portfolio_tail_risk_parity_imbalance(weights, mean_returns, std_returns, cov_matrix, tail_type='es', percentile=0.05):
    risk_contribution, risk_contribution_budget_sum = tail_risk_contribution(weights, mean_returns, cov_matrix, tail_type,percentile)
    risk_budget = np.ones(len(weights)) * risk_contribution_budget_sum / len(weights)
    risk_parity_imbalance = np.sum(np.square(risk_contribution-risk_budget))
    return risk_parity_imbalance

def func_portfolio_trp(x, cov, pca_matrix, tail_type='es', percentile=0.05):
    mean_returns = np.mean(x,axis=0)
    std_returns = np.std(x,axis=0)
    num_assets = pca_matrix.shape[1]
    args = (mean_returns, std_returns, cov, tail_type, percentile)
    constraints = ({'type':'eq','fun':lambda x:np.sum(x)-1})
    bound = (0, 1)
    bounds = tuple(bound for asset in range(num_assets))
    ftol = portfolio_tail_risk_parity_imbalance(np.array(num_assets*[1./num_assets,]),mean_returns,std_returns,cov,tail_type,percentile) / 1e8
    options = ({'maxiter':100,'ftol':ftol})
    
    weights = sopt.minimize(portfolio_tail_risk_parity_imbalance, num_assets*[1./num_assets,], \
                            args=args, method='SLSQP', bounds=bounds, constraints=constraints, options=options)
    return weights['x']
    
    
#%% tail risk parity
def tail_risk_pca_contribution(weights, mean_returns, cov_matrix, pca_matrix, tail_type='es', percentile=0.05):
    weights_pca = np.mutmul(pca_matrix, weights)
    ret_portfolio, vol_portfolio = portfolio_ret_vol(weights_pca, mean_returns, cov_matrix)
    vol_single = weights_pca * np.matmul(cov_matrix, weights_pca) / vol_portfolio
    ret_single = mean_returns
    tail_risk_single = tail_risk_measure(ret_single, vol_single, tail_type, percentile)
    tail_risk_portfolio = tail_risk_measure(ret_portfolio, vol_portfolio, tail_type, percentile)
    return tail_risk_single, tail_risk_portfolio

def portfolio_tail_risk_pca_parity_imbalance(weights, mean_returns, std_returns, cov_matrix, pca_matrix, tail_type='es', percentile=0.05):
    risk_contribution, risk_contribution_budget_sum = tail_risk_pca_contribution(weights, mean_returns, cov_matrix, pca_matrix, tail_type,percentile)
    weights_pca = np.mutmul(pca_matrix, weights)
    risk_budget = np.ones(len(weights_pca)) * risk_contribution_budget_sum / len(weights_pca)
    risk_parity_imbalance = np.sum(np.square(risk_contribution-risk_budget))
    return risk_parity_imbalance

def func_portfolio_trp_pca(x, cov, pca_matrix, tail_type='es', percentile=0.05):
    mean_returns = np.mean(x,axis=0)
    std_returns = np.std(x,axis=0)
    num_assets = pca_matrix.shape[1]
    args = (mean_returns, std_returns, cov, pca_matrix, tail_type, percentile)
    constraints = ({'type':'eq','fun':lambda x:np.sum(x)-1})
    bound = (0, 1)
    bounds = tuple(bound for asset in range(num_assets))
    ftol = portfolio_tail_risk_pca_parity_imbalance(np.array(num_assets*[1./num_assets,]),mean_returns,std_returns,cov,pca_matrix,tail_type,percentile) / 1e8
    options = ({'maxiter':100,'ftol':ftol})
    
    weights = sopt.minimize(portfolio_tail_risk_pca_parity_imbalance, num_assets*[1./num_assets,], \
                            args=args, method='SLSQP', bounds=bounds, constraints=constraints, options=options)
    return weights['x']    
    
