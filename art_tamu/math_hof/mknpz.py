import numpy as np
p=np.fromfile('profiles.bin',dtype=np.int32).reshape(11,4,1024)/2.0  # values of A,B (halves)
d={}
for i,k in enumerate(range(10,21)):
    d[f'k{k}_Amax']=p[i,0]; d[f'k{k}_Amin']=p[i,1]; d[f'k{k}_Bmax']=p[i,2]; d[f'k{k}_Bmin']=p[i,3]
d['ks']=np.arange(10,21)
d['readme']=np.array("Per octave [2^k,2^(k+1)), 1024 equal sub-bins; max/min of A(n)=c(n)-n/2 and B(n)=c*(n)-n/2 over each bin.")
np.savez_compressed('hof_profiles.npz',**d)
s=np.fromfile('small.bin',dtype=np.int32); L=(1<<16)+1
c=s[:L].astype(np.int64); a=s[L:].astype(np.int64); n=np.arange(L)
A=(c-n/2.0); B=(a-n/2.0); A[0]=B[0]=0
np.savez_compressed('hof_small.npz',n=n[1:],c=c[1:],cstar=a[1:],A=A[1:],B=B[1:])
