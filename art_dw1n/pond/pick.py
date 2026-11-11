# pick d=4 decompositions with rotational symmetry in the octagonal (Petrie) projection
import sys, json, itertools
sys.path.insert(0,'math_cube')
d=4; n=16
def ham_cycles():
    out=[]; path=[0]; used=[False]*n; used[0]=True
    def rec():
        v=path[-1]
        if len(path)==n:
            if bin(v).count('1')==1: out.append(tuple(path))
            return
        for i in range(d):
            w=v^(1<<i)
            if not used[w]:
                used[w]=True; path.append(w); rec(); path.pop(); used[w]=False
    rec(); return out
cyc=ham_cycles()
def arcset(c): return frozenset((c[k],c[(k+1)%n]) for k in range(n))
AS=[arcset(c) for c in cyc]
def mask(s):
    m=0
    for a,b in s: m|=1<<(a*4+((a^b).bit_length()-1))
    return m
A=[mask(s) for s in AS]; full=(1<<64)-1; sols=[]
def cover(m,ch):
    if m==full: sols.append(tuple(ch)); return
    free=(~m)&full; a=free&-free
    for i,x in enumerate(A):
        if x&a and not x&m: ch.append(i); cover(m|x,ch); ch.pop()
cover(0,[])
print(len(sols))
def s8(v):  # (x0,x1,x2,x3)->(x1,x2,x3,1-x0): new bit i = old bit i+1 ; new bit3 = 1-old bit0
    return (v>>1)|((1-(v&1))<<3)
def img(S,f): return frozenset((f(a),f(b)) for a,b in S)
idx={s:i for i,s in enumerate(AS)}
res=[]
for sol in sols:
    S=[AS[i] for i in sol]
    paired=any(frozenset((b,a) for a,b in s) in S for s in S)
    f=s8; g=lambda v:s8(s8(v))
    inv8=all(img(s,f) in S for s in S)
    inv4=all(img(s,g) in S for s in S)
    # permutation induced
    p8=[S.index(img(s,f)) for s in S] if inv8 else None
    p4=[S.index(img(s,g)) for s in S] if inv4 else None
    res.append((sol,paired,inv8,inv4,p8,p4))
print('paired',sum(r[1] for r in res),'inv8',sum(r[2] for r in res),'inv4',sum(r[3] for r in res))
for r in res:
    if r[2] or r[3]: print(r[1:], [cyc[i] for i in r[0]] if not r[1] else '')
json.dump([[cyc[i] for i in r[0]] for r in res if (r[2] or r[3])],open('pond/sym.json','w'))
