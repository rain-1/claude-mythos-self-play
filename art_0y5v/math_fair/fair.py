# Equal-area / equal-perimeter 3-partitions of a convex shape: Y-junction families (continuation) + chord pairs.
import numpy as np
from scipy.optimize import least_squares
from shapes import cross
# ---------------- Y ----------------
def Ypieces(sh,x):
    p=x[:2]; s=np.array([x[2],x[3],x[4],x[2]+sh.S]); B=sh.pt(s); Wv=sh.W(s); Lv=sh.length(s)
    d=np.linalg.norm(B-p,axis=1)
    area=0.5*(Wv[1:]-Wv[:-1]+cross(p,B[:-1])-cross(p,B[1:]))
    per=(Lv[1:]-Lv[:-1])+d[:-1]+d[1:]
    return area,per
def YF(sh,x):
    a,P=Ypieces(sh,x); return np.array([a[0]-sh.A/3,a[1]-sh.A/3,P[0]-P[1],P[1]-P[2]])
KINKS=None   # set to array of kink parameters (mod S) and period, to use one-sided differences near kinks
def jac(f,x,h=1e-7,sidx=None,force=None):
    f0=f(x); J=np.zeros((len(f0),len(x)))
    for j in range(len(x)):
        e=np.zeros(len(x)); e[j]=h
        if force and j in force:
            J[:,j]=(f(x+e)-f0)/h if force[j]>0 else (f0-f(x-e))/h; continue
        if KINKS is not None and sidx is not None and j in sidx:
            K,S=KINKS; y=np.mod(x[j],S); dist=np.min(np.abs(((K-y)+S/2)%S-S/2))
            if dist<2*h:
                # signed position relative to the nearest kink: difference on the side not containing it
                k=K[np.argmin(np.abs(((K-y)+S/2)%S-S/2))]; sg=((y-k)+S/2)%S-S/2
                J[:,j]=(f(x+e)-f0)/h if sg>=0 else (f0-f(x-e))/h; continue
        J[:,j]=(f(x+e)-f(x-e))/(2*h)
    return J
def Yangles(sh,x):
    p=x[:2]; B=sh.pt(np.array(x[2:5])); th=np.arctan2(B[:,1]-p[1],B[:,0]-p[0])
    return np.mod(np.roll(th,-1)-th,2*np.pi)
def inside(sh,p,poly):
    e=poly[1:]-poly[:-1]; k=np.linalg.norm(e,axis=1)>1e-9
    return bool(np.all(cross(e[k],p-poly[:-1][k])>1e-12))
def embed(sh,x):
    B=sh.pt(np.array(x[2:5])); return np.r_[x[:2],B.ravel()]
def relabels(sh,x):
    s=list(x[2:5]); out=[]
    for k in range(3):
        out.append(np.r_[x[:2],s]); s=[s[1],s[2],s[0]+sh.S]
    return out
def corrector(sh,x,tau=None,xp=None,it=30,tol=1e-13):
    for _ in range(it):
        f=YF(sh,x); J=jac(lambda y:YF(sh,y),x,sidx=(2,3,4))
        if tau is None:
            dx=-np.linalg.lstsq(J,f,rcond=None)[0]
        else:
            Fa=np.r_[f,tau@(x-xp)]; Ja=np.vstack([J,tau])
            try: dx=-np.linalg.solve(Ja,Fa)
            except np.linalg.LinAlgError: return x,False
        x=x+dx
        if np.abs(YF(sh,x)).max()<1e-13 or (np.linalg.norm(dx)<tol and np.abs(YF(sh,x)).max()<1e-12): return x,True
    return x,np.abs(YF(sh,x)).max()<1e-11
def tangent(sh,x,prev=None):
    J=jac(lambda y:YF(sh,y),x,sidx=(2,3,4)); t=np.linalg.svd(J)[2][-1]
    if prev is not None and t@prev<0: t=-t
    return t
def trace(sh,x0,h=0.01,maxsteps=20000,box=3.0):
    xs=[x0.copy()]; t=tangent(sh,x0)*np.sign(h); h=abs(h); x=x0.copy(); E0=[embed(sh,y) for y in relabels(sh,x0)]
    closed=False
    for k in range(maxsteps):
        hh=h
        while True:
            xp=x+hh*t; xn,ok=corrector(sh,xp.copy(),t,xp)
            if ok and np.linalg.norm(xn-x)<3*hh: break
            hh/=2
            if hh<1e-5:
                r=cross_kink(sh,x,xs[-2] if len(xs)>1 else x-1e-3*t)
                if r is None: return np.array(xs),False,'stuck'
                xk,tk=r; xs.append(xk.copy()); x=xk; t=tk; hh=h; continue
        tn=tangent(sh,xn,t); sec=(xn-x)/np.linalg.norm(xn-x)
        if tn@sec<0.9: tn=sec          # kink in the curve (endpoint crossing a vertex): use secant
        x=xn; t=tn; xs.append(x.copy())
        if np.abs(x[:2]).max()>box: return np.array(xs),False,'left box'
        sv=np.diff(np.r_[x[2:5],x[2]+sh.S])
        if sv.min()<1e-6: return np.array(xs),False,'collapse'
        if k>20:
            e=embed(sh,x)
            dmin=min(np.linalg.norm(e-E) for E in E0)
            if dmin<0.6*h: closed=True; break
    return np.array(xs),closed,'closed' if closed else 'maxsteps'
def cross_kink(sh,x,xprev):
    if KINKS is None: return None
    K,S=KINKS
    for j in (2,3,4):
        y=np.mod(x[j],S); dd=((K-y)+S/2)%S-S/2; i=np.argmin(np.abs(dd))
        if abs(dd[i])>2e-3: continue
        v=x[j]+dd[i]; sig=np.sign(x[j]-xprev[j]) or 1.0
        side=-sig            # side we come from
        free=[k for k in range(5) if k!=j]; z=x.copy(); z[j]=v
        for _ in range(40):
            f=YF(sh,z); J=jac(lambda w:YF(sh,w),z,force={j:side})[:,free]
            try: dz=np.linalg.solve(J,-f)
            except np.linalg.LinAlgError: break
            z[free]+=dz
            if np.abs(dz).max()<1e-14: break
        if np.abs(YF(sh,z)).max()>1e-11 or np.linalg.norm(z-x)>0.05: continue
        J=jac(lambda w:YF(sh,w),z,force={j:sig}); t=np.linalg.svd(J)[2][-1]
        if t[j]*sig<0: t=-t
        return z,t
    return None
def seeds(sh,n,rng,poly,physical_only=True):
    out=[]
    for _ in range(n):
        cen=np.mean(poly,0); p=cen+(poly[rng.integers(len(poly))]-cen)*np.sqrt(rng.uniform(0,0.95))
        s=np.sort(rng.uniform(0,sh.S,3))
        x0=np.r_[p,s]
        r=least_squares(lambda y:YF(sh,y),x0,method='trf',xtol=1e-15,ftol=1e-15,gtol=1e-15)
        x=r.x
        if np.abs(YF(sh,x)).max()<1e-10:
            sv=np.diff(np.r_[x[2:5],x[2]+sh.S])
            if sv.min()>1e-6 and (not physical_only or inside(sh,x[:2],poly)):
                x[2:5]-=np.floor(x[2]/sh.S)*sh.S; out.append(x)
    return out
# ---------------- chord pairs ----------------
def Cpieces(sh,x):
    s=np.array(x); B=sh.pt(s); Wv=sh.W(s); Lv=sh.length(s)
    c0=np.linalg.norm(B[1]-B[0]); c1=np.linalg.norm(B[3]-B[2])
    a0=0.5*(Wv[1]-Wv[0]+cross(B[1],B[0])); a1=0.5*(Wv[3]-Wv[2]+cross(B[3],B[2]))
    l0=Lv[1]-Lv[0]; l1=Lv[3]-Lv[2]
    P0=l0+c0; P1=l1+c1; Pm=sh.Ltot-l0-l1+c0+c1
    return np.array([a0,a1,sh.A-a0-a1]),np.array([P0,P1,Pm])
def CF(sh,x):
    a,P=Cpieces(sh,x); return np.array([a[0]-sh.A/3,a[1]-sh.A/3,P[0]-P[2],P[1]-P[2]])
def chord_solutions(sh,n,rng):
    sols=[]
    for _ in range(n):
        x0=np.sort(rng.uniform(0,sh.S,4))
        r=least_squares(lambda y:CF(sh,y),x0,method='lm',xtol=1e-15,ftol=1e-15,gtol=1e-15)
        x=r.x
        if np.abs(CF(sh,x)).max()<1e-11 and np.all(np.diff(x)>1e-7) and x[3]-x[0]<sh.S-1e-7:
            # chords must not cross: order s0<s1<s2<s3<s0+S guaranteed by sortedness
            x=x-np.floor(x[0]/sh.S)*sh.S
            B=sh.pt(x); key=np.sort([np.r_[B[0],B[1]].tolist(),np.r_[B[2],B[3]].tolist()],axis=0).ravel()
            if not any(np.allclose(key,k,atol=1e-7) for k,_ in sols): sols.append((key,x))
    return [x for _,x in sols]
# ---------------- piece geometry & congruence ----------------
def Ypolys(sh,x,ds=0.004):
    p=x[:2]; s=[x[2],x[3],x[4],x[2]+sh.S]; out=[]
    for i in range(3):
        arc=sh.sample(s[i],s[i+1],ds); out.append(np.vstack([p[None],arc]))
    return out
def Cpolys(sh,x,ds=0.004):
    s=x; capA=sh.sample(s[0],s[1],ds); capB=sh.sample(s[2],s[3],ds)
    mid=np.vstack([sh.sample(s[1],s[2],ds),sh.sample(s[3],s[0]+sh.S,ds)])
    return [capA,capB,mid]
def invariants(P):
    P=np.asarray(P); Q=np.roll(P,-1,0); cr=cross(P,Q); A=cr.sum()/2
    cx=((P[:,0]+Q[:,0])*cr).sum()/(6*A); cy=((P[:,1]+Q[:,1])*cr).sum()/(6*A)
    X=P-[cx,cy]; Y=Q-[cx,cy]; c2=cross(X,Y)
    Ixx=((X[:,1]**2+X[:,1]*Y[:,1]+Y[:,1]**2)*c2).sum()/12; Iyy=((X[:,0]**2+X[:,0]*Y[:,0]+Y[:,0]**2)*c2).sum()/12
    Ixy=((X[:,0]*Y[:,1]+2*X[:,0]*X[:,1]+2*Y[:,0]*Y[:,1]+Y[:,0]*X[:,1])*c2).sum()/24
    ev=np.linalg.eigvalsh(np.array([[Ixx,Ixy],[Ixy,Iyy]]))
    r=np.linalg.norm(X,axis=1)
    # corner angles (turning > 0.02 rad at a single vertex), sorted
    e1=P-np.roll(P,1,0); e2=Q-P
    turn=np.arctan2(cross(e1,e2),(e1*e2).sum(1))
    corners=np.sort(turn[np.abs(turn)>0.02])
    return dict(A=A,ev=ev,rmax=r.max(),rmin_v=r.min(),corners=corners)
def same(a,b,tol=1e-4):
    if abs(a['A']-b['A'])>tol: return False
    if np.abs(a['ev']-b['ev']).max()>tol*max(1,a['ev'].max()): return False
    if abs(a['rmax']-b['rmax'])>tol: return False
    if len(a['corners'])!=len(b['corners']) or np.abs(a['corners']-b['corners']).max()>1e-3: return False
    return True
def congruent_pairs(polys,tol=1e-4):
    inv=[invariants(P) for P in polys]
    return [(i,j) for i in range(3) for j in range(i+1,3) if same(inv[i],inv[j],tol)],inv
def noncong_margin(polys):
    """min over pairs of max invariant difference (0 => some pair looks congruent)."""
    inv=[invariants(P) for P in polys]; m=np.inf
    for i in range(3):
        for j in range(i+1,3):
            a,b=inv[i],inv[j]
            d=max(np.abs(a['ev']-b['ev']).max(),abs(a['rmax']-b['rmax']))
            m=min(m,d)
    return m
