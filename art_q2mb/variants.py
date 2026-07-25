"""Map the neighborhood of the counterexample: which nearby machines also fail?

Scans (all exact, full Schur expansion of X_{L(H')}):
  A. move one pendant of H to any other vertex
  B. add one extra edge to H (13-edge -> 13-vertex line graphs)
  C. structural family: cycle C_k (k=4,5,6), two triangles at various separations,
     two pendants at the remaining cycle vertices (all placements)
  D. random connected H' with 8..12 edges on <= 8 vertices (sampled)
Reports every Schur-negative case found.
"""
import itertools, math, random, json, sys
from collections import defaultdict

sys.setrecursionlimit(10000)
memo={}
def chi(mu,rho,L=18):
    if not rho: return 1
    key=(mu,rho)
    if key in memo: return memo[key]
    r=rho[0]; rest=rho[1:]
    beta=set((mu[i] if i<len(mu) else 0)+(L-1-i) for i in range(L))
    tot=0
    for b in beta:
        if b-r>=0 and (b-r) not in beta:
            nb=set(beta); nb.remove(b); nb.add(b-r)
            ht=sum(1 for x in beta if b-r<x<b)
            snb=sorted(nb,reverse=True)
            nmu=tuple(x-(L-1-i) for i,x in enumerate(snb))
            nmu=tuple(x for x in nmu if x>0)
            tot+=(-1)**ht*chi(nmu,rest,L)
    memo[key]=tot
    return tot

def partitions(n, maxp=None):
    if maxp is None: maxp=n
    if n==0: yield (); return
    for p in range(min(n,maxp),0,-1):
        for rest in partitions(n-p,p): yield (p,)+rest
PART = {n: list(partitions(n)) for n in range(1,15)}

def line_graph(hedges):
    n=len(hedges); ge=[]
    for i in range(n):
        for j in range(i+1,n):
            if set(hedges[i])&set(hedges[j]): ge.append((i,j))
    return n,ge

def p_expansion(NV, ge):
    parent=list(range(NV)); size=[1]*NV
    def find(x):
        while parent[x]!=x: x=parent[x]
        return x
    cp=defaultdict(int); NE=len(ge)
    def dfs(k,sign):
        if k==NE:
            roots={}
            for v in range(NV):
                r=find(v); roots[r]=size[r]
            cp[tuple(sorted(roots.values(),reverse=True))]+=sign
            return
        i,j=ge[k]; ri,rj=find(i),find(j)
        if ri==rj: return
        dfs(k+1,sign)
        if size[ri]<size[rj]: ri,rj=rj,ri
        parent[rj]=ri; size[ri]+=size[rj]
        dfs(k+1,-sign)
        parent[rj]=rj; size[ri]-=size[rj]
    dfs(0,1)
    return {l:v for l,v in cp.items() if v!=0}

def schur_negs(hedges):
    """negatives of X_{L(H)} (None if L(H) disconnected input assumed connected)"""
    nv,ge=line_graph(hedges)
    cp=p_expansion(nv,ge)
    negs={}
    for mu in PART[nv]:
        s=sum(v*chi(mu,lam) for lam,v in cp.items())
        if s<0: negs[mu]=s
    return nv, negs

def connected(hedges):
    vs=set(v for e in hedges for v in e)
    ad=defaultdict(set)
    for a,b in hedges: ad[a].add(b); ad[b].add(a)
    start=next(iter(vs)); seen={start}; st=[start]
    while st:
        x=st.pop()
        for y in ad[x]:
            if y not in seen: seen.add(y); st.append(y)
    return seen==vs

H = [('a','b'),('b','c'),('c','d'),('d','a'),
     ('a','u'),('a','v'),('u','v'),
     ('c','x'),('c','y'),('x','y'),
     ('b','l'),('d','m')]
VS = ['a','b','c','d','u','v','x','y']

found=[]
def report(tag, hedges, negs, nv):
    if negs:
        found.append((tag, hedges, {str(k):v for k,v in negs.items()}))
        print(f"  NEGATIVE [{tag}] |V(L)|={nv}: {negs}   H'={hedges}", flush=True)

# ---- A: move a pendant
print("A: pendant moves", flush=True)
base = H[:10]
others = ['a','b','c','d','u','v','x','y']
cnt=0
for p1 in others:
    for p2 in others:
        he = base + [(p1,'l'),(p2,'m')]
        if not connected(he): continue
        cnt+=1
        nv,negs = schur_negs(he)
        report(f"pend {p1},{p2}", he, negs, nv)
print(f"  scanned {cnt} pendant placements", flush=True)

# ---- B: add one edge to H
print("B: single edge additions (13-vertex line graphs)", flush=True)
allv = ['a','b','c','d','u','v','x','y','l','m']
existing = set(map(frozenset,H))
cnt=0
for p,q in itertools.combinations(allv,2):
    if frozenset((p,q)) in existing: continue
    he = H + [(p,q)]
    cnt+=1
    nv,negs = schur_negs(he)
    report(f"add {p}{q}", he, negs, nv)
print(f"  scanned {cnt} edge additions", flush=True)

# ---- C: structural family
print("C: cycle cores C4/C5/C6, two triangles, two pendants", flush=True)
cnt=0
for k in (4,5,6):
    cyc=[chr(ord('A')+i) for i in range(k)]
    cedges=[(cyc[i],cyc[(i+1)%k]) for i in range(k)]
    for t1,t2 in itertools.combinations(range(k),2):
        rest=[i for i in range(k) if i not in (t1,t2)]
        for pl in itertools.combinations_with_replacement(rest,2):
            he = cedges[:]
            he += [(cyc[t1],'u'),(cyc[t1],'v'),('u','v')]
            he += [(cyc[t2],'x'),(cyc[t2],'y'),('x','y')]
            he += [(cyc[pl[0]],'l'),(cyc[pl[1]],'m')]
            if len(he)>14: continue
            cnt+=1
            nv,negs = schur_negs(he)
            report(f"C{k} tri@{t1},{t2} pend@{pl}", he, negs, nv)
print(f"  scanned {cnt} structural variants", flush=True)

# ---- D: random connected sparse graphs
print("D: random connected H' (8..12 edges, <=8 vertices)", flush=True)
rnd=random.Random(2026)
seen_canon=set()
cnt=0
for trial in range(3000):
    nv_h = rnd.randint(5,8)
    ne_h = rnd.randint(8,12)
    verts=[str(i) for i in range(nv_h)]
    all_pairs=list(itertools.combinations(verts,2))
    if ne_h>len(all_pairs): continue
    he = rnd.sample(all_pairs,ne_h)
    if not connected(he): continue
    key=frozenset(map(frozenset,he))
    ck=tuple(sorted(tuple(sorted(e)) for e in key))
    if ck in seen_canon: continue
    seen_canon.add(ck)
    cnt+=1
    nv,negs = schur_negs(he)
    report(f"rand#{trial}", he, negs, nv)
    if cnt>=400: break
print(f"  scanned {cnt} random graphs", flush=True)

print(f"\nTOTAL negative cases found: {len(found)}", flush=True)
json.dump(found, open("art_q2mb/variants.json","w"), indent=1)
print("done", flush=True)
