import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import pandas as pd

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)


def animated(i):
    pull_data = pd.read_csv('sample.csv')
    ax1.clear()
    ax1.plot(pull_data)


ani = animation.FuncAnimation(fig, animated)
plt.show()
