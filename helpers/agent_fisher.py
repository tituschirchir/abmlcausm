import pandas as pd
from network.fin.bank_agent import Bank

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


def load_bs_data():
    data = pd.read_csv('data/bs_ms.csv', index_col=0)
    equities = data[data.Category == 'E']
    liabilities = data[data.Category == 'L']
    assets = data[data.Category == 'A']
    _inter_bank_liabilities = liabilities.loc[inter_bank_liabilities]
    _customer_deposits = liabilities.drop(inter_bank_liabilities)
    _inter_bank_assets = assets.loc[inter_bank_assets]
    _external_assets = assets.drop(inter_bank_assets)
    return data, equities, _inter_bank_liabilities, _customer_deposits, _inter_bank_assets, _external_assets


def get_agents(n):
    data, equities, _inter_bank_liabilities, _customer_deposits, _inter_bank_assets, _external_assets = load_bs_data()
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
