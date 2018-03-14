import pandas as pd

from network.fin.bank_agent import Bank
from structures.bank_structures import TimeSeries


def get_rows(df, bst_terms):
    return df.loc[bst_terms].dropna(axis=0, how='all')


def get_agents(n):
    ts = pd.read_csv('data/t_series.csv', index_col=0)
    df = pd.read_csv('data/bs_ms.csv', index_col=0)
    df = df.drop('Category', axis=1)
    i = 0
    agents = []
    for tkr, ser in df.iteritems():
        agents.append(Bank(tkr, i, None, ser, TimeSeries(ts[tkr])))
        i += 1
    return agents[0:n] if n < df.shape[1] else agents


def download_data():
    import quandl
    quandl.ApiConfig.api_key = 'iyeLXysv9-BtunNLWLGH'
    def_tick = 'JPM,BRK.b,BAC,WFC,C,GS,USB,MS,PNC,AXP,BLK,CB,SCHW,BK,CME,AIG,MET,SPGI,COF,PRU,BBT,ICE,MMC,STT,TRV,AON,' \
               'AFL,PGR,STI,ALL,MTB,DFS,MCO,TROW,SYF,FITB,KEY,AMP,NTRS,RF,CFG,WLTW,HIG,CMA,HBAN,LNC,PFG,ETFC,XL,L,IVZ,' \
               'CBOE,BEN,AJG,RJF,CINF,UNM,ZION,AMG,RE,NDAQ,TMK,LUK,PBCT,BHF,AIZ,NAVI'.split(',')
    t_series = pd.DataFrame()
    t_2 = quandl.get(['WIKI/{}'.format(tkr.replace('.', '_')) for tkr in def_tick])
    for tkr in def_tick:
        t_series[tkr] = t_2['WIKI/{} - Adj. Close'.format(tkr.replace('.', '_'))]

    t_series = t_series.dropna(axis=0, how='any')
    t_series.to_csv('data/t_series.csv')
