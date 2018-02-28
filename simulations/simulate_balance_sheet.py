import random

import numpy as np


def n_rands(N):
    return np.asarray([random.random() for x in range(0, N)])


class NetworkItem:
    def __init__(self, id, N, bs_total, steepness):
        self.id = id
        self.N = N
        self.nodes = []
        self.initialize(steepness, bs_total, self.N)

    def initialize(self, steepness, bs_total, N):
        dist = sum([1 / (steepness ** x) for x in range(0, N)])
        bs = np.asarray([bs_total / dist / steepness ** x for x in range(0, N)])
        lev = n_rands(N) * 10 + 1
        ret = np.multiply(n_rands(N), np.asarray([(.5 if random.random() > 0.2 else -.25) for x in range(0, N)]))
        vol = [(abs(bs_total * ret[x] * np.sqrt(lev[x])) / (random.random() * bs[x] * 100)) for x in range(0, N)]
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
                           st_liabilities[x], lt_liabilities[x], deposits[x], equities[x]) for x in range(0, N)]
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


class Node:
    def __init__(self, id, mu, sigma, cash, st_assets, lt_assets, st_liabilities, lt_liabilities, deposits, equities):
        self._id = id
        self.mu = mu
        self.sigma = sigma
        self.cash = cash
        self.st_assets = st_assets
        self.lt_assets = lt_assets
        self.deposits = deposits
        self.lt_liabilities = lt_liabilities
        self.st_liabilities = st_liabilities
        self.equities = equities
        self.bank_borrow, self.bank_lend = 0.0, 0.0
        self.edges_to = []

    def add_edge(self, edge):
        self.edges_to.append(edge)
        self.bank_borrow += edge.value
        self.st_liabilities -= edge.value
        edge.node_to.bank_lend += edge.value
        edge.node_to.st_assets -= edge.value


class Edge:
    def __init__(self, to, value):
        self._id = to._id
        self.node_to = to
        self.value = value

    def __str__(self):
        return "{}=>{}".format(self._id, self.value)