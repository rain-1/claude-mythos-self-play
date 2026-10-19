import numpy as np, itertools
w=np.exp(2j*np.pi/3); z=np.exp(2j*np.pi/5)
S3=[np.array(m,dtype=complex) for m in [[[1,0],[0,1]],[[0,1],[1,0]],[[0,1],[-1,-1]],[[-1,-1],[1,0]],[[1,0],[-1,-1]],[[-1,-1],[0,1]]]]
F=lambda a,b: a*b*(a+b)*(a*a+a*b+b*b)
roots=[np.array(r,dtype=complex) for r in [[0,1],[1,0],[1,-1],[w,1],[w*w,1]]]
lines=[]
for k in range(5):
  for i,M in enumerate(S3):
    Mz=z**k*M; lines.append(('G(%d,s%d)'%(k,i), np.array([np.r_[[1,0],Mz@[1,0]], np.r_[[0,1],Mz@[0,1]]])))
for i in range(5):
  for j in range(5):
    lines.append(('L(%d,%d)'%(i,j), np.array([np.r_[roots[i],[0,0]], np.r_[[0,0],roots[j]]])))
# verify on S
rng=np.random.default_rng(1)
for n,L in lines:
  for _ in range(3):
    p=rng.normal(size=2)@L; assert abs(F(p[0],p[1])-F(p[2],p[3]))<1e-9
print("55 lines verified on S")
rk=lambda A: np.linalg.matrix_rank(A,tol=1e-8)
planes=[]
for (n1,L1),(n2,L2) in itertools.combinations(lines,2):
  if rk(np.vstack([L1,L2]))==3:
    B=np.vstack([L1,L2]); 
    # normal vector
    nv=np.linalg.svd(B)[2][-1].conj()
    if not any(abs(abs(np.vdot(nv,q))-1)<1e-8 for q,_ in planes): planes.append((nv,None))
print("intersecting-line planes:",len(planes))
# for each plane count lines inside, and test residual
from collections import Counter
cnt=Counter(); info=[]
for nv,_ in planes:
  inside=[n for n,L in lines if np.allclose(L@nv.conj().conj() if False else L@np.conj(nv).conj(),0,atol=1e-8)]
  info.append((nv,inside)); cnt[len(inside)]+=1
print("distribution of #lines in such planes:",cnt)
np.save('planes.npy',np.array([p for p,_ in info]))
import pickle; pickle.dump(info,open('planes.pkl','wb'))
