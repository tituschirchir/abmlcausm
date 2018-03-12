import urllib as u

import pandas as pd
from bs4 import BeautifulSoup as bs

from network.fin.bank_agent import Bank


def get_rows(df, bst_terms):
    return df.loc[bst_terms].dropna(axis=0, how='all')


def get_agents(n):
    funda = pd.read_csv('data/fundamendals.csv', index_col=0)
    agents = []
    df = pd.read_csv('data/bs_ms.csv', index_col=0)
    df = df.drop('Category', axis=1)
    for i, tkr in enumerate(df.columns):
        mu, std = funda.loc['Perf Year', tkr], funda.loc['Volatility', tkr]
        agents.append(Bank(tkr, i, None, df[tkr], mu, std))
    return agents[0:n] if n < df.shape[1] else agents


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
