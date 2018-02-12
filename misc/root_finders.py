import numpy as np


# ROOT FINDERS FOR FUNCTION f between points (a,b)
def bisection(f, a, b, tol=0.0001):
    c = (a + b) / 2.0
    return c if b - a <= tol ** 2 else bisection(f, c, b, tol) if f(c) * f(a) > 0 else bisection(f, a, c, tol)


def secant(f, a, b, tol):
    return b if abs(f(b) - f(a)) <= tol else secant(f, b, b - (f(b) * (b - a) * 1.0) / (f(b) - f(a)), tol)


def newton_ralphson():
    pass


def fixed_point_iteration():
    pass


# AREA UNDER FUNCTION f ----
def simpson_rule(f, a, b, N):
    h = (b - a) / N
    xa = np.arange(a, b, h)
    xb = np.arange(a + h, b + h, h)
    part_2 = mapply(f, xa) + 4 * mapply(f, (xa + xb) / 2) + mapply(f, xb)
    return sum(np.multiply((xb - xa) / 6, part_2))


def mapply(f, arr):
    return np.asarray(list(map(f, arr)))


def trapezoid_rule(f, a, b, N):
    h = (b - a) / N
    the_sum = 0.5 * h * (f(a) + f(a + h))
    for i in range(0, N):
        the_sum = the_sum + 0.5 * h * (f(a + i * h) + f(a + (i + 1) * h))
    return the_sum
