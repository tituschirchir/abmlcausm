import random

import networkx as nx
import numpy as np
from simulations.original.bank import Bank
import pandas as pd


class Network:
    def __init__(self, N, p, A, theta, gamma):
        self.marketLoss = 0.0
        self.N = N
        self.p = p
        self.count = 1
        self.links = 0
        self.A = A
        self.theta = theta
        self.gamma = gamma
        self.banks = [Bank("B{}".format(x)) for x in range(0, N)]
        self.graph_model = nx.extended_barabasi_albert_graph(n=N, m=2, p=.4, q=.4, seed=None)
        #self.graph_model = nx.erdos_renyi_graph(n=N, p=p, directed=False)
        self.adj_mat = pd.DataFrame(data=0, columns=range(self.N), index=range(self.N))
        self.initialize_adjacency_matrix()
        self.initiate_network()

    def initialize_adjacency_matrix(self):
        adjacencies = list(self.graph_model._adj.values())
        for i in range(0, self.N):
            adjs = adjacencies[i]
            for j in adjs.keys():
                self.banks[i].add_counter_party(self.banks[j])

        for i in range(self.N):
            for j in range(self.N):
                if i != j and self.banks[j] in self.banks[i].counter_parties:
                    if self.banks[i] in self.banks[j].counter_parties and self.adj_mat.loc[j, i] == 1:
                        self.adj_mat.loc[i, j] = 0
                    else:
                        self.adj_mat.loc[i, j] = 1
                        self.links += 1

    def initiate_network(self):
        e_bk = 0.0 if self.links == 0 else self.theta * self.A / self.links

        for i in range(self.N):
            self.banks[i].interbankAssets = sum(self.adj_mat.loc[i]) * e_bk
            self.banks[i].interbank_borrowing = sum(self.adj_mat[i]) * e_bk
            excessAssets = self.A / self.N - self.banks[i].interbankAssets
            self.banks[i].externalAssets = excessAssets if excessAssets >= 0 else 0.0
            self.banks[i].capital = (self.banks[i].interbankAssets + self.banks[i].externalAssets) * self.gamma
            self.banks[i].customer_deposits = self.banks[i].externalAssets + self.banks[i].interbankAssets - self.banks[
                i].capital - self.banks[i].interbank_borrowing

    def get_total_shock(self):
        return sum([x.shock for x in self.banks])

    def shock_network(self, shock):
        unlucky = self.banks[3]
        unlucky.apply_initial_shock(shock)
        while self.get_total_shock() > 0.0:
            next_v = random.choice([x for x in self.banks if x.shock > 0.0])
            next_v.deal_with_shock()
            self.count += 1
        self.dead = len([x.name for x in self.banks if x.defaults])
