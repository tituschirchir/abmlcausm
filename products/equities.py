import math

import numpy as np


class Stock:
    def __init__(self, S, mu, std, dt):
        self.mu = mu
        self.S = S
        self.sigma = std
        self.dt = dt

    def evolve(self):
        pt_a = (self.mu - (self.sigma ** 2) / 2) * self.dt
        pt_b = self.sigma * math.sqrt(self.dt) * np.random.randn()
        self.S = self.S * math.exp(pt_a + pt_b)
