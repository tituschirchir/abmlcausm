"""
A fixed income security is an investment that provides a return in the form of fixed periodic payments and the
eventual return of principal at maturity.
"""
from products.contracts import Contract


class Bond(Contract):

    def __init__(self):
        super().__init__("Bond")

    def get_value(self):
        pass

    def get_premium(self):
        pass
