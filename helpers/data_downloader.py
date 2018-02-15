import csv
import math
import os

import pandas as pd
import pandas_datareader as web
import requests

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


def download_balancesheet(tickers):
    assets, liab, equities = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    for tkr in tickers:
        assets2, liab2, equities2 = pd.DataFrame(columns=[tkr]), pd.DataFrame(columns=[tkr]), pd.DataFrame(
            columns=[tkr])
        download = requests.get(
            'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={}&reportType=bs&period=12&dataType=A&order=asc&columnYear=5&number=3'.format(
                tkr))
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)[2:]
        is_reached = True
        arr_v = []
        for i in range(0, len(my_list)):
            val = my_list[i]
            if val[0] == "Assets":
                arr_v.append(i + 1)
            elif val[0] == "Liabilities":
                arr_v.append(i + 1)
            elif val[0] == "Stockholders' equity":
                arr_v.append(i + 1)
        i = 0
        for row in my_list:
            if len(row) == 1 and is_reached:
                is_reached = False
            elif len(row) > 1 and "Total" not in row[0]:
                value = 0.0 if row[-1] == '' else float(row[-1])
                if i < arr_v[1]:
                    assets2.loc[row[0]] = [value]
                elif i >= arr_v[2]:
                    equities2.loc[row[0]] = [value]
                else:
                    liab2.loc[row[0]] = [value]
                is_reached = True
            i += 1
        equities = equities.join(equities2, how='outer')
        liab = liab.join(liab2, how='outer')
        assets = assets.join(assets2, how='outer')

    assets['Category'] = ["A"] * assets.shape[0]
    liab['Category'] = ["L"] * liab.shape[0]
    equities['Category'] = ["E"] * equities.shape[0]
    assets = assets.fillna(0.0)
    liab = liab.fillna(0.0)
    equities = equities.fillna(0.0)
    bs = pd.concat([assets, liab, equities])
    bs = bs.drop(['Net loans'])

    return bs
