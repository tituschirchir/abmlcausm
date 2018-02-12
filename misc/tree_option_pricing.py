from math import sqrt, exp
import pandas as panda


def binomial_tree_generic(payoff, replication, is_call=True, is_american=False, K=20, Tt=1.0, S0=20, r=0.06, N=3,
                          sigma=0.2):
    dt = Tt / N
    nu = r - 0.5 * sigma ** 2
    dxu = sqrt(sigma ** 2 * dt + (nu * dt) ** 2)
    pu = 0.5 + 0.5 * nu * dt / dxu
    pd = 1 - pu
    disc = exp(-r * dt)
    cols, mid = N + 1, N + 1
    rows = N + 1
    p_mult = 1 if is_call else -1

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

    opt_val[str(N)] = [payoff(v) for v in stock[str(N)]]

    for i in range(N - 1, -1, -1):
        for j in range(0, i + 1):
            stock_val = stock.loc[j][str(i)]
            opt_val.loc[j][str(i)] = disc * replication(stock_val, pu, opt_val.loc[j][str(i + 1)], pd,
                                                        opt_val.loc[j + 1][str(i + 1)])
            if is_american:
                opt_val.loc[j][str(i)] = max(opt_val.loc[j][str(i)], p_mult * (stock_val - K))

    return opt_val.loc[0]["0"]


def euro_amer_binomial_tree(is_call=True, is_american=False, K=20, Tt=1, S0=20, r=0.06, N=3, sigma=0.2):
    def payoff(s):
        return max(0, (1 if is_call else -1) * (s - K))

    def replication(s, pu, vu, pd, vd):
        return pu * vu + pd * vd

    return binomial_tree_generic(payoff, replication, is_call, is_american, K, Tt, S0, r, N, sigma)


def up_and_out_binomial(is_call=True, is_american=False, K=10, Tt=0.3, S0=10, sigma=0.2, r=0.01, H=11, N=3):
    def payoff(s):
        return 0 if s > H else max(0, (1 if is_call else -1) * (s - K))

    def replication(s, pu, cu, pd, cd):
        return 0 if s > H else (pu * cu + pd * cd)

    return binomial_tree_generic(payoff, replication, is_call, is_american, K, Tt, S0, r, N, sigma)
