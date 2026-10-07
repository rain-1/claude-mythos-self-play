"""Glass terraces of the Riemann curve's winding number: layer k = {w >= k}, a floating tinted glass plate.
Numpy ray caster: jittered passes, soft sun, polka-dot paper table, coloured shadows, edge glints, fresnel sky."""
import numpy as np, sys, argparse
from PIL import Image
ap=argparse.ArgumentParser()
ap.add_argument('--field',default='proto/hf2000.npz'); ap.add_argument('--W',type=int,default=900); ap.add_argument('--H',type=int,default=1100)
ap.add_argument('--passes',type=int,default=6); ap.add_argument('--out',default='proto/h1.png')
ap.add_argument('--K',type=int,default=9); ap.add_argument('--th',type=float,default=0.10); ap.add_argument('--gap',type=float,default=0.30)
ap.add_argument('--z0',type=float,default=0.35); ap.add_argument('--elev',type=float,default=52); ap.add_argument('--dist',type=float,default=24)
ap.add_argument('--fov',type=float,default=0.42); ap.add_argument('--sun',type=str,default='-0.55,0.75,0.62'); ap.add_argument('--ya',type=int,default=0); ap.add_argument('--yb',type=int,default=-1)
ap.add_argument('--cy',type=float,default=-0.2); ap.add_argument('--npy',default='')
ap.add_argument('--s1',type=float,default=2.0); ap.add_argument('--s2',type=float,default=6.0); ap.add_argument('--expo',type=float,default=1.12)
a=ap.parse_args()
F=np.load(a.field); Wf=F["w"].astype(np.int16); U0,U1,V0,V1=F['ext']; G=Wf.shape[0]
K=a.K
# sorbet wheel per layer (layer 1 = pale strawberry ... )
WHEEL=np.array([[0.98,0.55,0.62],[1.0,0.68,0.52],[1.0,0.86,0.50],[0.80,0.93,0.55],[0.55,0.90,0.78],[0.55,0.80,0.98],[0.66,0.70,1.0],[0.80,0.66,0.98],[0.97,0.62,0.86]])
def tint(k): return WHEEL[(k-1)%len(WHEEL)]
SIG=np.array([-np.log(np.clip(tint(k),0.05,1))*(a.s1 if k==1 else a.s2) for k in range(1,K+1)])  # absorbance per unit thickness... scaled by th below
def lookup(u,v):
    i=np.clip(((u-U0)/(U1-U0)*G).astype(np.int32),0,G-1); j=np.clip(((v-V0)/(V1-V0)*G).astype(np.int32),0,G-1)
    out=Wf[j,i]; out[(u<U0)|(u>U1)|(v<V0)|(v>V1)]=0; return out
zb=[a.z0+(k-1)*(a.th+a.gap) for k in range(1,K+1)]
sun=np.array([float(s) for s in a.sun.split(',')]); sun/=np.linalg.norm(sun)
# camera: looks at (0,cy,~1) from the front (negative v) at elevation
el=np.radians(a.elev); tgt=np.array([0.0,a.cy,0.9])
cam=tgt+a.dist*np.array([0,-np.cos(el),np.sin(el)])
fw=(tgt-cam)/np.linalg.norm(tgt-cam); rt=np.cross(fw,[0,0,1.0]); rt/=np.linalg.norm(rt); up=np.cross(rt,fw)
W,H=a.W,a.H; yb=H if a.yb<0 else a.yb; ya=a.ya
rng=np.random.default_rng(7)
def dots(u,v):
    # sparse sorbet polka dots on cool white paper, hex lattice
    s=0.9; q=v/(s*0.866); r=np.round(q); uu=u/s-0.5*(r%2); c=np.round(uu)
    du=(uu-c)*s; dv=(q-r)*s*0.866; d=np.sqrt(du*du+dv*dv)
    idx=((c*7+r*13)%6).astype(int)
    DOT=np.array([[1,0.80,0.84],[1,0.90,0.76],[0.84,0.95,0.84],[0.80,0.90,1],[0.90,0.84,1],[1,0.95,0.78]])
    m=np.clip((0.075-d)/0.012,0,1)[...,None]
    base=np.array([0.995,0.99,0.985])
    return base*(1-m)+DOT[idx]*m
acc=np.zeros((yb-ya,W,3),np.float32)
for p in range(a.passes):
    jx,jy=rng.random(2)
    xs=(np.arange(W)+jx-W/2)/W*2*a.fov; ys=-(np.arange(ya,yb)+jy-H/2)/W*2*a.fov
    X,Y=np.meshgrid(xs,ys)
    d=fw[None,None,:]+X[...,None]*rt+Y[...,None]*up; d/=np.linalg.norm(d,axis=-1,keepdims=True)
    # soft sun jitter
    sj=sun+0.035*rng.standard_normal(3); sj/=np.linalg.norm(sj)
    T=np.ones(X.shape+(3,),np.float32); refl=np.zeros(X.shape+(3,),np.float32); glint=np.zeros(X.shape,np.float32)
    # traverse layers from top (nearest camera) to bottom
    for k in range(K,0,-1):
        zt=zb[k-1]+a.th; zm=zb[k-1]+a.th/2; z1=zb[k-1]
        pts=[cam[None,None,:]+d*((zz-cam[2])/d[...,2])[...,None] for zz in (zt,zm,z1)]
        ins=[lookup(pp[...,0],pp[...,1])>=k for pp in pts]
        frac=(ins[0].astype(np.float32)+ins[1]+ins[2])/3
        path=a.th/np.abs(d[...,2])
        cosi=np.abs(d[...,2]); R=0.04+0.96*(1-cosi)**5
        top=ins[0].astype(np.float32)
        sky=np.array([0.93,0.96,1.0])
        refl+=T*(top*R)[...,None]*sky
        T*=(1-top*R)[...,None]
        T*=np.exp(-SIG[k-1][None,None,:]*(frac*path)[...,None])
        edge=(ins[0]!=ins[2])
        glint+=edge*np.clip(np.dot(d.reshape(-1,3),-sj).reshape(X.shape)*0.5+0.7,0,1)*T.mean(-1)
    # table hit
    P=cam[None,None,:]+d*((0-cam[2])/d[...,2])[...,None]
    alb=dots(P[...,0],P[...,1])
    S=np.ones(X.shape+(3,),np.float32)
    for k in range(1,K+1):
        zm=zb[k-1]+a.th/2; q=P+sj*(zm/sj[2])
        ins=lookup(q[...,0],q[...,1])>=k
        S*=np.where(ins[...,None],np.exp(-SIG[k-1]*a.th/sj[2])*0.93,1)
    # ambient occlusion-ish: soft coverage straight above
    cov=(lookup(P[...,0],P[...,1])>=1).astype(np.float32)
    sunc=np.array([1.0,0.97,0.92]); amb=np.array([0.80,0.86,1.0])
    L=sunc*S*0.78+amb*0.34*(1-0.18*cov[...,None])
    col=alb*L*T+refl+glint[...,None]*0.55*np.array([1,1,1])
    acc+=col
img=acc/a.passes
if a.npy: np.save(a.npy,img); sys.exit()
x=img*a.expo; x=x*(1+x/1.44)/(1+x)  # extended reinhard white 1.2
Image.fromarray((np.clip(x,0,1)**(1/1.0)*255).astype(np.uint8)).save(a.out)
