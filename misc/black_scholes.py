from math import log, e

from scipy.stats import norm


class BSMerton:
    def __init__(self, Type, S, K, r, q, T, sigma):
        self.Type, self.S, self.K, self.r, self.q, self.T, self.sigma = Type, S, K, r, q, T, sigma
        self.sigmaT = self.sigma * self.T ** 0.5
        self.d1 = (log(self.S / self.K) + (self.r - self.q + 0.5 * (self.sigma ** 2)) * self.T) / self.sigmaT
        self.d2 = self.d1 - self.sigmaT

    def premium(self):
        tmpprem = self.Type * (
            self.S * e ** (-self.q * self.T) * norm.cdf(self.Type * self.d1) - self.K * e ** (
                -self.r * self.T) * norm.cdf(
                self.Type * self.d2))
        return tmpprem

    def delta(self):
        dfq = e ** (-self.q * self.T)
        return dfq * norm.cdf(self.d1) if self.Type == 1 else dfq * (norm.cdf(self.d1) - 1)

    # Vega for 1% change in vol
    def vega(self):
        return 0.01 * self.S * e ** (-self.q * self.T) * norm.pdf(self.d1) * self.T ** 0.5

    # Theta for 1 day change
    def theta(self):
        df = e ** -(self.r * self.T)
        dfq = e ** (-self.q * self.T)
        tmptheta = (1.0 / 365.0) \
                   * (-0.5 * self.S * dfq * norm.pdf(self.d1) * self.sigma / (self.T ** 0.5) + self.Type * (
            self.q * self.S * dfq * norm.cdf(self.Type * self.d1) - self.r * self.K * df * norm.cdf(
                self.Type * self.d2)))
        return tmptheta

    def rho(self):
        df = e ** -(self.r * self.T)
        return self.Type * self.K * self.T * df * 0.01 * norm.cdf(self.Type * self.d2)

    def phi(self):
        return 0.01 * -self.Type * self.T * self.S * e ** (-self.q * self.T) * norm.cdf(self.Type * self.d1)

    def gamma(self):
        return e ** (-self.q * self.T) * norm.pdf(self.d1) / (self.S * self.sigmaT)

    # Charm for 1 day change
    def d_delta_dt(self):
        dfq = e ** (-self.q * self.T)
        if self.Type == 1:
            return (1.0 / 365.0) * -dfq * (
                norm.pdf(self.d1) * ((self.r - self.q) / (self.sigmaT) - self.d2 / (2 * self.T)) + (-self.q) * norm.cdf(
                    self.d1))
        else:
            return (1.0 / 365.0) * -dfq * (
                norm.pdf(self.d1) * ((self.r - self.q) / (self.sigmaT) - self.d2 / (2 * self.T)) + self.q * norm.cdf(
                    -self.d1))

    # Vanna for 1% change in vol
    def d_delta_d_vol(self):
        return 0.01 * -e ** (-self.q * self.T) * self.d2 / self.sigma * norm.pdf(self.d1)

    # Vomma
    def d_vega_d_vol(self):
        return 0.01 * -e ** (-self.q * self.T) * self.d2 / self.sigma * norm.pdf(self.d1)

    def properties(self):
        return dict(Type=("Call" if self.Type == 1 else "Put"),
                    S=self.S,
                    r=self.r,
                    q=self.q,
                    T=self.T,
                    vol=self.sigma,
                    Price=self.premium(),
                    d1=self.d1,
                    d2=self.d2,
                    Delta=self.delta(),
                    Theta=self.theta(),
                    Rho=self.rho(),
                    Vega=self.vega(),
                    Gamma=self.gamma(),
                    Phi=self.phi(),
                    Charm=self.d_delta_dt(),
                    Vanna=self.d_delta_d_vol(),
                    Vomma=self.d_vega_d_vol()
                    )
