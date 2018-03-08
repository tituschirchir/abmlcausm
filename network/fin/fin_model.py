from network.core.scheduler import StagedActivation
from network.core.skeleton import Graph


class FinNetwork(Graph):
    def __init__(self, name, init_agents, net_type, p, k, m):
        super().__init__(name, init_agents, net_type, p, k, m)
        self.life_history = [self.N]
        self.disburse_exposure()

    def apply_shock(self, pos):
        unlucky = self.get_agent(pos)
        shock = unlucky.capital * 5 / 2
        unlucky.apply_initial_shock(shock)

    def step(self):
        self.schedule.step()
        self.life_history.append(len([x for x in self.schedule.agents if not x.defaults]))

    def get_scheduler(self):
        return StagedActivation(self, stage_list=["deal_with_shock"])

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
