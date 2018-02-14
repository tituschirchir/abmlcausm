from enum import Enum


class OptionTypes(Enum):
    EURO = "European"
    AMERICAN = "American"
    UP_AND_OUT = "Exotic"
    VANILLA = "Vanilla"


def mult(is_call): return 1 if is_call else -1


def payoff(s, K, is_call, flavor, H=0):
    if flavor == OptionTypes.UP_AND_OUT:
        return 0 if s > H else max(0, mult(is_call) * (s - K))
    else:
        return max(0, mult(is_call) * (s - K))


def replication(s, H, pu, vu, pm, vm, pd, vd, flavor):
    if flavor == OptionTypes.UP_AND_OUT:
        return 0 if s > H else (pu * vu + pm * vm + pd * vd)
    else:
        return pu * vu + pm * vm + pd * vd
