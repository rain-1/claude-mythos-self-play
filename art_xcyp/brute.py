from fractions import Fraction
from itertools import combinations
# independent brute force: circles through >=3 lattice points, r <= RB,
# exact rational arithmetic, collect max rim per exact interior n <= NB
RB, NB = Fraction(4), 20
B = 9   # points in [-B,B]^2 relative to anchor; anchor at origin, others lex-greater
pts = [(x,y) for x in range(-B,B+1) for y in range(-B,B+1) if (x,y)!=(0,0)]
seen = {}
best = {}
for (bx,by),(cx,cy) in combinations(pts,2):
    A = bx*cy - by*cx
    if A==0: continue
    nb = bx*bx+by*by; nc = cx*cx+cy*cy
    G = -nb*cy + nc*by; F = nb*cx - nc*bx
    if A<0: A,G,F = -A,-G,-F
    from math import gcd
    g = gcd(gcd(A,abs(G)),abs(F))
    A//=g; G//=g; F//=g
    num = G*G+F*F
    if Fraction(num,4*A*A) > RB*RB: continue
    key = (A, (-G)%(2*A), (-F)%(2*A), num)
    if key in seen: continue
    seen[key]=1
    # exact counts
    cxf = Fraction(-G,2*A); cyf = Fraction(-F,2*A); r2 = Fraction(num,4*A*A)
    R = int(float(r2)**0.5)+2
    on=0; inn=0
    for x in range(int(cxf)-R-2,int(cxf)+R+3):
        for y in range(int(cyf)-R-2,int(cyf)+R+3):
            v = A*(x*x+y*y)+G*x+F*y
            if v<0: inn+=1
            elif v==0: on+=1
    if inn<=NB and on>best.get(inn,0): best[inn]=on
for n in range(NB+1):
    print("B",n,best.get(n,0))
