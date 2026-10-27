"""Pappus configuration in the projective plane (hemisphere model), optimised for a pleasing,
well-spread drawing; then the Pappus line is bent to miss C3 -> non-Pappus pseudoline arrangement."""
import numpy as np, json, sys
def unit(v): return v/np.linalg.norm(v)
def meet(n1,n2):
    p=unit(np.cross(n1,n2)); return p if p[2]>=0 else -p
def join(p,q): return unit(np.cross(p,q))
def config(P,a=(-1.0,0.0,1.0),b=(-1.0,0.0,1.0)):
    # P: 3x3 projective matrix applied to a base Pappus config with params
    A=[np.array([x,0,1.]) for x in a]; B=[np.array([x,1.0,1.]) for x in b]   # l: y=0, m: y=1 meet at infinity
    A=[unit(P@x) for x in A]; B=[unit(P@x) for x in B]
    lines={'l':join(A[0],A[1]),'m':join(B[0],B[1])}
    for i in range(3):
        for j in range(3):
            if i!=j: lines[f'A{i+1}B{j+1}']=join(A[i],B[j])
    C={}
    for (i,j),k in (((0,1),3),((0,2),2),((1,2),1)):
        C[k]=meet(lines[f'A{i+1}B{j+1}'],lines[f'A{j+1}B{i+1}'])
    lines['p']=join(C[1],C[2])
    return lines,A,B,C
def crossings(lines):
    ks=list(lines); pts=[]
    for i in range(len(ks)):
        for j in range(i+1,len(ks)):
            pts.append(meet(lines[ks[i]],lines[ks[j]]))
    return np.array(pts)
def score(P,a=(-1.0,0.0,1.0),b=(-1.0,0.0,1.0)):
    lines,A,B,C=config(P,a,b); X=crossings(lines)
    xy=X[:,:2]/(1+X[:,2:3])
    # merge coincident (triple points)
    U=[]
    for p in xy:
        if not any(np.linalg.norm(p-q)<1e-6 for q in U): U.append(p)
    U=np.array(U); d=np.linalg.norm(U[:,None]-U[None],axis=2)+np.eye(len(U))*9
    r=np.linalg.norm(U,axis=1)
    # crossing angles (on the sphere = conformal = angle in stereographic picture)
    ks=list(lines); ang=9
    for i in range(len(ks)):
        for j in range(i+1,len(ks)):
            c=abs(np.dot(lines[ks[i]],lines[ks[j]])); ang=min(ang,np.arccos(min(1,c)))
    return min(d.min(),0.9*ang/np.pi*1.2)-1.5*max(0,r.max()-0.74), len(U)
if __name__=='__main__':
    rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 1)
    best=(-9,None)
    for it in range(20000):
        P=rng.normal(size=(3,3))
        s,nu=score(P)
        if s>best[0]: best=(s,P)
    # local refine
    s0,P=best
    for it in range(20000):
        Q=P+rng.normal(size=(3,3))*0.05*(1-it/20000)
        s,nu=score(Q)
        if s>s0: s0,P=s,Q
    print('score',s0,score(P)); np.save('P.npy',P)
