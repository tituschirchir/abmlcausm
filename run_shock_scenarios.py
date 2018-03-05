import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import network.core.skeleton as ns
from network.fin.struct import Bank, FinNetwork

inter_bank_assets = ['Cash and due from banks',
                     'Debt securities',
                     'Deposits with banks',
                     'Derivative assets',
                     'Equity securities',
                     'Federal funds sold',
                     'Fixed maturity securities',
                     'Investments',
                     'Loans',
                     'Loans, total',
                     'Receivables',
                     'Securities and investments',
                     'Short-term investments',
                     'Trading assets',
                     'Trading securities']
inter_bank_liabilities = ['Derivative liabilities',
                          'Federal funds purchased',
                          'Long-term debt',
                          'Minority Interest',
                          'Payables',
                          'Payables and accrued expenses',
                          'Short-term borrowing',
                          'Short-term debt',
                          'Trading liabilities',
                          'Unearned premiums']
data = pd.read_csv('data/bs_ms.csv', index_col=0)
equities = data[data.Category == 'E']
liabilities = data[data.Category == 'L']
assets = data[data.Category == 'A']
_inter_bank_liabilities = liabilities.loc[inter_bank_liabilities]
_customer_deposits = liabilities.drop(inter_bank_liabilities)
_inter_bank_assets = assets.loc[inter_bank_assets]
_external_assets = assets.drop(inter_bank_assets)


def get_agents(n):
    i = 0
    agents = []
    for tkr in data.columns[0:n]:
        if tkr != 'Category':
            bnk = Bank(tkr, i, None)
            bnk.externalAssets = sum(_external_assets[tkr])
            bnk.interbankAssets = sum(_inter_bank_assets[tkr])
            bnk.interbank_borrowing = sum(_inter_bank_liabilities[tkr])
            bnk.customer_deposits = sum(_customer_deposits[tkr])
            bnk.capital = sum(equities[tkr])
            i += 1
            agents.append(bnk)

    return agents


def per_bank(count, pos, n, p=.0):
    networks = [FinNetwork("Net {}".format(y), get_agents(n), net_type=ns.power_law_graph, p=p) for y in range(count)]
    deads = []
    for net in networks:
        net.apply_shock(pos)
        for i in range(10):
            net.step()
        deads.append(sum([1 for x in net.schedule.agents if x.defaults]))
    return sum(deads) / count


def per_probability(count, pos, n, p):
    networks = [FinNetwork("Net {}".format(y), get_agents(n), net_type=ns.power_law_graph, p=p) for y in range(count)]
    deads = []
    for net in networks:
        net.apply_shock(pos)
        for i in range(10):
            net.step()
        deads.append(sum([1 for x in net.schedule.agents if x.defaults]))
    return sum(deads) / count


# killed = [per_bank(10, x, n=29) for x in range(29)]
for i in range(29):
    killed = [per_probability(10, i, n=29, p=x) for x in np.arange(0.0, 1.0, 0.05)]
    plt.plot(np.arange(0.0, 1.0, 0.05), killed)
plt.show()
