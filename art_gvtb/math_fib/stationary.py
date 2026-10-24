# Stationary law mu of Y (Y' = U + V/Y) via fixed-point iteration of the CDF:
#   F(y) = 1/4 sum_{u,v} [y>u] (1 - F(v/(y-u)))
# on a log-uniform grid of G points over [a,b] (linear interpolation), then binned.
import numpy as np, sys, time
from eta_koopman import support, eta
G = 2**18; NB = 4000
def cdf(al, tol=1e-13, maxit=3000):
    a, b = support(al)
    ly = np.linspace(np.log(a), np.log(b), G); y = np.exp(ly)
    F = (ly-ly[0])/(ly[-1]-ly[0])
    pre = []
    for u in (1-al, 1+al):
        for v in (1-al, 1+al):
            m = y > u
            z = np.full(G, np.inf); z[m] = v/(y[m]-u)
            pre.append((m, np.log(np.clip(z, a, b))))
    for it in range(maxit):
        Fn = np.zeros(G)
        for m, lz in pre:
            Fn[m] += 1 - np.interp(lz[m], ly, F)
        Fn /= 4; Fn[0] = 0.0; Fn[-1] = 1.0
        d = np.abs(Fn-F).max(); F = Fn
        if d < tol: break
    return ly, F, (a, b), it
def mass(ly, F, edges):
    return np.diff(np.interp(np.log(edges), ly, F))
if __name__ == "__main__":
    alphas = np.round(np.arange(0.05, 0.951, 0.01), 2)
    H = np.zeros((len(alphas), NB)); HL = np.zeros_like(H); AB = np.zeros((len(alphas), 2))
    E = np.zeros(len(alphas)); EG = np.zeros(len(alphas))
    t = time.time()
    for i, al in enumerate(alphas):
        ly, F, (a, b), it = cdf(al)
        AB[i] = a, b
        H[i] = mass(ly, F, np.linspace(a, b, NB+1))
        HL[i] = mass(ly, F, np.exp(np.linspace(np.log(a), np.log(b), NB+1)))
        # E log Y = log b - int_a^b F(y)/y dy = log b - int F d(log y)
        EG[i] = ly[-1] - np.trapz(F, ly) if hasattr(np,'trapz') else ly[-1]-np.trapezoid(F, ly)
        E[i] = eta(al, 200)[0]
        print(f"{al:.2f} [{a:.6f},{b:.6f}] it={it} E_hist[logY]={EG[i]:.10f} eta={E[i]:.10f} ({time.time()-t:.0f}s)", flush=True)
    np.savez_compressed("stationary.npz", alphas=alphas, support=AB, hist_linear=H, hist_log=HL, nbins=NB,
        note="hist_linear[i,j] = mu_alpha mass of j-th of NB equal bins on [a,b]=support[i] (linear in y); "
             "hist_log = same with bins equally spaced in log y. Rows sum to 1. Density = mass/binwidth.",
        eta=E)
