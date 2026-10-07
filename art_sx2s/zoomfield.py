"""Winding + nearest-time field in a zoom box around phi(tc). Curve = FFT samples (2^logM) with the window
|t-tc|<Hw replaced by dense direct sums (numba)."""
import numpy as np, sys, argparse
from riemann import phi
from wind import winding
from local import phi_at
from scipy.ndimage import distance_transform_edt
ap=argparse.ArgumentParser(); ap.add_argument('--tc',type=float,default=1.0); ap.add_argument('--L',type=float,default=0.03)
ap.add_argument('--cx',type=float,default=None); ap.add_argument('--cy',type=float,default=None)
ap.add_argument('--G',type=int,default=2000); ap.add_argument('--Hw',type=float,default=0.03); ap.add_argument('--nd',type=int,default=2000000)
ap.add_argument('--N',type=int,default=3000); ap.add_argument('--logM',type=int,default=23); ap.add_argument('--out')
a=ap.parse_args()
M=1<<a.logM; zf=phi(M,nmax=300000); tf=np.arange(M)*2.0/M
td=np.linspace(a.tc-a.Hw,a.tc+a.Hw,a.nd); zd=phi_at(td%2.0,a.N)
keep=np.abs(((tf-a.tc+1)%2)-1)>=a.Hw
t_all=np.concatenate([tf[keep],td]); z_all=np.concatenate([zf[keep],zd])
o=np.argsort((t_all-a.tc-a.Hw)%2.0); t_all=t_all[o]; z_all=z_all[o]
c0=phi_at(np.array([a.tc%2.0]),a.N)[0]
cx=c0.real if a.cx is None else a.cx; cy=c0.imag if a.cy is None else a.cy
print('centre',cx,cy)
G=a.G; X=(z_all.real-(cx-a.L))/(2*a.L)*G; Y=(z_all.imag-(cy-a.L))/(2*a.L)*G
w=-winding(X,Y,G,G)
print(np.unique(w,return_counts=True))
s=np.minimum(t_all%2,2-t_all%2)
inb=(X>=0)&(X<G)&(Y>=0)&(Y<G)
grid=np.full((G,G),-1.0,np.float32); grid[Y[inb].astype(int),X[inb].astype(int)]=s[inb]
if (grid>=0).any():
    d,(J,I)=distance_transform_edt(grid<0,return_indices=True); smap=grid[J,I]
else: smap=np.zeros((G,G))
np.savez_compressed(a.out,w=np.clip(w,-1,120).astype(np.int8),ext=np.array([cx-a.L,cx+a.L,cy-a.L,cy+a.L]),s=smap.astype(np.float16))
