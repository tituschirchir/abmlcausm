from simulations.original.Network import Network
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    deaths = []
    probs = np.arange(0.05, 0.5, 0.025)
    for i in probs:
        dds = []
        for k in range(1000):
            dds.append(Network(25, .3, 10000, i, 0.1).dead)
        deaths.append(np.mean(dds))
    plt.plot(probs, deaths)
    plt.show()
