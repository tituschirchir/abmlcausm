from structures.bs_tree import build_bs_tree


class BalanceSheet:
    def __init__(self, data):
        self.balance_sheet = build_bs_tree()
        self.initialize_balance_sheet(data)

    def initialize_balance_sheet(self, data):
        data = data.groupby(level=0).sum()
        nodes = sorted(self.balance_sheet.get_all_terminal_nodes(), key=lambda x: x.name)
        for node in nodes:
            to_drop = None
            for idx in data.index:
                if node.name == idx:
                    node.value = data[idx]
                    to_drop = idx
                    break
            if to_drop:
                data = data.drop(to_drop)
        self.balance_sheet.re_aggregate()

    def get_level(self, *levels):
        level = self.balance_sheet
        for lvl in levels:
            level = level.find_child(lvl)
            if not level:
                print("{} Not found".format(levels))
        return level

#
# df = pd.read_csv('../data/bs_ms.csv', index_col=0)
# dd = df['JPM']
#
# bs = BalanceSheet(dd)
# print(bs)
