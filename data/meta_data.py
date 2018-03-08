from os.path import dirname

MAIN_DIRECTORY = dirname(dirname(__file__))

tickers = {'JP Morgan Chase & Co': 'JPM', 'Berkshire Hathaway B': 'BRK.b', 'Bank of America Corp': 'BAC',
           'Wells Fargo & Co': 'WFC', 'Citigroup Inc': 'C', 'Goldman Sachs Group Inc': 'GS', 'US Bancorp': 'USB',
           'Morgan Stanley': 'MS', 'PNC Finl Services Group': 'PNC', 'American Express Co': 'AXP',
           'Chubb Limited': 'CB', 'BlackRock Inc': 'BLK', 'Schwab Charles Corp': 'SCHW',
           'The Bank of New York Mellon Corp': 'BK', 'CME Group Inc A': 'CME', 'American Intl Group Inc': 'AIG',
           'Metlife Inc': 'MET', 'S&P Global Inc': 'SPGI', 'Capital One Financial': 'COF',
           'Prudential Financial Inc': 'PRU', 'BB&T Corp': 'BBT', 'Intercontinental Exchange Inc': 'ICE',
           'Marsh & McLennan Companies': 'MMC', 'State Street Corp': 'STT', 'Travelers Cos Inc': 'TRV',
           'Aon plc': 'AON', 'AFLAC Inc': 'AFL', 'Allstate Corp': 'ALL', 'SunTrust Banks Inc (GA)': 'STI',
           'Progressive Corp': 'PGR', 'Discover Financial Services': 'DFS', 'M&T Bank Corp': 'MTB',
           "Moody's Corp": 'MCO', 'Synchrony Financial': 'SYF', 'T Rowe Price Group Inc': 'TROW',
           'Ameriprise Financial Inc': 'AMP', 'Fifth Third Bancorp (OH)': 'FITB', 'Regions Financial Corp': 'RF',
           'Citizens Financial Group Inc': 'CFG', 'KeyCorp': 'KEY', 'Northern Trust Corp (IL)': 'NTRS',
           'Willis Towers Watson PLC': 'WLTW', 'Hartford Finl Services Group': 'HIG', 'Comerica Inc (MI)': 'CMA',
           'Huntington Bancshares (OH)': 'HBAN', 'Lincoln National Corp': 'LNC', 'Principal Financial Group': 'PFG',
           'E*TRADE Financial Corp': 'ETFC', 'Invesco Ltd': 'IVZ', 'Loews Corp': 'L',
           'Cboe Global Markets, Inc': 'CBOE', 'Franklin Resources Inc': 'BEN', 'Gallagher Arthur J. & Co': 'AJG',
           'Raymond James Financial Inc': 'RJF', 'Cincinnati Financial Corp': 'CINF', 'Unum Group': 'UNM',
           'XL Group Ltd': 'XL', 'Zions Bancorp (UT)': 'ZION', 'Affiliated Managers Grp': 'AMG',
           'Everest Re Group Ltd': 'RE', 'Nasdaq Inc': 'NDAQ', 'Torchmark Corp': 'TMK',
           'Leucadia National Corp (NY)': 'LUK', "People's United Financial Inc": 'PBCT',
           'Brighthouse Financial Inc': 'BHF', 'Assurant Inc': 'AIZ', 'Navient Corp': 'NAVI'}

kawai = "Kamada Kawai"
layouts = ['Circular', kawai, 'Random', 'Rescale', "Shell", "Spring", "Spectral", "Fruchterman Reingold"]
network_types = ['Erdos', 'Barabasi']

morning_star = 'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={}&reportType=bs&period=3&dataType=A&order=asc&columnYear=5&number=3'
