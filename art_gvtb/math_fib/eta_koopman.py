# eta(alpha) = E_mu log Y via iteration of the dual (Koopman) operator
#   (P h)(y) = 1/4 sum_{u,v} h(u + v/y)
# on functions analytic on the invariant interval [a,b], represented by Chebyshev
# interpolation in the variable log y.  P^k log -> eta (constant); min/max of P^k log bracket eta.
import numpy as np, sys
def support(al):
    lo, hi = 1-al, 1+al
    # a = lo + lo/b, b = hi + hi/a  ->  fixed point iteration
    a, b = lo, hi + hi/lo
    for _ in range(2000):
        a = lo + lo/b; b = hi + hi/a
    return a, b
def cheb_nodes(N):
    k = np.arange(N); return np.cos(np.pi*(2*k+1)/(2*N))
def bary_w(N):
    k = np.arange(N); return (-1)**k*np.sin(np.pi*(2*k+1)/(2*N))
def interp(x, f, w, xe):
    d = xe[:,None]-x[None,:]
    exact = np.isclose(d,0,atol=1e-300)
    d[exact] = 1.0
    c = w/d
    r = (c@f)/c.sum(1)
    i, j = np.nonzero(exact); r[i] = f[j]
    return r
def eta(al, N=200, tol=1e-15, maxit=5000, verbose=False):
    a, b = support(al)
    la, lb = np.log(a), np.log(b)
    x = cheb_nodes(N); w = bary_w(N)
    y = np.exp(la + (x+1)/2*(lb-la))
    h = np.log(y)
    imgs = []
    for u in (1-al, 1+al):
        for v in (1-al, 1+al):
            z = np.clip(np.log(u + v/y), la, lb)
            imgs.append(2*(z-la)/(lb-la)-1)
    # precompute interpolation matrices
    Ms = []
    for xe in imgs:
        d = xe[:,None]-x[None,:]; d[np.abs(d)<1e-300]=1e-300
        c = w/d; Ms.append(c/c.sum(1)[:,None])
    M = sum(Ms)/4
    for it in range(maxit):
        h = M@h
        spread = h.max()-h.min()
        if spread < tol: break
    return 0.5*(h.max()+h.min()), spread, it, (a,b)
if __name__ == "__main__":
    for al in [0.0, 0.05, 0.5, 0.9, 0.95]:
        for N in (100, 200, 400):
            e, s, it, ab = eta(al, N)
            print(al, N, repr(e), s, it, ab)
