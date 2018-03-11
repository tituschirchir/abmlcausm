import urllib as u
from math import sqrt

import pandas as pd
from bs4 import BeautifulSoup as bs

from helpers.bs_tree import get_balance_sheet_tree, flatten
from network.fin.bank_agent import Bank
from products.equities import Stock


def load_bs_data():
    bst = get_balance_sheet_tree()
    df = pd.read_csv('data/bs_ms.csv', index_col=0)
    df = df.drop('Category', axis=1)
    equities = get_rows(df, flatten(bst["Equities"]))
    _inter_bank_assets = get_rows(df, flatten(bst["Assets"]["Interbank"]))
    _external_assets = get_rows(df, flatten(bst["Assets"]["External"]))
    _inter_bank_liabilities = df.loc[flatten(bst["Liabilities"]["Interbank"])]
    _customer_deposits = get_rows(df, flatten(bst["Liabilities"]["Deposits and Others"]))
    _stock_ = equities
    return equities, _inter_bank_liabilities, _customer_deposits, _inter_bank_assets, _external_assets, _stock_


def get_rows(df, bst_terms):
    return df.loc[bst_terms].dropna(axis=0, how='all')


def get_agents(n):
    equities, _inter_bank_liabilities, _customer_deposits, _inter_bank_assets, _external_assets, _stock_ = load_bs_data()
    funda = pd.read_csv('data/fundamendals.csv', index_col=0)
    i = 0
    agents = []
    if n > equities.shape[1] - 1 or n < 1:
        n = equities.shape[1] - 1
    share_price = 1.00
    for tkr in equities.columns[0:n]:
        if tkr != 'Category':
            bnk = Bank(tkr, i, None)
            bnk.externalAssets = sum(_external_assets[tkr])
            bnk.interbankAssets = sum(_inter_bank_assets[tkr])
            bnk.interbank_borrowing = sum(_inter_bank_liabilities[tkr])
            bnk.customer_deposits = sum(_customer_deposits[tkr])
            bnk.capital = sum(equities[tkr])
            S, mu, std = funda.loc['Price', tkr], funda.loc['Perf Year', tkr], funda.loc['Volatility', tkr]
            bnk.issued_shares = sum(equities[tkr]) / S
            bnk.issued_shares = bnk.issued_shares / share_price * S
            bnk.stock = Stock(S=share_price, mu=mu / 100, std=std / 100 * sqrt(52), dt=1 / 252.0)
            i += 1
            agents.append(bnk)

    return agents


def get_stats(symbol, fields):
    try:
        print(symbol)
        url = r'http://finviz.com/quote.ashx?t={}'.format(symbol.lower())
        html = u.request.urlopen(url).read()
        soup = bs(html, 'lxml')
        # Change the text below to get a diff metric
        answers = []
        for fld in fields:
            pb = soup.find(text=r'{}'.format(fld))
            pb_ = float(pb.find_next(class_='snapshot-td2').text.replace('%', '').split()[0])
            answers.append(pb_)
        return answers

    except Exception as e:
        print(e)


def download_data():
    default_tick = 'JPM,BRK.b,BAC,WFC,C,GS,USB,MS,PNC,AXP,BLK,CB,SCHW,BK,CME,AIG,MET,SPGI,COF,PRU,BBT,ICE,MMC,STT,TRV,AON,' \
                   'AFL,PGR,STI,ALL,MTB,DFS,MCO,TROW,SYF,FITB,KEY,AMP,NTRS,RF,CFG,WLTW,HIG,CMA,HBAN,LNC,PFG,ETFC,XL,L,IVZ,' \
                   'CBOE,BEN,AJG,RJF,CINF,UNM,ZION,AMG,RE,NDAQ,TMK,LUK,PBCT,BHF,AIZ,NAVI'
    def_tick = default_tick.split(',')
    df = pd.DataFrame(columns=def_tick, index=['Price', 'Perf Year', 'Volatility'])
    for tkr in def_tick:
        df[tkr] = get_stats(tkr.replace('.', '-'), ['Price', 'Perf Year', 'Volatility'])
    df.to_csv('data/fundamendals.csv')
