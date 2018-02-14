import os
import urllib as u

import pandas as pd
from bs4 import BeautifulSoup as bs


def get_company_data(url_v, symbol, fields_dict, qt):
    res = []
    try:
        url = url_v.format(symbol)
        html = u.request.urlopen(url).read()
        soup = bs(html, 'lxml')
        soup.prettify()
        for k in fields_dict:
            i = 0
            mix = soup.find(text=k)
            while i < qt:
                mix = mix.find_next()
                i += 1
            value = mix.text
            replace_comma = value.replace(',', '')
            replace_comma = replace_comma.replace('$', '')
            res.append(0.0 if replace_comma == "--" else float(replace_comma) * 1000)
        res.append(0.0)
    except Exception as e:
        print(e)
    return res


def scrape_balance_sheet_data(qt, stock_list):
    url_v = 'https://eresearch.fidelity.com/eresearch/evaluate/fundamentals/financials.jhtml?stockspage=financials&symbols={}&period=quarterly'
    fields_dict = ["ASSETS TOTAL",
                   " Cash and Short-Term Investments – Total",
                   " Receivables – Total",
                   " Inventories – Total",
                   " Current  Assets – Other – Total",
                   "Liabilities Total",
                   "Shareholders' Equity Total" + "\t",
                   " Debt in Current Liabilities",
                   'Account Payable/Creditors – Trade']
    cnames = ["LT_A", "cash_A", "AccRec_A", "Inventories_A", "Other_curr_A", 'Other_L', 'Debt_L', 'AccPay_L',
              'Equity', 'LT_L']
    data = pd.DataFrame(columns=stock_list)
    xf = "data/balance_sheet.csv"
    indices = []
    if os.path.isfile(xf):
        data = pd.read_csv(xf, index_col=0)
        indices = data.index
        data = data.transpose()
    for sym in stock_list:
        if sym not in indices:
            data[sym] = get_company_data(symbol=sym, fields_dict=fields_dict, url_v=url_v, qt=qt)
    data = data.transpose()
    data.columns = cnames
    data['LT_L'] = data['Other_L'] - data['AccPay_L'] - data['Debt_L']
    data['LT_A'] = data['LT_A'] - data['cash_A'] - data['AccRec_A'] - data["Inventories_A"] - data[
        "Other_curr_A"]
    data.to_csv(xf)
    return data.ix[stock_list]
