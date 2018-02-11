import unittest

from misc.black_scholes import BSMerton


class TestBlackScholes(unittest.TestCase):
    def test_call(self):
        bsm = BSMerton(args=[1, 100, 99, .0142, 0.0, 3 * 365, .25])
        expected = dict(Type='Call', S=100.0, r=0.0142, q=0.0, T=3.0, vol=0.25, Price=19.386905422210063,
                        d1=0.33809709325788295, d2=-0.09491560863433635, Delta=0.632354989526313,
                        Theta=-0.009155689620436062, Rho=1.315457805912637, Vega=0.6526024039985233,
                        Gamma=0.008701365386646977, Phi=-1.897064968578939, Charm=-5.0181713513674874e-05,
                        Vanna=0.0014304927800286294, Vomma=0.0014304927800286294)
        self.assertDictEqual(bsm.properties(), expected)

    def test_put(self):
        bsm = BSMerton(args=[-1, 100, 99, .0142, 0.0, 3 * 365, .25])
        expected = dict(Type='Put', S=100.0, r=0.0142, q=0.0, T=3.0, vol=0.25, Price=14.258073917562605,
                        d1=0.33809709325788295, d2=-0.09491560863433635, Delta=-0.36764501047368703,
                        Theta=-0.005464811284452482, Rho=-1.5306772489479392, Vega=0.6526024039985233,
                        Gamma=0.008701365386646977, Phi=1.102935031421061, Charm=-5.0181713513674874e-05,
                        Vanna=0.0014304927800286294, Vomma=0.0014304927800286294)
        self.assertDictEqual(bsm.properties(), expected)


if __name__ == '__main__':
    unittest.main()
