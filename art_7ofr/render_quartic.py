# The quartic surface x^4+y^4+2z^4=1 painted by the Bremner-Choudhry-Ulas elliptic fibration
#   t = 2(xy+z^2)/(x^2+y^2+1)   (each level set is a genus-1 curve; MO 515812)
import numpy as np, json, sys
from PIL import Image

def f(p): return p[...,0]**4+p[...,1]**4+2*p[...,2]**4-1
def gradf(p): return np.stack([4*p[...,0]**3,4*p[...,1]**3,8*p[...,2]**3],-1)
def tfun(p):
    x,y,z=p[...,0],p[...,1],p[...,2]; return 2*(x*y+z*z)/(x*x+y*y+1)

TARGET=(0,0,-0.08)
def look(eye,target,up=(0,0,1)):
    fwd=np.array(target,float)-eye; fwd/=np.linalg.norm(fwd)
    r=np.cross(fwd,up); r/=np.linalg.norm(r); u=np.cross(r,fwd); return fwd,r,u

def hit(o,d,maxit=None):
    sh=d.shape[:-1]; o=np.broadcast_to(o,d.shape).reshape(-1,3); d=d.reshape(-1,3)
    b=(o*d).sum(-1); c=(o*o).sum(-1)-1.25**2; mm=(b*b-c)>0
    F=np.zeros(len(d),bool); S=np.zeros(len(d)); Pp=np.zeros((len(d),3))
    if mm.any():
        f_,s_,p_=_hit(o[mm],d[mm]); F[mm]=f_; S[mm]=s_; Pp[mm]=p_
    return F.reshape(sh),S.reshape(sh),Pp.reshape(sh+(3,))

def _hit(o,d):
    # convex body inside sphere radius 1.25: march to the first sign change, then bisect
    b=(o*d).sum(-1); c=(o*o).sum(-1)-1.25**2; disc=b*b-c
    m=disc>0; sq=np.sqrt(np.clip(disc,0,None)); s0=-b-sq; s1=-b+sq
    n=48; lo=s0.copy(); hi=s0.copy(); found=np.zeros(s0.shape,bool)
    for k in range(1,n+1):
        sk=s0+(s1-s0)*k/n
        inside=f(o+sk[...,None]*d)<0
        new=inside&~found&m
        lo=np.where(new,s0+(s1-s0)*(k-1)/n,lo); hi=np.where(new,sk,hi); found|=new
    for _ in range(36):
        mid=(lo+hi)/2; inside=f(o+mid[...,None]*d)<0
        hi=np.where(inside,mid,hi); lo=np.where(inside,lo,mid)
    p=o+hi[...,None]*d
    return found,hi,p

def hsv2rgb(h,s,v):
    h=(h%1)*6; i=np.floor(h).astype(int); fr=h-i
    p=v*(1-s); q=v*(1-s*fr); t=v*(1-s*(1-fr))
    out=np.zeros(h.shape+(3,))
    for k,(a,b,c) in enumerate([(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)]):
        mk=i%6==k; out[mk]=np.stack([a[mk] if np.ndim(a) else np.full(mk.sum(),a),b[mk] if np.ndim(b) else np.full(mk.sum(),b),c[mk] if np.ndim(c) else np.full(mk.sum(),c)],-1)
    return out

WHEEL=np.array([[0.98,0.62,0.68],[1.0,0.76,0.62],[1.0,0.90,0.62],[0.80,0.93,0.62],[0.62,0.92,0.80],[0.62,0.84,0.97],[0.70,0.74,0.98],[0.84,0.70,0.96],[0.98,0.68,0.88],[0.98,0.62,0.68]])
def wheel(u):
    u=np.clip(u,0,1)*(len(WHEEL)-1); i=np.minimum(u.astype(int),len(WHEEL)-2); fr=(u-i)[...,None]
    return WHEEL[i]**(1-fr)*WHEEL[i+1]**fr

def render(W=1024,out='_quartic.png',eye=(2.6,-3.4,2.2),nb=40,pts=None,t0=None,fov=0.42,yarn=0.004):
    eye=np.array(eye,float); fwd,r,u=look(eye,TARGET)
    yy,xx=np.mgrid[0:W,0:W]
    sx=(xx+0.5-W/2)/(W/2)*fov; sy=-(yy+0.5-W/2)/(W/2)*fov
    d=fwd+sx[...,None]*r+sy[...,None]*u; d/=np.linalg.norm(d,axis=-1,keepdims=True)
    o=np.broadcast_to(eye,d.shape)
    ok,s,p=hit(o,d)
    img=np.ones((W,W,3))*np.array([0.992,0.986,0.978])
    L=np.array([-0.45,-0.55,0.75]); L/=np.linalg.norm(L)
    # ground plane z=-zmax-0.02, soft shadow by sampling a few light directions
    zg=-(0.5**0.25)-0.02
    tg=(zg-eye[2])/d[...,2]; g=(tg>0)&~ok
    pg=eye+tg[...,None]*d
    rng=np.random.default_rng(0)
    Wl=min(W,512); yl,xl=np.mgrid[0:Wl,0:Wl]
    sxl=(xl+0.5-Wl/2)/(Wl/2)*fov; syl=-(yl+0.5-Wl/2)/(Wl/2)*fov
    dl=fwd+sxl[...,None]*r+syl[...,None]*u; dl/=np.linalg.norm(dl,axis=-1,keepdims=True)
    tl=(zg-eye[2])/dl[...,2]; gl=tl>0; pl=eye+tl[...,None]*dl
    shl=np.zeros(gl.shape)
    for j in range(16):
        Lj=L+0.10*rng.normal(size=3); Lj/=np.linalg.norm(Lj)
        okj,_,_=hit(pl[gl]+1e-3*Lj,np.broadcast_to(Lj,pl[gl].shape))
        shl[gl]+=okj/16
    from PIL import Image as _I
    sh=np.asarray(_I.fromarray(shl.astype(np.float32)).resize((W,W),_I.BICUBIC))
    shade=np.array([0.62,0.62,0.86])
    img[g]=img[g]*(1-0.30*sh[g][:,None]*(1-shade))
    # surface
    P=p[ok]; N=gradf(P); N/=np.linalg.norm(N,axis=-1,keepdims=True)
    T=tfun(P); tmin,tmax=-1.0,1.6
    v=(T-tmin)/(tmax-tmin)
    base=wheel(v)
    vK=v*nb
    vfull=np.where(ok,(tfun(p)-tmin)/(tmax-tmin)*nb,0)
    gy,gx=np.gradient(vfull); gm=np.hypot(gx,gy)[ok]+1e-6
    j=np.round(vK); dl=(vK-j)/gm            # signed pixel distance to the nearest strand centre
    wpx=W*yarn
    q=np.clip(np.abs(dl)/wpx,0,1)
    cov=np.clip((wpx-np.abs(dl))*1.0,0,1)
    hue=wheel(np.clip(j/nb,0,1))
    tube=np.sqrt(1-q**2)
    strand=hue**1.5*(0.70+0.30*tube)[:,None]+0.22*(tube**8)[:,None]
    pearlc=np.array([0.985,0.975,0.99])
    col=pearlc*(1-cov[:,None])+strand*cov[:,None]
    T=T
    if t0 is not None:
        e0=np.abs((T-t0)/(tmax-tmin)*nb)/gm
        c0=np.clip(W*yarn*1.3-e0,0,1)
        col=col*(1-c0[:,None])+c0[:,None]*np.array([0.97,0.45,0.42])
    diff=np.clip(N@L,0,1); amb=0.55+0.25*N[:,2]
    V=-d[ok]; H=L+V; H/=np.linalg.norm(H,axis=-1,keepdims=True)
    spec=np.clip((N*H).sum(-1),0,1)**60
    fres=(1-np.clip((N*V).sum(-1),0,1))**4
    c=col*(0.74+0.12*amb+0.22*diff)[:,None]+0.35*spec[:,None]*(1-0.5*cov[:,None])+0.10*fres[:,None]
    img[ok]=c
    if pts is not None:
        # beads at rational points: projected discs with simple shading
        Pp=np.array(pts)
        rel=Pp[:,:3]-eye; zc=rel@fwd; px=(rel@r)/zc/fov*(W/2)+W/2; py=-(rel@u)/zc/fov*(W/2)+W/2
        nn=gradf(Pp[:,:3]); nn/=np.linalg.norm(nn,axis=-1,keepdims=True)
        vis=(nn*(eye-Pp[:,:3])).sum(-1)>0
        for i in np.argsort(-zc):
            if not vis[i]: continue
            rad=W*0.010*max(0.35,1.2-0.18*np.log10(max(10,Pp[i,3])))
            x0,y0=px[i],py[i]
            ys,xs=np.mgrid[int(y0-rad-2):int(y0+rad+3),int(x0-rad-2):int(x0+rad+3)]
            rr=np.hypot(xs-x0,ys-y0)/rad
            a=np.clip((1-rr)*rad,0,1)
            pearl=np.array([0.99,0.92,0.90])*(0.85+0.15*(1-rr**2))[...,None]
            gl=np.exp(-((xs-x0+0.35*rad)**2+(ys-y0+0.35*rad)**2)/(0.08*rad*rad))
            pc=pearl+gl[...,None]*0.6
            sl=(slice(ys[0,0],ys[-1,0]+1),slice(xs[0,0],xs[0,-1]+1))
            img[sl]=img[sl]*(1-a[...,None])+np.clip(pc,0,1)*a[...,None]*np.array([1,1,1])
            ring=np.clip(1-np.abs(rr-1)*rad/1.2,0,1)
            img[sl]=img[sl]*(1-0.8*ring[...,None])+0.8*ring[...,None]*np.array([0.90,0.42,0.40])
    print('t range',T.min(),T.max())
    Image.fromarray((np.clip(img,0,1)**(1/2.2)*255).astype(np.uint8)).save(out)

if __name__=="__main__":
    import json
    Q=json.load(open('quartic_pts.json'))
    pts=[p[:4] for p in Q['pts']]
    render(W=1024,out='_q1.png',eye=(2.4,-4.6,5.6),fov=0.22,t0=Q['t'],pts=pts,nb=26,yarn=0.006)
    render(W=1024,out='_q2.png',eye=(1.2,-5.6,4.4),fov=0.22,t0=Q['t'],pts=pts,nb=26,yarn=0.006)
