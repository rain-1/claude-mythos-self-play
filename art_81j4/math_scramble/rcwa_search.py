# Search class-wise affine orthomorphisms g of Z: g(m t + r) = a_r t + b_r,
# requiring g and y -> y+g(y) both bijective (and optionally y -> g(y)-y).
from fractions import Fraction as Fr
from itertools import product, combinations_with_replacement
import sys
M=int(sys.argv[1]); A=int(sys.argv[2])
avals=[a for a in range(-A,A+1) if a!=0]
found=0
def exact_cover(classes):  # list of (residue, modulus) ; check exact cover
    L=1
    from math import lcm
    for _,q in classes: L=lcm(L,q)
    cnt=[0]*L
    for r,q in classes:
        for z in range(r%q,L,q): cnt[z]+=1
    return all(c==1 for c in cnt)
for m in range(1,M+1):
  for avec in product(avals,repeat=m):
    if any(m+a==0 for a in avec) or sum(Fr(1,abs(a)) for a in avec)!=1: continue
    if sum(Fr(1,abs(m+a)) for a in avec)!=1: continue
    # choose b_r mod |a_r|
    for bvec in product(*[range(abs(a)) for a in avec]):
        if not exact_cover([(b,abs(a)) for a,b in zip(avec,bvec)]): continue
        if not exact_cover([(r+b,abs(m+a)) for r,(a,b) in enumerate(zip(avec,bvec))]): continue
        print('m',m,'a',avec,'b',bvec); found+=1
        if found>20: sys.exit()
print('found',found)
