import time

from simulations.original.Network import Network
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp


def run_net(j):
    networks = [Network(25, 0.3, 10000, 0.3, j) for k in range(100)]
    for nt in networks:
        nt.shock_network(1000)
    return np.mean([x.dead for x in networks])


result_list = []
def log_result(result):
    result_list.append(result)


if __name__ == '__main__':
    deaths = []
    t_start = time.time()
    probs = np.arange(0.0, 0.20, 0.005)
    pool = mp.Pool(processes=36)
    for i in probs:
        pool.apply_async(run_net, args=(i,), callback=log_result)
    pool.close()
    pool.join()
    print("T1:{}".format(time.time()-t_start))
    deaths = result_list
    plt.plot(probs, deaths)
    s = np.pi * (15 * np.random.rand(len(probs))) ** 2
    colors = np.random.rand(len(probs))
    plt.plot(probs, deaths, 'r--')
    plt.xlabel("Probs")
    plt.ylabel("Deaths")
    plt.show()
