import unittest
from tkinter import Tk
from main import CryptoCompare
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


class TestCryptoCompare(unittest.TestCase):

    def setUp(self):
        self.root = Tk()
        self.crypto_compare = CryptoCompare(self.root)

    def test_fetch_data(self):
        self.crypto_compare.start_unix = '1640995200'
        self.crypto_compare.end_unix = '1672531200'
        self.crypto_compare.coin_ids = ['bitcoin', 'ethereum']
        self.crypto_compare.fetch_data()

        self.assertEqual(len(self.crypto_compare.coin_dfs), 2)
        self.assertEqual(self.crypto_compare.coin_dfs[0].index.name, 'timestamp')
        self.assertEqual(self.crypto_compare.coin_dfs[1].index.name, 'timestamp')

    def test_plot_data(self):
        # This is a simple test to ensure that the plot_data method runs without errors.
        # It doesn't test the correctness of the plot itself.
        self.crypto_compare.start_unix = '1640995200'
        self.crypto_compare.end_unix = '1672531200'
        self.crypto_compare.coin_ids = ['bitcoin', 'ethereum']
        self.crypto_compare.fetch_data()

        try:
            self.crypto_compare.plot_data()
        except Exception as e:
            self.fail(f"plot_data failed with error: {e}")

if __name__ == '__main__':
    unittest.main()
