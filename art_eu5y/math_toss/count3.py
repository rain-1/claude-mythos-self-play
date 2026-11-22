"""count3.py n [procs] : predicted R(n) - a(n-1) if tossprint classes = closures under direct-sum flips.
Reads pairs<n>.txt from ./gen (every flip w -> w' that is not an ordinary BTvW move), maps each word
to its ribbon (BTvW) class, and counts  #ribbon classes touched - #connected components."""
import sys
from multiprocessing import Pool
from count2 import closure
def rid(w): return min(closure(w, True))
if __name__=='__main__':
    n=int(sys.argv[1]); procs=int(sys.argv[2]) if len(sys.argv)>2 else 4
    pairs=[l.split() for l in open(f'pairs{n}.txt')]
    words=sorted(set(w for p in pairs for w in p))
    with Pool(procs) as P: ids=P.map(rid, words, chunksize=2000)
    I=dict(zip(words,ids)); par={i:i for i in set(ids)}
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for w,v in pairs:
        a,b=f(I[w]),f(I[v])
        if a!=b: par[a]=b
    comps=len(set(f(x) for x in par))
    print(f'n={n} N={n-1}: predicted R-a = {len(par)-comps}   ({len(pairs)} flips, {len(words)} words, {len(par)} ribbon classes, {comps} components)', flush=True)
