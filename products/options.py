import misc.options_util as ou
import misc.tree_option_pricing as eabt
from misc.black_scholes import BSMerton
from products.derivatives import Option


class EuropeanOption(Option):
    def __init__(self, Type, S, K, r, q, T, sigma):
        name = "European {} Option".format("Call" if Type == 1 else "Put")
        super().__init__(name, Type, S, K, r, q, T, sigma)
        self.bsModel = []

    def get_premium(self, **kwargs):
        if "is_tree" in kwargs.keys():
            N = kwargs.get("N")
            res = eabt.euro_amer_binomial_tree(self.is_call, False, K=self.K, Tt=self.T, S0=self.S, r=self.r, N=N,
                                               sigma=self.sigma)
            return res
        return BSMerton(self.Type, self.S, self.K, self.r, self.q, self.T, self.sigma)

    def get_value(self):
        return ou.mult(self.Type == "Call") * (self.S - self.K)


class AmericanOption(Option):
    def __init__(self, Type, S, K, r, q, T, sigma):
        name = "American {} Option".format("Call" if Type == 1 else "Put")
        super().__init__(name, Type, S, K, r, q, T, sigma)

    def get_premium(self, **kwargs):
        N = kwargs.get("N")
        res = eabt.euro_amer_binomial_tree(self.is_call, True, K=self.K, Tt=self.T, S0=self.S, r=self.r, N=N,
                                           sigma=self.sigma)
        return res.loc[0]["0"]


class KnockOutOption(Option):
    def __init__(self, Type, S, K, r, q, T, sigma):
        name = "American {} Option".format("Call" if Type == 1 else "Put")
        super().__init__(name, Type, S, K, r, q, T, sigma)

    def get_premium(self, **kwargs):
        N = kwargs.get("N")
        res = eabt.up_and_out_binomial(self.is_call, True, K=self.K, Tt=self.T, S0=self.S, r=self.r, N=N,
                                       sigma=self.sigma)
        return res.loc[0]["0"]

    def get_value(self):
        return ou.mult(self.Type == "Call") * (self.S - self.K)
