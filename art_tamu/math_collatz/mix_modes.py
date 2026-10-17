# Control with a DIFFERENT multiplier set: T(n) = (3n+1)/2^v if n=1 mod 4, (5n+1)/2^v if n=3 mod 4 (v>=2 always).
# Random-walk model: step = log2(a) - v, a in {3,5} w.p. 1/2, P(v=k)=2^-(k-1), k>=2.
# Mode q decays at rate Re beta, beta solving (1/2) sum_a e^{2 pi i q log2 a} e^{-beta log2 a} * E[e^{beta v}] = 1.
import numpy as np
from gen_modes import coefs
t3,t5=np.log2(3),np.log2(5)
def Ev(b): return (np.exp(2*b)/2)/(1-np.exp(b)/2)          # sum_{k>=2} 2^{-(k-1)} e^{bk}
def beta_mix(q,steps=400):
    e3=q*t3-round(q*t3); e5=q*t5-round(q*t5); b=0j
    for t in np.linspace(0,1,steps+1)[1:]:
        for _ in range(40):
            F=lambda b:0.5*(np.exp(2j*np.pi*t*e3-b*t3)+np.exp(2j*np.pi*t*e5-b*t5))*Ev(b)-1
            h=1e-7; b-=F(b)/((F(b+h)-F(b))/h)
    return b.real,e3,e5
B=2048; LOG=26
C=np.fromfile('mix35_d1.u32',dtype=np.uint32).reshape(LOG,B,10)[:,:,1:].astype(float)
qs=np.arange(1,1024)
r2,n2,pb=coefs(C,23,qs); r1,n1,_=coefs(C,15,qs)
print("basin shares:",np.round(pb[:3],4))
A=2*np.abs(r2[:,0]); top=np.argsort(-A)[:12]
print("top modes 2^23-25, basin 1 (noise %.1e):"%(2*n2[0]*1.4))
for i in top:
    rp,e3,e5=beta_mix(qs[i]); rm=np.log(abs(r1[i,0])/abs(r2[i,0]))/8
    print("  q=%4d amp=%.4f  eps3=%+.4f eps5=%+.4f  rate_meas=%.4f rate_pred=%.4f"%(qs[i],A[i],e3,e5,rm,rp))
print("q=12,53 amps:",np.round(A[[11,52]],5)," predicted rates:",[round(beta_mix(q)[0],3) for q in (12,53)])
pr=np.array([beta_mix(q)[0] for q in qs]); o=np.argsort(pr)[:8]
print("slowest predicted modes:",[(int(qs[i]),round(pr[i],4)) for i in o])
