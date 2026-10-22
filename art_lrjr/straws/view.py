import numpy as np
from scipy.spatial import ConvexHull
from cell import V0
from knot import crossings, ham_cycles, determinant
def rot_to(nrm):
    # rotation taking nrm to camera-back direction
    from cell import camera
    eye,fwd,right,up=camera()
    a=nrm/np.linalg.norm(nrm); b=-fwd
    v=np.cross(a,b); c=a@b
    K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    return np.eye(3)+K+K@K/(1+c)
h=ConvexHull(V0)
T=[c for c in ham_cycles() if determinant(V0[list(c)])==3][0]
for k,eq in enumerate(h.equations):
    R=rot_to(eq[:3])
    from cell import camera
    eye,fwd,right,up=camera()
    proj=np.stack([right,up,-fwd])
    X=crossings(V0[list(T)], proj@R)
    print(k, len(X))
R0 = rot_to(h.equations[0][:3])
