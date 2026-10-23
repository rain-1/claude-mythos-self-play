# Computer-assisted (interval branch-and-bound + Krawczyk) proof that the only Y-partitions of the
# unit disc into 3 pieces of equal area and equal perimeter are the 120-degree one and the mirror one.
# Variables: p=(r,0), r in [0,1]; t_i = Kepler^{-1}(c+2pi i/3, r) (equal areas <=> equally spaced mean anomalies).
# G1=Q0-Q1, G2=Q1-Q2,  Q_i = u(t_{i+1})+v(t_i), u=d+r sin t, v=d-r sin t, d=|p-A(t)|.
import numpy as np, time
from iv import I,isin,icos,isqrt,dn,up
TP=2*np.pi/3
def kep(M,r):
    M=np.asarray(M,float)+0*np.asarray(r,float); r=np.asarray(r,float)+0*M
    a=M-r-1e-9; b=M+r+1e-9          # |E-M|<=r, f(t)=t-r sin t-M increasing
    for _ in range(64):
        m=0.5*(a+b); f=m-r*np.sin(m)-M
        a=np.where(f<0,m,a); b=np.where(f<0,b,m)
    return 0.5*(a+b)
def kep_iv(M,r):
    """enclosure of E(M,r) over box M in [M.lo,M.hi], r in [r.lo,r.hi]; E increasing in M, monotone in r for fixed M."""
    lo=np.minimum(kep(M.lo,r.lo),kep(M.lo,r.hi)); hi=np.maximum(kep(M.hi,r.lo),kep(M.hi,r.hi))
    # validate by sign of Kepler residual (f increasing in t): f(lo-eps)<=0 at (M.lo, any r)...
    pl=np.full(lo.shape,1e-13); ph=pl.copy()
    for _ in range(12):
        bad=np.zeros(lo.shape,bool); badh=bad.copy()
        for rr in (r.lo,r.hi):
            a=I(lo-pl); b=I(hi+ph); R_=I(rr)
            bad|=~((a-R_*isin(a)-I(M.lo)).hi<0); badh|=~((b-R_*isin(b)-I(M.hi)).lo>0)
        if not (bad.any() or badh.any()): break
        pl=np.where(bad,pl*10,pl); ph=np.where(badh,ph*10,ph)
    else: raise AssertionError('kepler enclosure')
    lo=lo-pl; hi=hi+ph
    return I(lo,hi)
def parts(r,c,deriv=False):
    out=[]
    for i in range(3):
        M=c+I(dn(TP*i,2),up(TP*i,2)); t=kep_iv(M,r); s=isin(t); co=icos(t)
        d=isqrt(1+r*r-2*r*co)
        rec=dict(u=d+r*s, v=d-r*s)
        if deriv:
            den=1-r*co; tM=den.recip(); tr=s*tM
            dr=(r-co)/d; dt=r*s/d
            ur=dr+s; ut=dt+r*co; vr=dr-s; vt=dt-r*co
            rec.update(u_r=ur+ut*tr, u_c=ut*tM, v_r=vr+vt*tr, v_c=vt*tM)
        out.append(rec)
    return out
def Gfun(r,c,deriv=False):
    P=parts(r,c,deriv)
    Q=[P[(i+1)%3]['u']+P[i]['v'] for i in range(3)]
    G=[Q[0]-Q[1],Q[1]-Q[2]]
    if not deriv: return G
    Qr=[P[(i+1)%3]['u_r']+P[i]['v_r'] for i in range(3)]
    Qc=[P[(i+1)%3]['u_c']+P[i]['v_c'] for i in range(3)]
    J=[[Qr[0]-Qr[1],Qc[0]-Qc[1]],[Qr[1]-Qr[2],Qc[1]-Qc[2]]]
    return G,J
def excluded(rlo,rhi,clo,chi):
    r=I(rlo,rhi); c=I(clo,chi)
    ex=np.zeros(rlo.shape,bool)
    z=rlo==0
    if np.any(~z):
        G=Gfun(I(rlo[~z],rhi[~z]),I(clo[~z],chi[~z]))
        ex[~z]=~G[0].contains0()|~G[1].contains0()
    if np.any(z):
        # G(0,c)=0, so G/r in dG/dr([0,rhi],c)  (mean value theorem)
        _,J=Gfun(I(rlo[z],rhi[z]),I(clo[z],chi[z]),deriv=True)
        ex[z]=~J[0][0].contains0()|~J[1][0].contains0()
    return ex
if __name__=="__main__":
    t0=time.time()
    C0,C1=-0.05,np.pi/3+0.05
    n=64
    R=np.linspace(0,1,n+1); Cg=np.linspace(C0,C1,n+1)
    rl,cl=np.meshgrid(R[:-1],Cg[:-1]); rh,ch=np.meshgrid(R[1:],Cg[1:])
    boxes=np.stack([rl.ravel(),rh.ravel(),cl.ravel(),ch.ravel()],1)
    total=0; MIN=2e-4; left=[]
    while len(boxes):
        total+=len(boxes)
        ex=excluded(*boxes.T)
        b=boxes[~ex]
        small=(b[:,1]-b[:,0]<MIN)
        left.append(b[small]); b=b[~small]
        rm=0.5*(b[:,0]+b[:,1]); cm=0.5*(b[:,2]+b[:,3])
        boxes=np.concatenate([np.stack([b[:,0],rm,b[:,2],cm],1),np.stack([rm,b[:,1],b[:,2],cm],1),
                              np.stack([b[:,0],rm,cm,b[:,3]],1),np.stack([rm,b[:,1],cm,b[:,3]],1)])
    left=np.concatenate(left)
    print('boxes processed',total,'unresolved',len(left),'time %.1fs'%(time.time()-t0))
    if len(left):
        print('unresolved hull r[%.6f,%.6f] c[%.6f,%.6f]'%(left[:,0].min(),left[:,1].max(),left[:,2].min(),left[:,3].max()))
    # Krawczyk on a box around the mirror solution r*, c=0
    rs=0.6082600268414115
    hw=np.array([5e-3,5e-3])
    x=np.array([rs,0.0])
    assert left[:,0].min()>=x[0]-hw[0] and left[:,1].max()<=x[0]+hw[0] and left[:,2].min()>=-hw[1] and left[:,3].max()<=hw[1]
    Gx=Gfun(I(np.array([x[0]])),I(np.array([x[1]])))
    _,Jb=Gfun(I(np.array([x[0]-hw[0]]),np.array([x[0]+hw[0]])),I(np.array([-hw[1]]),np.array([hw[1]])),deriv=True)
    Jm=np.array([[Jb[i][j].mid()[0] for j in range(2)] for i in range(2)]); Y=np.linalg.inv(Jm)
    # K = x - Y G(x) + (I - Y J) (B-x)
    K=[]
    for i in range(2):
        acc=I(x[i])-(I(Y[i,0])*Gx[0]+I(Y[i,1])*Gx[1])
        for j in range(2):
            Mij=I(1.0 if i==j else 0.0)-(I(Y[i,0])*Jb[0][j]+I(Y[i,1])*Jb[1][j])
            acc=acc+Mij*I(-hw[j],hw[j])
        K.append(acc)
    ok=all(K[i].lo[0]>x[i]-hw[i] and K[i].hi[0]<x[i]+hw[i] for i in range(2))
    print('Krawczyk box',[(K[i].lo[0],K[i].hi[0]) for i in range(2)],'contained:',ok)
    # c=0 is a solution line of the symmetric reduction, so the unique root in the box is the mirror one (c=0).
    print('done %.1fs'%(time.time()-t0))
