"""count2.py n [procs] : same prediction as count.py, parallel and lean (for n = 60 ... 100).
Each task = one (b, a, gamma, alpha); returns {min member of closure class: #ribbon classes - 1}."""
import sys, itertools
from multiprocessing import Pool
from verify import comp, cls, neighbours
def strings(L): return [''.join(p) for p in itertools.product('01', repeat=L)]
def closure(w, strict=False):          # uncached closure for full-length strings
    seen={w}; st=[w]
    while st:
        u=st.pop()
        for v in neighbours(u, strict):
            if v not in seen: seen.add(v); st.append(v)
    return seen
def task(args):
    n,b,a,g,al = args
    r = n//(a*b); x = comp(g,[al]*r); res = {}; seen=set()
    byones={}
    for be in strings(b-1): byones.setdefault(be.count('1'),[]).append(be)
    for k,bl in byones.items():
        if len(bl)<2: continue
        for tup in itertools.product(bl, repeat=r):
            if len(set(tup))==1: continue
            w = comp(x,[t for t in tup for _ in range(a)])
            if w in seen: continue
            C = closure(w); seen |= C
            left=set(C); k2=0
            while left:
                u=next(iter(left)); left -= closure(u, True); k2+=1
            res[min(C)] = k2-1
    return res
if __name__=='__main__':
    n=int(sys.argv[1]); procs=int(sys.argv[2]) if len(sys.argv)>2 else 3
    tasks=[]
    for b in range(3,n):
        if n%b: continue
        m=n//b
        for a in range(3,m):
            if m%a or m//a<2: continue
            for al in strings(a-1):
                if len(cls(al))>1:
                    for g in strings(m//a-1): tasks.append((n,b,a,g,al))
    tot={}
    with Pool(procs) as P:
        for i,res in enumerate(P.imap_unordered(task, tasks, chunksize=1)):
            tot.update(res)
            if i%200==0: print(f'  {i}/{len(tasks)} tasks, {len(tot)} classes, running sum {sum(tot.values())}', file=sys.stderr, flush=True)
    print(f'n={n} N={n-1}: predicted R-a = {sum(tot.values())}  ({len(tot)} closure classes)', flush=True)
