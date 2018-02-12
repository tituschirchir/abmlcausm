from scipy.stats import norm
from math import sqrt, exp, log

from misc.black_scholes import BSMerton

# Value of option using explicit functions defined by Niklas Waterman ----
from misc.tree_option_pricing import euro_amer_binomial_tree, up_and_out_binomial


def explicit_up_and_out_niklas(S=9, K=10, tau=0.3, r=0.01, vol=0.2, H=11, div=0):
    def cbs(x, y):
        return BSMerton(Type=1, S=x, K=y, T=tau, r=r, sigma=vol, q=0).premium()

    nu = r - div - vol ** 2 / 2

    def dbs(x, y):
        return (log(x / y) + nu * tau) / (vol * sqrt(tau))

    mult = (H - K) * exp(-r * tau)
    part_1 = mult * norm.cdf(dbs(S, H))
    part_2 = mult * norm.cdf(dbs(H, S))
    part_3 = cbs(H ** 2 / S, K) - cbs(H ** 2 / S, H) - part_2
    return cbs(S, K) - cbs(S, H) - part_1 - (H / S) ** (2 * nu / vol ** 2) * part_3


# Up-and-In European call option using explicit method described by Niklas Waterman ----
def explicit_up_and_in_niklas(S=10, K=10, tau=0.3, r=0.01, vol=0.2, H=11, div=0):
    nu = r - div - vol ** 2 / 2

    def cbs(x, y, cp):
        return BSMerton(Type=cp, S=x, K=y, T=tau, r=r, sigma=vol, q=0).premium()

    def dbs(x, y):
        return (log(x / y) + nu * tau) / (vol * sqrt(tau))

    mult = (H - K) * exp(-r * tau)
    part_1 = (cbs(H ** 2 / S, K, -1) - cbs(H ** 2 / S, H, -1) + mult * norm.cdf(-dbs(H, S)))
    return (H / S) ** (2 * nu / vol ** 2) * part_1 + cbs(S, H, 1) + mult * norm.cdf(dbs(S, H))


# In and Out Euro call using the In-Out parity ----
def up_and_in_using_in_out_parity(S=10, K=10, tau=0.3, r=0.01, vol=0.2, H=11, div=0):
    bs_merton = BSMerton(Type=1, S=S, K=K, T=tau, r=r, sigma=vol, q=div).premium()
    niklas = explicit_up_and_out_niklas(S=S, K=K, tau=tau, r=r, vol=vol, H=H, div=div)
    return bs_merton - niklas


# Value of Up and In American option as outlined by MIN DAI and YUE KUEN KWOK
def explicit_up_and_in_american_put_option(S=10, K=10, tau=0.3, r=0.01, vol=0.2, H=11, div=0, N=100):
    def vanilla_euro_put(S0, Tt, X):
        return BSMerton(-1, S=S0, K=X, T=Tt, r=r, sigma=vol, q=0).premium()

    def vanilla_american_put(S0, Tt, X):
        return euro_amer_binomial_tree(is_call=False, is_american=True, K=X, Tt=Tt, S0=S0, r=r, N=N, sigma=vol)

    up_out = up_and_out_binomial(is_call=False, is_american=False, K=K, Tt=tau, S0=S, sigma=vol, r=r, H=H, N=N)

    def up_and_in_eu_put(S0, Tt):
        return vanilla_euro_put(S0, Tt, K) - up_out

    return (S / H) ** (1 - 2 * (r - div) / vol ** 2) * (
    vanilla_american_put(H ** 2 / S, tau, K) - vanilla_euro_put(H ** 2 / S, tau, K)) + up_and_in_eu_put(S, tau)
