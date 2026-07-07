"""
CURVE-SHORTENING FLOW (Gage-Hamilton-Grayson) — the isoperimetric optimum.
d(gamma)/dt = kappa * N  (each point moves by its curvature normal).
Every embedded closed curve becomes convex, then round, then a point; the
isoperimetric ratio L^2/(4*pi*A) decreases monotonically to 1 = the circle.
We save nested snapshots; the flow's own time-scale piles them up at extinction
(the singularity is free detail).
"""
import numpy as np, time
from PIL import Image
from scipy.ndimage import gaussian_filter

def resample(P, M):
    """Resample closed polyline P to M points, uniform arc length."""
    d = np.sqrt(((np.roll(P,-1,0)-P)**2).sum(1))
    s = np.concatenate([[0], np.cumsum(d)])
    L = s[-1]
    Pc = np.vstack([P, P[0]])
    snew = np.linspace(0, L, M, endpoint=False)
    x = np.interp(snew, s, Pc[:,0])
    y = np.interp(snew, s, Pc[:,1])
    return np.c_[x,y], L

def area(P):
    x,y = P[:,0],P[:,1]
    return 0.5*abs(np.dot(x, np.roll(y,-1))-np.dot(y, np.roll(x,-1)))

def curvature_normal(P):
    """Discrete curvature-normal gamma'' wrt arc length (central differences)."""
    Pm = np.roll(P,1,0); Pp = np.roll(P,-1,0)
    e0 = P-Pm; e1 = Pp-P
    l0 = np.hypot(*e0.T)[:,None]; l1 = np.hypot(*e1.T)[:,None]
    # second derivative wrt arclength: 2/(l0+l1) * (e1/l1 - e0/l0)
    v = 2.0/(l0+l1) * (e1/np.maximum(l1,1e-12) - e0/np.maximum(l0,1e-12))
    return v

def flow(P0, M=1200):
    P,_ = resample(P0, M)
    A0 = area(P)
    snaps=[]; ratios=[]
    A=A0; step=0
    next_frac = 1.0
    # save at geometric area fractions -> equal spacing near extinction
    targets = list(A0*np.geomspace(1.0, 0.00025, 210))
    ti=0
    while A > A0*0.0003 and step < 2000000:
        V = curvature_normal(P)
        d = np.sqrt(((np.roll(P,-1,0)-P)**2).sum(1))
        h = d.mean()
        dt = 0.20*h*h
        P = P + dt*V
        step+=1
        if step % 3 == 0:
            P,_ = resample(P, M)
        A = area(P)
        while ti < len(targets) and A <= targets[ti]:
            L = np.sqrt(((np.roll(P,-1,0)-P)**2).sum(1)).sum()
            snaps.append(P.copy()); ratios.append(L*L/(4*np.pi*A))
            ti+=1
    return snaps, np.array(ratios), A0

def star_curve(M=2000, seed=3):
    rng=np.random.default_rng(seed)
    t=np.linspace(0,2*np.pi,M,endpoint=False)
    # lumpy star: several random harmonics
    r=1.0
    for k in range(2,9):
        r = r + rng.uniform(-0.5,0.5)/k*np.cos(k*t+rng.uniform(0,6.28))
    r = 0.35+0.65*(r-r.min())/(r.max()-r.min())
    return np.c_[r*np.cos(t), r*np.sin(t)]

def ramp(t, anchors):
    cols=np.array([c for _,c in anchors]); pos=np.array([p for p,_ in anchors])
    return np.stack([np.interp(t,pos,cols[:,k]) for k in range(3)],-1)

PAL=[(0.0,(0.99,0.97,0.88)),(0.25,(0.98,0.80,0.35)),(0.5,(0.95,0.45,0.22)),
     (0.72,(0.70,0.18,0.48)),(0.88,(0.34,0.20,0.66)),(1.0,(0.16,0.20,0.55))]

def render(snaps, ratios, S=1024, save=None, lw=1.6, center=True):
    from PIL import ImageDraw
    sup=2
    Sp=S*sup
    img=Image.new('RGB',(Sp,Sp),(2,2,6))
    dr=ImageDraw.Draw(img,'RGBA')
    # centre on the INITIAL curve (fills frame); extinction lands where it will
    off=snaps[0].mean(0) if center else np.zeros(2)
    lr=np.log(np.maximum(ratios,1.0)); lr=(lr-lr.min())/(lr.max()-lr.min()+1e-9)
    sc=Sp*0.45
    def MP(P): return [(Sp/2+(P[j,0]-off[0])*sc, Sp/2-(P[j,1]-off[1])*sc) for j in range(len(P))]
    for i in range(len(snaps)-1,-1,-1):
        P=snaps[i]
        col=ramp(np.array([1-lr[i]]),PAL)[0]
        al=215
        c=tuple(int(255*x) for x in col)+(al,)
        pts=MP(P); pts.append(pts[0])
        dr.line(pts, fill=c, width=max(1,int(lw*sup)), joint='curve')
    arr=np.asarray(img).astype(np.float32)/255
    # extinction-point glow at the TRUE final location
    fc=snaps[-1].mean(0)
    exx=int(Sp/2+(fc[0]-off[0])*sc); exy=int(Sp/2-(fc[1]-off[1])*sc)
    ex=np.zeros((Sp,Sp))
    if 0<=exx<Sp and 0<=exy<Sp: ex[exy,exx]=1.0
    ex=gaussian_filter(ex,Sp/130); ex/=ex.max()+1e-9
    arr=arr+0.95*ex[...,None]*np.array([1.0,0.96,0.88])[None,None,:]
    bloom=gaussian_filter(arr,(Sp/420,Sp/420,0))
    arr=np.clip(arr+0.5*bloom,0,1)
    out=Image.fromarray((arr*255).astype(np.uint8)).resize((S,S),Image.LANCZOS)
    if save: out.save(save); print("->",save)
    return out

if __name__=='__main__':
    t0=time.time()
    snaps,ratios,A0=flow(star_curve(seed=3))
    print(f"snaps={len(snaps)} ratio {ratios[0]:.2f}->{ratios[-1]:.3f}  {time.time()-t0:.1f}s")
    render(snaps,ratios,S=900,save='/home/user/claude-mythos-self-play/art_bcm8/prev_csf.png')
