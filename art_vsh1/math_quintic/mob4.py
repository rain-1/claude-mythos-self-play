import numpy as np, itertools
w=np.exp(2j*np.pi/3)
R=[0,np.inf,-1,w,w*w]
def mob_from(p,q):
    # Mobius sending p[0..2]->q[0..2]; use cross-ratio matrices
    def M(z):
        z1,z2,z3=z
        # sends z1->0, z2->inf, z3->1
        def col(x): return np.array([1,-x]) if np.isfinite(x) else np.array([0,1])
        a=col(z1); b=col(z2)  # (t - z1)/(t - z2) * (z3-z2)/(z3-z1)
        m=np.array([[a[0],a[1]],[b[0],b[1]]],complex)
        v=m@ (np.array([z3,1]) if np.isfinite(z3) else np.array([1,0]))
        return np.diag([v[1],v[0]])@m
    return np.linalg.inv(M(q))@M(p)
def ap(m,x):
    v=m@(np.array([x,1]) if np.isfinite(x) else np.array([1,0]))
    return v[0]/v[1] if abs(v[1])>1e-12*abs(v[0]) else np.inf
def eq(x,y): return (np.isinf(x) and np.isinf(y)) or (np.isfinite(x) and np.isfinite(y) and abs(x-y)<1e-9)
found=0
for P in itertools.combinations(range(5),4):
  for Q in itertools.permutations(range(5),4):
    m=mob_from([R[i] for i in P[:3]],[R[i] for i in Q[:3]])
    if eq(ap(m,R[P[3]]),R[Q[3]]):
      p=[i for i in range(5) if i not in P][0]; q=[i for i in range(5) if i not in Q][0]
      img=ap(m,R[p])
      if not eq(img,R[q]): found+=1; print("4-point match not in stabilizer:",P,Q,img)
print("Mobius maps sending 4 roots to 4 roots but not preserving R:",found)
