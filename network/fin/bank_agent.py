from network.core.skeleton import Node


class Bank(Node):
    def __init__(self, name, unique_id, model):
        super().__init__(unique_id, model)
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
        self.edges = []

    def apply_initial_shock(self, shock):
        self.shock = shock
        if self.externalAssets < self.shock:
            self.externalAssets = 0.0
            self.bad_debt = self.shock - self.externalAssets
        else:
            self.externalAssets -= self.shock
        self.deal_with_shock(tremor=False)

    def deal_with_shock(self, tremor=True):
        if self.shock == 0:
            return
        if tremor:
            if self.interbankAssets < self.shock:
                self.interbankAssets = 0.0
                self.bad_debt = self.shock - self.interbankAssets
            else:
                self.interbankAssets -= self.shock
        if self.capital > self.shock:
            self.capital -= self.shock
            self.affected = True
        else:
            residual = self.shock - self.capital
            self.capital = 0.0
            self.defaults = True
            living = [x for x in [y.node_to for y in self.edges] if not x.defaults]
            k = len(living)
            if k > 0:
                for x in living:
                    x.shock += residual / k
        self.shock = 0.0
