import multiprocessing as mp
import time
import matplotlib.pyplot as plt
import numpy as np
import network.core.skeleton as ns
from helpers.agent_fisher import get_agents
from network.fin.fin_model import FinNetwork


def per_probability(count, n, pos, arange):
    all_deads = []
    for k in arange:
        networks = [FinNetwork("Net {}".format(y), get_agents(n), net_type=ns.power_law_graph, p=k) for y in
                    range(count)]
        deads = []
        for net in networks:
            net.apply_shock(pos)
            for i in range(10):
                net.step()
            deads.append(sum([1 for x in net.schedule.agents if x.defaults]))
        all_deads.append(sum(deads) / count)
    return pos, all_deads


result_list = {}


def log_result(result):
    k, v = result
    result_list[k] = v


def build_graph(model_):
    import networkx as nx
    model_graph = nx.DiGraph()
    for node in model_.schedule.agents:
        model_graph.add_node(node)
        for edge in node.edges:
            model_graph.add_edge(edge.node_from, edge.node_to)
    return model_graph


if __name__ == '__main__':
    t_start = time.time()
    # pool = mp.Pool(processes=4)
    # arange = np.arange(0.0, 1.0, 0.025)
    # for x in range(29):
    #     pool.apply_async(per_probability, args=(2, 29, x, arange,), callback=log_result)
    # pool.close()
    # pool.join()
    # for k, v in result_list.items():
    #     plt.plot(arange, v)

    fin_network = FinNetwork("Net 1", get_agents(10), net_type=ns.power_law_graph, p=.5)
    gg = build_graph(fin_network)
    print("T1:{}".format(time.time() - t_start))
    plt.show()
