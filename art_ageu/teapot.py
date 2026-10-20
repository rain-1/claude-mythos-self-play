"""Newell teapot from the 32 bicubic Bézier patches (data from three.js TeapotGeometry.js)."""
import re, numpy as np, os
import porcelain as P
HERE=os.path.dirname(os.path.abspath(__file__))
def patches():
    s=open(os.path.join(HERE,'mesh/TeapotGeometry.js')).read()
    s=re.sub(r'/\*.*?\*/','',s,flags=re.S)
    pa=s[s.index('const teapotPatches'):]; pa=pa[pa.index('[')+1:pa.index('];')]
    ve=s[s.index('const teapotVertices'):]; ve=ve[ve.index('[')+1:ve.index('];')]
    Pt=np.array([int(x) for x in re.findall(r'-?\d+',pa)]).reshape(-1,16)
    Vt=np.array([float(x.replace(' ','')) for x in re.findall(r'-\s*[\d.]+|[\d.]+',ve)]).reshape(-1,3)
    return Pt,Vt
def bern(t):
    t=np.asarray(t); s=1-t
    return np.stack([s**3,3*t*s*s,3*t*t*s,t**3],-1)
def teapot(n=40, lid=True, body=True, blinn=True):
    Pt,Vt=patches()
    VV=[];FF=[];nv=0
    u=np.linspace(0,1,n+1); B=bern(u)
    for pi,p in enumerate(Pt):
        C=Vt[p].reshape(4,4,3)
        X=np.einsum('ui,vj,ijk->uvk',B,B,C)
        V=X.reshape(-1,3)
        i=np.arange(n)[:,None]*(n+1)+np.arange(n)[None,:]; i=i.ravel()
        F=np.concatenate([np.stack([i,i+n+1,i+1],1),np.stack([i+1,i+n+1,i+n+2],1)])
        VV.append(V); FF.append(F+nv); nv+=len(V)
    V=np.concatenate(VV); F=np.concatenate(FF)
    if blinn: V[:,2]*=4/3*0.75  # mild squash like Blinn's (teapot looks better slightly squat)
    V=V[:,[0,2,1]]*np.array([1,1,-1])     # z-up -> y-up
    V,F=P.weld(V,F,1e-5)
    # orient faces outward-consistent for normals: use vertex normal pointing away from axis-ish centroid
    F=orient(F,V)
    N=P.vertex_normals(V,F)
    return V,F,N
def orient(F,V):
    from collections import defaultdict, deque
    F=F.copy(); m=len(F)
    E=defaultdict(list)
    for f in range(m):
        a,b,c=F[f]
        for e in ((a,b),(b,c),(c,a)): E[(min(e),max(e))].append(f)
    done=np.zeros(m,bool)
    for start in range(m):
        if done[start]: continue
        comp=[start]; done[start]=True; q=deque([start])
        while q:
            f=q.popleft(); a,b,c=F[f]
            for (x,y) in ((a,b),(b,c),(c,a)):
                for g in E[(min(x,y),max(x,y))]:
                    if done[g]: continue
                    A,B,C=F[g]
                    same=((A,B)==(x,y)) or ((B,C)==(x,y)) or ((C,A)==(x,y))
                    if same: F[g]=F[g][::-1]
                    done[g]=True; q.append(g); comp.append(g)
        comp=np.array(comp)
        # global sign: signed volume of component positive
        T=V[F[comp]]
        vol=np.einsum('ij,ij->i',T[:,0],np.cross(T[:,1],T[:,2])).sum()
        if vol<0: F[comp]=F[comp][:,::-1]
    return F
if __name__=='__main__':
    V,F,N=teapot(); print(V.shape,F.shape,V.min(0),V.max(0))
