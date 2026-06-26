"""Extended binary Golay code [24,12,8], built and verified.
[23,12] cyclic Golay from generator polynomial g(x)=x^11+x^10+x^6+x^5+x^4+x^2+1,
then extended with an overall parity bit -> [24,12,8]."""
import numpy as np, itertools, collections, random

G_POLY=[1,0,1,0,1,1,1,0,0,0,1,1]   # coeffs x^0..x^11

def generator():
    rows=[]
    for i in range(12):
        r=np.zeros(23,int)
        for k,c in enumerate(G_POLY): r[i+k]=c
        rows.append(r)
    G23=np.array(rows)                          # 12 x 23
    par=G23.sum(1)%2
    G24=np.concatenate([G23, par[:,None]],axis=1)
    return G24                                   # 12 x 24

def codewords():
    G=generator(); out=[]
    for bits in range(4096):
        v=np.zeros(24,int)
        for k in range(12):
            if (bits>>k)&1: v^=G[k]
        out.append(v)
    return np.array(out)

def weight_dist():
    w=codewords().sum(1); return dict(sorted(collections.Counter(w.tolist()).items()))

def octads():
    C=codewords(); return C[C.sum(1)==8]

if __name__=="__main__":
    print("weight distribution:", weight_dist())
    O=octads(); print("octads:", len(O))
    Oset=[frozenset(np.where(o)[0].tolist()) for o in O]
    random.seed(1); ok=True
    for _ in range(400):
        five=frozenset(random.sample(range(24),5))
        if sum(1 for o in Oset if five<=o)!=1: ok=False; break
    print("S(5,8,24):", ok)
