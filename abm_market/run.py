from abm_market.model import *
# import numpy as np
# import matplotlib.pyplot as plt

model = MarketModel(10)
for i in range(25):
    model.step()
    print(model.VWAP)