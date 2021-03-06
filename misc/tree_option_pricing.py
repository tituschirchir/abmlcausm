from math import sqrt, exp

import pandas as panda

from misc import options_util
from misc.options_util import OptionTypes


def trinomial_tree_generic(flavor, is_call, is_american, K, Tm, S, r, sig, N, div, H):
    dx = sig * sqrt(3 * Tm / N)
    dt = Tm / N
    nu = r - div - 0.5 * sig ** 2
    pu = 0.5 * dt / dx * ((sig ** 2 + nu ** 2 * dt + nu * dx) / dx)
    pm = 1.0 - (sig ** 2 * dt + nu ** 2 * dt ** 2) / dx ** 2
    pd = pu - nu * dt / dx
    rows = 2 * N + 1
    cols = N + 1
    disc = exp(-r * dt)
    c_names = [str(x) for x in range(0, cols)]
    stocks = [S * exp((N - x) * dx) for x in range(0, rows)]
    stock = panda.DataFrame(data=0.0, columns=c_names, index=range(0, rows))
    opt_val = panda.DataFrame(data=0.0, columns=c_names, index=range(0, rows))

    for i in range(N, -1, -1):
        stock[str(i)] = [0.0] * (N - i) + stocks[N - i:N + i + 1] + [0.0] * (N - i)
    opt_val[str(N)] = [options_util.payoff(v, K, flavor, H) for v in stock[str(N)]]
    for j in range(cols - 2, -1, -1):
        for i in range((cols - j - 1), (cols + j - 1 + 1)):
            st_val = stock.loc[i][str(j)]
            opt_val.loc[i][str(j)] = disc * options_util.replication(st_val, H,
                                                                     pu, opt_val.loc[i - 1][str(j + 1)],
                                                                     pm, opt_val.loc[i][str(j + 1)],
                                                                     pd, opt_val.loc[i + 1][str(j + 1)], flavor=flavor)
            if is_american:
                opt_val.loc[i][str(j)] = max(opt_val.loc[i][str(j)], options_util.mult(is_call) * (st_val - K))
    return opt_val.loc[N]["0"]


def binomial_tree_generic(flavor, is_call=True, is_american=False, K=20, Tt=1.0, S0=20, r=0.06, N=3, sigma=0.2, H=0):
    dt = Tt / N
    nu = r - 0.5 * sigma ** 2
    dxu = sqrt(sigma ** 2 * dt + (nu * dt) ** 2)
    pu = 0.5 + 0.5 * nu * dt / dxu
    pd = 1 - pu
    disc = exp(-r * dt)
    cols, mid = N + 1, N + 1
    rows = N + 1
    c_names = [str(x) for x in range(0, cols)]
    opt_val = panda.DataFrame(data=0.0, columns=c_names, index=range(0, rows))
    stock = panda.DataFrame(data=0.0, columns=c_names, index=range(0, rows))
    stocks = [S0 * exp((N - x) * dxu) for x in range(0, 2 * N + 1)]
    start = 0
    for i in range(0, N + 1):
        stk = (stocks[start:N + 1 + i] + [0] * int(start / 2))
        stk.reverse()
        stock.loc[i] = stk
        start += 2

    opt_val[str(N)] = [options_util.payoff(v, K, is_call, flavor, H) for v in stock[str(N)]]

    for i in range(N - 1, -1, -1):
        for j in range(0, i + 1):
            stock_val = stock.loc[j][str(i)]
            opt_val.loc[j][str(i)] = disc * options_util.replication(stock_val, H,
                                                                     pu, opt_val.loc[j][str(i + 1)],
                                                                     0.0, 0.0,
                                                                     pd, opt_val.loc[j + 1][str(i + 1)],
                                                                     flavor=flavor)
            if is_american:
                opt_val.loc[j][str(i)] = max(opt_val.loc[j][str(i)], options_util.mult(is_call) * (stock_val - K))

    return opt_val.loc[0]["0"]


def euro_amer_binomial_tree(is_call=True, is_american=False, K=20, Tt=1, S0=20, r=0.06, N=3, sigma=0.2):
    return binomial_tree_generic(OptionTypes.VANILLA, is_call, is_american, K, Tt, S0, r, N, sigma)


def euro_amer_trinomial_tree(is_call=True, is_american=False, K=100, Tm=1, S=100, r=0.06, sig=0.2, N=3, div=0.03):
    return trinomial_tree_generic(OptionTypes.VANILLA, is_call, is_american, K, Tm, S, r, sig, N, div, 0)


def up_and_out_binomial(is_call=True, is_american=False, K=10, Tt=0.3, S0=10, sigma=0.2, r=0.01, H=11, N=100):
    return binomial_tree_generic(OptionTypes.UP_AND_OUT, is_call, is_american, K, Tt, S0, r, N, sigma, H)


def up_and_out_trinomial(is_call=True, is_american=False, K=10, Tm=0.3, S=10, r=0.01, sig=0.2, N=100, div=0.00, H=11):
    return trinomial_tree_generic(OptionTypes.UP_AND_OUT, is_call, is_american, K, Tm, S, r, sig, N, div, H)
