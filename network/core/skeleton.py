import random

import pandas as pd

from network.core.components import Agent, Model

power_law_graph = 'power_law_graph'
random_graph = 'erdos_renyi_graph'


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

    def add_edge(self, other, kind=1):
        node_from = self if kind == 1 else other
        node_to = other if kind == 1 else self
        node_from.edges.append(Edge(node_from, node_to, 1, 0.0))
        node_to.edges.append(Edge(node_from, node_to, 0, 0.0))


class Graph(Model):
    def __init__(self, name, init_agents, net_type, p):
        super().__init__()
        self.schedule = self.get_scheduler()
        random.shuffle(init_agents)
        self.init_agents = init_agents
        self.schedule.agents = []
        self.name = name
        self.N = len(init_agents)
        self.p = p
        getattr(self, net_type)()

    def new_node(self, unique_id):
        pass

    def erdos_renyi_graph(self):
        self.schedule.add_all([self.new_node(agent.unique_id) for agent in self.init_agents])
        for i in self.schedule.agents:
            subset = random_subset(self.schedule.agents, p=self.p, exc=i)
            for j in subset:
                i.add_edge(j, 1 if random.random() > 0.5 else 0)

    def power_law_graph(self):
        self.init_agents = sorted(self.init_agents, key=lambda x: x.capital)
        for agt in self.init_agents:
            node = self.new_node(agt.unique_id)
            if self.schedule.agents:
                subset = random_subset(self.schedule.agents, p=self.p, exc=None)
                for j in subset:
                    node.add_edge(j, 1)
            self.schedule.add(node)

    def _adj_mat(self):
        idx = [x.unique_id for x in self.init_agents]
        df = pd.DataFrame(data=0, columns=idx, index=idx)
        for nd in self.schedule.agents:
            for edg in nd.edges:
                df.loc[edg.i, edg.j] = 1
        return df

    def get_scheduler(self):
        pass


def random_subset(seq, p, exc):
    return [x for x in seq if x != exc and random.random() <= p]
