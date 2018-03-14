import datetime
import random

import pandas as pd

from abm.bank_agent import Bank
from network.core.scheduler import StagedActivation
from network.core.skeleton import Graph
from products.derivatives import Derivative
from products.positions import Position


class FinancialModel(Graph):
    def __init__(self, data, stock_data, network_type):
        super().__init__(network_type, n=data.shape[1] - 1)
        self.running = True
        self.shock = 0.0
        self.to_shock = True
        self.bailed_out = []
        self.dead = []
        self.date = datetime.date.today()
        self.num_agents = data.shape[1] - 1
        self.schedule = StagedActivation(self, stage_list=["settle_contracts", "equity_change"])
        # Create agents
        self.initialize_model(data, stock_data)
        self.all_agents = pd.DataFrame(columns=[x.ticker for x in self.schedule.agents])

    def initialize_model(self, data, stock_data):
        unique_id = 0
        for st in data.columns:
            if st == 'Category':
                break
            bank = Bank(unique_id, st, data[[st, 'Category']], stock_data.ix[st], model=self)
            self.schedule.add(bank)
            unique_id += 1
        self.initialize_adjacency_matrix()
        # self.add_derivatives()

    def step(self):
        # Shock!
        agents = self.schedule.agents
        living = [x for x in agents if x.state in ["Alive", "Infected"]]
        if self.shock == 0.0 and living:
            unlucky_agent = random.choice(living)
            if random.random() > 0.95:
                unlucky_agent.shock_quantity = 100.0
                unlucky_agent.state = 'Infected'
                print("Unlucky agent is {}".format(unlucky_agent.ticker))
        self.prep_for_shock()
        self.schedule.step()
        self.shock = sum([x.shock_quantity for x in agents])
        self.dead = [x.ticker for x in agents if x.state == "Dead"]
        self.date += datetime.timedelta(days=1)
        df = pd.DataFrame(columns=[x.ticker for x in agents])
        df.loc[self.date] = [x.liquidity() for x in agents]
        self.all_agents = self.all_agents.append(df)
        for x in agents:
            x.model = self

    def prep_for_shock(self):
        for x in self.schedule.agents:
            if x.shock_quantity > 0:
                x.to_shock = True
                break

    def total_bad_debt(self):
        return sum([v.bad_debt for v in self.schedule.agents])

    def add_derivatives(self):
        for x in self.schedule.agents:
            if x.neighbors_to:
                leverage = random.randint(1, 10)
                num = len(x.neighbors_to)
                value = x.cash_A / (4 * num)
                premium = 2 * value / 100
                for y in x.neighbors_to:
                    contract = Derivative(name="CDS", premium=premium, value=value, leverage=leverage)
                    x.contracts.append(Position(contract, 1, long=True, counter_party=y))
                    y.contracts.append(Position(contract, 1, long=False, counter_party=x))
