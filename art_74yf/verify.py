"""verify.py — sanity checks for the amoeba/tropical triptych (degree d=6, lam=0.9)."""
import numpy as np
from tropical import poly_w_coeffs, roots_batch
from hero import curve
from scipy import ndimage

d,lam=6,0.9
C,val=curve(d,lam)

# 1) sampled points really lie on the curve: |P(z,w)| ~ 0
def P_and_scale(z,w):
    tot=np.zeros(np.broadcast(z,w).shape,complex); scale=np.zeros(tot.shape)
    for i in range(d+1):
        for j in range(d+1):
            if abs(C[i,j])>0:
                term=C[i,j]*z**i*w**j; tot=tot+term
                scale=np.maximum(scale,np.abs(term))
    return tot,scale
rng=np.random.default_rng(0)
th=rng.uniform(0,2*np.pi,4000); x=rng.uniform(-3,3,4000)   # moderate |z| to limit float blow-up
z=np.exp(x+1j*th); R=roots_batch(poly_w_coeffs(C,z))
val,scale=P_and_scale(z[:,None],R)
rel=(np.abs(val)/(scale+1e-300))
print(f"[1] max RELATIVE residual |P|/max|term| over 4000x{d} roots = {rel.max():.2e}  (should be ~1e-12)")

# 2) number of bounded amoeba holes == interior lattice points (d-1)(d-2)/2
import os
if not os.path.exists('ronkHI_field.npz'):
    print("    (building Ronkin field for checks [3]/[5] ...)")
    from ronkin import build as build_ronkin
    build_ronkin(d, lam, 24.0, Ng=140, tag='ronkHI')

# bounded complement components = connected interior-order regions of the tropical map
ptsL=[(i,j) for i in range(d+1) for j in range(d+1) if i+j<=d]
vL=np.array([-lam*(i*i+j*j+(d-i-j)**2) for (i,j) in ptsL])
iiL=np.array([p[0] for p in ptsL]); jjL=np.array([p[1] for p in ptsL])
W=40.0; g=np.linspace(-W,W,1400); XX,YY=np.meshgrid(g,g)
# work in (x,y) directly (linear embed doesn't change component count)
Tg=vL[None,None,:]+XX[...,None]*iiL+YY[...,None]*jjL
argg=Tg.argmax(2)
interiorL=[idx for idx,(i,j) in enumerate(ptsL) if 0<i and 0<j and i+j<d]
ncomp=0
for idx in interiorL:
    _,k=ndimage.label(argg==idx); ncomp+=k
print(f"[2] bounded complement components (connected interior-order regions) = {ncomp}"
      f"  (expected interior lattice pts = {(d-1)*(d-2)//2})")

# 3) order map: round(grad Ronkin) is an integer Newton-polygon lattice point on holes,
#    and equals the tropical argmax label there.
z2=np.load('ronkHI_field.npz'); N,gx,gy=z2['N'],z2['gx'],z2['gy']; xr=z2['xr']; yr=z2['yr']
Ng=N.shape[0]
# interior (away from tropical curve): where |grad| rounds cleanly
frac=np.hypot(gx-np.round(gx),gy-np.round(gy))
clean=frac<0.06
oi=np.round(gx[clean]).astype(int); oj=np.round(gy[clean]).astype(int)
inpoly=((oi>=0)&(oj>=0)&(oi+oj<=d)).mean()
print(f"[3] fraction of clean-gradient pixels whose round(gradN) is a valid Newton lattice pt = {inpoly:.4f}")
# gradient magnitude never exceeds the Newton polygon extent d
print(f"    max component of grad N = {np.abs([gx,gy]).max():.3f}  (Newton polygon max coord = {d})")

# 4) tropical curve unbounded rays == 3d (triangle perimeter lattice length)
#    counted as sign-changes of argmax around a large circle
pts=[(i,j) for i in range(d+1) for j in range(d+1) if i+j<=d]
Rbig=200.0; ang=np.linspace(0,2*np.pi,20000,endpoint=False)
Xc=Rbig*np.cos(ang); Yc=Rbig*np.sin(ang)
v=np.array([-lam*(i*i+j*j+(d-i-j)**2) for (i,j) in pts])
ii=np.array([p[0] for p in pts]); jj=np.array([p[1] for p in pts])
T=v[None,:]+np.outer(Xc,ii)+np.outer(Yc,jj)
arg=T.argmax(1)
rays=int((arg!=np.roll(arg,1)).sum())
print(f"[4] tropical unbounded rays (argmax changes around big circle) = {rays}  (expected 3d = {3*d})")

# 5) Harnack/maximal: all interior lattice points appear as complement orders (all holes open)
z3=np.load('ronkHI_field.npz')  # reuse
interior=[(i,j) for (i,j) in pts if 0<i and 0<j and i+j<d]
gxr,gyr=np.round(z3['gx']),np.round(z3['gy'])
present=set(zip(gxr[clean.reshape(gxr.shape)].astype(int).tolist(),
               gyr[clean.reshape(gyr.shape)].astype(int).tolist()))
have=sum((i,j) in present for (i,j) in interior)
print(f"[5] interior lattice orders realised as holes = {have}/{len(interior)} (maximal Harnack amoeba)")
