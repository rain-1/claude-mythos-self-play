# MO 515594: sign of minors of [binom(i,j)^r] (rows a, cols b, b_t <= a_t) -- random search, mpmath
import mpmath as mp, random, itertools
mp.mp.dps=60
def minor(rows,cols,r):
    M=mp.matrix([[mp.binomial(i,j)**r if j<=i else 0 for j in cols] for i in rows])
    return mp.det(M)
random.seed(1)
worst={}
for r in [0.1,0.25,0.5,0.75,0.9,1.5,2,3,5]:
    best=(mp.inf,None)
    for trial in range(4000):
        n=random.randint(4,14); k=random.randint(2,min(5,n))
        rows=sorted(random.sample(range(n+1),k)); cols=sorted(random.sample(range(n+1),k))
        if any(c>rr for c,rr in zip(cols,rows)): continue
        d=minor(rows,cols,r)
        # normalise by product of diagonal
        p=mp.mpf(1)
        for c,rr in zip(cols,rows): p*=mp.binomial(rr,c)**r
        v=d/p
        if v<best[0]: best=(v,(rows,cols))
    print(r, mp.nstr(best[0],8), best[1])
