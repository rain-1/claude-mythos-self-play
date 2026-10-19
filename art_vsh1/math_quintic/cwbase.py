# implicit equation of CW base curve B in P1xP1 (bidegree (3,3)) and its 72 images; membership test
import numpy as np, itertools
S3=[np.array(m,float) for m in [[[1,0],[0,1]],[[0,1],[1,0]],[[0,1],[-1,-1]],[[-1,-1],[1,0]],[[1,0],[-1,-1]],[[-1,-1],[0,1]]]]
def cwbase(t):
    return np.array([(t+1)*(t*t-4*t-1), 2*(3*t*t+1)]), np.array([(t+1)*(t*t+4*t-1),(t-1)*(t*t-4*t-1)])
def mons(x,y,dx=3,dy=3):
    return np.array([x[0]**i*x[1]**(dx-i)*y[0]**k*y[1]**(dy-k) for i in range(dx+1) for k in range(dy+1)])
ts=np.linspace(-3,3,40)+0.0137
Mt=np.array([mons(*cwbase(t)) for t in ts])
H=np.linalg.svd(Mt)[2][-1]
print("CW base implicit eq residual:",np.linalg.svd(Mt)[1][-2:])
def Hval(x,y): return mons(x,y)@H
def in_cw_orbit(points):
    """points: list of (x,y) pairs of 2-vectors (complex ok) on a base curve. True if all lie on some Aut_Q image of B_CW"""
    for M in S3:
        for N in S3:
            for sw in (0,1):
                ok=True
                for x,y in points:
                    X,Y=(M@x,N@y) if not sw else (N@y,M@x)
                    v=Hval(X/np.linalg.norm(X),Y/np.linalg.norm(Y))
                    if abs(v)>1e-7: ok=False;break
                if ok: return True
    return False
