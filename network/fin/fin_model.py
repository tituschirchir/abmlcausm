import random

from network.core.scheduler import StagedActivation
from network.core.skeleton import Graph
from structures.shock_absorber import ExposureAllocator


class FinNetwork(Graph):
    def __init__(self, name, init_agents, net_type, p, k, m):
        super().__init__(name, init_agents, net_type, p, k, m)
        allocator = ExposureAllocator(self.schedule.agents)
        allocator.disburse_exposure()

    def apply_shock(self, pos):
        unlucky = self.get_agent(pos)
        if unlucky:
            shock = unlucky.capital.value * random.random()
            unlucky.apply_initial_shock(shock)

    def step(self):
        if random.random() > 0.95:
            self.apply_shock(random.randint(0, self.N))
        self.schedule.step()

    def get_scheduler(self):
        return StagedActivation(self, no_of_steps=2)

    def initialize_model(self):
        for x in self.schedule.agents:
            x.model = self