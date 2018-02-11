import unittest

import misc.implied_volatility as iv
import misc.root_finders as rf
from misc.black_scholes import BSMerton


def func1(x):
    return x ** 3 - x + 2


class TestBlackScholes(unittest.TestCase):
    def test_call(self):
        bsm = BSMerton(Type=1, S=100, K=99, r=.0142, q=0.0, T=3, sigma=.25)
        expected = dict(Type='Call', S=100.0, r=0.0142, q=0.0, T=3.0, vol=0.25, Price=19.386905422210063,
                        d1=0.33809709325788295, d2=-0.09491560863433635, Delta=0.632354989526313,
                        Theta=-0.009155689620436062, Rho=1.315457805912637, Vega=0.6526024039985233,
                        Gamma=0.008701365386646977, Phi=-1.897064968578939, Charm=-5.0181713513674874e-05,
                        Vanna=0.0014304927800286294, Vomma=0.0014304927800286294)
        self.assertDictEqual(bsm.properties(), expected)

    def test_put(self):
        bsm = BSMerton(Type=-1, S=100, K=99, r=.0142, q=0.0, T=3, sigma=.25)
        expected = dict(Type='Put', S=100.0, r=0.0142, q=0.0, T=3.0, vol=0.25, Price=14.258073917562605,
                        d1=0.33809709325788295, d2=-0.09491560863433635, Delta=-0.36764501047368703,
                        Theta=-0.005464811284452482, Rho=-1.5306772489479392, Vega=0.6526024039985233,
                        Gamma=0.008701365386646977, Phi=1.102935031421061, Charm=-5.0181713513674874e-05,
                        Vanna=0.0014304927800286294, Vomma=0.0014304927800286294)
        self.assertDictEqual(bsm.properties(), expected)

    def test_bisection(self):
        bisct = rf.bisection(func1, a=-10, b=10, tol=0.0001)
        secnt = rf.secant(func1, a=-10, b=10, tol=0.0001)
        self.assertAlmostEqual(0, func1(bisct), 7)
        self.assertAlmostEqual(0, func1(secnt), 7)
        self.assertAlmostEqual(bisct, secnt, 7)

    def test_implied_vol(self):
        est_vol = iv.implied_vol(C=19.386905422210063, S=100, K=99, T=3, r=.0142, Type=1, q=0.0)
        self.assertAlmostEqual(.25, est_vol, 7)


if __name__ == '__main__':
    unittest.main()
