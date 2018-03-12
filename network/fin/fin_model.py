import random

from network.core.scheduler import StagedActivation
from network.core.skeleton import Graph


class FinNetwork(Graph):
    def __init__(self, name, init_agents, net_type, p, k, m):
        super().__init__(name, init_agents, net_type, p, k, m)
        self.life_history = [self.schedule.agents[0].stock.S]
        self.disburse_exposure()

    def apply_shock(self, pos):
        unlucky = self.get_agent(pos)
        if unlucky:
            shock = unlucky.capital * .25
            unlucky.apply_initial_shock(shock)

    def step(self):
        if random.random() > 0.75:
            self.apply_shock(random.randint(0, self.N))
        self.schedule.step()

    def get_scheduler(self):
        return StagedActivation(self, no_of_steps=2)

    def initialize_model(self):
        for x in self.schedule.agents:
            x.model = self

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
