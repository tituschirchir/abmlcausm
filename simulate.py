from simulations.sim_network import Network
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    n = 100
    steepnesses = np.arange(1.0, 3.0, 0.1)
    deaths = []
    for stp in steepnesses:
        nets = [Network(x, n, 100000, 1.05) for x in range(0, 100)]
        deads = []
        for net in nets:
            for i in range(0, 30):
                net.step()
            deads.append(sum([1 for x in net.schedule.agents if not x.is_alive]))
        deaths.append(np.mean(deads))
    plt.plot(steepnesses, deaths)
    plt.show()
