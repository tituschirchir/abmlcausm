from model import *
# import numpy as np
# import matplotlib.pyplot as plt
from mesa.batchrunner import BatchRunner

model = MarketModel(10)
for i in range(25):
    model.step()
    print(model.VWAP)

# gini = model.datacollector.get_model_vars_dataframe()
# gini.plot()
# plt.show()

# agent_wealth = model.datacollector.get_agent_vars_dataframe()
# end_wealth = agent_wealth.xs(99, level="Step")["Wealth"]
# end_wealth.hist(bins = range(agent_wealth.Wealth.max()+1))
# plt.show()

# one_agent_wealth = agent_wealth.xs(14, level="AgentID")
# one_agent_wealth.Wealth.plot()
# plt.show()

# fixed_params = {"width": 10, "height": 10}
# variable_params = {"N": range(10, 500, 10)}

# batch_run = BatchRunner(MoneyModel, 
#                        fixed_parameters=fixed_params,
#                        variable_parameters=variable_params,
#                        iterations=5,
#                        max_steps=100,
#                        model_reporters={"Gini": compute_gini})
# batch_run.run_all()
# run_data = batch_run.get_model_vars_dataframe()
# run_data.head()
# plt.scatter(run_data.N, run_data.Gini)
# plt.show()
