from network.components import Agent
from products.equities import Stock


class Node(Agent):
    def __init__(self, id, mu, sigma, cash, st_assets, lt_assets, st_liabilities, lt_liabilities, deposits,
                 equities, model):
        super().__init__(id, model)
        self._id = id
        self.mu = mu
        self.sigma = sigma
        self.cash = cash
        self.st_assets = st_assets
        self.lt_assets = lt_assets
        self.deposits = deposits
        self.lt_liabilities = lt_liabilities
        self.st_liabilities = st_liabilities
        self.stock_issue = 100
        self.equities = equities
        self.stock_price = self.equities / self.stock_issue
        self.stock = Stock(S=self.stock_price, std=self.sigma, mu=self.mu, dt=1. / 252)
        self.bank_borrow, self.bank_lend = 0.0, 0.0
        self.edges_to = []
        self.shock = 0.0
        self.is_alive = True
        self.equity_history = [self.equities]

    def add_edge(self, edge):
        self.edges_to.append(edge)
        self.bank_borrow += edge.value
        self.st_liabilities -= edge.value
        edge.node_to.bank_lend += edge.value
        edge.node_to.st_assets -= edge.value

    def equity_change(self):
        if self.is_alive:
            self.stock.evolve()
            init_eq = self.equities
            self.equities = self.stock.S * self.stock_issue
            delta = self.equities - init_eq
            self.cash += delta
        self.equity_history.append(self.equities)

    def spread_shock(self):
        if self.is_alive and self.shock > 0.0:
            res = self.equities - self.shock
            if res < 0.0:
                print(" {} dies and spreads".format(self._id))
                self.equities = 0.0
                self.is_alive = False
                for x in self.edges_to:
                    print("   cascade infection: {} by {}".format(x._id, self._id))
                    x.node_to.bank_lend -= x.value
                    x.node_to.shock = x.value
            else:
                print(" {} absorbs!".format(self._id))
                self.equities = res
            self.shock = 0.0
            self.stock.S = self.equities / self.stock_issue


class Edge:
    def __init__(self, to, value):
        self._id = to._id
        self.node_to = to
        self.value = value
