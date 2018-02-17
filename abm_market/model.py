# model.py
import random
from mesa import Agent, Model
from mesa.time import RandomActivation
#from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import pandas as pd
import numpy as np


class MarketAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
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
            order_type = 1 #ask
        else:
            order_type = 0 #bid
            num_shares = -num_shares
        price = trade_price
        #print((max(self.model.orders.index)+1))
        # make below a pd series
        self.model.orders.loc[max(self.model.orders.index)+1] = [self.unique_id, order_type, num_shares, price]



class MarketModel(Model):
    """A model with some number of agents."""
    def __init__(self, N):#, stock_price, total_stock_shares, rf_rate):
        self.running = True
        self.num_agents = N
        self.total_stock_shares = 1000 #total_stock_shares
        self.rf_rate = 0.01 #rf_rate
        self.current_step = 0
        self.VWAP = 10
        self.schedule = RandomActivation(self)

        d = {'agent_id': [], 'order_type': [], 'n_shares': [], 'price': []} #add time
        self.orders = pd.DataFrame(data=d)
        self.orders = self.orders[['agent_id', 'order_type', 'n_shares', 'price']]
        self.orders.loc[0] = [-1, -1, -1, -1]

        dd = {'step_id': [], 'price': [], 'volume': []} #add time
        self.settled_trades = pd.DataFrame(data=dd)
        self.settled_trades = self.settled_trades[['step_id', 'price', 'volume']]
        self.settled_trades.loc[0] = [-1, 0, 0]

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
        self.settle()   #self?
        self.VWAP = self.calculate_VWAP()
        self.current_step += 1 

    def calculate_VWAP(self):
        curr_step_trades = self.settled_trades[self.settled_trades.step_id == self.current_step]
        if curr_step_trades.empty: return self.VWAP
        return sum(np.multiply(curr_step_trades.volume, curr_step_trades.price))/sum(curr_step_trades.volume)


    def settle(self):
        
        bids = self.orders[self.orders['order_type'] == 0]
        asks = self.orders[self.orders['order_type'] == 1]
        if bids.empty or asks.empty: return
        #rank asks by price first and then by number of shares
        asks.sort_values(by='n_shares', ascending=False)
        asks['price_rank'] = asks.rank(axis=0, method='first')['price']

        for i in range(1, int(max(asks['price_rank']))):
            ask = asks[asks['price_rank'] == i]
            ask_price = float(ask['price'])
            ask_shares = float(ask['n_shares'])
            #rank asks by price first and then by number of shares
            bids.sort_values(by='n_shares', ascending=False)
            bids['price_rank'] = bids.rank(axis=0, method='first')['price']
           # bids.index = bids.price_rank

            for j in range(1, int(max(bids['price_rank']))):
                bid = bids[bids['price_rank'] == j]
                bid_price = float(bid['price'])
                bid_shares = float(bid['n_shares'])

                if abs(ask_price - bid_price) < 0.03:
                    agreed_price = (ask_price + bid_price)/2
                    n_traded_shares = 0
                    buyer = self.schedule.agents[int(bid['agent_id'])]
                    seller = self.schedule.agents[int(ask['agent_id'])]

                    if ask_shares > bid_shares:
                        n_traded_shares = bid_shares
                        buyer.stock_shares -= n_traded_shares
                        buyer.cash += n_traded_shares * agreed_price
                        seller.stock_shares += n_traded_shares
                        seller.cash -= n_traded_shares * agreed_price

                        self.orders.drop(self.orders.index[bid.index])
                        ask['n_shares'] -= n_traded_shares

                    if ask_shares < bid_shares:
                        n_traded_shares = ask_shares
                        buyer.stock_shares -= n_traded_shares
                        buyer.cash += n_traded_shares * agreed_price
                        seller.stock_shares += n_traded_shares
                        seller.cash -= n_traded_shares * agreed_price

                        self.orders.drop(self.orders.index[ask.index])
                        bids.loc[bids.index[bids.price_rank == j]]['n_shares'] = \
                        bid.n_shares.values[0] - n_traded_shares
                        break

                    if ask_shares == bid_shares:
                        n_traded_shares = ask_shares
                        buyer.stock_shares -= n_traded_shares
                        buyer.cash += n_traded_shares * agreed_price
                        seller.stock_shares += n_traded_shares
                        seller.cash -= n_traded_shares * agreed_price

                        self.orders.drop(self.orders.index[ask.index])
                        self.orders.drop(self.orders.index[bid.index])
                        break

                    self.settled_trades.loc[max(self.settled_trades.index)+1] = \
                    [self.current_step, agreed_price, n_traded_shares]



def compute_gini(model):
	agent_wealths = [agent.wealth for agent in model.schedule.agents]
	x = sorted(agent_wealths)
	N = model.num_agents
	B = sum(xi * (N-i) for i, xi in enumerate(x)) / (N * sum(x))
	return (1 + (1/N) - 2*B)

