import random

from products.contracts import Contract


class Derivative(Contract):
    def __init__(self, name, premium, value, leverage):
        super().__init__("Derivative")
        self.value = value
        self.premium = premium
        self.leverage = leverage
        self.name = name

    def get_value(self):
        mult = random.random()
        div = random.random()
        c_val = self.leverage * self.value
        return c_val + (c_val * div * (1 if mult > .90 else -1)) / 10

    def get_premium(self):
        return self.premium


class Option(Derivative):
    def __init__(self, name, Type, S, K, r, q, T, sigma):
        super().__init__(name, 0.0, 0.0, 1)
        self.name = name
        self.Type, self.S, self.K, self.r, self.q, self.T, self.sigma = Type, S, K, r, q, T, sigma
        self.is_call = Type == 1

    def get_value(self):
        pass

    def get_premium(self):
        pass
