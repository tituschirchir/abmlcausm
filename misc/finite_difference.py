from math import exp

import pandas as panda

from misc import options_util


def explicit_finite_difference(is_call, is_american, flavor, K, Tm, S, r, sig, N, div, dx):
    dt = Tm / N
    nu = r - div - 0.5 * sig ** 2
    pu = 0.5 * dt * ((sig / dx) ** 2 + nu / dx)
    pm = 1.0 - dt * (sig / dx) ** 2 - r * dt
    pd = 0.5 * dt * ((sig / dx) ** 2 - nu / dx)
    rows = 2 * N + 1
    cols = N + 1
    c_names = [str(x) for x in range(0, cols)]
    stock = panda.DataFrame(data=0.0, columns=c_names, index=range(0, rows))
    stock.loc[N][str(0)] = S
    stocks = [S * exp((N - x) * dx) for x in range(0, 2 * N + 1)]
    for i in range(N, -1, -1):
        stock[str(i)] = [0.0] * (N - i) + stocks[N - i:N + i + 1] + [0.0] * (N - i)

    opt_val = panda.DataFrame(data=0.0, columns=c_names, index=range(0, rows))
    opt_val[str(N)] = [options_util.payoff(v, K, is_call, flavor=flavor) for v in stock[str(N)]]
    for i in range(N - 1, -1, -1):
        for j in range(1, 2 * N):
            opt_val.loc[j][str(i)] = pu * opt_val.loc[j - 1][str(i + 1)] + \
                                     pm * opt_val.loc[j][str(i + 1)] + \
                                     pd * opt_val.loc[j + 1][str(i + 1)]
        stock_term = (stock.loc[0][str(N)] - stock.loc[1][str(N)]) if is_call else (
                stock.loc[rows - 2][str(N)] - stock.loc[rows - 1][str(N)])
        opt_val.loc[rows - 1][str(i)] = opt_val.loc[rows - 2][str(i)] + (0 if is_call else stock_term)
        opt_val.loc[0][str(i)] = opt_val.loc[0 + 1][str(i)] + (stock_term if is_call else 0)

        if is_american:
            opt_val[str(i)] = [max(opt_val.loc[k][str(i)], options_util.mult(is_call) * (stock.loc[k][str(i)] - K)) \
                               for k in range(0, rows)]

    return opt_val
