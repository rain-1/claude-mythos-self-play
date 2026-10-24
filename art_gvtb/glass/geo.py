import numpy as np
def icosa():
    p=(1+5**.5)/2
    V=[(-1,p,0),(1,p,0),(-1,-p,0),(1,-p,0),(0,-1,p),(0,1,p),(0,-1,-p),(0,1,-p),(p,0,-1),(p,0,1),(-p,0,-1),(-p,0,1)]
    F=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),
       (3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
    V=np.array(V,float); V/=np.linalg.norm(V,axis=1)[:,None]
    return V,F
def subdivide(V,F):
    V=list(map(tuple,V)); idx={}
    def mid(a,b):
        k=(min(a,b),max(a,b))
        if k not in idx:
            m=(np.array(V[a])+np.array(V[b]))/2; m/=np.linalg.norm(m)
            idx[k]=len(V); V.append(tuple(m))
        return idx[k]
    G=[]
    for a,b,c in F:
        ab,bc,ca=mid(a,b),mid(b,c),mid(c,a)
        G+=[(a,ab,ca),(b,bc,ab),(c,ca,bc),(ab,bc,ca)]
    return np.array(V),G
def geodesic(k):
    V,F=icosa()
    # ensure outward ccw orientation
    F=[f if np.dot(np.cross(V[f[1]]-V[f[0]],V[f[2]]-V[f[0]]),V[f[0]])>0 else (f[0],f[2],f[1]) for f in F]
    for _ in range(k): V,F=subdivide(V,F)
    return V,F
