# Full spectrum (integer q up to 32767) of basin densities in one octave, from 65536 bins.
import numpy as np, sys
from beta import pred, th
def spec(fn,k,B=65536):
    c=np.fromfile(fn,dtype=np.uint32).reshape(B,4)[:,1:].astype(float); tot=c.sum(1); N=tot.sum()
    pbar=c.sum(0)/N
    d=c-np.outer(tot,pbar)
    # coefficient at integer q: (1/N) sum_b d_b exp(-2pi i q (k+(b+.5)/B)); k integer -> drop
    F=np.fft.fft(d,axis=0)/N*np.exp(-1j*np.pi*np.arange(B)/B)[:,None]
    q=np.arange(B//2); F=F[:B//2]/np.sinc(q/B)[:,None]
    return q,2*np.abs(F),np.sqrt(pbar*(1-pbar)/N)
if __name__=="__main__":
    q30,A30,s30=spec('oct30_65536.u32',30); q22,A22,s22=spec('oct22_65536.u32',22)
    eps=q30*th-np.round(q30*th)
    print("noise level (2|c| std) oct30: %.1e  oct22: %.1e"%(2*s30[0],2*s22[0]))
    o=np.argsort(A30[:,0])[::-1][:40]
    print("Top 40 modes of basin-1 density in octave 2^30..2^31 (q<32768):")
    print("   q      eps        amp_oct30  amp_oct22  rate_meas  rate_pred")
    for i in sorted(o):
        p=pred(i); rm=np.log(A22[i,0]/A30[i,0])/8
        print("  %5d %+.6f  %.5f   %.5f   %+.5f  %.5f"%(i,eps[i],A30[i,0],A22[i,0],rm,p['rate_exact']))
    for qq in [12,41,53,106,306,359,665,971,1636,15601]:
        print("q=%5d amp30=%s amp22=%s"%(qq,np.round(A30[qq],5),np.round(A22[qq],5)))
    # how much variance is in modes with |eps|<0.01 vs total
    tot=(A30[1:,0]**2).sum(); sm=(A30[1:,0]**2*(abs(eps[1:])<0.005)).sum()
    print("fraction of oscillation power (q>=1) at |eps|<0.005: %.3f ; number of such q: %d"%(sm/tot,(abs(eps[1:])<0.005).sum()))
