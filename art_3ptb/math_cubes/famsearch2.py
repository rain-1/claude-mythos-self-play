import sys, itertools, json
from math import gcd
from famlib import int_kernel
zeros=[list(map(int,l.split())) for l in open(sys.argv[1])]
R=int(sys.argv[2])
best={}
seen=set()
for z in zeros:
    A=z[0::2]; C=z[1::2]
    M=[[a*a for a in A],[a*c for a,c in zip(A,C)],[c*c for c in C]]
    ker=int_kernel(M,6); k=len(ker)
    N=int_kernel([A,C],6)              # orthogonal complement
    W=int_kernel(N,6)                  # Z^6 ∩ span(A,C), 2 vectors
    if len(W)!=2: continue
    # fixed direction A' : find via a B with Q != 0
    for co in itertools.product(range(-R,R+1),repeat=k):
        if not any(co): continue
        B=[sum(co[j]*ker[j][i] for j in range(k)) for i in range(6)]
        b1=sum(W[0][i]*B[i]**2 for i in range(6)); b2=sum(W[1][i]*B[i]**2 for i in range(6))
        if b1==0 and b2==0: continue
        g=gcd(b1,b2)
        Ap=[(b2*W[0][i]-b1*W[1][i])//g for i in range(6)]
        if 0 in Ap: break
        ga=0
        for a in Ap: ga=gcd(ga,a)
        Ap=[a//ga for a in Ap]
        # extended gcd for w
        def eg(a,b):
            if b==0: return (1 if a>=0 else -1,0)
            x,y=eg(b,a%b); return (y, x-(a//b)*y)
        u1,u2=eg(b1,b2)
        w=[u1*W[0][i]+u2*W[1][i] for i in range(6)]
        beta=sum(w[i]*B[i]**2 for i in range(6)); assert beta==g
        # reduce w modulo A' to make it small (w + jA' is equivalent)
        bestw=min((([w[i]+j*Ap[i] for i in range(6)]) for j in range(-50,51)), key=lambda v:max(map(abs,v)))
        w=bestw
        # reduce B modulo A' (x-shift) and w (t-shift)
        cands=[]
        for j1 in range(-6,7):
            for j2 in range(-6,7):
                Bc=[B[i]+j1*Ap[i]+j2*w[i] for i in range(6)]
                cands.append((max(map(abs,Bc)),j2,Bc))
        _,j2,Bc=min(cands)
        alpha=sum(b**3 for b in Bc)
        mod=3*abs(beta); res=alpha%mod
        H=max(max(map(abs,Ap)),max(map(abs,w)),max(map(abs,Bc)))
        key=(mod,res)
        if key not in best or best[key][0]>H:
            best[key]=(H,Ap,Bc,w,alpha,beta)
mods={}
for (mod,res),v in best.items(): mods.setdefault(mod,[]).append(res)
for mod in sorted(mods)[:12]:
    print(mod, len(mods[mod]), sorted(mods[mod])[:40])
json.dump([[k[0],k[1]]+list(v) for k,v in best.items()], open(sys.argv[3],'w'))
