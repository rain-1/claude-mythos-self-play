import numpy as np
def flow(V,P,D,T):
    """advance particles P (n,2) with unit directions D (n,2) by time T inside triangle V (3,2), specular reflection"""
    P=P.copy(); D=D.copy(); rem=np.full(len(P),T)
    E=[(V[e],V[(e+1)%3]) for e in range(3)]
    N=[]
    for a,b in E:
        s=b-a; n=np.array([-s[1],s[0]]); n/=np.linalg.norm(n)
        if np.dot(V.mean(0)-a,n)<0: n=-n   # inward normal
        N.append((a,n))
    for _ in range(100000):
        act=rem>1e-12
        if not act.any(): break
        tmin=np.full(len(P),np.inf); wall=np.full(len(P),-1)
        for k,(a,n) in enumerate(N):
            dn=D@n; dist=(P-a)@n   # >=0 inside
            t=np.where(dn<-1e-15,dist/np.maximum(-dn,1e-300),np.inf)
            t=np.where(t<1e-13,np.inf,t)
            m=t<tmin; tmin[m]=t[m]; wall[m]=k
        step=np.minimum(tmin,rem); step[~act]=0
        P+=D*step[:,None]; rem-=step
        hit=act&(tmin<=rem+step)&(step==tmin)
        for k,(a,n) in enumerate(N):
            m=hit&(wall==k)
            D[m]-=2*(D[m]@n)[:,None]*n[None,:]
    return P
