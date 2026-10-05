import numpy as np
rng=np.random.default_rng(1)
def hits(P,Q,c,R):
    d=Q-P; t=np.einsum('ij,ij->i',c-P,d)/np.einsum('ij,ij->i',d,d)
    F=P+t[:,None]*d; return np.linalg.norm(F-c,axis=1)<R
def pts(c,R,M):
    a=rng.uniform(0,2*np.pi,M); return c+R*np.stack([np.cos(a),np.sin(a)],1)
def config(kind,r):
    R1,R2,R3=1,r,r*r   # red, black, green
    if kind=='chain':  # red - black - green collinear
        return np.array([0,0.]),np.array([R1+R2,0.]),np.array([R1+2*R2+R3,0.]),(R1,R2,R3)
    # mutually tangent: red at 0, black at (R1+R2,0), green placed tangent to both
    a=R1+R2; b=R1+R3; c=R2+R3
    x=(a*a+b*b-c*c)/(2*a); y=np.sqrt(max(b*b-x*x,0))
    return np.array([0,0.]),np.array([a,0.]),np.array([x,y]),(R1,R2,R3)
M=2_000_000
for kind in ['chain','mutual']:
  for blackmid in [True]:
    for r in [0.5,0.8,1.0,1.6]:
        cr,cb,cg,(R1,R2,R3)=config(kind,r)
        A=pts(cr,R1,M);B=pts(cg,R3,M);C=pts(cg,R3,M)
        print(kind,r,'P(AB hits black)=%.4f P(BC hits black)=%.4f'%(hits(A,B,cb,R2).mean(),hits(B,C,cb,R2).mean()))
print('--- search radii assignments')
import itertools
M=1_000_000
def chain3(Ra,Rb,Rc):  # circles in a row: a - b - c
    return np.array([0,0.]),np.array([Ra+Rb,0.]),np.array([Ra+2*Rb+Rc,0.])
def mutual3(Ra,Rb,Rc):
    a=Ra+Rb; b=Ra+Rc; c=Rb+Rc; x=(a*a+b*b-c*c)/(2*a); y=np.sqrt(b*b-x*x)
    return np.array([0,0.]),np.array([a,0.]),np.array([x,y])
for r in [0.6,1.5]:
  rad=[1,r,r*r]
  for perm in itertools.permutations(range(3)):
    Rr,Rb,Rg=[rad[i] for i in perm]
    for name,f in [('mutual',mutual3)]+[('chain'+''.join(o),None) for o in itertools.permutations('rbg')]:
        if f: cr,cb,cg=f(Rr,Rb,Rg)
        else:
            o=name[5:]; R={'r':Rr,'b':Rb,'g':Rg}; c=chain3(*[R[k] for k in o]); C=dict(zip(o,c)); cr,cb,cg=C['r'],C['b'],C['g']
        A=pts(cr,Rr,M);B=pts(cg,Rg,M);Cc=pts(cg,Rg,M)
        p1,p2=hits(A,B,cb,Rb).mean(),hits(B,Cc,cb,Rb).mean()
        if abs(p1-p2)<0.004: print(r,perm,name,'%.4f %.4f'%(p1,p2))
