import numpy as np, numba
def modulus(e,M=8192):
    return np.abs(np.fft.fft(np.asarray(e,float),M))/np.sqrt(len(e))
def rudin_shapiro(k):
    p=np.array([1]); q=np.array([1])
    for _ in range(k): p,q=np.concatenate([p,q]),np.concatenate([p,-q])
    return p
def legendre(p,rot):
    from sympy import legendre_symbol
    e=np.array([1]+[legendre_symbol(i,p) for i in range(1,p)]); return np.roll(e,rot)
@numba.njit
def anneal(N,steps,seed,M,e0,T0,pw):
    np.random.seed(seed)
    e=e0.astype(np.float64).copy()
    # precompute cos/sin tables on M points
    th=2*np.pi*np.arange(M)/M
    re=np.zeros(M); im=np.zeros(M)
    for k in range(N):
        re+=e[k]*np.cos(k*th); im+=e[k]*np.sin(k*th)
    def cost(re,im):
        m=np.sqrt(re*re+im*im)/np.sqrt(N)-1.0; return (np.mean(m**pw))**(1.0/pw)
    c=cost(re,im); best=c; beste=e.copy()
    for s in range(steps):
        T=T0*(1-s/steps)+1e-4
        k=np.random.randint(N)
        cr=np.cos(k*th); ci=np.sin(k*th)
        nre=re-2*e[k]*cr; nim=im-2*e[k]*ci
        nc=cost(nre,nim)
        if nc<c or np.random.rand()<np.exp((c-nc)/T):
            re=nre; im=nim; e[k]=-e[k]; c=nc
            if c<best: best=c; beste=e.copy()
    return beste,best
if __name__=="__main__":
    import time
    for name,e in [('random',np.where(np.random.default_rng(4).random(128)<0.5,-1,1)),('RS',rudin_shapiro(7)),('Leg',legendre(127,32))]:
        m=modulus(e); print(name,len(e),m.min(),m.max())
    import sys
    N=int(sys.argv[1]); 
    from sympy import prevprime
    p=N if N==127 else prevprime(N+1)
    e0=legendre(127,32) if N==127 else np.where(np.random.default_rng(1).random(N)<0.5,-1,1)
    best=None
    for seed in range(4):
        t=time.time(); e,b=anneal(N,int(sys.argv[2]),seed,1024,np.asarray(e0,float),0.01,32); m=modulus(e); print('anneal',seed,time.time()-t,b,m.min(),m.max(),flush=True)
        if best is None or max(m.max()-1,1-m.min())<best[0]: best=(max(m.max()-1,1-m.min()),e)
    np.save('proto/flat_best.npy',best[1]); print('best',best[0])
