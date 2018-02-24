class BalanceSheet:
    def __init__(self, data, company):
        self.line_items = [LineItem(idx, row.Category, row[company]) for idx, row in data.iterrows()]

    def get_value(self, cat):
        return sum([x.value for x in self.line_items if x.category == cat])

    def total_assets(self):
        return self.get_value('A')

    def total_liabilities(self):
        return self.get_value('L')

    def total_equity(self):
        return self.get_value('E')

    def identity(self):
        return self.total_equity() + self.total_liabilities() - self.total_assets()


class LineItem:
    def __init__(self, name, category, value):
        self.name = name
        self.category = category
        self.tier = 1
        self.value = value
