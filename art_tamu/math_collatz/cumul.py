# Cumulative proportion p_j(n) = #{odd m<=n in basin j}/#{odd m<=n}; spectrum of its fluctuation in log2 n.
import numpy as np
from beta import pred
B=2048
C=np.fromfile('fine2048.u32',dtype=np.uint32).reshape(32,B,4).astype(float)[:, :, 1:].reshape(-1,3)
cum=np.cumsum(C,0); p=cum/cum.sum(1)[:,None]
x=np.arange(32*B)/B+1/B      # right bin edges
for a,b in [(14,20),(20,26),(25,31)]:
    s=(x>=a)&(x<b); xs=x[s]; y=p[s,0]
    y=y-np.polyval(np.polyfit(xs,y,3),xs)   # remove slow trend
    print("window 2^%d..2^%d  cumulative p_1: amplitude 2|c_q| (1e-5):"%(a,b),
          {q:round(2*abs(np.mean(y*np.exp(-2j*np.pi*q*xs)))*1e5,2) for q in [5,7,12,17,24,41,53,94,106,359]})
    # ratio between successive maxima
    from scipy.signal import find_peaks
    Y=np.fft.rfft(y); f=np.fft.rfftfreq(len(y),1/B); Y[f>30]=0; ys=np.fft.irfft(Y,len(y))
    pk,_=find_peaks(ys)
    r=np.diff(xs[pk]); print("   (low-passed <30 c/oct) mean spacing of maxima (octaves) %.5f -> ratio %.5f ; 1/12=%.5f"%(np.mean(r),2**np.mean(r),1/12))
