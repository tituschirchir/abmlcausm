def bisection(f, a, b, tol=0.0001):
    c = (a + b) / 2.0
    return c if b - a <= tol ** 2 else bisection(f, c, b, tol) if f(c) * f(a) > 0 else bisection(f, a, c, tol)


def secant(f, a, b, tol):
    return b if abs(f(b) - f(a)) <= tol else secant(f, b, b - (f(b) * (b - a) * 1.0) / (f(b) - f(a)), tol)


def newton_ralphson():
    pass


def fixed_point_iteration():
    pass
