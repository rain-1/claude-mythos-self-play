import sys, itertools, subprocess, math, json
from functools import reduce
def primes_of(g):
    ps=[];d=2
    while d*d<=g:
        if g%d==0:
            ps.append(d)
            while g%d==0: g//=d
        d+=1
    if g>1: ps.append(g)
    return ps
def minper(s):
    n=len(s)
    for p in range(1,n+1):
        if n%p==0 and s==s[p:]+s[:p]: return p
def precarious(s):
    n=len(s)
    if minper(s)<n: return False
    for c in set(s):
        r=s.replace(c,'')
        if minper(r)==len(r): return False
    return True
def canon(s):
    cols=sorted(set(s)); best=None
    n=len(s)
    for t in (s, s[::-1]):
        for r in range(n):
            u=t[r:]+t[:r]
            # relabel by first occurrence
            m={};out=[]
            for ch in u:
                if ch not in m: m[ch]=chr(65+len(m))
                out.append(m[ch])
            u=''.join(out)
            if best is None or u<best: best=u
    return best
def parts(n,k,lo=1):
    if k==1:
        if n>=lo: yield (n,)
        return
    for a in range(lo, n//k+1):
        for rest in parts(n-a,k-1,a): yield (a,)+rest
def search(k,n,maxsol=10**6):
    sols=set(); combos=0
    for cv in parts(n,k):
        opts=[]
        for c in range(k):
            g=reduce(math.gcd,[cv[d] for d in range(k) if d!=c])
            opts.append(primes_of(g))
        if any(not o for o in opts): continue
        for ps in itertools.product(*opts):
            combos+=1
            out=subprocess.run(['./bt',str(k),str(n)]+[str(x) for x in cv]+[str(p) for p in ps]+[str(maxsol)],capture_output=True,text=True).stdout.split()
            for s in out:
                assert precarious(s), s
                sols.add(canon(s))
    return sols, combos
if __name__=='__main__':
    k=int(sys.argv[1]); n0=int(sys.argv[2]); n1=int(sys.argv[3])
    for n in range(n0,n1+1):
        sols,combos=search(k,n)
        print(k,n,'combos',combos,'classes',len(sols),sorted(sols)[:20],flush=True)
