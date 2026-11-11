# MO 208368: partition the 2*d*2^(d-1) arcs of the bidirected d-cube into d directed Hamiltonian cycles.
import sys, itertools
sys.setrecursionlimit(10000)
def ham_cycles(d):
    n=1<<d; out=[]
    path=[0]; used=[False]*n; used[0]=True
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
def arcs(c,d):
    n=len(c); m=0
    for k in range(n):
        a=c[k]; b=c[(k+1)%n]; i=(a^b).bit_length()-1
        m|=1<<(a*d+i)
    return m
d=int(sys.argv[1])
cyc=ham_cycles(d); A=[arcs(c,d) for c in cyc]
print(d,'directed ham cycles',len(cyc))
# exact cover: choose d cycles, pairwise disjoint arcs
byarc={}
for idx,m in enumerate(A):
    low=(m & -m).bit_length()-1
count=0; sols=[]
full=(1<<(d<<d))-1
def cover(mask,chosen):
    global count
    if mask==full:
        count+=1
        if len(sols)<5: sols.append(list(chosen))
        return
    free=(~mask)&full; a=(free&-free)
    for idx,m in enumerate(A):
        if m&a and not m&mask:
            chosen.append(idx); cover(mask|m,chosen); chosen.pop()
cover(0,[])
print('decompositions (unordered sets):',count)
for s in sols[:2]:
    for i in s: print(cyc[i])
    print()
