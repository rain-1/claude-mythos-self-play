# brute-force cross-check of pinwheel.c for n<=9 + count pinwheel primes (for the art)
import itertools, math, sys
from sympy import isprime
def orbits(n):
    seen=set(); out=[]
    for i in range(n):
        for j in range(n):
            if (i,j) in seen: continue
            o=[]; a,b=i,j
            while (a,b) not in o: o.append((a,b)); a,b=b,n-1-a
            seen|=set(o); out.append(o)
    return out
def numbers(n):
    O=orbits(n); nb=n*n
    vals=[sum(1<<(nb-1-(a*n+b)) for a,b in o) for o in O]
    c0=[k for k,o in enumerate(O) if (0,0) in o][0]
    rest=[v for k,v in enumerate(vals) if k!=c0]
    for bits in itertools.product((0,1),repeat=len(rest)):
        yield vals[c0]+sum(v for v,b in zip(rest,bits) if b)
if __name__=="__main__":
    for n in range(2,int(sys.argv[1])+1):
        sq=pr=tot=0
        for N in numbers(n):
            tot+=1; r=math.isqrt(N)
            if r*r==N: sq+=1
            if isprime(N): pr+=1
        print(n,tot,'squares',sq,'primes',pr)
