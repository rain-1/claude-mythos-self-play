import numpy as np, sys, time, json
from PIL import Image
from wc import *

def chord(n,k=1): return 2*np.sin(np.pi*k/n)

def side_poly(P,Q,n,k,tri_c):
    """regular {n/k} polygon in a unit circle having PQ as an edge, centre away from tri_c"""
    P,Q=np.array(P,float),np.array(Q,float)
    M=(P+Q)/2; L=np.linalg.norm(Q-P); u=(Q-P)/L; nrm=np.array([-u[1],u[0]])
    if np.dot(nrm,M-tri_c)<0: nrm=-nrm
    h=np.sqrt(max(1-(L/2)**2,0))
    # centre on far side for minor arcs (k/n<1/2)
    O=M+nrm*h
    a0=np.arctan2(*(P-O)[::-1]); a1=np.arctan2(*(Q-O)[::-1])
    step=2*np.pi*k/n
    sgn=1 if abs(((a0+step-a1+np.pi)%(2*np.pi))-np.pi)<1e-6 else -1
    V=[O+np.array([np.cos(a0+sgn*step*j),np.sin(a0+sgn*step*j)]) for j in range(n)]
    return O,np.array(V)

def render(W,H,out,seed=5,**kw):
    S=Sheet(H,W,seed=seed)
    paint_flower(S,**kw)
    Image.fromarray(to8(S.finish())).save(out)
    return S

def paint_flower(S,legs=((6,1),(10,1)),hyp=(5,1),scale=0.27,center=(0.5,0.47),rot=0.0,pal=None,dens=0.16,tri_dens=0.32,labels=True):
    W,H,s=S.W,S.H,S.s
    a=chord(*legs[0]); b=chord(*legs[1]); c=chord(*hyp)
    assert abs(a*a+b*b-c*c)<1e-9,(a,b,c)
    Cc=np.array([0,0.]); B=np.array([a,0.]); A=np.array([0,b])
    tri=np.array([Cc,B,A]); cen=tri.mean(0)
    R=np.array([[np.cos(rot),-np.sin(rot)],[np.sin(rot),np.cos(rot)]])
    def X(p): # world->px (y up)
        p=(np.asarray(p)-cen)@R.T
        return np.stack([center[0]*W+p[...,0]*scale*W, center[1]*H-p[...,1]*scale*W],-1)
    polys=[(legs[0],Cc,B),(legs[1],A,Cc),(hyp,B,A)]
    pal=pal or [('sky','mint'),('butter','peach'),('rose','lilac')]
    C=dict(rose='#ee7f9c',mint='#62cfa8',butter='#f2cb52',sky='#78b6ec',lilac='#ad92e6',peach='#f7a174',coral='#f2735f')
    K={k:pigment(hexrgb(v)) for k,v in C.items()}
    for (nk,P,Q),(p1,p2) in zip(polys,pal):
        O,V=side_poly(P,Q,nk[0],nk[1],cen)
        n=len(V)
        Op=X(O)
        S.halo(*Op,scale*W*1.08,K[p1]*0.5+K[p2]*0.5,dens=0.045)
        if labels:
            lab='{%d}'%nk[0] if nk[1]==1 else '{%d/%d}'%nk
            dirv=(O-cen); dirv/=np.linalg.norm(dirv)
            lp=X(O+dirv*1.18)
            S.text(tuple(lp),lab,0.022*W*scale/0.105,anchor='mm',weight=0.8)
        S.circle(*Op,scale*W,0.55,overshoot=0.2)
        if nk[1]>1:
            Vp=X(V); pad=int(30*s)+8
            box=(int(Vp[:,1].min())-pad,int(Vp[:,1].max())+pad,int(Vp[:,0].min())-pad,int(Vp[:,0].max())+pad)
            w=np.abs(winding(Vp,box)); L=w.max()
            for lev in range(1,L+1):
                t=(lev-1)/max(L-1,1)
                S.wash(mask_sd(w>=lev),box,K[p1]*(1-t)+K[p2]*t,dens=dens*(1.0 if lev==1 else 0.8),edge=0.45,pool=0.3,
                       wobble=3.0,mottle=0.12,gran=0.3)
            for j in range(n): S.line(X(O),X(V[j]),0.25)
        for j in range(n if nk[1]==1 else 0):
            t=j/(n-1)
            seg=np.array([O,V[j],V[(j+1)%n]])
            # shrink toward centroid: white reserve between segments
            g=seg.mean(0); segs=g+(seg-g)*0.965
            S.wash_poly(X(segs),K[p1],K2=K[p2],mix=t,dens=dens*(0.8+0.4*(j%2)+0.15*S.rng.standard_normal()),edge=0.5,pool=0.3,
                        wobble=4.0,mottle=0.14,gran=0.35,bloom=0.35 if S.rng.random()<0.25 else 0.0)
        for j in range(n): S.line(X(V[j]),X(V[(j+1)%n]),0.5,over=8*s)
        S.circle(*Op,3*s,0.6)
    S.wash_poly(X(tri),K['coral'],dens=tri_dens,edge=0.6,wobble=3,mottle=0.1)
    for i in range(3): S.line(X(tri[i]),X(tri[(i+1)%3]),0.9,over=14*s)
    q=0.07*b
    S.stroke(X(np.array([[q,0],[q,q],[0,q]])),0.7)
    return X
if __name__=='__main__':
    t=time.time()
    render(1024,1024,'../proto/f1.png')
    print(time.time()-t)
