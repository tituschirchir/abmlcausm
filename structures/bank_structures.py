# Assets
loans_receivable = ['Loans', 'Loans, total', 'Receivables', 'Premiums and other receivables']
derivative_assets = ['Trading assets', 'Derivative assets', 'Debt securities', 'Securities borrowed',
                     'Securities and investments', 'Fixed maturity securities', 'Equity securities']
cash_desc = ['Cash and cash equivalents', 'Cash and due from banks', 'Deposits with banks', 'Short-term investments']
fixed_assets_cat = ['Premises and equipment', 'Goodwill', 'Intangible assets', 'Other intangible assets',
                    'Other assets', 'Property and equipment']
sold_fed_funds = ['Federal funds sold']

# Liabilities
cust_deposits = ['Deposits', 'Future policy benefits']
purch_fed_funds = ['Federal funds purchased']
derivative_liabilities = ['Trading liabilities', 'Derivative liabilities']
loans_payable = ['Payables', 'Short-term borrowing', 'Unearned premiums', 'Deferred income taxes']
long_term_liabilities = ['Other liabilities', 'Long-term debt']

# Equity
equity_desc = ['Common stock', 'Preferred stock', 'Treasury stock']
capital = ['Retained earnings', 'Accumulated other comprehensive income', 'Additional paid-in capital']


class BalanceSheet:
    def __init__(self, data, company):
        self.line_items = [LineItem(idx, row.Category, row[company]) for idx, row in data.iterrows()]
        self.debtors = self.aggregate(loans_receivable)
        self.creditors = self.aggregate(loans_payable)
        self.cash = self.aggregate(cash_desc)
        self.equity = self.aggregate(equity_desc)
        self.total_equity = self.aggregate(['E'], 'category')
        self.total_assets = self.aggregate(['A'], 'category')
        self.total_liabilities = self.aggregate(['L'], 'category')

    def identity(self):
        return self.total_equity + self.total_liabilities - self.total_assets

    def aggregate(self, check, attr='name'):
        return sum([x.value for x in self.line_items if getattr(x, attr) in check])


class LineItem:
    def __init__(self, name, category, value):
        self.name = name
        self.category = category
        self.tier = 1
        self.value = value

    def __str__(self):
        return self.name + "=" + str(self.value)
