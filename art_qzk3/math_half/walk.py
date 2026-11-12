"""Metropolis walk over simple graphs on n vertices looking for C(G) = 2^(m-1)."""
import numpy as np, numba as nb, sys, json, time
@nb.njit(cache=True)
def count(n,adj,e,c):
    N=1<<n
    for S in range(1,N):
        low=S&-S; l=0
        while (1<<l)!=low: l+=1
        R=S^low; x=adj[l]&R; pc=0
        while x: x&=x-1; pc+=1
        e[S]=e[R]+pc
    for S in range(1,N):
        low=S&-S; R=S^low; tot=np.int64(1)<<e[S]
        sub=R
        while sub>0:
            sub=(sub-1)&R
            T=low|sub
            tot-=c[T]*(np.int64(1)<<e[S^T])
        c[S]=tot
    return c[N-1]
@nb.njit(cache=True)
def walk(n,seed,steps,beta,hits,mtarget):
    np.random.seed(seed); N=1<<n
    adj=np.zeros(n,np.int64); e=np.zeros(N,np.int64); c=np.zeros(N,np.int64)
    m=0
    for i in range(n):
        for j in range(i+1,n):
            if np.random.random()<0.42: adj[i]|=1<<j; adj[j]|=1<<i; m+=1
    C=count(n,adj,e,c)
    E=30.0 if C<=0 else abs(np.log2(C)-(m-1))+0.02*abs(m-mtarget)
    nh=0
    for s in range(steps):
        i=np.random.randint(n); j=np.random.randint(n)
        if i==j: continue
        adj[i]^=1<<j; adj[j]^=1<<i
        m2=m+(1 if (adj[i]>>j)&1 else -1)
        C2=count(n,adj,e,c)
        E2=30.0 if C2<=0 else abs(np.log2(C2)-(m2-1))+0.02*abs(m2-mtarget)
        if C2>0 and 2*C2==(np.int64(1)<<m2) and nh<hits.shape[0]:
            hits[nh,:n]=adj; hits[nh,n]=m2; nh+=1
        if E2<=E or np.random.random()<np.exp(-beta*(E2-E)):
            m=m2; E=E2
        else:
            adj[i]^=1<<j; adj[j]^=1<<i
    return nh
if __name__=='__main__':
    n=int(sys.argv[1]); seed=int(sys.argv[2]); budget=float(sys.argv[3]); mt=int(sys.argv[4])
    t0=time.time(); out=[]; seen=set(); r=0
    chunk=max(200,int(3e9/3**n))
    while time.time()-t0<budget:
        hits=np.zeros((64,n+1),np.int64)
        nh=walk(n,seed*100003+r,chunk,6.0,hits,mt); r+=1
        for h in hits[:nh]:
            key=tuple(int(v) for v in h)
            if key in seen: continue
            seen.add(key)
            edges=[(i,j) for i in range(n) for j in range(i+1,n) if (key[i]>>j)&1]
            out.append(dict(n=n,m=int(h[n]),edges=edges)); print(n,int(h[n]),edges,flush=True)
            json.dump(out,open(f'{__file__[:-7]}walk_n{n}_s{seed}.json','w'))
    print('done',n,'chunks',r,'chunk',chunk,'hits',len(out))
