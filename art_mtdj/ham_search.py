# MO 515726: search weighted graphs G, G'=G+v whose unique optimal Hamiltonian cycles share no edge.
import itertools, random, sys
def tours(n):
    for p in itertools.permutations(range(1,n)):
        if p[0] < p[-1]: yield (0,)+p
def best(n, w):
    res=[]
    for t in tours(n):
        c=0; ok=True
        for i in range(n):
            e=w.get(frozenset((t[i],t[(i+1)%n])))
            if e is None: ok=False;break
            c+=e
        if ok: res.append((c,t))
    res.sort()
    if not res: return None
    if len(res)>1 and res[1][0]-res[0][0]<1e-9: return 'tie'
    return res[0]
def edges(t): n=len(t); return {frozenset((t[i],t[(i+1)%n])) for i in range(n)}
random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 1)
n=int(sys.argv[1])
for trial in range(200000):
    w={}
    p=random.random()
    for a,b in itertools.combinations(range(n),2):
        if random.random()<0.7: w[frozenset((a,b))]=random.randint(1,20)
    b1=best(n,w)
    if b1 in (None,'tie'): continue
    k=random.randint(2,n)
    for x in random.sample(range(n),k): w[frozenset((x,n))]=random.randint(1,20)
    b2=best(n+1,w)
    if b2 in (None,'tie'): continue
    if not (edges(b1[1]) & edges(b2[1])):
        print('FOUND n=',n,'trial',trial); print('T1',b1,'T2',b2)
        print({tuple(sorted(e)):v for e,v in w.items()}); break
else: print('none')
