import sys, json, math, collections, numpy as np
fn, PM, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
R={}
for line in open(fn):
    a=line.rstrip('\n').split('\t'); p=int(a[0])
    if p>PM or a[1]=='-1': continue
    par=[]
    for t in a[3].strip(',').split(','):
        if t: q,e=t.split('^'); par.append([int(q),int(e)])
    R[p]=dict(p=p,witness=int(a[1]),parents=par,gen=int(a[2]))
L=[R[p] for p in sorted(R)]
json.dump(L,open(out,'w'),separators=(',',':'))
print('wrote',out,len(L))
# stats
gens=collections.Counter(r['gen'] for r in L); print('gen dist',sorted(gens.items()))
gcdc=[r['p'] for r in L if any(q==r['p'] for q,e in r['parents'])]; print('captures where witness has p^e,e>1 (gcd step):',len(gcdc),gcdc[:10])
rat=sorted(((math.log(r['witness'])/math.log(r['p']),r['p'],r['witness']) for r in L if r['p']>2),reverse=True)
print('largest log s/log p:',[(round(a,3),b,c) for a,b,c in rat[:8]])
k=[r['witness']//r['p'] for r in L]
big=sorted(((r['witness']/r['p'],r['p'],r['witness']) for r in L),reverse=True)[:8]
print('largest cofactor s/p:',[(int(a),b,c) for a,b,c in big])
pp=np.array([r['p'] for r in L],float); kk=np.array([r['witness']/r['p'] for r in L])
for lo,hi in [(10,1e2),(1e2,1e3),(1e3,1e4),(1e4,1e5),(1e5,1e6),(1e6,2e6)]:
    m=(pp>=lo)&(pp<hi)
    if m.sum(): print(f'p in [{lo:.0e},{hi:.0e}): n={m.sum()} median s/p={np.median(kk[m]):.1f} mean log10(s/p)={np.mean(np.log10(kk[m])):.2f} max s/p={kk[m].max():.0f} frac p in S={np.mean(kk[m]==1):.3f}')
def chain(p):
    r=R[p]; c=[p]
    while r['parents'] and r['gen']>0:
        q=max((q for q,e in r['parents'] if q!=p and q in R),key=lambda q:R[q]['gen']); c.append(q); r=R[q]; p=q
        if r['gen']==0: break
    return c
deep=[r for r in L if r['gen']==max(gens)]
print('deepest gen',max(gens),'count',len(deep))
for r in deep[:6]:
    print('  chain',' <- '.join(f"{q}[{R[q]['witness']}]" for q in chain(r['p'])))
