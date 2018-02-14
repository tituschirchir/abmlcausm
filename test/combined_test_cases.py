import unittest

import misc.implied_volatility as iv
import misc.root_finders as rf
import misc.tree_option_pricing as eabt
from misc.finite_difference import explicit_finite_difference
from misc.heston import heston_call_closed_form
from misc.options_util import OptionTypes
from products.options import EuropeanOption


def func1(x):
    return x ** 3 - x + 2


class TestBlackScholes(unittest.TestCase):
    def test_call(self):
        option = EuropeanOption(Type=1, S=100, K=99, r=.0142, q=0.0, T=3, sigma=.25)
        expected = dict(Type='Call', S=100.0, r=0.0142, q=0.0, T=3.0, vol=0.25, Price=19.386905422210063,
                        d1=0.33809709325788295, d2=-0.09491560863433635, Delta=0.632354989526313,
                        Theta=-0.009155689620436062, Rho=1.315457805912637, Vega=0.6526024039985233,
                        Gamma=0.008701365386646977, Phi=-1.897064968578939, Charm=-5.0181713513674874e-05,
                        Vanna=0.0014304927800286294, Vomma=0.0014304927800286294)
        self.assertDictEqual(option.get_premium().properties(), expected)

    def test_put(self):
        option = EuropeanOption(Type=-1, S=100, K=99, r=.0142, q=0.0, T=3, sigma=.25)
        expected = dict(Type='Put', S=100.0, r=0.0142, q=0.0, T=3.0, vol=0.25, Price=14.258073917562605,
                        d1=0.33809709325788295, d2=-0.09491560863433635, Delta=-0.36764501047368703,
                        Theta=-0.005464811284452482, Rho=-1.5306772489479392, Vega=0.6526024039985233,
                        Gamma=0.008701365386646977, Phi=1.102935031421061, Charm=-5.0181713513674874e-05,
                        Vanna=0.0014304927800286294, Vomma=0.0014304927800286294)
        self.assertDictEqual(option.get_premium().properties(), expected)

    def test_bisection(self):
        bisct = rf.bisection(func1, a=-10, b=10, tol=0.0001)
        secnt = rf.secant(func1, a=-10, b=10, tol=0.0001)
        self.assertAlmostEqual(0, func1(bisct), 7)
        self.assertAlmostEqual(0, func1(secnt), 7)
        self.assertAlmostEqual(bisct, secnt, 7)

    def test_implied_vol(self):
        est_vol = iv.implied_vol(C=19.386905422210063, S=100, K=99, T=3, r=.0142, Type=1, q=0.0)
        self.assertAlmostEqual(.25, est_vol, 7)

    def test_area_calcs(self):
        self.assertEqual(rf.simpson_rule(func1, 0, 2, 5), 6.0)
        self.assertAlmostEqual(rf.trapezoid_rule(func1, 0, 2, 1000), 6.0, 2)


class TestTreePricing(unittest.TestCase):
    def tree_euro_options(self, is_call=False, is_american=True, expected=0.0):
        values = eabt.euro_amer_binomial_tree(is_call, is_american, K=20, Tt=1, S0=20, r=0.06, N=3, sigma=0.2)
        self.assertAlmostEqual(values, expected, 5)

    def test_european_call(self):
        self.tree_euro_options(True, False, 2.318398)
        self.tree_euro_options(True, True, 2.318398)
        self.tree_euro_options(False, False, 1.158088)
        self.tree_euro_options(False, True, 1.232422)

    def tree_up_out_options(self, is_call=False, is_american=True, expected=0.0):
        values = eabt.up_and_out_binomial(is_call, is_american, K=10, Tt=0.3, S0=10, sigma=0.2, r=0.01, H=11, N=3)
        self.assertAlmostEqual(values, expected, 5)

    def test_up_out_european_call(self):
        self.tree_up_out_options(True, False, 0.16014)
        self.tree_up_out_options(True, True, 0.4860549)
        self.tree_up_out_options(False, False, 0.4585154)
        self.tree_up_out_options(False, True, 0.4610887)

    def test_compare_binomial_with_bs(self):
        option = EuropeanOption(Type=-1, S=100, K=99, r=.0142, q=0.0, T=3, sigma=.25)
        bsMerton = option.get_premium()
        kwargs = {"is_tree": True, "N": 100}
        binomial = option.get_premium(**kwargs)
        self.assertAlmostEqual(bsMerton.premium(), binomial, 1)

        option = EuropeanOption(Type=1, S=100, K=101, r=.0142, q=0.0, T=3, sigma=.25)
        bsMerton = option.get_premium()
        kwargs = {"is_tree": True, "N": 100}
        binomial = option.get_premium(**kwargs)
        self.assertAlmostEqual(bsMerton.premium(), binomial, 1)


class TestHeston(unittest.TestCase):
    def heston_runner(self, K, kappa, theta=0.1, sigma=0.2, S0=1, lmd=0, rho=-0.3, V0=0.1, r=0, q=0, tau=5):
        return round(heston_call_closed_form(theta, sigma, S0, lmd, rho, V0, r, q, tau, K, kappa), 5)

    # test with values from Mikhailov's and Sergei's paper
    def test_heston_call_closed_form(self):
        self.assertListEqual([self.heston_runner(0.5, x) for x in [4, 2, 1]], [0.54228, 0.54285, 0.54364])
        self.assertListEqual([self.heston_runner(0.75, x) for x in [4, 2, 1]], [0.38554, 0.3853, 0.38445])
        self.assertListEqual([self.heston_runner(1, x) for x in [4, 2, 1]], [0.27521, 0.2739, 0.27112])
        self.assertListEqual([self.heston_runner(1.25, x) for x in [4, 2, 1]], [0.19844, 0.19631, 0.1922])
        self.assertListEqual([self.heston_runner(1.5, x) for x in [4, 2, 1]], [0.14483, 0.14221, 0.13749])


class TestFiniteDifferenceMethods(unittest.TestCase):
    def finite_diff_runner(self, is_call, is_american, flavor):
        fd = explicit_finite_difference(is_call=is_call, is_american=is_american, flavor=flavor, K=100, Tm=1, S=100,
                                        r=0.06, sig=0.25, N=3, div=0.03, dx=0.2)
        return fd[str(0)].values

    def test_explicit_finite_difference(self):
        self.assertEqual(10.792942352920473, self.finite_diff_runner(True, True, OptionTypes.VANILLA)[3])
        self.assertEqual(10.792942352920473, self.finite_diff_runner(True, False, OptionTypes.VANILLA)[3])
        self.assertEqual(8.248140028322315, self.finite_diff_runner(False, True, OptionTypes.VANILLA)[3])
        self.assertEqual(7.872837436899252, self.finite_diff_runner(False, False, OptionTypes.VANILLA)[3])
        self.assertEqual(0.0, self.finite_diff_runner(True, True, OptionTypes.UP_AND_OUT)[3])
        self.assertEqual(0.0, self.finite_diff_runner(True, False, OptionTypes.UP_AND_OUT)[3])
        self.assertEqual(0.0, self.finite_diff_runner(False, True, OptionTypes.UP_AND_OUT)[3])
        self.assertEqual(0.0, self.finite_diff_runner(False, False, OptionTypes.UP_AND_OUT)[3])


if __name__ == '__main__':
    unittest.main()
