import numpy as np, itertools, json, sys
from scipy.spatial import ConvexHull
from knot import ham_cycles, determinant
def segdist(p1,q1,p2,q2):
    best=1e9
    for s in np.linspace(0,1,81):
        a=p1+s*(q1-p1); d=q2-p2; t=np.clip(np.dot(a-p2,d)/np.dot(d,d),0,1)
        best=min(best,np.linalg.norm(a-(p2+t*d)))
    return best
def anti(delta, h=0.5774):
    rho=np.sqrt(1-h*h); V=[]
    for k in range(3):
        a=2*np.pi*k/3; V.append([rho*np.cos(a),rho*np.sin(a),h])
        b=a+np.pi/3+np.radians(delta); V.append([rho*np.cos(b),rho*np.sin(b),-h])
    return np.array(V)
for delta in [-30,-25,-20,-15,15,20,25,30]:
    V=anti(delta)
    m=min(segdist(V[a],V[b],V[c],V[d]) for (a,b),(c,d) in itertools.combinations(itertools.combinations(range(6),2),2) if len({a,b,c,d})==4)
    T=[c for c in ham_cycles() if determinant(V[list(c)])==3]
    print(delta, round(m,3), T)
