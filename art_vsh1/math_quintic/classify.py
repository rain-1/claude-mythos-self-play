import numpy as np
from numpy.polynomial import polynomial as Pn
def trim(p,tol=1e-8):
    p=np.array(p,complex); s=max(1,np.max(abs(p)))
    while len(p)>1 and abs(p[-1])<tol*s: p=p[:-1]
    return p
def mapdeg(A,B,tol=1e-5):
    A=trim(A); B=trim(B)
    ra=list(Pn.polyroots(A)) if len(A)>1 else []
    rb=list(Pn.polyroots(B)) if len(B)>1 else []
    common=0
    for r in ra:
        m=[i for i,s in enumerate(rb) if abs(s-r)<tol*max(1,abs(r))]
        if m: rb.pop(m[0]); common+=1
    da=len(A)-1; db=len(B)-1
    return max(da,db)-common
grid=[np.array(v,complex) for v in [[0,1],[1,0],[1,-1],[np.exp(2j*np.pi/3),1],[np.exp(-2j*np.pi/3),1]]]
def which_root(x,y,tol=1e-5):
    for i,g in enumerate(grid):
        if abs(x*g[1]-y*g[0])<tol*max(abs(x),abs(y)): return i
    return None
def signature(A,B,C,D,j):
    # points t (roots of F(A,B)F(C,D), plus inf) -> (x-root index, y-root index)
    from gn import parts
    FAB=trim(parts(A,B)[0]); FCD=trim(parts(C,D)[0])
    ts=list(Pn.polyroots(FCD)) if len(FCD)>1 else []
    sig=[]
    for t in ts:
        x=Pn.polyval(t,A),Pn.polyval(t,B); y=Pn.polyval(t,C),Pn.polyval(t,D)
        sig.append((which_root(*x),which_root(*y)))
    return sorted(sig,key=str)
