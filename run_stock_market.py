from abm_market.model import MarketModel

model = MarketModel(100000)
for i in range(30):
    model.step()
    print(model.VWAP)
