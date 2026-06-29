import numpy as np
from itertools import product

def moser_spindle():
    O=np.array([0.0,0.0])
    D=2*np.arcsin(1/(2*np.sqrt(3)))     # rotation between rhombi
    th1=-D/2; th2=+D/2
    def rhombus(th):
        v=np.sqrt(3)*np.array([np.cos(th),np.sin(th)])
        mid=v/2
        perp=np.array([-np.sin(th),np.cos(th)])
        u1=mid+0.5*perp; u2=mid-0.5*perp
        return v,u1,u2
    v1,u1,u2=rhombus(th1)
    v2,w1,w2=rhombus(th2)
    V=np.array([O,u1,u2,v1,w1,w2,v2])  # 0..6 ; v1=3, v2=6
    names=['O','u1','u2','v1','w1','w2','v2']
    edges=[(0,1),(0,2),(1,3),(2,3),(1,2),  # rhombus1
           (0,4),(0,5),(4,6),(5,6),(4,5),  # rhombus2
           (3,6)]                          # v1-v2
    return V,edges,names

def verify(V,edges):
    bad=[]
    for (i,j) in edges:
        d=np.linalg.norm(V[i]-V[j])
        if abs(d-1)>1e-9: bad.append((i,j,d))
    return bad

def chromatic_number(n,edges):
    adj=[set() for _ in range(n)]
    for i,j in edges: adj[i].add(j); adj[j].add(i)
    for k in range(1,8):
        # try k-coloring by backtracking
        col=[-1]*n
        def bt(v):
            if v==n: return True
            for c in range(k):
                if all(col[u]!=c for u in adj[v]):
                    col[v]=c
                    if bt(v+1): return True
                    col[v]=-1
            return False
        if bt(0): return k,col
    return None,None

if __name__=="__main__":
    V,edges,names=moser_spindle()
    print("bad edges (should be empty):",verify(V,edges))
    chi,col=chromatic_number(7,edges)
    print("chromatic number:",chi,"coloring:",col)
