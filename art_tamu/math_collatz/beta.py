# Exact random-walk prediction for the decay rate / frequency shift of Fourier mode q.
# Walk X -> X + theta - v, P(v=k)=2^-k. Wald martingale z^K e^{-beta (X_K - x)}, z = e^{2 pi i q theta}.
# E[z^K] ~ C e^{-beta x}; beta solves z e^{beta(1-theta)} = 2 - e^beta, branch through beta(z=1)=0.
import numpy as np
th=np.log2(3)
def beta(eps, steps=200):
    b=0j
    for t in np.linspace(0,1,steps+1)[1:]:      # continuation in eps
        z=np.exp(2j*np.pi*eps*t)
        for _ in range(30):
            F=z*np.exp(b*(1-th))-2+np.exp(b); dF=z*(1-th)*np.exp(b*(1-th))+np.exp(b)
            b-=F/dF
    return b
VAR_SLOPE=2/(2-th)**3; MEAN_SLOPE=1/(2-th)
def pred(q):
    e=q*th-round(q*th); b=beta(e)
    return dict(q=q,eps=e,rate_exact=b.real,rate_gauss=2*np.pi**2*e*e*VAR_SLOPE,
                fshift_exact=-b.imag/(2*np.pi), fshift_lin=e*MEAN_SLOPE)
if __name__=="__main__":
    print("mean slope 1/(2-th)=%.4f  var slope 2/(2-th)^3=%.3f"%(MEAN_SLOPE,VAR_SLOPE))
    print(" q   eps        rate_exact  rate_gauss  fshift_exact fshift_lin")
    for q in [1,5,7,12,17,24,29,41,53,65,94,106,118,159,212,306,359,665]:
        p=pred(q); print("%4d %+.6f  %.6f  %.6f  %+.6f %+.6f"%(q,p['eps'],p['rate_exact'],p['rate_gauss'],p['fshift_exact'],p['fshift_lin']))
