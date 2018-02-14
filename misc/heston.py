from cmath import exp, log, sqrt, pi

from misc.root_finders import simpson_rule

'''
Outlined in (Mikhailov, Sergei and Nögel, Ulrich.) Heston’s stochastic volatility model: 
Implementation, calibration and some extensions Wilmott Journal, 2004.
'''


def heston_call_closed_form(theta=0.1, sigma=0.2, S0=1, lmd=0, rho=-0.3, V0=0.1, r=0, q=0, tau=5, K=0.5, kappa=4):
    def heston_integrand(j, phi):
        b = kappa + lmd
        if j == 1:
            b = b - rho * sigma
            u = 0.5
        else:
            u = -0.5

        d = sqrt((rho * sigma * phi * 1j - b) ** 2 - (sigma ** 2) * (2 * u * phi * 1j - phi ** 2))
        g = (b - rho * sigma * phi * 1j + d) / (b - rho * sigma * phi * 1j - d)
        C = (r - q) * phi * 1j * tau + (kappa * theta / (sigma ** 2)) * (
                (b - rho * sigma * phi * 1j + d) * tau - 2 * log((1 - g * exp(d * tau)) / (1 - g)))
        D = ((b - rho * sigma * phi * 1j + d) / (sigma ** 2)) * ((1 - exp(d * tau)) / (1 - g * exp(d * tau)))
        psi = exp(C + D * V0 + 1j * phi * log(S0 * exp(r * tau)))
        return ((exp(-1j * phi * log(K)) * psi) / (1j * phi)).real

    def p1_function(psi):
        return heston_integrand(1, psi)

    def p2_function(psi):
        return heston_integrand(2, psi)

    p1 = 0.5 + simpson_rule(p1_function, a=10 ** -20, b=743, N=24 ** 2) / pi
    p2 = 0.5 + simpson_rule(p2_function, a=10 ** -20, b=743, N=24 ** 2) / pi
    return (S0 * p1 - K * exp(-(r - q) * tau) * p2).real
