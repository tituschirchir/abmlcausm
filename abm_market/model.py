# model.py
import random
from mesa import Agent, Model
from mesa.time import RandomActivation
#from mesa.space import MultiGrid
#from mesa.datacollection import DataCollector
import numpy as np
from order import *


class MarketAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.order_count = 0
        self.wealth = 1000
        self.stock_preference = random.random() 
        #self.gamma = 0.5 #absloute risk averson
        #self.return_exp = 0.1
        #self.variance_exp = 0.2**2
        #self.stock_shares = ((1 + self.return_exp) - (1 + self.model.rf_rate)) / (self.gamma*self.variance_exp)
        self.stock_shares = 20
        self.stock_weight = (self.stock_shares * self.model.VWAP) / self.wealth
        self.cash = self.wealth - self.stock_shares * self.model.VWAP

    def step(self):
        self.recalculate_portfolio()
        #self.return_exp = self.caclulate_expectations()
        self.rebalance()

    def recalculate_portfolio(self):
        self.wealth = self.cash + self.stock_shares * self.model.VWAP
        self.stock_weight = (self.stock_shares * self.model.VWAP) / self.wealth

    # def caclulate_expectations(self):
    #     return_exp = self.return_exp + (random.random()-0.5)/100
    #     return return_exp

    def rebalance(self):
        shares_demand = self.calculate_share_demand()
        trade_shares = shares_demand - self.stock_shares
        trade_price = self.calculate_trade_price()
        self.order_trade(trade_shares, trade_price)

    def calculate_share_demand(self):
        self.stock_preference = self.stock_preference*0.9 + random.random()*0.1
        stock_demand = self.stock_preference*self.wealth
        # stock_demand = ((1 + self.return_exp)*self.model.VWAP
        #                 - (1 + self.model.rf_rate)*self.model.VWAP) / (self.gamma*self.variance_exp)
        shares_demand = stock_demand/self.model.VWAP
        return shares_demand

    def calculate_trade_price(self):
        return self.model.VWAP + (random.random()-0.5)

    def order_trade(self, num_shares, trade_price):
        if num_shares > 0:
            side = 'sell'
        else:
            side = 'buy'
            num_shares = -num_shares
        price = trade_price

        order = Order(self.unique_id, self.order_count, side, 'market',\
         num_shares, price, self.model.current_step)
        self.model.order_book.add_order(order)

        if self.order_count < 50:
            self.order_count +=1
        else:
            self.order_count = 0



class MarketModel(Model):
    """A model with some number of agents."""
    def __init__(self, N):#, stock_price, total_stock_shares, rf_rate):
        self.running = True
        self.num_agents = N
        self.total_stock_shares = 1000 #total_stock_shares
        self.rf_rate = 0.01 #rf_rate
        self.current_step = 0
        self.matched_trades = []
        self.VWAP = 10
        self.schedule = RandomActivation(self)
        self.order_book = OrderBook()

        # dd = {'step_id': [], 'price': [], 'volume': []} #add time
        # self.settled_trades = pd.DataFrame(data=dd)
        # self.settled_trades = self.settled_trades[['step_id', 'price', 'volume']]
        # self.settled_trades.loc[0] = [-1, 0, 0]

        # Create agents
        for i in range(self.num_agents):
            a = MarketAgent(i, self)
            self.schedule.add(a)

    	# self.datacollector = DataCollector(
     #    	#model_reporters={"Gini": compute_gini},
     #        model_reporters={"Gini": compute_gini},
     #    	agent_reporters={"Wealth": lambda a: a.wealth, "Cash": lambda a: a.cash, "Shares": lambda a: a.stock_shares})

    def step(self):
        '''Advance the model by one step.'''
        #self.datacollector.collect(self)
        self.schedule.step()
        self.matched_trades = self.order_book.get_matched_trades()
        self.settle()   #self?
        self.VWAP = self.calculate_VWAP()
        self.current_step += 1 

    def settle(self):
        for trade in self.matched_trades:
            agent = self.schedule.agents[trade.agent_id]
            agent.stock_shares += trade.quantity
            agent.cash -= trade.quantity * trade.price

    def calculate_VWAP(self):
        if not self.matched_trades: return self.VWAP
        trades = [x for x in self.matched_trades if x.quantity > 0]
        return sum(np.multiply([x.quantity for x in trades], [x.price for x in trades]))\
        /sum([x.quantity for x in trades])



# def compute_gini(model):
# 	agent_wealths = [agent.wealth for agent in model.schedule.agents]
# 	x = sorted(agent_wealths)
# 	N = model.num_agents
# 	B = sum(xi * (N-i) for i, xi in enumerate(x)) / (N * sum(x))
# 	return (1 + (1/N) - 2*B)

