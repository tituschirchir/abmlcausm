import random

import pandas as pd

from network.core.components import Agent, Model

power_law_cluster_graph = 'power_law_cluster_graph'
barabasi_albert_graph = 'barabasi_albert_graph'
random_graph = 'erdos_renyi_graph'
newman_watts_strogatz_graph = 'newman_watts_strogatz_graph'
watts_strogatz_graph = 'watts_strogatz_graph'
all_nets = [power_law_cluster_graph, barabasi_albert_graph, random_graph, watts_strogatz_graph,
            newman_watts_strogatz_graph]


class Edge:
    def __init__(self, fro, to, kind, value):
        self.kind = kind
        self.node_to = to
        self.node_from = fro
        self.i = fro.unique_id
        self.j = to.unique_id
        self.value = value


class Node(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.edges = []

    def add_edge(self, other):
        self.edges.append(Edge(self, other, 0, 0.0))


class Graph(Model):
    def __init__(self, name, init_agents, net_type, p=.5, k=3, m=2):
        super().__init__()
        self.schedule = self.get_scheduler()
        self.init_agents = init_agents
        self.schedule.agents = []
        self.name = name
        self.N = len(init_agents)
        self.p = p
        self.k = k
        self.m = m
        self.initialize_graph(getattr(self, net_type)())

    def new_node(self, unique_id):
        pass

    def erdos_renyi_graph(self):
        import networkx as nx
        return nx.fast_gnp_random_graph(n=self.N, p=self.p)._adj

    def barabasi_albert_graph(self):
        import networkx as nx
        return nx.barabasi_albert_graph(n=self.N, m=self.m)._adj

    def power_law_cluster_graph(self):
        import networkx as nx
        return nx.powerlaw_cluster_graph(n=self.N, m=self.m, p=self.p)._adj

    def watts_strogatz_graph(self):
        import networkx as nx
        return nx.watts_strogatz_graph(n=self.N, k=self.k, p=self.p)._adj

    def newman_watts_strogatz_graph(self):
        import networkx as nx
        return nx.newman_watts_strogatz_graph(n=self.N, k=self.k, p=self.p)._adj

    def agent_by_id(self, id):
        return [x for x in self.schedule.agents if x.unique_id == id][0]

    def initialize_graph(self, adj):
        self.schedule.add_all([self.new_node(agent.unique_id) for agent in self.init_agents])
        self.schedule.agents = sorted(self.schedule.agents, key=lambda x: x.interbankAssets)
        for i in self.schedule.agents:
            neighbors = list(adj.get(i.unique_id).keys())
            for x in neighbors:
                i.add_edge(self.agent_by_id(x))

    def _adj_mat(self):
        idx = [x.unique_id for x in self.schedule.agents]
        df = pd.DataFrame(data=0, columns=idx, index=idx)
        for nd in self.schedule.agents:
            for edg in nd.edges:
                df.loc[edg.i, edg.j] = 1
        return df

    def get_scheduler(self):
        pass


def random_subset(seq, p, exc):
    return [x for x in seq if x != exc and random.random() <= p]
