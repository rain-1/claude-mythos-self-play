import json, os, networkx as nx
D='/home/user/claude-mythos-self-play/art_331l/math_paths'
best={}   # k -> dict
def load(fn,n):
    for l in open(fn):
        k,m,u,v,g6=l.split(); k,m,u,v=int(k),int(m),int(u),int(v)
        if k in best and (best[k]['n']<n or (best[k]['n']==n and best[k]['m']<=m)): continue
        best[k]=dict(n=n,m=m,u=u,v=v,g6=g6)
for n in range(2,10): load(f'{D}/census2_n{n}.txt',n)
have10=all(os.path.exists(f'{D}/census_n10_{i}.txt') and os.path.getsize(f'{D}/census_n10_{i}.txt')>0 for i in (0,1))
if have10:
    for i in (0,1): load(f'{D}/census_n10_{i}.txt',10)
maxn=10 if have10 else 9
K=4
while K in best: K+=1
out={'description':'f(G)=max_{u!=v} #simple u-v paths. For each k: minimal #vertices n (exhaustive over all connected graphs on <= %d vertices via nauty geng), then minimal #edges m among n-vertex graphs, witness (tie-break: smallest sum of squared degrees for n<=9), maximising pair (u,v) (0-based), and all k paths for k<=60.'%maxn,
     'exhaustive_max_n':maxn,'not_achieved_with_n_le_%d_below_%d'%(maxn,max(best)): '%d values (all > %d); see census keys'%(len([k for k in range(1,max(best)) if k not in best and k!=3]),K-1),
     'contiguous_range':[4,K-1],'census':{}}
for k in sorted(best):
    b=best[k]
    G=nx.from_graph6_bytes(b['g6'].encode())
    e=sorted(tuple(sorted(x)) for x in G.edges())
    ent=dict(k=k,n=b['n'],m=b['m'],edges=e,pair=[b['u'],b['v']],graph6=b['g6'],degrees=[d for _,d in sorted(G.degree())])
    cnt=sum(1 for _ in nx.all_simple_paths(G,b['u'],b['v'])) if k<=5000 else None
    if cnt is not None: assert cnt==k,(k,cnt)
    # verify maximality for small graphs
    if k<=60:
        ent['paths']=sorted(nx.all_simple_paths(G,b['u'],b['v']),key=lambda p:(len(p),p))
        mx=max(sum(1 for _ in nx.all_simple_paths(G,x,y)) for x in G for y in G if x<y)
        assert mx==k
    out['census'][str(k)]=ent
json.dump(out,open(f'{D}/census.json','w'),separators=(",",":"))
json.dump({'description':out['description'],'census':{k:v for k,v in out['census'].items() if int(k)<=200}},open(f'{D}/census_k_le_200.json','w'),indent=1)
# compact table
with open(f'{D}/census_table.tsv','w') as f:
    f.write('k\tn_min\tm_min\tpair\tedges\n')
    for k in sorted(best):
        e=out['census'][str(k)]; f.write(f"{k}\t{e['n']}\t{e['m']}\t{e['pair']}\t{e['edges']}\n")
print('maxn',maxn,'contiguous 4..',K-1,'entries',len(best))
from collections import Counter
nm={k:best[k]['n'] for k in best}
for n in range(2,maxn+1):
    ks=[k for k in nm if nm[k]==n]; print(n,len(ks),'first k needing n:',min(ks) if ks else None)
