class Bank:
    def __init__(self, name):
        self.name = name
        self.interbankAssets = 0.0
        self.interbank_borrowing = 0.0
        self.externalAssets = 0.0
        self.capital = 0.0
        self.customer_deposits = 0.0
        self.visits = 0
        self.shock = 0.0
        self.defaults = False
        self.affected = False
        self.counter_parties = []
        self.bad_debt = 0.0

    def get_assets(self):
        return self.interbankAssets + self.externalAssets

    def get_liabilities(self):
        return self.customer_deposits + self.interbank_borrowing

    def add_counter_party(self, other):
        self.counter_parties.append(other)

    def __str__(self):
        return "B:{} L: {} C: {}, E:{}, CD: {}".format(
            self.interbank_borrowing,
            self.interbankAssets,
            self.capital,
            self.externalAssets,
            self.customer_deposits
        )

    def apply_initial_shock(self, shock):
        self.shock = shock
        if self.externalAssets < self.shock:
            self.externalAssets = 0.0
            self.bad_debt = self.shock - self.externalAssets
        else:
            self.externalAssets -= self.shock
        self.deal_with_shock(tremor=False)

    def deal_with_shock(self, tremor=True):
        if tremor:
            if self.interbankAssets < self.shock:
                self.interbankAssets = 0.0
                self.bad_debt = self.shock - self.interbankAssets
            else:
                self.interbankAssets -= self.shock
        if self.capital >= self.shock:
            self.capital -= self.shock
        else:
            residual = self.shock - self.capital
            self.capital = 0.0
            self.defaults = True
            living = [x for x in self.counter_parties if not x.defaults]
            k = len(living)
            if k > 0:
                for x in living:
                    x.shock += residual / k
        self.shock = 0.0
