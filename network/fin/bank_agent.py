import random

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
        self.issued_shares = 0.0
        self.edges = []
        self.stock = None
        self.price_history = []

    def equity_change(self):
        init_S = self.stock.S
        self.price_history.append(init_S)
        self.stock.evolve()
        self.capital += (self.stock.S - init_S) * self.issued_shares
        self.externalAssets += (self.stock.S - init_S) * self.issued_shares

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
            debt_collected = self.collect_debts(recovery=.9, residual=residual)
            if residual - debt_collected > 0.0:
                self.deal_with_bankruptcy(residual - debt_collected)
        self.shock = 0.0

    def deal_with_bankruptcy(self, residual):
        if random.random() > 0.25:
            self.process_bankruptcy(residual)
        else:
            self.borrow_to_offset(residual)

    def process_bankruptcy(self, residual):
        self.capital = 0.0
        self.defaults = True
        living = [x for x in [y.node_to for y in self.edges] if not x.defaults]
        self.edges = []
        k = len(living)
        if k > 0:
            for x in living:
                x.remove_edge(to=self)
                x.shock += residual / k

    def borrow_to_offset(self, residual):
        all_agents = self.model.schedule.agents
        viable_lenders = [agt for agt in all_agents if agt.externalAssets > 2 * residual]
        if viable_lenders:
            lender = random.choice(viable_lenders)
            edge = self.edge_exists(lender)
            edge.value += residual
            self.interbank_borrowing += residual
            self.externalAssets += residual
            lender.interbankAssets += residual
            lender.externalAssets += residual
        else:
            self.process_bankruptcy(residual)

    def collect_debts(self, recovery, residual):
        total_loans = sum(x.value for x in self.in_degree)
        fract = residual / total_loans
        if fract < 1:
            for x in self.in_degree:
                temp = x.value
                x.value -= fract * x.value
                x.node_from.interbank_borrowing -= temp * fract
            self.interbankAssets -= total_loans * fract
            return residual
        else:
            for x in self.in_degree:
                self.remove_edge(x)
                x.node_from.interbank_borrowing -= x.value
            return total_loans
