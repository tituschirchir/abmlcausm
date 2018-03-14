import csv
import os

import pandas as pd
import requests

import data.meta_data as md


def download_balance_sheet(tickers, f_loc='data/bs_ms.csv', prev_quarter=3, save=True):
    i_loc = -prev_quarter
    assets, liab, equities = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    for tkr in tickers:
        assets2, liab2, equities2 = pd.DataFrame(columns=[tkr]), pd.DataFrame(columns=[tkr]), pd.DataFrame(
            columns=[tkr])
        download = requests.get(md.morning_star.format(tkr))
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)[2:]
        is_reached = True
        arr_v = []
        for j in range(0, len(my_list)):
            val = my_list[j]
            if val[0] == "Assets":
                arr_v.append(j + 1)
            elif val[0] == "Liabilities":
                arr_v.append(j + 1)
            elif val[0] == "Stockholders' equity":
                arr_v.append(j + 1)
        i = 0
        for row in my_list:
            if len(row) == 1 and is_reached:
                is_reached = False
            elif len(row) > 1 and "Total" not in row[0] and row[i_loc] != '':
                value = float(row[i_loc])
                if i < arr_v[1]:
                    value += assets2.loc[row[0]] if row[0] in assets2.index else 0
                    assets2.loc[row[0]] = [value]
                elif i >= arr_v[2]:
                    value += equities2.loc[row[0]] if row[0] in equities2.index else 0
                    equities2.loc[row[0]] = [value]
                else:
                    name = 'Deferred income taxes - L' if row[0] == 'Deferred income taxes' else row[0]
                    value += liab2.loc[name] if name in liab2.index else 0
                    liab2.loc[name] = [value]
                is_reached = True
            i += 1
        if not equities2.empty and not liab2.empty and not assets2.empty:
            equities = equities.join(equities2, how='outer')
            liab = liab.join(liab2, how='outer')
            assets = assets.join(assets2, how='outer')

    assets['Category'] = ["A"] * assets.shape[0]
    liab['Category'] = ["L"] * liab.shape[0]
    equities['Category'] = ["E"] * equities.shape[0]
    assets, liab, equities = assets.fillna(0.0), liab.fillna(0.0), equities.fillna(0.0)
    bs = pd.concat([assets, liab, equities])
    if not bs.empty:
        bs = bs.drop(['Net loans'])
        if save:
            bs.to_csv(f_loc)
    return bs


def bs_load_all_and_filter(tickers, new=False, f_loc='/data/bs_ms.csv', save=True):
    f_loc = md.MAIN_DIRECTORY + f_loc
    if new or not os.path.isfile(f_loc):
        bs = download_balance_sheet(list(md.tickers.values()), f_loc=f_loc, save=save)
    else:
        bs = pd.read_csv(f_loc, index_col=0)
    tickers = list(set(bs.columns & tickers))
    return bs[tickers + ['Category']], tickers
