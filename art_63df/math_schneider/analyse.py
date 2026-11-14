import json,glob
from fractions import Fraction as F
R=[]
for f in glob.glob('survey_*.json'): R+=json.load(open(f))
print(len(R), sum(r['exact'] for r in R))
drops={}
for r in R:
    if not r['exact']: continue
    a=[F(x) for x in r['a']]
    for n in range(1,len(a)):
        d=a[n-1]-a[n]
        naive=(n+1)*a[n]-((n+2)*a[n-1]-2)
        drops.setdefault(n,[]).append((d,a[n-1],a[n],naive,r['M']))
for n in sorted(drops):
    L=drops[n]
    print('n',n,'max drop',[str(x) for x in max(L,key=lambda t:t[0])[:3]], max(L,key=lambda t:t[0])[4],'| min drop',[str(x) for x in min(L,key=lambda t:t[0])[:3]])
    v=[t for t in L if t[3]<0]
    print('  naive violations',len(v),'of',len(L))
    for t in sorted(v,key=lambda t:t[3])[:3]: print('   ',[str(x) for x in t[:4]],t[4])
    # envelope: for bins of a_n, the min a_{n+1}
    env={}
    for t in L:
        k=t[1]
        if k not in env or t[2]<env[k][0]: env[k]=(t[2],t[4])
    ks=sorted(env)
    print('  envelope (a_n -> min a_{n+1}):',[(str(k),str(env[k][0])) for k in ks if env[k][0] < k][:40])
print('max a_1',max(F(r['a'][0]) for r in R), 'a increasing anywhere?', sum(1 for n in drops for t in drops[n] if t[0]<0))
