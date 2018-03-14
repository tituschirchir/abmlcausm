import random

import structures.constants as bst
from network.core.skeleton import Node
from products.equities import Stock
from structures.bank_structures import BalanceSheet, double_entry


class Bank(Node):
    def __init__(self, name, unique_id, model, data, time_series):
        super().__init__(unique_id, model)
        self.name = name
        self.time_series = time_series
        self.balance_sheet = BalanceSheet(data, "BS")
        self.interbankAssets = self.balance_sheet.find_node_series("Assets", "Interbank")
        self.interbank_borrowing = self.balance_sheet.find_node_series("Liabilities", "Interbank")
        self.externalAssets = self.balance_sheet.find_node_series("Assets", "External")
        self.capital = self.balance_sheet.find_node("Equities")
        self.customer_deposits = self.balance_sheet.find_node_series("Liabilities", "Deposits and Others")
        self.shock = 0.0
        self.defaults, self.affected = False, False
        self.counter_parties = []
        self.bad_debt = 0.0
        self.issued_shares = self.capital.value
        self.price_history = [1.0]
        self.stock = Stock(S=1.0, mu=time_series.mu, std=time_series.vol, dt=1.0 / 252.)
        self.allocated_credit = self.balance_sheet.find_node_series("Liabilities", "Interbank").value

    def step_1(self):
        self.equity_change()

    def step_2(self):
        self.deal_with_shock()

    def equity_change(self):
        init__s = self.stock.S
        self.stock.evolve()
        self.capital.value += (self.stock.S - init__s) * self.issued_shares
        self.externalAssets.value += (self.stock.S - init__s) * self.issued_shares
        self.price_history.append(self.stock.S)

    def apply_initial_shock(self, shock):
        self.shock = shock
        if self.externalAssets.value < self.shock:
            self.externalAssets.value = 0.0
            self.bad_debt = self.shock - self.externalAssets.value
        else:
            self.externalAssets.value -= self.shock
        self.deal_with_shock(tremor=False)

    def deal_with_shock(self, tremor=True):
        # If no shock felt by bank, return
        if self.shock == 0.0:
            return
        if tremor:
            if self.interbankAssets.value < self.shock:
                self.interbankAssets.value = 0.0
                self.bad_debt = self.shock - self.interbankAssets.value
            else:
                self.interbankAssets.value -= self.shock
        # Check if enough money is set aside to cover losses (provision for defaults)
        allowance_for_losses = self.balance_sheet.find_node(bst.allowance_for_loan_losses)
        if -allowance_for_losses.value > self.shock:
            allowance_for_losses.value += self.shock
        else:
            self.shock += allowance_for_losses.value
            double_entry(allowance_for_losses, self.balance_sheet.find_node(bst.loans), allowance_for_losses.value,
                         'di')
            if self.capital.value > self.shock:
                self.capital.value -= self.shock
                self.affected = True
            else:
                residual = self.shock - self.capital
                debt_collected = self.collect_debts(recovery=.9, residual=residual)
                if residual - debt_collected > 0.0:
                    self.deal_with_bankruptcy(residual - debt_collected)
        self.shock = 0.0
        self.stock.S = self.capital.value / self.issued_shares

    def deal_with_bankruptcy(self, residual):
        if random.random() > 0.25:
            self.process_bankruptcy(residual)
        else:
            self.borrow_to_offset(residual)

    def process_bankruptcy(self, residual):
        self.capital.value = 0.0
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
            self.interbank_borrowing.value += residual
            self.externalAssets.value += residual
            lender.interbankAssets.value += residual
            lender.externalAssets.value += residual
        else:
            self.process_bankruptcy(residual)

    def collect_debts(self, recovery, residual):
        total_loans = sum(x.value for x in self.in_degree)
        fract = residual / total_loans
        if fract < 1:
            for x in self.in_degree:
                temp = x.value
                x.value -= fract * x.value
                x.node_from.interbank_borrowing.value -= temp * fract
            self.interbankAssets.value -= total_loans * fract
            return residual
        else:
            for x in self.in_degree:
                self.remove_edge(x)
                x.node_from.interbank_borrowing.value -= x.value
            return total_loans
