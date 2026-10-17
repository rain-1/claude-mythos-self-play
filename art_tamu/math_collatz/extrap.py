# Extrapolate: which mode dominates the local density (and the cumulative proportion) of basin 1 at larger n,
# assuming A_q(x) = A_q(30) * exp(-r_q (x-30)) with r_q the Wald rate. Uses modes q<32768 with amplitude > 10 sigma at 2^30.
import numpy as np
from hispec import spec
from beta import th
q,A,s=spec('oct30_65536.u32',30)
m=2-th
def rate(q):  # vectorised Wald rate: exact root of z e^{b(1-th)} = 2 - e^b via quadratic-start Newton
    e=q*th-np.round(q*th); z=np.exp(2j*np.pi*e)
    b=(-m+np.sqrt(m*m-4j*2*np.pi*e+0j))/2         # quadratic approximation as start
    for t in np.linspace(0.05,1,20):
        zt=np.exp(2j*np.pi*e*t)
        for _ in range(20):
            F=zt*np.exp(b*(1-th))-2+np.exp(b); dF=zt*(1-th)*np.exp(b*(1-th))+np.exp(b); b=b-F/dF
    return b.real
ok=(A[:,0]>10*2*s[0])&(q>0); qq=q[ok]; AA=A[ok,0]; rr=rate(qq.astype(float))
print("%d modes above 10 sigma"%ok.sum())
for lab,w in [("local density",np.ones_like(AA)),("cumulative p_1(n)",np.log(2)/np.abs(np.log(2)+2j*np.pi*qq))]:
    prev=None; print(lab+": dominant mode as x=log2 n grows (extrapolated):")
    for x in np.arange(30,4001,1.0):
        amp=AA*w*np.exp(-rr*(x-30)); i=np.argmax(amp)
        if qq[i]!=prev: print("   from x~%5.0f (n~10^%.0f): q=%d  amp=%.2e"%(x,x*np.log10(2),qq[i],amp[i])); prev=qq[i]
    # 665 vs 53 specifically
    i53=np.where(qq==53)[0][0]; i665=np.where(qq==665)[0][0]
    xc=30+np.log(AA[i53]*w[i53]/(AA[i665]*w[i665]))/(rr[i53]-rr[i665])
    print("   q=665 overtakes q=53 at x~%.0f (n~10^%.0f)"%(xc,xc*np.log10(2)))
