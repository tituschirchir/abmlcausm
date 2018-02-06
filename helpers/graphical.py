import random

from mesa import Agent, Model
import pandas as pd
import networkx as nx


class Vertex(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.neighbors_to = []
        self.neighbors_from = []

    def add_neighbor(self, neighbor, direction=0):
        if direction == 1:
            self.neighbors_to.append(neighbor)
            neighbor.neighbors_from.append(self)
        else:
            self.neighbors_from.append(neighbor)
            neighbor.neighbors_to.append(self)

    def solvent_neighbors_to(self):
        return [x for x in self.neighbors_to if x.state in ['Alive', 'Infected']]

    def neighbor_as_list(self):
        return [x.ticker for x in self.neighbors_to]


class Graph(Model):
    def __init__(self, network_type, n):
        super().__init__()
        if network_type == "Erdos":
            self.graph_model = nx.gnp_random_graph(n, p=.3)
        else:
            self.graph_model = nx.barabasi_albert_graph(n, m=1)
        self.graph = nx.DiGraph()
        self.adjacency_matrix = []

    def initialize_adjacency_matrix(self):
        colnames = [x.ticker for x in self.schedule.agents]
        self.adjacency_matrix = pd.DataFrame(0, columns=colnames, index=colnames)
        for entity in self.schedule.agents:
            self.graph.add_node(entity.ticker, bank=entity, weight=entity.equity)

        for i in range(0, len(self.schedule.agents)):
            adjs = list(self.graph_model._adj[i].keys())
            tk = self.schedule.agents[i]
            for j in adjs:
                other_agent = self.schedule.agents[j]
                self.adjacency_matrix.loc[tk.ticker, other_agent.ticker] = 1
                self.graph.add_edge(tk.ticker, other_agent.ticker)
                tk.add_neighbor(other_agent, 1)
