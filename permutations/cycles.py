import numpy as np

def cycles_of(perm):
    n=len(perm); seen=np.zeros(n,bool); cyc=[]
    for i in range(n):
        if not seen[i]:
            c=[]; j=i
            while not seen[j]:
                seen[j]=True; c.append(j); j=perm[j]
            cyc.append(c)
    return cyc

def verify_stats(n=2000, trials=400, seed=0):
    rng=np.random.default_rng(seed)
    ncyc=[]; longest=[]
    for _ in range(trials):
        p=rng.permutation(n)
        cy=cycles_of(p)
        ncyc.append(len(cy)); longest.append(max(len(c) for c in cy)/n)
    Hn=np.sum(1/np.arange(1,n+1))
    GD=0.6243299885
    return np.mean(ncyc), Hn, np.mean(longest), GD

if __name__=="__main__":
    m_nc, Hn, m_long, GD = verify_stats()
    print(f"mean #cycles = {m_nc:.3f}  vs H_n = {Hn:.3f}")
    print(f"mean longest-cycle fraction = {m_long:.3f}  vs Golomb-Dickman = {GD:.4f}")
