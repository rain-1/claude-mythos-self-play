# Fourier modes of local basin densities g_j(x), x=log2 n, from fine2048.u32 (2048 bins/octave).
import numpy as np, sys
from beta import pred, th
B=2048
C=np.fromfile('fine2048.u32',dtype=np.uint32).reshape(32,B,4).astype(float)
def window(a,w=2):
    c=C[a:a+w].reshape(-1,4); tot=c[:,1:].sum(1)
    x=(np.arange(w*B)+0.5)/B+a
    g=c[:,1:]/tot[:,None]
    return x,g,tot
def coef(a,q,w=2):
    x,g,tot=window(a,w)
    gm=g-g.mean(0)
    e=np.exp(-2j*np.pi*q*x)
    c=(gm*e[:,None]).mean(0)               # uniform weight in x
    var=(g*(1-g)/tot[:,None]).sum(0)/len(x)**2   # binomial noise of c (complex), approx
    return c, np.sqrt(var/2)
if __name__=="__main__":
    qs=[1,5,7,12,17,24,29,41,53,65,94,106,118,159,212,306,359,665]
    print("amplitude 2|c_q| of basin-1 density g_1 (in units of 1e-4); noise sigma in last col for q=53")
    print("win  "+" ".join("%7d"%q for q in qs))
    for a in range(10,31):
        row=[];
        for q in qs:
            c,s=coef(a,q); row.append(2*abs(c[0])*1e4)
        print("%2d-%2d "%(a,a+2)+" ".join("%7.2f"%r for r in row)+"   noise %.2f"%(2*s[0]*1e4*1.4))
