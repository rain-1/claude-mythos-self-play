import numpy as np, numba
@numba.njit
def seqs(N):
    c=np.zeros(N+1,np.int64); s=np.zeros(N+1,np.int64)
    c[1]=c[2]=1; s[1]=s[2]=1
    for n in range(3,N+1):
        c[n]=c[c[n-1]]+c[n-c[n-1]]
        s[n]=n-s[s[n-1]]-s[n-s[n-1]]
    return c,s
N=2**21
c,s=seqs(N)
n=np.arange(N+1); A=c-n/2; Bv=s-n/2
np.savez_compressed('lake/seq.npz',A=A.astype(np.float32),B=Bv.astype(np.float32))
slack=A-np.abs(Bv)
print('min slack n>=1',slack[1:].min(),'#equal',(slack[1:]==0).sum())
eq=np.nonzero(slack==0)[0]; print('equality points (first 40):',eq[:40], 'last', eq[-10:])
for k in range(4,21):
    lo,hi=2**k,2**(k+1); print(k,'maxA %.0f maxB %.0f minB %.0f  A(2^k)=%g B(2^k)=%g'%(A[lo:hi].max(),Bv[lo:hi].max(),Bv[lo:hi].min(),A[lo],Bv[lo]))
