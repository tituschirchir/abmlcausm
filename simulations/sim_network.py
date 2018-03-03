import random

import numpy as np
import pandas as pd

from network.components import Model
from network.scheduler import StagedActivation
from simulations.sim_bank import Edge, Node


def n_rands(N):
    return np.asarray([random.random() for x in range(0, N)])


class Network(Model):
    def __init__(self, id, N, bs_total, steepness):
        super().__init__()
        self.running = True
        self.schedule = StagedActivation(self, stage_list=["equity_change", 'spread_shock'])
        self.id = id
        self.N = N
        self.nodes = []
        self.initialize(steepness, bs_total, self.N)
        for nd in self.nodes:
            self.schedule.add(nd)

    def step(self):
        agents = self.schedule.agents
        if random.random() > .9:
            shock = 2500
            chosen = random.choice(agents)
            chosen.shock += shock
            chosen.cash -= chosen.shock
        self.schedule.step()

    def initialize(self, steepness, bs_total, N):
        dist = sum([1 / (steepness ** x) for x in range(0, N)])
        bs = np.asarray([bs_total / dist / steepness ** x for x in range(0, N)])
        lev = n_rands(N) * 10 + 1
        ret = np.multiply(n_rands(N), np.asarray([(.5 if random.random() > 0.2 else -.25) for x in range(0, N)]))
        vol = [np.sqrt(abs(bs[x] * ret[x]) / (random.random() * bs_total)) for x in range(0, N)]
        equities = np.divide(bs, lev)
        liabilities = bs - equities
        deposits = np.divide(liabilities, n_rands(N) * 7 + 1)
        liability_ratio = n_rands(N)
        st_liabilities = np.multiply(liability_ratio, liabilities - deposits)
        lt_liabilities = liabilities - deposits - st_liabilities

        current_ratio = abs(np.multiply(np.divide(bs, st_liabilities + deposits), n_rands(N)) - lev / 10) + 1
        st_assets = np.multiply(current_ratio, st_liabilities + deposits)

        cash_and_equivalents = st_assets / ((n_rands(N) + 1) * 5)
        st_assets = (bs - cash_and_equivalents) / ((n_rands(N) + 1) * 5)
        lt_assets = bs - st_assets - cash_and_equivalents

        self.nodes = [Node(x, ret[x], vol[x], cash_and_equivalents[x], st_assets[x], lt_assets[x],
                           st_liabilities[x], lt_liabilities[x], deposits[x], equities[x], self) for x in range(0, N)]
        self.initialize_edges()

    def initialize_edges(self):
        all_liabilities = sum([x.st_liabilities + x.lt_liabilities for x in self.nodes])
        all_assets = sum([x.lt_assets + x.st_assets for x in self.nodes])
        self.nodes = sorted(self.nodes, key=lambda x: x.st_liabilities + x.lt_liabilities, reverse=False)
        fracts = [(x.st_liabilities + x.lt_liabilities) / all_liabilities for x in self.nodes]
        lending_prob = [(x.lt_assets + x.st_assets) / all_assets for x in self.nodes]
        fracts = fracts / fracts[self.N - 1]
        i = 0
        for nd in self.nodes:
            cc = np.random.choice(self.nodes, random.randint(0, int(fracts[i] * self.N)), p=lending_prob, replace=False)
            tot_assets = sum([x.st_assets + x.lt_assets for x in cc if x != nd])
            for x in cc:
                if x != nd:
                    edge = Edge(x, (nd.st_liabilities + nd.lt_liabilities) * (x.lt_assets + x.st_assets) / tot_assets)
                    nd.add_edge(edge)
            i += 1

    def get_loan_matrix(self):
        loan_matrix = pd.DataFrame(data=0.0, index=range(0, self.N), columns=range(0, self.N))
        for nd in self.nodes:
            for edge in nd.edges_to:
                loan_matrix.loc[nd._id, edge.node_to._id] = edge.value
        return loan_matrix
