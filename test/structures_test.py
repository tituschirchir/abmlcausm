"""
This class is to test the facilities in the structures directory
"""
import unittest

from structures.bank_structures import BalanceSheet
import pandas as pd


class TestBalanceSheetStructure(unittest.TestCase):
    def test_balance_sheet(self):
        data = pd.read_csv('sample_bs.csv', index_col=0)
        bs_sheets = [BalanceSheet(data[[st, 'Category']], st) for st in data.columns if st != 'Category']
        self.assertEqual(5, len(bs_sheets))
        self.assertEqual(72, len(bs_sheets[0].line_items))
        self.assertListEqual([2573126, 526186, 2104534, 1687155, 1842530], [x.total_assets() for x in bs_sheets])
        self.assertListEqual([2341061, 286016, 1861063, 1502761, 1631996], [x.total_liabilities() for x in bs_sheets])
        self.assertListEqual([232065, 240170, 243471, 184394, 210534], [x.total_equity() for x in bs_sheets])
        self.assertListEqual([0] * 5, [x.identity() for x in bs_sheets])
