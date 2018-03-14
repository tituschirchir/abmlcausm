accrued_investment_income = 'Accrued investment income'
allowance_for_loan_losses = 'Allowance for loan losses'
cash_and_cash_equivalents = 'Cash and cash equivalents'
cash_and_due_from_banks = 'Cash and due from banks'
debt_securities = 'Debt securities'
deferred_income_tax_assets = 'Deferred income tax assets'
deferred_income_taxes = 'Deferred income taxes'
deferred_income_taxes_liabilities = 'Deferred income taxes - L'
deferred_taxes_liabilities = 'Deferred taxes liabilities'
deferred_policy_acquisition_costs = 'Deferred policy acquisition costs'
deposits_with_banks = 'Deposits with banks'
derivative_assets = 'Derivative assets'
equity_securities = 'Equity securities'
federal_funds_sold = 'Federal funds sold'
fixed_maturity_securities = 'Fixed maturity securities'
goodwill = 'Goodwill'
intangible_assets = 'Intangible assets'
investments = 'Investments'
loans = 'Loans'
loans__total = 'Loans, total'
net_property__plant_and_equipment = 'Net property, plant and equipment'
other_assets = 'Other assets'
other_current_assets = 'Other current assets'
other_intangible_assets = 'Other intangible assets'
other_long_term_assets = 'Other long-term assets'
premises_and_equipment = 'Premises and equipment'
premiums_and_other_receivables = 'Premiums and other receivables'
prepaid_expenses = 'Prepaid expenses'
prepaid_pension_benefit = 'Prepaid pension benefit'
property_and_equipment = 'Property and equipment'
receivables = 'Receivables'
restricted_cash = 'Restricted cash'
restricted_cash_and_cash_equivalents = 'Restricted cash and cash equivalents'
securities_and_investments = 'Securities and investments'
securities_borrowed = 'Securities borrowed'
separate_account_assets = 'Separate account assets'
short_term_investments = 'Short-term investments'
trading_assets = 'Trading assets'
trading_securities = 'Trading securities'
accounts_payable = 'Accounts payable'
accrued_expenses_and_liabilities = 'Accrued expenses and liabilities'
accrued_liabilities = 'Accrued liabilities'
deferred_revenues = 'Deferred revenues'
deferred_taxes = 'Deferred taxes'
deposits = 'Deposits'
derivative_liabilities = 'Derivative liabilities'
federal_funds_purchased = 'Federal funds purchased'
future_policy_benefits = 'Future policy benefits'
long_term_debt = 'Long-term debt'
minority_interest = 'Minority Interest'
minority__interest = 'Minority interest'
other_current_liabilities = 'Other current liabilities'
other_liabilities = 'Other liabilities'
other_long_term_liabilities = 'Other long-term liabilities'
payables = 'Payables'
payables_and_accrued_expenses = 'Payables and accrued expenses'
policyholder_funds = 'Policyholder funds'
separate_account_liabilities = 'Separate account liabilities'
short_term_borrowing = 'Short-term borrowing'
short_term_debt = 'Short-term debt'
taxes_payable = 'Taxes payable'
trading_liabilities = 'Trading liabilities'
unearned_premiums = 'Unearned premiums'
accumulated_other_comprehensive_income = 'Accumulated other comprehensive income'
additional_paid_in_capital = 'Additional paid-in capital'
common_stock = 'Common stock'
other_equity = 'Other Equity'
preferred_stock = 'Preferred stock'
retained_earnings = 'Retained earnings'
treasury_stock = 'Treasury stock'
equity_and_other_investments = "Equity and other investments"
inventories = "Inventories"
pensions_and_other_benefits = "Pensions and other benefits"

liquid_inter_bank_assets = [deposits_with_banks, cash_and_due_from_banks, federal_funds_sold, short_term_investments,
                            equity_and_other_investments]
illiquid_inter_bank_assets = [debt_securities, derivative_assets, equity_securities, fixed_maturity_securities,
                              investments, loans, loans__total, receivables, securities_and_investments, trading_assets,
                              trading_securities]

liquid_external_assets = [restricted_cash_and_cash_equivalents, allowance_for_loan_losses,
                          securities_borrowed, cash_and_cash_equivalents, restricted_cash,
                          separate_account_assets, other_current_assets, inventories]

illiquid_external_assets = [deferred_income_taxes, other_intangible_assets, deferred_income_tax_assets,
                            deferred_policy_acquisition_costs, other_assets,
                            property_and_equipment, premises_and_equipment, prepaid_expenses, prepaid_pension_benefit,
                            premiums_and_other_receivables, accrued_investment_income,
                            net_property__plant_and_equipment, other_long_term_assets, goodwill,
                            intangible_assets]

st_inter_bank_liabilities = [federal_funds_purchased, unearned_premiums, payables, derivative_liabilities,
                             payables_and_accrued_expenses, short_term_borrowing, short_term_debt, trading_liabilities]

lt_inter_bank_liabilities = [long_term_debt, minority_interest, minority__interest, pensions_and_other_benefits]

customer_deposits = [deposits, deferred_revenues, accounts_payable, accrued_liabilities, separate_account_liabilities,
                     accrued_expenses_and_liabilities, other_current_liabilities]
other_liabilities_ = [deferred_income_taxes_liabilities, deferred_taxes_liabilities,
                      other_long_term_liabilities, future_policy_benefits, policyholder_funds,
                      other_liabilities, deferred_taxes, taxes_payable]

inter_bank_assets = liquid_inter_bank_assets + illiquid_inter_bank_assets
external_assets = liquid_external_assets + illiquid_external_assets
inter_bank_liabilities = st_inter_bank_liabilities + lt_inter_bank_liabilities
deposits_and_other_liabilities = customer_deposits + other_liabilities_
equities = [accumulated_other_comprehensive_income, additional_paid_in_capital, common_stock, other_equity,
            preferred_stock, retained_earnings, treasury_stock]

liabilities = inter_bank_liabilities + deposits_and_other_liabilities
assets = inter_bank_assets + external_assets
