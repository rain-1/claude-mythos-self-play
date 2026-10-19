import numpy as np, pickle, itertools
from scipy.optimize import least_squares
info=pickle.load(open('planes.pkl','rb'))
F=lambda a,b: a*b*(a+b)*(a*a+a*b+b*b)
rng=np.random.default_rng(0)
def basis(nv):
  # 3 vectors spanning {x: x.nv=0}
  return np.linalg.svd(nv.reshape(1,4))[2][1:].conj()
def isrational(nv):
  k=np.argmax(abs(nv)); v=nv/nv[k]
  return np.allclose(v.imag,0,atol=1e-9) and np.allclose(v.real,np.round(v.real*60)/60,atol=1e-9), v
res=[]
for nv,inside in info:
  if len(inside)!=2: continue
  E=basis(nv)
  G=lambda p: (lambda x: F(x[0],x[1])-F(x[2],x[3]))(p@E)
  # singular points of S∩H = points where gradient of G (in plane coords) vanishes; exclude those on the 2 lines
  sing=[]
  for _ in range(60):
    p0=rng.normal(size=3)+1j*rng.normal(size=3)
    def fun(q):
      p=q[:3]+1j*q[3:]; h=1e-6
      g=[ (G(p+h*e)-G(p-h*e))/(2*h) for e in np.eye(3)]
      nrm=np.vdot(p,p)-1
      return np.r_[np.real(g),np.imag(g),nrm.real,0]
    # instead use polynomial gradient via complex-step-free finite diff; fine
    r=least_squares(lambda q: fun(q)[:7], np.r_[p0.real,p0.imag]/np.linalg.norm(p0), xtol=1e-14,ftol=1e-14,gtol=1e-14)
    if np.linalg.norm(r.fun)<1e-8:
      p=r.x[:3]+1j*r.x[3:]; sing.append(p/p[np.argmax(abs(p))])
  # dedupe
  U=[]
  for s in sing:
    if not any(np.allclose(s,u,atol=1e-5) for u in U): U.append(s)
  rat,v=isrational(nv)
  res.append((inside,len(U),rat,v))
from collections import Counter
print(Counter((r[1],r[2]) for r in res))
for r in res:
  if r[2]: print(r[0], 'nsing',r[1], 'plane',np.round(r[3].real,4))
print()
for r in res:
  print(r[0],r[1])
