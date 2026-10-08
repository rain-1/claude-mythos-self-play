# Rational points on one genus-1 fibre of x^4+y^4+2z^4=w^4 (MO 515812, Bremner-Choudhry-Ulas pencil):
#   Q1: x^2+y^2-w^2 = t(xy-z^2),  Q2: t(x^2+y^2+w^2) = 2(xy+z^2).
# Four points of a quadric-intersection curve are coplanar iff they sum to a constant, so the plane through
# three rational points meets the curve in a fourth: with known points on the coordinate vertices of the
# plane, the two restricted conics are m12 uv+m13 uw+m23 vw=0 and are LINEAR in (1/u,1/v,1/w).
from fractions import Fraction as F
import itertools, json, math, sys
a,c,d,e=110135,244580,249568,325193
t=F(2*(a*d+c*c)*e*e, (a*a+d*d+e*e)*e*e)
def Q1(p,q): # bilinear form of Q1
    return p[0]*q[0]+p[1]*q[1]-p[3]*q[3]-t*(F(1,2)*(p[0]*q[1]+p[1]*q[0])-p[2]*q[2])
def Q2(p,q):
    return t*(p[0]*q[0]+p[1]*q[1]+p[3]*q[3])-(p[0]*q[1]+p[1]*q[0])-2*p[2]*q[2]
def norm(p):
    import math
    g=p[3] if p[3]!=0 else next(v for v in p if v!=0)
    p=[v/g for v in p]
    return tuple(p)
def fourth(A,B,C):
    m=(Q1(B,C),Q1(A,C),Q1(A,B)); n=(Q2(B,C),Q2(A,C),Q2(A,B))
    cr=(m[1]*n[2]-m[2]*n[1], m[2]*n[0]-m[0]*n[2], m[0]*n[1]-m[1]*n[0])
    if any(v==0 for v in cr): return None
    u,v,w=(1/cr[0],1/cr[1],1/cr[2])
    D=[u*A[i]+v*B[i]+w*C[i] for i in range(4)]
    if D[3]==0: return None
    return norm(D)
def height(p):
    return max(max(abs(v.numerator),abs(v.denominator)) for v in p)
base=[]
for sx in (1,-1):
  for sz in (1,-1):
    for sw in (False,True):
      X,Y=(a,d) if not sw else (d,a)
      base.append(norm([F(sx*X),F(sx*Y),F(sz*c),F(e)]))
for p in base: assert Q1(p,p)==0 and Q2(p,p)==0
S={p:0 for p in base}
gen=0
N=int(sys.argv[1]) if len(sys.argv)>1 else 400
while len(S)<N and gen<3:
    gen+=1
    pts=sorted(S,key=height)[:40+20*gen]
    new={}
    for A,B,C in itertools.combinations(pts,3):
        D=fourth(A,B,C)
        if D and D not in S and D not in new:
            new[D]=gen
    # keep the lowest-height new points
    for D in sorted(new,key=height)[:max(60,N//4)]:
        S[D]=gen
        if len(S)>=N: break
    print(gen,len(S),min(math.log10(height(p)) for p in new) if new else None,flush=True)
out=[[float(v) for v in p[:3]]+[math.log10(height(p)),g] for p,g in S.items()]
json.dump({'t':float(t),'pts':out},open('quartic_pts.json','w'))
