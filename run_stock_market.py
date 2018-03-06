import network.core.skeleton as ns
from helpers.agent_fisher import get_agents
from network.fin.fin_model import FinNetwork

fin_network = FinNetwork("Net 1", get_agents(10), net_type=ns.power_law_graph, p=.4)

for nd in fin_network.schedule.agents:
    print("{} (${})-{}".format(nd.unique_id, nd.interbankAssets, [x.node_to.unique_id for x in nd.edges]))

print(fin_network._adj_mat())
