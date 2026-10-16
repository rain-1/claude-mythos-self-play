# Independent check: 5x5 Cayley-Menger determinant over all 720 permutations.
import numpy as np, itertools, sys
E=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
def cm(L):
    D=np.zeros((4,4))
    for (i,j),l in zip(E,L): D[i,j]=D[j,i]=l*l
    M=np.ones((5,5)); M[0,0]=0; M[1:,1:]=D
    return np.linalg.det(M)  # = 288 V^2
def tri(a,b,c): return a+b+c>2*max(a,b,c)
def valid(L):
    faces=[(0,1,3),(0,2,4),(1,2,5),(3,4,5)]
    return all(tri(L[a],L[b],L[c]) for a,b,c in faces) and cm(L)>0
bad=0; n=0
for line in open(sys.argv[1]):
    t=line.split(); p=list(map(float,t[1:7]))
    perms=list(itertools.permutations(range(6)))
    vs=[valid([p[q[e]] for e in range(6)]) for q in perms]
    nv=sum(vs)//24
    if t[0]=='S':
        a=list(map(int,t[7:13])); ok=valid([p[i] for i in a]) and nv==int(t[13])
        vol=np.sqrt(cm([p[i] for i in a])/288); ok = ok and abs(vol-float(t[14]))<1e-9
        best=max(np.sqrt(cm([p[q[e]] for e in range(6)])/288) for q,v in zip(perms,vs) if v)
        ok = ok and abs(best-vol)<1e-9
    else: ok = nv==0
    bad+= not ok; n+=1
print("checked",n,"mismatches",bad)
