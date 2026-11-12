"""Where the Night Touches the Moon: the dragon of order 27 near its nearest missing point -u,
enlarged so that every Gaussian integer is a square. On the tangent line x = -u the missing
points are exactly the heights in the Moser-de Bruijn set (base-4 digits 0/1) -- the fact the
proof in math_dragon/PROOF.md rests on.   usage: python3 fjord_print.py OUT [K]"""
import sys, numpy as np
from scipy import ndimage as ndi
from hanga import Sheet, INK, SERIF_B, SERIF_I, SERIF
from fjord_pts import window
out=sys.argv[1]; K=int(sys.argv[2]) if len(sys.argv)>2 else 27
assert K%4==3; u=(2**(2*((K-2)//4)+1)+1)//3
NC=160; CELL=21; W=4096; S=Sheet(W,seed=17); sc=4
xa,xb=-u-112,-u-112+NC-1; ya,yb=-36,-36+NC-1
inD,dig=window(K,xa,xb,ya,yb)                     # rows: y from yb down to ya
xs=np.arange(xa,xb+1); ys=np.arange(yb,ya-1,-1); XX,YY=np.meshgrid(xs,ys)
disc=(XX.astype(float)**2+YY.astype(float)**2)<u*u
assert inD[disc].all()                             # the moon is inside the dragon
online=(XX==-u)&(~inD); heights=sorted(YY[online].tolist())
def moser(n):
    Y=[0]; p=1
    while p<=n: Y+=[v+p for v in Y]; p*=4
    return [v for v in Y if ya<=v<=yb]
assert heights==moser(yb), heights
m=10; cls=dig[m]+2*dig[m+1]+4*dig[m+2]; sub=sum(dig[7+i].astype(int)<<i for i in range(6))
X0=(W-NC*CELL)//2; Y0=190
def up(a):
    full=np.zeros((W,W),np.float32)
    full[Y0:Y0+NC*CELL,X0:X0+NC*CELL]=np.kron(a.astype(np.float32),np.ones((CELL,CELL),np.float32))
    return full
frame=np.zeros((W,W),np.float32); frame[Y0:Y0+NC*CELL,X0:X0+NC*CELL]=1
# hand-cut softness for all cell masks
soft=lambda a: ndi.gaussian_filter(a,1.6)
night=soft(up(~inD))*frame
S.block(night,INK['prussian'],strength=0.93,k=5,rim=0)
S.block(night,INK['indigo'],strength=0.88,bokashi=0.45+0.55*S.grad_r(X0/W+0.25,Y0/W+0.42,0.05,0.75),k=5,rim=0)
S.block(night,INK['sumi'],strength=0.30,k=2,rim=0)
# class / sub-class boundaries carved to paper
def bnd(A,mask):
    b=np.zeros(A.shape,bool)
    b[:,1:]|=(A[:,1:]!=A[:,:-1])&mask[:,1:]&mask[:,:-1]; b[1:,:]|=(A[1:,:]!=A[:-1,:])&mask[1:,:]&mask[:-1,:]
    return b
big_cls=np.kron(cls,np.ones((CELL,CELL),np.int16)); big_sub=np.kron(sub,np.ones((CELL,CELL),np.int16)); big_in=np.kron(inD,np.ones((CELL,CELL),bool))
def upb(b):
    full=np.zeros((W,W),np.float32); full[Y0:Y0+NC*CELL,X0:X0+NC*CELL]=b; return full
c1=ndi.gaussian_filter(upb(ndi.binary_dilation(bnd(big_cls,big_in),iterations=4)),1.2)
c2=ndi.gaussian_filter(upb(ndi.binary_dilation(bnd(big_sub,big_in),iterations=1)),1.0)
gy,gx=np.mgrid[0:W,0:W]
grid=((((gx-X0)%CELL)==0)|(((gy-Y0)%CELL)==0)).astype(np.float32)      # faint lattice: one square per integer
carve=np.clip(1-c1-0.55*c2-0.16*ndi.gaussian_filter(grid,0.6)*2,0,1)
INKS=[INK['celadon'],INK['peach'],INK['aqua'],INK['straw'],(0.74,0.70,0.86),INK['rose'],INK['moss'],INK['sky']]
DEEP=[INK['pine'],INK['vermilion'],INK['prussian'],INK['ochre'],INK['indigo'],INK['plum'],INK['pine'],INK['prussian']]
moon=soft(up(disc)); land=soft(up(inD))
for c in range(8):
    mk=inD&(cls==c)
    if not mk.any(): continue
    d=ndi.distance_transform_edt(np.kron(mk,np.ones((CELL,CELL),bool))).astype(np.float32)
    mm=soft(up(mk))*carve
    S.block(mm*(1-0.72*moon),INKS[c],strength=0.95,k=c%6,rim=0)
    S.block(mm*(1-moon),DEEP[c],strength=0.45,bokashi=upb(np.exp(-d/26.0)),k=c%6,rim=0)
S.block(moon,INK['straw'],strength=0.50,bokashi=S.grad_r((X0+(NC-48)*CELL)/W-0.02,0.5,0.02,0.55),k=1,rim=0)
# the missing points on the tangent line: vermilion squares
red=soft(up(online))
S.img[:]=S.img*(1-red[...,None])+red[...,None]*np.array([0.955,0.92,0.84],np.float32)
S.block(red,INK['vermilion'],strength=0.97,rim=0.25)
# key block: the circle (radius u about the origin, far off the sheet) and the frame
ox=X0+(0-xa+0.5)*CELL; oy=Y0+(yb-0+0.5)*CELL
rr=np.hypot(gx-ox,gy-oy); arc=np.exp(-((rr-u*CELL)/3.2)**2)*frame
fr=np.zeros((W,W),np.float32); t=9
fr[Y0-t:Y0,X0-t:X0+NC*CELL+t]=1; fr[Y0+NC*CELL:Y0+NC*CELL+t,X0-t:X0+NC*CELL+t]=1
fr[Y0-t:Y0+NC*CELL+t,X0-t:X0]=1; fr[Y0-t:Y0+NC*CELL+t,X0+NC*CELL:X0+NC*CELL+t]=1
S.key(np.clip(arc+fr,0,1),strength=0.88)
# heights written beside the squares, in the moon
items=[]
for h in heights:
    px=(X0+(-u-xa+1)*CELL+16)/W; py=(Y0+(yb-h+0.5)*CELL)/W
    items.append((px+(0.0 if h%4==0 else 0.016+0.004*len(str(h-1))),py,str(h),SERIF_B,0.0058,'lm'))
S.key(S.text_mask(items),strength=0.80,rough=0.2)
xl=(X0-9)/W; xr=(X0+NC*CELL+9)/W; yb_=(Y0+NC*CELL)/W
cap=S.text_mask([(xl,yb_+0.034,'Where the Night Touches the Moon',SERIF_B,0.0215,'ls'),
 (xl,yb_+0.060,f'The dragon of order {K}, enlarged: one square for each Gaussian integer. The moon\u2019s centre is {u:,} squares to the right.',SERIF_I,0.0152,'ls'),
 (xl,yb_+0.081,'Along the tangent the night comes ashore at heights 0, 1, 4, 5, 16, 17, 20, 21, 64, \u2026 \u2014 the numbers written with 0s and 1s in base four.',SERIF_I,0.0152,'ls'),
 (xr,yb_+0.034,'MO 514916',SERIF,0.0125,'rs')])
S.key(cap,strength=0.88,rough=0.25)
S.save(out)
