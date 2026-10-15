# Backtracking search for class-wise affine g(m t + r) = a_r t + b_r such that
# g, y+g(y), g(y)-y are all bijections of Z (=> f(x,y)=x+g(y) also scrambles anti-diagonals).
# Coverage tracked as bitsets on Z/L0; all moduli must divide L0.
import sys
from fractions import Fraction as Fr
M=int(sys.argv[1]); A=int(sys.argv[2]); L0=int(sys.argv[3]) if len(sys.argv)>3 else 5040
FULL=(1<<L0)-1
cache={}
def cls(b,q):
    key=(b%q,q)
    if key not in cache:
        x=0
        for z in range(b%q,L0,q): x|=1<<z
        cache[key]=x
    return cache[key]
found=0
for m in range(1,M+1):
    av=[a for a in range(-A,A+1) if a not in (0,m,-m) and L0%abs(a)==0 and L0%abs(m+a)==0 and L0%abs(a-m)==0]
    sol=[]
    def rec(r,c1,c2,c3,s1,s2,s3):
        global found
        if r==m:
            if c1==FULL and c2==FULL and c3==FULL:
                print('m',m,'a,b =',sol,flush=True); found+=1
                if found>=5: sys.exit()
            return
        for a in av:
            t1=s1+Fr(1,abs(a)); t2=s2+Fr(1,abs(m+a)); t3=s3+Fr(1,abs(a-m))
            if t1>1 or t2>1 or t3>1: continue
            if r==m-1 and (t1!=1 or t2!=1 or t3!=1): continue
            for b in range(abs(a)):
                k1=cls(b,abs(a))
                if c1&k1: continue
                k2=cls(r+b,abs(m+a))
                if c2&k2: continue
                k3=cls(b-r,abs(a-m))
                if c3&k3: continue
                sol.append((a,b)); rec(r+1,c1|k1,c2|k2,c3|k3,t1,t2,t3); sol.pop()
    rec(0,0,0,0,0,0,0)
    print('done m',m,'found so far',found,flush=True)
