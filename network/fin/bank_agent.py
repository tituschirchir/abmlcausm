import random

import structures.constants as bst
from network.core.skeleton import Node
from products.equities import Stock
from structures.bank_structures import BalanceSheet


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
        self.unallocated_credit = self.balance_sheet.find_node_series("Liabilities", "Interbank").value
        self.unallocated_debt = self.balance_sheet.find_node_series("Assets", "Interbank").value

    def step_1(self):
        self.equity_change()

    def step_2(self):
        self.deal_with_shock()

    def equity_change(self):
        init__s = self.stock.S
        self.stock.evolve()
        common = self.capital.find_node(bst.common_stock)
        other = self.capital.find_node_series(bst.other_equity)
        preferred = self.capital.find_node_series(bst.preferred_stock)
        total = sum([x.value for x in [common, other, preferred]])
        delta = (self.stock.S - init__s) * self.issued_shares
        for x in [common, other, preferred]:
            if x.value != 0.0:
                value_total = delta * x.value / total
                x.value += value_total
        self.balance_sheet.find_node(bst.cash_and_cash_equivalents).value += delta
        self.price_history.append(self.stock.S)
        self.balance_sheet.re_aggregate()

    def apply_initial_shock(self, shock):
        self.shock = shock
        if self.externalAssets.value < self.shock:
            self.externalAssets.value = 0.0
            self.bad_debt = self.shock - self.externalAssets.value
        else:
            self.externalAssets.value -= self.shock
        self.deal_with_shock(tremor=False)
        self.balance_sheet.re_aggregate()

    def deal_with_shock(self, tremor=True):
        # If no shock felt by bank, return
        equity_impact = 0.0
        recovery = 0.6
        if self.shock == 0.0:
            return
        # if shock is resulting from interbank reverberations ----
        self.affected = True
        if tremor:
            liquid_external_assets = self.balance_sheet.find_node_series("Assets", "External", "Liquid")
            disbursable = max(0.0, min(liquid_external_assets.value, self.shock))
            liquid_nodes = liquid_external_assets.get_all_terminal_nodes()
            for ln in liquid_nodes:
                ln.value -= ln.value * disbursable / liquid_external_assets.value
            equity_impact += disbursable
            self.shock -= disbursable
            # if shock cannot be absorbed by liquid assets
            if self.shock > 0.0:
                illiquid_external_assets = self.balance_sheet.find_node_series("Assets", "External", "Illiquid")
                recovery_value = illiquid_external_assets.value * recovery
                disbursable = min(self.shock, recovery_value)
                for iln in illiquid_external_assets.get_all_terminal_nodes():
                    iln.value -= iln.value * disbursable / recovery / illiquid_external_assets.value

                retained_earnings_hit = disbursable * (1 - recovery) / recovery
                self.balance_sheet.find_node_series("Equities", bst.retained_earnings).value -= retained_earnings_hit

                equity_impact += disbursable
                self.shock -= disbursable
                if self.shock > 0.0:
                    self.deal_with_bankruptcy(self.shock)

            equity = self.balance_sheet.find_node_series("Equities")
            if equity.value < equity_impact:
                self.defaults = True
            for eqty in equity.children:
                eqty.value -= equity_impact * eqty.value / equity.value
            equity.re_aggregate()
            self.stock.S = equity.value / self.issued_shares

    def deal_with_bankruptcy(self, residual):
        if random.random() > 0.5:
            self.process_bankruptcy(residual)
        else:
           self.borrow_to_offset(residual)

    def process_bankruptcy(self, residual):
        self.defaults = True
        self.shock = 0.0
        living = [x for x in [y.node_to for y in self.edges] if not x.defaults]
        self.edges = []
        k = len(living)
        if k > 0:
            for x in living:
                x.remove_edge(to=self)
                x.shock += residual / k

    def borrow_to_offset(self, residual):
        all_agents = self.model.schedule.agents
        viable_lenders = [agt for agt in all_agents if agt.externalAssets.value > 2 * residual]
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
