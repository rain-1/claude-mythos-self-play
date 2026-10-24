# Verify MO 516332: a(n,m)=d(n^2+m^2), b(n,m)=#{(x,y): x,y>=0, n^2-4y(y+m)=x^2}
import numpy as np, math, sys
from sympy import divisor_count
def b_brute(n,m):
    N=n*n+m*m
    z=np.arange(m, math.isqrt(N)+1, 2, dtype=np.int64)   # z=2y+m
    r=N-z*z; s=np.sqrt(r).astype(np.int64)
    s+= (s+1)**2<=r; s-= s*s>r
    return int(np.count_nonzero(s*s==r))
def inc(m):
    if m%2==0: return False
    p=3
    while p*p<=m:
        while m%p==0:
            if p%4==3: return False
            m//=p
        p+=2
    return m==1 or m%4==1
def theorem_pred(n,m):  # predicted truth of a=2b for n>m^2/4-1, N nonsquare
    return inc(math.gcd(n,m))
if __name__=="__main__":
    EXTRA=int(sys.argv[1]) if len(sys.argv)>1 else 2000
    MMAX=int(sys.argv[2]) if len(sys.argv)>2 else 100
    bad_thm=0; checked=0
    for m in range(1,MMAX+1):
        T=m*m//2; fails=[]; 
        lim = T+EXTRA if inc(m) else T+min(EXTRA,300)
        for n in range(1, lim+1):
            a=int(divisor_count(n*n+m*m)); b=b_brute(n,m)
            ok = (a==2*b)
            if not ok: fails.append(n)
            N=n*n+m*m
            if n>T:
                checked+=1
                if ok!=theorem_pred(n,m): bad_thm+=1; print("THM MISMATCH",n,m)
        if inc(m):
            print(f"m={m} in c: floor(m^2/2)={T}, largest failing n={max(fails) if fails else None}, #fails={len(fails)}, any fail>T: {any(f>T for f in fails)}")
        elif m<=12:
            print(f"m={m} not in c: first fails above T: {[f for f in fails if f>T][:8]}")
    print("theorem checks above threshold:",checked,"mismatches:",bad_thm)
