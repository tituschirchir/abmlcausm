from simulations.sim_network import Network
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    n = 100
    net = Network(1, n, 100000, 1.05)
    for i in range(0, 365):
        net.step()
    print([x.sigma for x in net.schedule.agents])
    print([x._id for x in net.schedule.agents if not x.is_alive])

    df = pd.DataFrame()
    for i in range(0, n):
        df[i] = net.schedule.agents[i].equity_history
    df.plot()
    plt.show()
