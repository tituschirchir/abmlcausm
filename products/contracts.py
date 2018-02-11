import random


class Contract:
    def __init__(self, name):
        self.name = name


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


class Loan(Contract):
    def __init__(self, counter_party, principal, rate, time):
        super().__init__("Loan")
        self.counter_party = counter_party
        self.rate = rate
        self.time = time
        self.principal = principal
        self.premium = 0.0

    def get_value(self):
        return self.principal * (1 + self.rate) ** self.time

    def get_premium(self):
        return self.rate * self.principal


class Position:
    def __init__(self, contract, size, long, counter_party):
        self.long = long
        self.size = size
        self.contract = contract
        self.counter_party = counter_party

    def value(self):
        return self.size * self.contract.get_value() * (1 if self.long else -1)

    def premium(self):
        return self.contract.get_premium() * (1 if self.long else -1)
