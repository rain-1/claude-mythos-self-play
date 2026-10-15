# Recursive search for class-wise affine g(m t + r) = a_r t + b_r with g, y+g(y)
# bijective (orthomorphism), and if STRONG also g(y)-y bijective.
import sys
from fractions import Fraction as Fr
from itertools import product
from math import lcm
M=int(sys.argv[1]); A=int(sys.argv[2]); STRONG=int(sys.argv[3])
def exact_cover(classes):
    L=1
    for _,q in classes: L=lcm(L,q)
    if L>5000: return False
    cnt=[0]*L
    for r,q in classes:
        for z in range(r%q,L,q):
            cnt[z]+=1
            if cnt[z]>1: return False
    return all(c==1 for c in cnt)
found=0
for m in range(1,M+1):
    av=[a for a in range(-A,A+1) if a!=0 and a!=-m and (not STRONG or a!=m)]
    def rec(pre,s1,s2,s3):
        global found
        if len(pre)==m:
            if s1==1 and s2==1 and (not STRONG or s3==1):
                for bvec in product(*[range(abs(a)) for a in pre]):
                    if not exact_cover([(b,abs(a)) for a,b in zip(pre,bvec)]): continue
                    if not exact_cover([(r+b,abs(m+a)) for r,(a,b) in enumerate(zip(pre,bvec))]): continue
                    if STRONG and not exact_cover([(b-r,abs(a-m)) for r,(a,b) in enumerate(zip(pre,bvec))]): continue
                    print('m',m,'a',pre,'b',bvec,flush=True); found+=1
                    if found>=8: sys.exit()
            return
        for a in av:
            t1=s1+Fr(1,abs(a)); t2=s2+Fr(1,abs(m+a)); t3=s3+(Fr(1,abs(a-m)) if STRONG else 0)
            if t1<=1 and t2<=1 and t3<=1: rec(pre+[a],t1,t2,t3)
    rec([],0,0,0)
print('found',found)
