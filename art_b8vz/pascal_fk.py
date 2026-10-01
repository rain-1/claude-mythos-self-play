import mpmath as mp
mp.mp.dps=50
def f(k,r,s=1):
    return mp.det(mp.matrix([[mp.binomial(i,j)**r for j in range(0,k)] for i in range(s,s+k)]))
for k in range(2,16):
    rs=[mp.mpf(x)/200 for x in range(1,200)]
    vals=[f(k,r) for r in rs]
    neg=[float(r) for r,v in zip(rs,vals) if v<0]
    ch=[float(rs[i]) for i in range(len(rs)-1) if (vals[i]<0)!=(vals[i+1]<0)]
    print(k, 'neg span', (min(neg),max(neg)) if neg else None, 'sign changes', ch, flush=True)
