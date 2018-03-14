from structures.bank_structures import BalanceSheet


class Shock:
    def __init__(self, origin, target, amount):
        self.target = target
        self.amount = amount
        self.origin = origin


def external_shock(shock):
    return shock


def interbank_shock(balance_sheet, shock):
    return shock


import pandas as pd

data = pd.read_csv("../data/bs_ms.csv", index_col=0)
bs = BalanceSheet(data['JPM'], "BS")

print(bs)
