import sys, numpy as np, math, collections
fn=sys.argv[1]
P=[];W=[];Gn=[];PA=[]
for line in open(fn):
    a=line.rstrip('\n').split('\t')
    P.append(int(a[0]));W.append(int(a[1]));Gn.append(int(a[2]));PA.append(a[3].rstrip(','))
o=np.argsort(P);P=np.array(P)[o];W=np.array(W,dtype=object)[o];Gn=np.array(Gn)[o];PA=[PA[i] for i in o]
def primes_upto(n):
    s=np.ones(n+1,bool);s[:2]=0
    for i in range(2,int(n**.5)+1):
        if s[i]: s[i*i::i]=0
    return np.nonzero(s)[0]
for N in [10**3,10**4,10**5,10**6,10**7]:
    pr=primes_upto(N); have=set(P[P<=N].tolist())
    miss=[int(p) for p in pr if p not in have]
    print(N,'primes',len(pr),'captured',len(have),'missing',len(miss),'first missing',miss[:5])
    if miss: break
    m=P<=N; print('  gen dist',sorted(collections.Counter(Gn[m].tolist()).items()))
