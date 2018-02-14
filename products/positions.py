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
