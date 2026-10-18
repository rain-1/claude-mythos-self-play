import sys, numpy as np
fn=sys.argv[1]
cap=set();app=set()
for line in open(fn):
    a=line.split('\t'); p=int(a[0]); app.add(p)
    if a[1]!='-1': cap.add(p)
N=int(sys.argv[2]) if len(sys.argv)>2 else 10**6
s=np.ones(N+1,bool);s[:2]=0
for i in range(2,int(N**.5)+1):
    if s[i]: s[i*i::i]=0
pr=np.nonzero(s)[0]
nc=[int(p) for p in pr if p not in cap]
print('first uncaptured primes:',nc[:15])
print('  of which absent from all S elements:',[p for p in nc[:15] if p not in app])
for X in [100,1000,10**4,10**5,10**6]:
    if X>N: break
    k=sum(1 for p in pr if p<=X and p in cap); print(X,'captured',k,'of',int((pr<=X).sum()))
