"""The Moon the Dragon Keeps: binary dragon D_k (MO 514916), one pixel per Gaussian integer,
with the largest disc about 0 that it contains and the nearest missing point.
usage: python3 dragon_print.py K SIZE OUT   (K=18 -> 1024, K=22 -> 4096)"""
import sys, numpy as np
from scipy import ndimage as ndi
from hanga import Sheet, INK, fbm, stroke, SERIF_B, SERIF_I, SERIF
from dragon_pts import dragon, closed

def missing_pt(k):
    j=(k-2)//4; r=(k-2)%4; u=(2**(2*j+1)+1)//3
    return [(-(u-1)//2,(u+1)//2),(-u,0),(-u,-u),(0,-2*u)][r]

K=int(sys.argv[1]); size=int(sys.argv[2]); out=sys.argv[3]
x,y=dragon(K); idx=np.arange(len(x))
S=Sheet(size,seed=11); W=size; sc=W/1024
fx0,fy0,fx1,fy1=0.055,0.055,0.945,0.905
# place: lattice (x,y) -> pixel (cx + x - xm, cy - (y - ym)), dragon centred in the frame
xm=int(x.min()+x.max())//2; ym=int(y.min()+y.max())//2
cx=int(round((fx0+fx1)/2*W)); cy=int(round((fy0+fy1)/2*W))
px=cx+(x-xm); py=cy-(y-ym)
ok=(px>=0)&(px<W)&(py>=0)&(py<W); assert ok.all(), 'dragon does not fit'
L=np.full((W,W),-1,np.int16); L[py,px]=(idx&511).astype(np.int16)
ox=cx-xm; oy=cy+ym          # pixel of the origin
inD=(L>=0).astype(np.float32)
yy,xx=np.mgrid[0:W,0:W]
frame=((xx>=fx0*W)&(xx<fx1*W)&(yy>=fy0*W)&(yy<fy1*W)).astype(np.float32)
R=np.sqrt(closed(K)); rr=np.hypot(xx-ox,yy-oy).astype(np.float32)
moon=np.clip(R-0.5-rr,0,1)
assert inD[rr<R-0.01].all(), 'disc not inside dragon'
mx,my=missing_pt(K); mpx=ox+mx; mpy=oy-my; assert L[mpy,mpx]==-1 and abs(np.hypot(mx,my)-R)<1e-6

# ---- night ground, a few stars left as bare paper ----
far=ndi.distance_transform_edt(1-inD)
srng=np.random.default_rng(5); stars=np.zeros((W,W),np.float32)
for _ in range(90):
    sx=srng.uniform(fx0+0.02,fx1-0.02)*W; sy=srng.uniform(fy0+0.02,fy1-0.02)*W; r=srng.choice([1.3,1.3,1.8,1.8,2.6,3.6])*sc
    if far[int(sy),int(sx)]<28*sc: continue
    stars+=np.clip(r-np.hypot(xx-sx,yy-sy),0,1)
night=frame*(1-inD)*(1-np.clip(stars,0,1))
S.block(night,INK['prussian'],strength=0.93,k=5,rim=0)
S.block(night,INK['indigo'],strength=0.90,bokashi=0.35+0.65*S.grad_y(fy0-0.02,0.70,1.0),k=5,rim=0)
S.block(night,INK['sumi'],strength=0.45,bokashi=S.grad_y(fy0-0.02,0.40,1.2),k=2,rim=0)

# ---- dragon: 8 inks, bokashi toward each piece's edge, carved scale lines ----
INKS=[INK['celadon'],INK['peach'],INK['aqua'],INK['straw'],(0.74,0.70,0.86),INK['rose'],INK['moss'],INK['sky']]
DEEP=[INK['pine'],INK['vermilion'],INK['prussian'],INK['ochre'],INK['indigo'],INK['plum'],INK['pine'],INK['prussian']]
L8=np.where(L>=0,L&7,-1); L64=np.where(L>=0,L&63,-1); L512=L
def bnd(A):
    b=np.zeros(A.shape,bool)
    b[:,1:]|=(A[:,1:]!=A[:,:-1])&(A[:,1:]>=0)&(A[:,:-1]>=0)
    b[1:,:]|=(A[1:,:]!=A[:-1,:])&(A[1:,:]>=0)&(A[:-1,:]>=0)
    return b
c64=ndi.gaussian_filter(ndi.binary_dilation(bnd(L64),iterations=max(1,int(0.9*sc))).astype(np.float32),0.5*sc)
c512=ndi.gaussian_filter(bnd(L512).astype(np.float32),0.45*sc)
carve=np.clip(1-1.0*c64-(0.55 if K<20 else 0.8)*c512,0,1)
wb=7.0*sc*2**((K-18)/2)/ (sc)   # bokashi width follows the dragon, not the canvas
for c in range(8):
    m=(L8==c)
    d=ndi.distance_transform_edt(m).astype(np.float32)
    mm=m.astype(np.float32)*carve*(1-moon)
    S.block(mm,INKS[c],strength=0.95,k=c%6,rim=0.0)
    S.block(mm,DEEP[c],strength=0.50,bokashi=np.exp(-d/wb),k=c%6,rim=0.0)

# ---- the moon: bare paper, a breath of straw at the rim, the rings of earlier moons ----
S.block(moon,INK['straw'],strength=0.55,bokashi=np.clip((rr/R),0,1)**3,k=1,rim=0)
ring=np.zeros((W,W),np.float32); dots=np.zeros((W,W),np.float32)
for j,k in enumerate(range(K-1,max(K-13,5),-1)):
    r=np.sqrt(closed(k)); ring+=np.exp(-((rr-r)/(0.9*sc))**2)*(0.9 if j<8 else 0.5)
    qx,qy=missing_pt(k); dr=max(2.2*sc,7.0*sc*0.8**j)
    dots+=np.clip(dr-np.hypot(xx-(ox+qx),yy-(oy-qy)),0,1)
S.block(np.clip(ring,0,1)*moon,INK['slate'],strength=0.75,rim=0,grain=0.05)
S.block(np.clip(dots,0,1)*moon,INK['vermilion'],strength=0.80,rim=0)
# the nearest missing point: a vermilion seal dot on the rim, and the origin
dm=np.hypot(xx-mpx,yy-mpy); big=np.clip(15*sc-dm,0,1)*np.clip(dm-9.5*sc,0,1)
S.block(big,INK['vermilion'],strength=0.97,rim=0.3)
S.key(np.clip(np.exp(-((rr-R)/(1.1*sc))**2)+np.clip(4.5*sc-rr,0,1),0,1),strength=0.85)
# frame + caption
fr=np.zeros((W,W),np.float32); t=int(max(2,2.2*sc))
a,b,c_,d_=int(fx0*W),int(fy0*W),int(fx1*W),int(fy1*W)
fr[b:b+t,a:c_]=1; fr[d_-t:d_,a:c_]=1; fr[b:d_,a:a+t]=1; fr[b:d_,c_-t:c_]=1
S.key(fr,strength=0.9)
u=(2**((K-2)//4*2+1)+1)//3
cap=S.text_mask([(fx0,0.928,'The Moon the Dragon Keeps',SERIF_B,0.0215,'ls'),
  (fx0,0.957,f'Every pixel is a Gaussian integer; the dragon of order {K} holds {2**K:,} of them. The nearest one it lacks lies at distance \u221a{int(R*R):,} from 0.',SERIF_I,0.0152,'ls'),
  (fx1,0.928,'MO 514916',SERIF,0.0125,'rs')])
S.key(cap,strength=0.88,rough=0.25)
S.save(out)
