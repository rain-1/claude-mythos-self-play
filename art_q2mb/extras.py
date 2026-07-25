"""Supplementary exact data + minimality probe within the family L(H'), H' <= H."""
import itertools, math, json
from fractions import Fraction
from collections import defaultdict

H_edges = [('a','b'),('b','c'),('c','d'),('d','a'),
           ('a','u'),('a','v'),('u','v'),
           ('c','x'),('c','y'),('x','y'),
           ('b','l'),('d','m')]

def line_graph(hedges):
    n = len(hedges)
    ge = []
    for i in range(n):
        for j in range(i+1,n):
            if set(hedges[i]) & set(hedges[j]): ge.append((i,j))
    return n, ge

def partitions(n, maxp=None):
    if maxp is None: maxp = n
    if n == 0: yield (); return
    for p in range(min(n,maxp), 0, -1):
        for rest in partitions(n-p, p):
            yield (p,)+rest

def zlam(lam):
    z=1; mult=defaultdict(int)
    for p in lam: mult[p]+=1
    for p,m in mult.items():
        z*=p**m; z*=math.factorial(m)
    return z

# ---- Murnaghan-Nakayama, generic n
memo={}
def chi(mu,rho,L=16):
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

def p_expansion(NV, ge):
    """signed edge-subset DFS with cycle-cancellation pruning"""
    parent=list(range(NV)); size=[1]*NV
    def find(x):
        while parent[x]!=x: x=parent[x]
        return x
    cp=defaultdict(int)
    NE=len(ge)
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

def schur_expansion(NV, ge):
    cp=p_expansion(NV, ge)
    return {mu: sum(v*chi(mu,lam) for lam,v in cp.items()) for mu in partitions(NV)}

# ================= extras on the main G =================
NV, Gedges = line_graph(H_edges)
adj=[[False]*NV for _ in range(NV)]
for i,j in Gedges: adj[i][j]=adj[j][i]=True

# independence number & max cliques
best=0
for r in range(1,NV+1):
    found=False
    for S in itertools.combinations(range(NV),r):
        if all(not adj[a][b] for a,b in itertools.combinations(S,2)):
            found=True; break
    if found: best=r
    else: break
alpha=best
omega=0
for r in range(1,NV+1):
    found=False
    for S in itertools.combinations(range(NV),r):
        if all(adj[a][b] for a,b in itertools.combinations(S,2)):
            found=True; break
    if found: omega=r
    else: break
print(f"alpha(G) = {alpha}, omega(G) = {omega}")

# stable partition census by type (blocks = independent sets)
census=defaultdict(int)
order=list(range(NV))
def stab(i, blocks):
    if i==NV:
        census[tuple(sorted(map(len,blocks),reverse=True))]+=1
        return
    v=order[i]
    for b in blocks:
        if all(not adj[v][w] for w in b):
            b.append(v); stab(i+1,blocks); b.pop()
    blocks.append([v]); stab(i+1,blocks); blocks.pop()
stab(0,[])
print(f"total stable partitions: {sum(census.values())}")
# verify against chromatic polynomial: sum N_lam * falling(k, l(lam)) = chi(k)
cp=p_expansion(NV,Gedges)
def chrom(k): return sum(v*k**len(l) for l,v in cp.items())
for k in (4,5,6):
    s=sum(N*math.prod(range(k,k-len(l),-1)) for l,N in census.items())
    assert s==chrom(k),(k,s,chrom(k))
print("stable-partition census verified against chromatic polynomial (k=4,5,6)")
c4=sorted(((l,N) for l,N in census.items() if len(l)<=4), reverse=True)
print("stable partitions with <=4 blocks (the 4-coloring ecology):")
for l,N in c4: print(f"   type {l}: {N}")
acyc=abs(chrom(-1))
print(f"acyclic orientations |chi(-1)| = {acyc}")

# ================= minimality probe =================
# every connected H' subgraph of H (on the vertices its edges cover) gives a
# claw-free line graph L(H') with < 12 vertices when |E(H')| < 12.
# scan ALL 2^12 edge subsets for Schur-negativity of X_{L(H')}.
print("\n-- minimality probe over all subgraphs H' of H --")
found=[]
for mask in range(1, 1<<12):
    he=[H_edges[i] for i in range(12) if mask>>i & 1]
    n=len(he)
    if n<3: continue
    # connected as an edge set? (line graph connected <-> H' connected up to isolated verts)
    vs=set(v for e in he for v in e)
    ad=defaultdict(set)
    for a,b in he: ad[a].add(b); ad[b].add(a)
    start=next(iter(vs)); seen={start}; st=[start]
    while st:
        x=st.pop()
        for y in ad[x]:
            if y not in seen: seen.add(y); st.append(y)
    if seen!=vs: continue
    nv,ge=line_graph(he)
    a_s=schur_expansion(nv,ge)
    negs={mu:v for mu,v in a_s.items() if v<0}
    if negs:
        found.append((n, he, negs))
        print(f"  NEGATIVE at |E|={n}: H'={he}  negs={negs}")
print(f"connected subgraphs scanned; negative cases found: {len(found)}")
if found:
    mn=min(f[0] for f in found)
    print(f"smallest negative within family: {mn} vertices")
    for n,he,negs in sorted(found):
        if n==mn: print("   ", he, negs)
else:
    print("NO smaller counterexample inside the subgraph family — H is minimal in its own family.")

json.dump({"alpha":alpha,"omega":omega,
           "census":{" ".join(map(str,l)):N for l,N in sorted(census.items(),reverse=True)},
           "acyclic":acyc,
           "family_negatives":[[n,he,{ " ".join(map(str,m)):v for m,v in negs.items()}] for n,he,negs in found]},
          open("art_q2mb/extras.json","w"), indent=1)
print("extras written")
