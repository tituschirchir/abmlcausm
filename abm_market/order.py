class Order:
    def __init__(self, agent_id, order_id, side, order_type, quantity, price, time):
        self.order_id = order_id
        self.agent_id = agent_id
        self.side = side
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.time = time


class Trade:
    def __init__(self, agent_id, quantity, price, time):
        self.agent_id = agent_id
        self.quantity = quantity
        self.price = price
        self.time = time


class Stock:
    def __init__(self, ticker, model, initial_price=10, outstading_shares=1000,
                 equil_dividend=0.2, divident_vol=0.2):
        self.ticker = ticker
        self.model = model
        self.price = initial_price
        self.outstading_shares = outstading_shares
        self.price_hist = {0: initial_price}
        self.market_cap = self.price * outstading_shares
        self.equil_dividend = equil_dividend
        self.divident_vol = divident_vol
        self.dividend = equil_dividend
        self.price_MA_5 = initial_price
        self.price_MA_10 = initial_price
        self.price_MA_50 = initial_price
        self.price_MA_100 = initial_price
        self.price_MA_5_hist = {0: initial_price}
        self.price_MA_10_hist = {0: initial_price}
        self.price_MA_50_hist = {0: initial_price}
        self.price_MA_100_hist = {0: initial_price}
        self.PID_ratio = (self.price * self.model.rf_rate) / self.dividend

    def update_price(self, time_step, new_price):
        self.price_hist[time_step] = new_price
        self.price = new_price
        self.market_cap = self.price * self.outstading_shares
        self.price_MA_5 = self.calculate_MA(5, time_step)
        self.price_MA_10 = self.calculate_MA(10, time_step)
        self.price_MA_50 = self.calculate_MA(50, time_step)
        self.price_MA_100 = self.calculate_MA(100, time_step)
        self.price_MA_5_hist[time_step] = self.price_MA_5
        self.price_MA_10_hist[time_step] = self.price_MA_10
        self.price_MA_50_hist[time_step] = self.price_MA_50
        self.price_MA_100_hist[time_step] = self.price_MA_100

    def update_dividend(self):
        self.dividend = self.equil_dividend + \
                        0.95 * (self.dividend - self.equil_dividend) + random.gauss(0, self.divident_vol)
        self.PID_ratio = (self.price * self.model.rf_rate) / dividend

    def calculate_MA(self, periods, time_step):
        if periods < time_step - 1:
            return sum([v for k, v in self.price_hist.items()][-periods:]) / periods
        else:
            return sum([v for k, v in self.price_hist.items()]) / (time_step + 1)

        # lat = [v for k, v in self.price_hist.items()]
        # den = (self.model.current_step + 1)
        # if periods < self.model.current_step:
        #     lat = lat[-periods:]
        #     den = periods
        # return sum(lat) / den


class OrderBook:
    def __init__(self):
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)

    def remove_order(self, agent_id, order_id):
        self.orders = [x for x in self.orders if x.order_id != order_id and x.agent_id != agent_id]

    def age_all_orders(self):
        for order in self.orders:
            order.time += 1

    def get_matched_trades(self, tolerance=0.1):
        matched_trades = []
        sells = [x for x in self.orders if x.side == 'sell']
        buys = [x for x in self.orders if x.side == 'buy']
        if buys and sells:
            sells = sorted(sells, key=lambda x: (x.price, x.quantity), reverse=False)
            buys = sorted(buys, key=lambda x: (x.price, x.quantity), reverse=True)

            for sell in sells:
                for buy in buys:
                    if abs(sell.price - buy.price) > tolerance:
                        break
                    else:
                        agreed_price = (sell.price + buy.price) / 2

                        if sell.quantity > buy.quantity:
                            n_traded_shares = buy.quantity
                            matched_trades.append(Trade(buy.agent_id, n_traded_shares, agreed_price, 0))
                            matched_trades.append(Trade(sell.agent_id, -n_traded_shares, agreed_price, 0))

                            self.remove_order(buy.agent_id, buy.order_id)
                            sell.quantity -= n_traded_shares
                            self.remove_order(sell.agent_id, sell.order_id)
                            self.add_order(Order(sell.agent_id, sell.order_id, sell.side, \
                                                 sell.order_type, sell.quantity, sell.price, sell.time))
                            # remove buy
                            buys = [x for x in buys if x.order_id != buy.order_id and x.agent_id != buy.order_id]

                        if sell.quantity < buy.quantity:
                            n_traded_shares = sell.quantity
                            matched_trades.append(Trade(buy.agent_id, n_traded_shares, agreed_price, 0))
                            matched_trades.append(Trade(sell.agent_id, -n_traded_shares, agreed_price, 0))

                            self.remove_order(sell.agent_id, sell.order_id)
                            buy.quantity -= n_traded_shares
                            self.remove_order(buy.agent_id, buy.order_id)
                            self.add_order(Order(buy.agent_id, buy.order_id, buy.side, \
                                                 buy.order_type, buy.quantity, buy.price, buy.time))
                            break

                        if sell.quantity == buy.quantity:
                            n_traded_shares = sell.quantity
                            matched_trades.append(Trade(buy.agent_id, n_traded_shares, agreed_price, 0))
                            matched_trades.append(Trade(sell.agent_id, -n_traded_shares, agreed_price, 0))

                            self.remove_order(buy.agent_id, buy.order_id)
                            self.remove_order(sell.agent_id, sell.order_id)
                            # remove buy
                            buys = [x for x in buys if x.order_id != buy.order_id and x.agent_id != buy.order_id]
                            break

                        # self.settled_trades.loc[max(self.settled_trades.index)+1] = \
                        # [self.current_step, agreed_price, n_traded_shares]
        return matched_trades
