"""Uniform random sorting networks of n wires: hook-walk SYT of the staircase + Edelman–Greene."""
import numpy as np, numba as nb, sys
@nb.njit(cache=True)
def hook_walk_syt(n,seed):
    np.random.seed(seed)
    m=n-1                      # staircase rows 0..m-1, row i has m-i cells
    rowlen=np.empty(m,np.int64)
    for i in range(m): rowlen[i]=m-i
    N=m*(m+1)//2
    T=np.zeros((m,m),np.int64)
    for val in range(N,0,-1):
        # pick uniform cell of current shape
        tot=0
        for i in range(m): tot+=rowlen[i]
        r=np.random.randint(tot)
        i=0
        while r>=rowlen[i]: r-=rowlen[i]; i+=1
        j=r
        while True:
            arm=rowlen[i]-j-1
            leg=0
            while i+leg+1<m and rowlen[i+leg+1]>j: leg+=1
            if arm+leg==0: break
            k=np.random.randint(arm+leg)
            if k<arm: j=j+1+k
            else: i=i+1+(k-arm)
        T[i,j]=val; rowlen[i]-=1
    return T
@nb.njit(cache=True)
def edelman_greene(T,n):
    m=n-1; N=m*(m+1)//2
    T=T.copy(); word=np.empty(N,np.int64)
    for s in range(N):
        # locate max
        bi=0;bj=0;bv=-1
        for i in range(m):
            j=m-1-i
            if T[i,j]>bv: bv=T[i,j]; bi=i; bj=j
        word[s]=bj    # corner in row bi, column bj=m-1-bi
        # slide hole from (bi,bj) toward (0,0)
        i=bi; j=bj
        while i>0 or j>0:
            up=T[i-1,j] if i>0 else -1
            lf=T[i,j-1] if j>0 else -1
            if up>lf: T[i,j]=up; i-=1
            else: T[i,j]=lf; j-=1
        T[0,0]=0
        for a in range(m):
            for b in range(m-a): T[a,b]+=1
    return word
def network(n,seed=1):
    T=hook_walk_syt(n,seed); w=edelman_greene(T,n)
    return w     # swap positions w[k], w[k]+1 at time k (0-based positions)
def trajectories(n,w):
    perm=np.arange(n); pos=np.zeros((len(w)+1,n),np.int32); pos[0]=np.arange(n)
    where=np.arange(n)
    for k,a in enumerate(w):
        x,y=perm[a],perm[a+1]
        assert x<y, 'not reduced'
        perm[a],perm[a+1]=y,x; where[x]=a+1; where[y]=a
        pos[k+1]=where
    assert (perm==np.arange(n)[::-1]).all()
    return pos
if __name__=='__main__':
    n=int(sys.argv[1]); w=network(n,int(sys.argv[2]))
    P=trajectories(n,w); print('ok',n,len(w)); np.save(f'net_{n}_{sys.argv[2]}.npy',w)
