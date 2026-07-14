"""Companion 1 — 'The Only Road': the edge-violation potential over v9-space,
rendered as shaded relief. The flex locus {R=0} = a glowing gold road; the
forbidden terrain rises around it; the void = configs that cannot exist at all."""
import numpy as np, sys
from scipy.ndimage import gaussian_filter
from art_50e7.steffen_flex import trilaterate, config

s166=np.sqrt(166.0)
V1=np.array([0.0,-8.5,s166/2]); V2=np.array([0.0,8.5,s166/2])
V3=np.array([-5.5,0,0]); V4=np.array([5.5,0,0])
Vrest=config(0.0)
ref={5:Vrest[4],6:Vrest[5],7:Vrest[6],8:Vrest[7]}
STRUCT={5:[(V1,10),(V3,5)],6:[(V1,10),(V4,5)],7:[(V2,10),(V3,5)],8:[(V2,10),(V4,5)]}

def tri_vec(P1,P2,V9,r1,r2,r3,refpt):
    M=V9.shape[0]
    ex=(P2-P1); d=np.linalg.norm(ex); ex=ex/d
    W=V9-P1; i=W@ex
    temp=W - i[:,None]*ex[None,:]
    tn=np.linalg.norm(temp,axis=1); tn=np.where(tn<1e-9,1e-9,tn)
    ey=temp/tn[:,None]; ez=np.cross(np.broadcast_to(ex,(M,3)),ey)
    j=np.einsum('ij,ij->i',ey,W)
    x=(r1*r1-r2*r2+d*d)/(2*d); j=np.where(np.abs(j)<1e-9,1e-9,j)
    y=(r1*r1-r3*r3+i*i+j*j)/(2*j) - (i/j)*x
    z2=r1*r1-x*x-y*y; valid=z2>-1e-9
    z=np.sqrt(np.clip(z2,0,None))
    base=P1[None,:]+x*ex[None,:]+y[:,None]*ey
    s1=base+z[:,None]*ez; s2=base-z[:,None]*ez
    p1=np.linalg.norm(s1-refpt[None,:],axis=1)<=np.linalg.norm(s2-refpt[None,:],axis=1)
    return np.where(p1[:,None],s1,s2), valid

def resid_grid(ys,zs):
    Y,Z=np.meshgrid(ys,zs)
    V9=np.stack([np.zeros(Y.size),Y.ravel(),Z.ravel()],1)
    good=np.ones(V9.shape[0],bool); mv={}
    for j,lst in STRUCT.items():
        (P1,r1),(P2,r2)=lst
        sol,valid=tri_vec(P1,P2,V9,r1,r2,12.0,ref[j]); mv[j]=sol; good&=valid
    R =(np.linalg.norm(V3[None,:]-V9,axis=1)-10)**2+(np.linalg.norm(V4[None,:]-V9,axis=1)-10)**2
    R+=(np.linalg.norm(mv[5]-mv[6],axis=1)-11)**2+(np.linalg.norm(mv[7]-mv[8],axis=1)-11)**2
    return np.where(good,R,np.nan).reshape(Y.shape)

S=int(sys.argv[1]) if len(sys.argv)>1 else 900
ys=np.linspace(-13.5,13.5,S); zs=np.linspace(-13.5,13.5,S)
F=resid_grid(ys,zs)
valid=np.isfinite(F)
Rmax=np.nanmax(F)
Ff=np.where(valid,F,Rmax*1.5)

# terrain potential (log) + hillshade
terr=np.log1p(Ff)
tn=(terr-terr.min())/(np.ptp(terr)+1e-9)
sc=S/700.0
gy,gx=np.gradient(gaussian_filter(tn,1.4*sc))
lz=1.0/np.sqrt(1+ (gx/sc*55)**2+(gy/sc*55)**2)
shade=np.clip(0.30+1.0*lz,0,1.2)
# subtle topographic sediment (gentle, non-mechanical)
bands=0.5+0.5*np.cos(2*np.pi*terr/(np.ptp(terr)/13))
sed=0.93+0.07*bands

# palette: deep indigo basin (low R, near road) -> warm violet/ember ridges (high R)
base=np.zeros((S,S,3))
c_basin=np.array([0.12,0.15,0.34])   # cool near the road
c_mid  =np.array([0.40,0.24,0.42])   # violet slope
c_ridge=np.array([0.72,0.40,0.30])   # warm ember ridge (costly configs)
def ramp(t):
    t=t[...,None]
    lo=np.where(t<0.5, c_basin*(1-2*t)+c_mid*(2*t), c_mid*(1-2*(t-0.5))+c_ridge*(2*(t-0.5)))
    return lo
# gate luminance by FEASIBILITY: only the basin hugging the road glows;
# the far, costly ridges dissolve into the void (focus + negative space)
focus=np.exp(-Ff/7.0)
base=ramp(tn)*shade[...,None]*sed[...,None]*(0.07+0.98*focus)[...,None]
void=~valid
base[void]=np.array([0.02,0.025,0.06])

# full road-ring gamma: y^2+z^2 = r^2, brightness = realizability exp(-R)
r_g=np.sqrt(69.75)
gold=np.array([1.0,0.82,0.42])
Yg,Zg=np.meshgrid(ys,zs)
ringd=np.abs(np.sqrt(Yg**2+Zg**2)-r_g)          # distance to gamma (world units)
du=(ys[1]-ys[0])
ring=np.exp(-(ringd/(1.4*du))**2)               # thin ring mask
sc=S/700.0
real=np.exp(-Ff/0.8)                             # realizable where R~0
ring_bright=ring*(0.18+1.0*real)                 # dim ghost ring + bright open arc
for c in range(3):
    base[...,c]+=1.7*ring_bright*gold[c]
rb=gaussian_filter(ring*real,4*sc)+0.5*gaussian_filter(ring*real,14*sc)
for c in range(3):
    base[...,c]+=0.9*rb*gold[c]

img=1.0-np.exp(-1.6*base)
img=np.clip(img,0,1)**0.92
from PIL import Image
out=(np.clip(img[::-1],0,1)*255).astype(np.uint8)
name='proto_road.png' if S<2000 else 'comp_road.png'
Image.fromarray(out).save('/home/user/claude-mythos-self-play/art_50e7/'+name)
print("saved %s; valid frac %.2f open-arc px %d"%(name,valid.mean(),int((ring*real>0.3).sum())))
