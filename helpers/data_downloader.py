import math
import os

import pandas as pd
import pandas_datareader as web

import data.meta_data as md


def download_data(start, end, stocks_list, lag=1):
    # We will look at stock prices over the past year, starting at January 1, 2016
    xf = "data/stocks.csv"
    if os.path.isfile(xf):
        stocks = pd.read_csv(xf, index_col=0)
        stats = pd.read_csv("data/stats.csv", index_col=0)
    else:
        all_stocks = [v for k, v in md.tickers.items()]
        apple = web.DataReader(all_stocks, "google", start, end)
        stocks = apple["Close", :, :]
        stock_return = stocks.apply(lambda x: (x - x.shift(lag)) / x)
        stock_return = stock_return.dropna(axis=0, how='any')
        stats = stock_return.describe().T
        stats['annual_ret'] = stats['mean'] * 252 / lag
        stats['annual_std'] = stats['std'] * math.sqrt(252 / lag)
        stats['current_price'] = stocks[-1:].T.values
        stats.to_csv("data/stats.csv")
        stocks.to_csv(xf)
    return stats.ix[stocks_list], stocks[stocks_list]
