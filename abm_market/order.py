class Order:
    def __init__(self, agent_id, order_id, order_type, n_shares, price, order_age):
        self.order_id = order_id
        self.agent_id = agent_id
        self.order_type = order_type
        self.n_shares = n_shares
        self.price = price
        self.order_age = order_age


class OrderList:
    def __init__(self):
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)

    def remove_order(self, agent_id, order_id):
        self.orders = [x for x in self.orders if x.order_id != order_id and x.agent_id != agent_id]

    def age_all_orders(self):
        for order in self.orders:
            order.order_age += 1

    def match_orders(self):
        asks = [x for x in self.orders if x.order_type == 0]
        bids = [x for x in self.orders if x.order_type == 1]




