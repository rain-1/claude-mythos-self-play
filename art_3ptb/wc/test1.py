import numpy as np, sys, time
from PIL import Image
from wc import *
W=H=1024
t=time.time()
S=Sheet(H,W,seed=3)
s=S.s
C=dict(rose='#e8708f',mint='#58c7a2',butter='#f0c548',sky='#6aaee6',lilac='#a68ae0',peach='#f5966a')
K={k:pigment(hexrgb(v)) for k,v in C.items()}
cx,cy,R=W/2,H/2,0.36*W
def ngon(n,rot=-np.pi/2,k=1):
    a=rot+2*np.pi*k*np.arange(n)/n
    return np.stack([cx+R*np.cos(a),cy+R*np.sin(a)],1)
S.circle(cx,cy,R,0.8,overshoot=0.15)
S.wash_poly(ngon(10),K['butter'],dens=0.30,pool=0.25)
S.wash_poly(ngon(6),K['mint'],dens=0.30,pool=0.25)
S.wash_poly(ngon(5),K['rose'],dens=0.30,pool=0.25,bloom=0.5)
for n in (5,6,10):
    P=ngon(n); 
    for i in range(n): S.line(P[i],P[(i+1)%n],0.6,over=6*s)
print(time.time()-t)
Image.fromarray(to8(S.finish())).save('../proto/t1.png')
