"""Verify the six-vertex hero sample: ice rule, frozen-corner purity, and that
the arctic curve is FOUR ELLIPSE ARCS (Colomo-Pronko ASM), not a circle."""
import numpy as np, sys

tag=sys.argv[1] if len(sys.argv)>1 else "hero512"
H=np.load(f"art_eygo/H_{tag}.npy").astype(np.int64); N=H.shape[0]-1
# 1) ice rule = valid +-1 height everywhere
ice = (np.abs(np.diff(H,axis=0))==1).all() and (np.abs(np.diff(H,axis=1))==1).all()
# 2) c-vertex field
f00=H[:-1,:-1]; f10=H[1:,:-1]; f11=H[1:,1:]; f01=H[:-1,1:]
isc=((f10-f00)*(f01-f11)>0); n=isc.shape[0]
k=n//7
corners={'BL':isc[:k,:k],'BR':isc[-k:,:k],'TL':isc[:k,-k:],'TR':isc[-k:,-k:]}
print(f"ice-rule valid: {ice}")
print(f"c-vertex density overall: {isc.mean()*100:.2f}%")
for nm,c in corners.items(): print(f"  frozen corner {nm}: c-density {c.mean()*100:.3f}% (want ~0)")
print(f"  temperate centre: c-density {isc[n//2-k:n//2+k,n//2-k:n//2+k].mean()*100:.2f}%")

# 3) arctic curve = boundary of temperate region; fit bottom arc to conic vs circle
# coarse c-density in (x=row,y=col); find, per x, the smallest y with temperate support
b=4; nb=n//b
D=isc[:nb*b,:nb*b].reshape(nb,b,nb,b).mean((1,3))       # coarse c-density
from scipy.ndimage import gaussian_filter
Ds=gaussian_filter(D.astype(float),1.0)
thr=0.06
pts=[]
for xi in range(nb):
    col=Ds[xi]
    yy=np.where(col>thr)[0]
    if yy.size>4:
        pts.append((xi, yy.min())); pts.append((xi, yy.max()))
for yi in range(nb):
    row=Ds[:,yi]; xx=np.where(row>thr)[0]
    if xx.size>4:
        pts.append((xx.min(), yi)); pts.append((xx.max(), yi))
P=np.array(pts,float); P=(P+0.5)/nb                      # normalize to [0,1]^2
x,y=P[:,0],P[:,1]
# circle fit: x^2+y^2 + Dx + Ey + F = 0
Ac=np.c_[x,y,np.ones_like(x)]; bc=-(x**2+y**2)
cc,_,_,_=np.linalg.lstsq(Ac,bc,rcond=None)
xc,yc=-cc[0]/2,-cc[1]/2; Rc=np.sqrt(xc**2+yc**2-cc[2])
res_circ=np.sqrt((x-xc)**2+(y-yc)**2)-Rc
# conic (ellipse) fit: A x^2+B xy+C y^2+D x+E y+F=0, ||.||=1
M=np.c_[x**2,x*y,y**2,x,y,np.ones_like(x)]
_,_,Vt=np.linalg.svd(M); conic=Vt[-1]
res_con=(M@conic)
# normalize conic residual to comparable scale (algebraic); report RMS of each
print(f"\narctic-curve fit ({len(P)} boundary pts):")
print(f"  best-fit CIRCLE: centre=({xc:.3f},{yc:.3f}) R={Rc:.3f}  RMS radial resid={np.sqrt((res_circ**2).mean()):.4f}")
A,B,Cc=conic[0],conic[1],conic[2]
disc=B**2-4*A*Cc
print(f"  best-fit CONIC:  B^2-4AC={disc:.3f} ({'ELLIPSE' if disc<0 else 'hyperbola/parab'})  algebraic RMS={np.sqrt((res_con**2).mean()):.4e}")
# temperate area fraction
print(f"\n temperate-area fraction (c-density>{thr}): {(Ds>thr).mean():.3f}")
