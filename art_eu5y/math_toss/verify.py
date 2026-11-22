"""verify.py n groupsfile : check that every tossprint class found by brute force (toss2)
is connected by (a) reversal and (b) the STUTTER MOVE:
   w = (gamma o alpha) o (beta_1..beta_r), beta constant on each alpha-block, all beta_k with the
   same number of 1s;  replace alpha by any alpha' in the (recursively computed) class of alpha.
Ordinary BTvW moves are the case 'all beta_k equal'."""
import sys
from functools import lru_cache
sys.setrecursionlimit(10000)
def comp(x, blocks):           # x o (blocks): blocks[0] x0 blocks[1] x1 ...
    out=[]
    for i,b in enumerate(blocks):
        out.append(b)
        if i<len(x): out.append(x[i])
    return ''.join(out)
def split(w, m):               # n = m*b points -> m blocks of length b-1 and separator string of length m-1
    n=len(w)+1; b=n//m
    blocks=[w[i*b:i*b+b-1] for i in range(m)]
    x=''.join(w[i*b+b-1] for i in range(m-1))
    return x, blocks
def neighbours(w, strict=False):
    n=len(w)+1; res=set([w[::-1]])
    for m in range(3,n+1):
        if n%m: continue
        x,blocks=split(w,m)
        if len(set(b.count('1') for b in blocks))>1: continue
        for a in range(3,m+1):
            if m%a or a==n: continue
            r=m//a
            g,chunks=split(x,r)
            if len(set(chunks))>1: continue
            if any(len(set(blocks[k*a:(k+1)*a]))>1 for k in range(r)): continue
            if strict and len(set(blocks))>1: continue      # ordinary (BTvW) moves only
            al=chunks[0]
            for al2 in cls(al, strict):
                if al2!=al:
                    res.add(comp(comp(g,[al2]*r), blocks))
    return res
@lru_cache(maxsize=None)
def cls(w, strict=False):
    seen={w}; st=[w]
    while st:
        u=st.pop()
        for v in neighbours(u, strict):
            if v not in seen: seen.add(v); st.append(v)
    return frozenset(seen)
if __name__=='__main__':
    n=int(sys.argv[1]); bad=0; tot=0; extra=0; sizes={}
    for line in open(sys.argv[2]):
        G=line.split(); tot+=1
        full=set(G)|set(g[::-1] for g in G)
        c=cls(G[0])
        if c!=full:
            bad+=1
            if bad<=5: print('NOT EXPLAINED', sorted(full), 'closure', sorted(c))
        # how many ribbon (strict) classes inside this tossprint class
        k=len(set(cls(g,True) for g in full)); extra+=k-1
        sizes[len(full)]=sizes.get(len(full),0)+1
    print(f'n={n}: {tot} nontrivial tossprint classes, {bad} not explained by stutter moves; '
          f'a - R = -{extra}; class sizes {dict(sorted(sizes.items()))}')
