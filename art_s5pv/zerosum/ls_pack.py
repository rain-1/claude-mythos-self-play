# local-search set packing: maximise the number of disjoint zero-sum subsets (sizes 5..8); N = packed + 1
import numpy as np,sys,time
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
L=[list(map(int,l.split()[1:])) for f in ('zerosum/sets.txt','zerosum/sets8u.txt') for l in open(f)]
n=len(L);A=np.full((n,8),629,np.int32)
for i,s in enumerate(L):A[i,:len(s)]=s
size=(A<629).sum(1)
def cands(free):  # sets entirely inside free (free has an extra True slot at 629)
    return np.nonzero(free[A].all(1))[0]
def greedy(free,chosen):
    while True:
        c=cands(free)
        if len(c)==0:return
        # prefer small sets whose elements are rarely available elsewhere
        cnt=np.bincount(A[c].ravel(),minlength=630)[:629]
        sc=size[c]*1.0+ (cnt[np.minimum(A[c],628)]*(A[c]<629)).sum(1)/size[c]*0.02+rng.random(len(c))*0.6
        k=c[np.argmin(sc)];chosen.append(k);free[A[k]]=False;free[629]=True
free=np.ones(630,bool);chosen=[];greedy(free,chosen)
best=list(chosen);print('greedy',len(best),flush=True)
t0=time.time();T=float(sys.argv[2]) if len(sys.argv)>2 else 600
it=0
owner=np.full(630,-1,np.int64)   # which chosen set owns each element
for k in chosen: owner[A[k]]=k
owner[629]=-1
while time.time()-t0<T:
    it+=1
    # plateau / improving move: a random set touching at most one chosen set and otherwise free elements
    T_=rng.integers(n)
    ow=owner[A[T_]];ow=np.unique(ow[(ow>=0)])
    if len(ow)>1: 
        if rng.random()>0.02: continue
    for k in ow:
        chosen.remove(k);owner[A[k]]=-1;free[A[k]]=True
    free[629]=True
    chosen.append(T_);owner[A[T_]]=T_;free[A[T_]]=False;owner[629]=-1;free[629]=True
    before=len(chosen)
    new=list(chosen);greedy(free,new)
    for k in new[before:]:owner[A[k]]=k
    owner[629]=-1
    chosen=new
    if len(chosen)>len(best):best=list(chosen);print(f'{time.time()-t0:7.1f}s it {it} packed {len(best)} -> N={len(best)+1}',flush=True)
    if len(chosen)<len(best)-3:   # drifted too far: restart from best
        chosen=list(best);free=np.ones(630,bool);owner[:]=-1
        for k in chosen: free[A[k]]=False;owner[A[k]]=k
        free[629]=True;owner[629]=-1
out=sys.argv[3] if len(sys.argv)>3 else 'zerosum/best_packing.txt'
open(out,'w').write('\n'.join(' '.join(str(e) for e in A[k] if e<629) for k in best))
print('final packed',len(best),'N',len(best)+1,'covered',int(size[best].sum()))
