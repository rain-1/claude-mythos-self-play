"""MO 515776: normalised increments Q_x(h) = (R(x+h)-R(x))/h^{3/4} of Riemann's function R = pi*Re(phi),
x in [0,2] across, log h down (big h at the top). Warm = rising, cool = falling. Right panel: the law of Q
for each row (conditional density) — the same law at every scale."""
import numpy as np, sys, argparse
from riemann import phi
from PIL import Image
from scipy.ndimage import gaussian_filter
ap=argparse.ArgumentParser(); ap.add_argument('--W',type=int,default=1400); ap.add_argument('--H',type=int,default=900)
ap.add_argument('--logM',type=int,default=22); ap.add_argument('--out',default='proto/cur1.png'); ap.add_argument('--npy',default='')
ap.add_argument("--panel",type=float,default=0.16); ap.add_argument("--dens",type=float,default=0.75)
a=ap.parse_args()
M=1<<a.logM; R=np.pi*phi(M,nmax=400000).real
SS=2
Wc=int(a.W*(1-a.panel)); Wp=a.W-Wc
Hc=a.H
# rows: h from 1.0 down to ~ 2 pixel widths
hmax=1.0; hmin=2*2.0/Wc/SS*0.5
hs=np.geomspace(hmax,hmin,Hc*SS)
ms=np.maximum(1,np.round(hs*M/2).astype(np.int64))
cur=np.zeros((Hc*SS,Wc*SS)); law=np.zeros((Hc*SS,Wp*SS))
qgrid=np.linspace(-9,9,Wp*SS+1)
bins=M//(Wc*SS)
for r,m in enumerate(ms):
    h=2*m/M; Q=(np.roll(R,-m)-R)/h**0.75
    cur[r]=Q[:bins*Wc*SS].reshape(Wc*SS,bins).mean(1)
    hist,_=np.histogram(Q,bins=qgrid); law[r]=hist/hist.max()
if a.npy: np.savez(a.npy,cur=cur,law=law,hs=hs)
# colour
STRAW=np.array([0.98,0.52,0.60]); PEACH=np.array([1.0,0.74,0.56]); SKY=np.array([0.52,0.76,1.0]); PERI=np.array([0.64,0.62,1.0])
PAPER=np.array([0.994,0.990,0.984])
v=np.tanh(cur/3.2)
mag=np.abs(v)[...,None]
warm=PEACH*(1-mag)+STRAW*mag; cool=SKY*(1-mag)+PERI*mag
tint=np.where(v[...,None]>0,warm,cool)
A=-np.log(np.clip(tint,0.05,1))*a.dens*mag**0.9
img=PAPER*np.exp(-A)
# law panel: density as lilac silk, coral threads at the M^-4 tail
L=gaussian_filter(law,(1.0,1.0))
dens=np.clip(L,0,1)**0.45
LIL=np.array([0.80,0.70,0.98])
pan=PAPER*np.exp(-(-np.log(LIL))*2.2*dens[...,None])
gap=np.ones((Hc*SS,6*SS,3))*PAPER
full=np.concatenate([img,gap,pan],axis=1)[:, :a.W*SS]
im=Image.fromarray((np.clip(full,0,1)*255).astype(np.uint8)).resize((a.W,a.H),Image.LANCZOS)
im.save(a.out)
