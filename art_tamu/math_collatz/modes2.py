# Count-weighted Fourier coefficients of basin indicators over odd n in [2^a, 2^(a+w)):
#   c_{j,q} = (1/N) sum_n (1[basin(n)=j] - pbar_j) exp(-2 pi i q log2 n)
# computed from 2048-bins/octave counts (bin-centre phase; sinc loss corrected).
import numpy as np
from beta import pred, th
B=2048
C=np.fromfile('fine2048.u32',dtype=np.uint32).reshape(32,B,4).astype(float)
def coefs(a,qs,w=2):
    c=C[a:a+w].reshape(-1,4)[:,1:]; tot=c.sum(1); N=tot.sum()
    pbar=c.sum(0)/N
    x=(np.arange(w*B)+0.5)/B+a
    qs=np.asarray(qs,float)
    E=np.exp(-2j*np.pi*np.outer(qs,x))           # (nq, nbins)
    r=E@(c-np.outer(tot,pbar))/N                  # (nq,3)
    r/=np.sinc(qs/B)[:,None]                      # bin-averaging correction
    noise=np.sqrt(pbar*(1-pbar)/N/2)              # std of Re or Im part
    return r,noise,pbar
if __name__=="__main__":
    import sys
    qs=np.arange(1,1024)
    r,noise,_=coefs(29,qs)
    A=2*np.abs(r[:,0]); o=np.argsort(A)[::-1][:25]
    print("Top 25 modes, window 2^29..2^31, basin 1, amplitude 2|c| (1e-4), noise %.2e"%(2*noise[0]*1.41))
    for i in o:
        p=pred(qs[i]); print("  q=%4d amp=%7.2f  eps=%+.5f pred_rate=%.5f"%(qs[i],A[i]*1e4,p['eps'],p['rate_exact']))
