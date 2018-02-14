from products.contracts import Contract


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
