import random

from network.core.scheduler import StagedActivation
from network.core.skeleton import Graph, Node


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
            living = [x for x in [y.node_to for y in self.edges] if not x.defaults]
            k = len(living)
            if k > 0:
                for x in living:
                    x.shock += residual / k
        self.shock = 0.0


class FinNetwork(Graph):
    def __init__(self, name, init_agents, net_type, p):
        super().__init__(name, init_agents, net_type, p)
        self.disburse_exposure()

    def apply_shock(self, pos):
        unlucky = [x for x in self.schedule.agents if x.unique_id == pos][0]
        shock = unlucky.interbank_borrowing
        unlucky.apply_initial_shock(shock)

    def step(self):
        self.schedule.step()

    def new_node(self, unique_id):
        return [x for x in self.init_agents if x.unique_id == unique_id][0]

    def get_scheduler(self):
        return StagedActivation(self, stage_list=["deal_with_shock"])

    def disburse_exposure(self):
        for node in self.schedule.agents:
            debtors = [x for x in node.edges if x.kind == 1]
            tot_debt = sum([dbt.node_to.interbank_borrowing for dbt in debtors])
            creditors = [x for x in node.edges if x.kind == 0]
            tot_loan = sum([cr.node_to.interbank_borrowing for cr in creditors])
            for dbt in debtors:
                dbt.value = dbt.node_to.interbank_borrowing * node.interbankAssets / tot_debt

            for cdt in creditors:
                cdt.value = cdt.node_to.interbankAssets * node.interbank_borrowing / tot_loan


def random_subset(seq, p, exc):
    return [x for x in seq if x != exc and random.random() <= p]
