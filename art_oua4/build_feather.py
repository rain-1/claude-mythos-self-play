import numpy as np, time, sys
from PIL import Image
from scipy.ndimage import gaussian_filter

N    = int(sys.argv[1]) if len(sys.argv)>1 else 60000
S    = int(sys.argv[2]) if len(sys.argv)>2 else 1400
ae   = float(sys.argv[3]) if len(sys.argv)>3 else 0.070
ao   = float(sys.argv[4]) if len(sys.argv)>4 else 0.110
tag  = sys.argv[5] if len(sys.argv)>5 else ""
rotd = float(sys.argv[6]) if len(sys.argv)>6 else -51.0

def traj_par(n):
    out=[n%2]; v=n
    while v!=1:
        v=v//2 if v%2==0 else 3*v+1; out.append(v%2)
    return out[::-1]  # root(1)->leaf

t0=time.time()
ALLX=[];ALLY=[]; xmin=ymin=1e9;xmax=ymax=-1e9
cxs=0.0;cys=0.0;cnt=0
for n in range(2,N+1):
    par=np.array(traj_par(n))
    dang=np.where(par[1:]==0,ae,-ao)
    ang=np.concatenate([[np.pi/2],np.pi/2+np.cumsum(dang)])
    x=np.concatenate([[0.0],np.cumsum(np.cos(ang[1:]))])
    y=np.concatenate([[0.0],np.cumsum(np.sin(ang[1:]))])
    ALLX.append(x);ALLY.append(y)
    cxs+=x.sum();cys+=y.sum();cnt+=len(x)
    xmin=min(xmin,x.min());xmax=max(xmax,x.max());ymin=min(ymin,y.min());ymax=max(ymax,y.max())
print("built",N-1,"polylines in",round(time.time()-t0,1),"s")

# rotate by rotd (deg) so the bright spine stands vertical, tip(value 1) at bottom
rot=np.radians(rotd)
cR,sR=np.cos(rot),np.sin(rot)

t0=time.time()
acc=np.zeros((S,S),np.float64)
# recompute bbox after rotation (origin = tip = value 1 stays at (0,0))
RX=[];RY=[]
xmn=ymn=1e9;xmx=ymx=-1e9
for x,y in zip(ALLX,ALLY):
    rx=cR*x - sR*y; ry=sR*x + cR*y
    RX.append(rx);RY.append(ry)
    xmn=min(xmn,rx.min());xmx=max(xmx,rx.max());ymn=min(ymn,ry.min());ymx=max(ymx,ry.max())
dxf  = float(sys.argv[7]) if len(sys.argv)>7 else -0.159
dyf  = float(sys.argv[8]) if len(sys.argv)>8 else 0.10
W=xmx-xmn;H=ymx-ymn; mg=0.05
sc=(1-2*mg)*S/max(W,H)
ox=S/2 - sc*(xmn+xmx)/2 + dxf*S         # centre on bright mass
oy=S/2 - sc*(ymn+ymx)/2 + dyf*S
samp_per_px=1.0
for rx,ry in zip(RX,RY):
    X=ox+sc*rx; Y=S-1-(oy+sc*ry)  # tip(origin) -> lower area since ry small; canopy up
    seg=np.hypot(np.diff(X),np.diff(Y)); cum=np.concatenate([[0],np.cumsum(seg)]); tot=cum[-1]
    ns=max(2,int(tot*samp_per_px)); s=np.linspace(0,tot,ns)
    px=np.interp(s,cum,X); py=np.interp(s,cum,Y)
    xi=np.floor(px).astype(int); yi=np.floor(py).astype(int); fx=px-xi; fy=py-yi
    for ddx,wx in ((0,1-fx),(1,fx)):
        for ddy,wy in ((0,1-fy),(1,fy)):
            Xp=xi+ddx;Yp=yi+ddy;mm=(Xp>=0)&(Xp<S)&(Yp>=0)&(Yp<S)
            np.add.at(acc,(Yp[mm],Xp[mm]),(wx*wy)[mm])
print("rasterized in",round(time.time()-t0,1),"s  acc max",round(acc.max(),1))
np.save(f"/home/user/claude-mythos-self-play/art_oua4/feather_acc{tag}.npy",acc)
print("saved acc", tag)
