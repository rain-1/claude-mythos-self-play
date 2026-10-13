# Block construction of precarious necklaces and lower bound (see NOTES.md)
import sys, itertools, math, json
from functools import reduce
def primes(r):
    ps=[];x=2
    while len(ps)<r:
        if all(x%p for p in ps): ps.append(x)
        x+=1
    return ps
def letters(k):
    import string
    return (string.ascii_uppercase+string.ascii_lowercase)[:k]
def even_word(j, qs=None, cols=None):
    """k=2j colours a_t,b_t (t<j). Block i (0<=i<P): concat over t of a_t b_t if i%q_t else b_t a_t."""
    qs=qs or primes(j); P=math.prod(qs)
    cols=cols or letters(2*j)
    out=[]
    for i in range(P):
        blk=''
        for t in range(j):
            a,b=cols[2*t],cols[2*t+1]
            blk+=(a+b if i%qs[t] else b+a)
        out.append(blk)
    return out  # list of blocks (strings of length 2j)
def construct(k):
    j=k//2; cols=letters(k)
    if k%2==0:
        return ''.join(even_word(j,cols=cols))
    qs=primes(j+1); q=qs[-1]
    blocks=even_word(j,qs[:j],cols[:2*j])*q   # W^q, P_{j+1} blocks
    z=cols[2*j]
    return ''.join((z if i%q==0 else '')+b for i,b in enumerate(blocks))
def minper(s):
    n=len(s)
    # smallest d | n with s periodic of period d; use prefix function
    pi=[0]*n; kk=0
    for i in range(1,n):
        while kk and s[i]!=s[kk]: kk=pi[kk-1]
        if s[i]==s[kk]: kk+=1
        pi[i]=kk
    d=n-pi[-1]
    return d if n%d==0 else n
def check(s):
    n=len(s); res={'n':n,'minper':minper(s),'mult':{}}
    ok=res['minper']==n
    for c in sorted(set(s)):
        r=s.replace(c,''); m=len(r)//minper(r); res['mult'][c]=m
        ok = ok and m>=2
    res['precarious']=ok
    return res
def formula(k):
    j=k//2; P=primes(j+1)
    if k%2==0: return 2*j*math.prod(P[:j])
    return 2*j*math.prod(P)+math.prod(P[:j])
def lower_bound(k, maxprime_count=None):
    """min over prime assignments p_c (each prime used <=2 times) of sum_d lcm_{c!=d} p_c.
       WLOG distinct primes used are some subset; search over multisets from first k primes."""
    ps=primes(k+2); best=None; arg=None
    # each prime multiplicity 0,1,2; total k
    def rec(i, rem, cur):
        nonlocal best,arg
        if rem==0:
            ms=[p for p,m in cur for _ in range(m)]
            tot=sum(reduce(lambda a,b:a*b//math.gcd(a,b),[ms[c] for c in range(k) if c!=d],1) for d in range(k))
            if best is None or tot<best: best,arg=tot,ms
            return
        if i==len(ps): return
        for m in (2,1,0):
            if m<=rem: rec(i+1,rem-m,cur+[(ps[i],m)])
    rec(0,k,[])
    return best,arg
if __name__=='__main__':
    ex={}
    for k in range(2,int(sys.argv[1])+1):
        s=construct(k); r=check(s)
        lb=lower_bound(k) if k<=14 else None
        print(k,'len',len(s),'formula',formula(k),'LB',lb,'precarious',r['precarious'],'mults',r['mult'])
