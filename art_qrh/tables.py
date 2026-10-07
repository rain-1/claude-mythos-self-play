"""All n in Z[w] with norm <= D: primary associate, Moebius, prime factorisation; sextic symbols (u/p)_6 for a row set."""
import numpy as np, sys, pickle
from eis import *
D=int(sys.argv[1]); R=int(math.isqrt(D))+1
P=eisenstein_primes(D); byp={}
for (a,b,N,k) in P:
    if k=='s': byp.setdefault(N,[]).append((a,b))
pidx={(a,b):i for i,(a,b,N,k) in enumerate(P)}
# enumerate primary n with norm <= D (a = 1 mod 3, b = 0 mod 3)
prim=[]
for a in range(-R,R+1):
    if (a-1)%3: continue
    for b in range(-R,R+1):
        if b%3: continue
        N=norm(a,b)
        if 0<N<=D: prim.append((a,b,N))
prim.sort(key=lambda t:t[2]); print('primary n:',len(prim))
mu=np.zeros(len(prim),np.int8); fac=[]
for i,(a,b,N) in enumerate(prim):
    f=factor(a,b,byp); fac.append(f)
    mu[i]=0 if any(e>1 for e in f.values()) else (-1)**len(f)
print('squarefree:',(mu!=0).sum())
# row set: all u with norm <= U (coprime to 3 or not, any)
U=int(sys.argv[2]); rows=[]
for a in range(-int(U**0.5)-1,int(U**0.5)+2):
    for b in range(-int(U**0.5)-1,int(U**0.5)+2):
        if 0<norm(a,b)<=U: rows.append((a,b))
rows.sort(key=lambda t:norm(*t)); print('rows:',len(rows))
# symbol table: sym[prime index][row index] in 0..5 or -1
S=[Sextic(a,b,k) for (a,b,N,k) in P]
sym=np.full((len(P),len(rows)),-1,np.int8)
for i,s in enumerate(S):
    for j,(ua,ub) in enumerate(rows): sym[i,j]=s.sym(ua,ub)
pickle.dump(dict(D=D,prim=prim,mu=mu,fac=fac,primes=P,pidx=pidx,rows=rows,sym=sym),open('tables_%d.pkl'%D,'wb'))
print('done')
