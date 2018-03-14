import numpy as np

import structures.constants as bst

assets = "Assets"
external = "External"
liquid = "Liquid"
interbank = "Interbank"
illiquid = "Illiquid"
deposits_etc = "Deposits and Others"
liab = "Liabilities"


class TreeNode:
    def __init__(self, name, value=0.0):
        self.value = value
        self.name = name
        self.parent = None
        self.children = []

    def find_child(self, name):
        for i in self.children:
            if i.name == name:
                return i
        return None

    def find_node_series(self, *args):
        node = self.find_node(args[0])
        for arg in args[1:]:
            node = node.find_node(arg)
        return node

    def find_node(self, x):
        if self.name == x:
            return self
        for node in self.children:
            n = node.find_node(x)
            if n:
                return n
        return None

    def add_child(self, name):
        child = self.find_child(name)
        if not child:
            child = TreeNode(name)
            child.parent = self
            self.children.append(child)
        return child

    def add_children(self, args):
        for v in args:
            self.add_child(v)

    def get_all_nodes(self, nodes):
        if self.children:
            for child in self.children:
                child.get_all_nodes(nodes=nodes)
        else:
            nodes.append(self)

    def get_all_terminal_nodes(self):
        nodes = []
        self.get_all_nodes(nodes)
        return nodes

    def re_aggregate(self):
        if self.children:
            if self.parent:
                self.value = sum([x.value for x in (self.get_all_terminal_nodes())])
            for x in self.children:
                x.re_aggregate()
        if self.name == "BS":
            self.value = self.find_child("Assets").value - self.find_child("Liabilities").value - self.find_child(
                "Equities").value

    def __str__(self, level=0):
        ret = "\t" * level + "{}:{}".format(self.name, self.value) + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret


class BalanceSheet(TreeNode):
    def __init__(self, data, name):
        super().__init__(name)
        self.build_bs_tree()
        self.initialize_balance_sheet(data)

    def initialize_balance_sheet(self, data):
        data = data.groupby(level=0).sum()
        nodes = sorted(self.get_all_terminal_nodes(), key=lambda x: x.name)
        for node in nodes:
            to_drop = None
            for idx in data.index:
                if node.name == idx:
                    node.value = data[idx] + 3.0
                    to_drop = idx
                    break
            if to_drop:
                data = data.drop(to_drop)
        self.re_aggregate()

    def build_bs_tree(self):
        self.add_child(assets).add_child(external).add_child(liquid).add_children(bst.liquid_external_assets)
        self.add_child(assets).add_child(external).add_child(illiquid).add_children(bst.illiquid_external_assets)
        self.add_child(assets).add_child(interbank).add_child(liquid).add_children(bst.liquid_inter_bank_assets)
        self.add_child(assets).add_child(interbank).add_child(illiquid).add_children(bst.illiquid_inter_bank_assets)
        self.add_child(liab).add_child(interbank).add_child("Short Term").add_children(bst.st_inter_bank_liabilities)
        self.add_child(liab).add_child(interbank).add_child("Long Term").add_children(bst.lt_inter_bank_liabilities)
        self.add_child(liab).add_child(deposits_etc).add_child("Customer").add_children(bst.customer_deposits)
        self.add_child(liab).add_child(deposits_etc).add_child("Institutional").add_children(bst.other_liabilities_)
        self.add_child("Equities").add_children(bst.equities)


class TimeSeries:
    def __init__(self, series):
        self.series = np.asarray(series)
        self.N = len(self.series)
        self.returns = self.returns()
        self.mu = self.mean_returns()
        self.vol = self.standard_dev()

    def returns(self):
        as_array = np.asarray(self.series)
        init_val = as_array[0:self.N - 1]
        return np.divide(as_array[1:self.N] - init_val, init_val)

    def mean_returns(self):
        return np.average(self.returns)

    def standard_dev(self):
        return np.std(self.returns)

    def __str__(self):
        return "Mean: {} StDev: {}".format(self.mu, self.vol)


def double_entry(node_1, node_2, value, fm='dd'):
    if node_1.children:
        print("{} not a terminal node!".format(node_1))
    elif node_2.children:
        print("{} not a terminal node!".format(node_2))
    elif fm == "ii":
        node_1.value += value
        node_2.value += value
    elif fm == "id":
        node_1.value += value
        node_2.value -= value
    elif fm == "di":
        node_1.value -= value
        node_2.value += value
    else:
        node_1.value -= value
        node_2.value -= value
