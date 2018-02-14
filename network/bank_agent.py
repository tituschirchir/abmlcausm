from network.network_structure import Vertex
from products.equities import Stock


class Bank(Vertex):
    def __init__(self, unique_id, ticker, data, stock_data, model):
        super().__init__(unique_id, model)
        self.ticker = ticker
        self.lt_assets = data.LT_A
        self.cash_A = data.cash_A
        self.accRec_A = data.AccRec_A
        self.inventories_assets = data.Inventories_A
        self.other_curr_assets = data.Other_curr_A
        self.other_liab = data.Other_L
        self.debt_liab = data.Debt_L
        self.accPay_liab = data.AccPay_L
        self.lt_liab = data.LT_L
        self.equity = data.Equity
        self.state = 'Alive'
        self.shock_quantity = 0.0
        self.to_shock = False
        self.bad_debt = 0.0
        self.contracts = []
        self.stock = Stock(S=stock_data.current_price, std=stock_data.annual_std, mu=stock_data.annual_ret, dt=1. / 252)
        self.stock_issue = self.equity / self.stock.S

    def equity_change(self):
        if self.to_shock:
            self.shock()
        if self.state != 'Dead':
            self.stock.evolve()
            init_eq = self.equity
            self.equity = self.stock.S * self.stock_issue
            delta = self.equity - init_eq
            self.cash_A += delta

    def shock(self):
        if self.equity <= self.shock_quantity:
            residual = self.shock_quantity - self.equity
            self.cash_A = 0.0
            self.equity = 0.0
            self.state = "Dead"
            self.infect_neighborhood(residual)
            self.shock_quantity = 0.0
        else:
            self.cash_A -= self.shock_quantity
            self.equity -= self.shock_quantity
            self.shock_quantity = 0.0
        self.to_shock = False

    def settle_contracts(self):
        dead_c = [y for y in self.contracts if y.counter_party.state == "Dead"]
        for j in dead_c:
            self.cash_A -= j.value()
            self.equity -= j.value()
        self.contracts = [y for y in self.contracts if y.counter_party.state != "Dead"]
        for x in self.contracts:
            self.cash_A -= x.premium()
            self.equity -= x.premium()

    def infect_neighborhood(self, residual):
        solvent_neighbors = self.solvent_neighbors_to()
        if solvent_neighbors:
            num = len(solvent_neighbors)
            for sn in solvent_neighbors:
                shared_loss = residual / num
                sn.shock_quantity += shared_loss
                sn.state = 'Infected'
        else:
            self.bad_debt += residual

    def position_value(self):
        return sum([x.value() for x in self.contracts])

    def liquidity(self):
        return self.position_value() + self.equity

