import numpy as np
from scipy.stats import uniform, poisson, geom, ttest_ind

lmbda = 3
q = 0.1
p1 = [0.98, 0.019, 0.001]
p2 = [0.975, 0.024, .001]
alpha = 0.01
n = 1000

def generate_counterfactuals(n, lam, q):
    final_array = np.zeros((n,2))
    final_array[:,0]=poisson.rvs(mu=lam,size=n)
    final_array[:,1]=geom.rvs(p=q,size=n)+5
    return final_array


def generate_revenues(n, lam, q, p):
    revenues = np.zeros(n)
    counterfactuals = generate_counterfactuals(n,lam,q)
    U = uniform.rvs(size = n)

    cond1 = U <= p[0]
    cond2 = U <= p[0] + p[1]

    revenues[cond1] = 0
    revenues[~cond1 & cond2] = counterfactuals[~cond1 & cond2, 0]
    revenues[~cond2] = counterfactuals[~cond2, 1]
    return revenues

def run_experiment(n, lam, q, p1, p2, alpha):
    sample_p1 = generate_revenues(n,lam,q,p1)
    sample_p2 = generate_revenues(n,lam,q,p2)
    t_stat,p_val = ttest_ind(sample_p1,sample_p2,equal_var=False,alternative='less')
    if p_val <alpha:
        return 1
    else:
        return 0

def calc_power(n, m, lam, q, p1, p2, alpha):
    rejections = 0
    for _ in range(m):
        rejections += run_experiment(n, lam, q, p1, p2, alpha)
    power = rejections/m
    return power

## output the result here
m = 1000
power = calc_power(n, m, lmbda, q, p1, p2, alpha)
print(power)
