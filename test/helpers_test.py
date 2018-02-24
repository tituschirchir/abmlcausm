"""
This class is to test the facilities in the structures directory
"""
import unittest

import helpers.data_downloader as dd


class TestDataDownloader(unittest.TestCase):
    def test_download_balance_sheet(self):
        tickers = ["BAC", "GS", "MS", "PNC"]
        bs = dd.download_balancesheet(tickers, save=False)
        assets = bs[bs.Category == "A"][tickers]
        liabilities = bs[bs.Category == "L"][tickers]
        equity = bs[bs.Category == "E"][tickers]
        bs_condition = list(equity.sum().values + liabilities.sum().values - assets.sum().values)
        self.assertListEqual([0.0, 0.0, 0.0, 0.0], bs_condition)


if __name__ == '__main__':
    unittest.main()
