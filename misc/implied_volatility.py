import misc.root_finders as rf
from misc.black_scholes import BSMerton


def implied_vol(C, S, K, T, r, q, Type):
    def func(vol):
        return C - BSMerton(Type=Type, S=S, K=K, r=r, q=q, T=T, sigma=vol).premium()

    return rf.secant(f=func, a=0.001, b=5.0, tol=0.0001)
