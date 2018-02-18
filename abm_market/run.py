from model import *
# import numpy as np
# import matplotlib.pyplot as plt

model = MarketModel(100000)
for i in range(30):
    model.step()
    print(model.VWAP)