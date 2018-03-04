import random
import numpy as np
from network.components import Agent, Model
from network.scheduler import RandomActivation
from .order import Order, OrderBook, Stock


class MarketAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.order_count = 0
        self.wealth = 1000
        self.stock_preference = random.random()
        self.stock_shares = 50 
        self.stock_weight = (self.stock_shares * self.model.stock.price) / self.wealth
        self.cash = self.wealth - self.stock_shares * self.model.stock.price

    def step(self):
        self.recalculate_portfolio()
        self.rebalance()

    def recalculate_portfolio(self):
        self.wealth = self.cash + self.stock_shares * self.model.stock.price
        self.stock_weight = (self.stock_shares * self.model.stock.price) / self.wealth

    def rebalance(self):
        shares_demand = self.calculate_share_demand()
        trade_shares = shares_demand - self.stock_shares
        trade_price = self.calculate_trade_price()
        self.order_trade(trade_shares, trade_price)

    def calculate_share_demand(self):
        self.stock_preference = self.stock_preference * 0.9 + random.random() * 0.1
        stock_demand = self.stock_preference * self.wealth
        shares_demand = stock_demand / self.model.stock.price
        return shares_demand

    def calculate_trade_price(self):
        return self.model.stock.price + (random.random() - 0.5)

    def order_trade(self, num_shares, trade_price):
        if num_shares > 0:
            side = 'sell'
        else:
            side = 'buy'
            num_shares = -num_shares
        price = trade_price

        order = Order(self.unique_id, self.order_count, side, 'market', num_shares, price, self.model.current_step)
        self.model.order_book.add_order(order)

        if self.order_count < 50:
            self.order_count += 1
        else:
            self.order_count = 0


class MarketModel(Model):
    def __init__(self, N):
        super().__init__()
        self.running = True
        self.num_agents = N
        self.rf_rate = 0.01
        self.current_step = 0
        self.matched_trades = []
        self.stock = Stock(ticker="STK", model=self, initial_price=10, outstading_shares=1000,
            equil_dividend=0.2, divident_vol=0.2)
        self.schedule = RandomActivation(self)
        self.order_book = OrderBook()
        for i in range(self.num_agents):
            a = MarketAgent(i, self)
            self.schedule.add(a)

    def step(self):
        self.schedule.step()
        self.matched_trades = self.order_book.get_matched_trades()
        self.settle()
        self.current_step += 1
        self.stock.update_price(self.current_step, self.calculate_VWAP())


    def settle(self):
        for trade in self.matched_trades:
            agent = self.schedule.agents[trade.agent_id]
            agent.stock_shares += trade.quantity
            agent.cash -= trade.quantity * trade.price

    def calculate_VWAP(self):
        if not self.matched_trades: return self.stock.price
        trades = [x for x in self.matched_trades if x.quantity > 0]
        return sum(np.multiply([x.quantity for x in trades], [x.price for x in trades])) / sum(
            [x.quantity for x in trades])
