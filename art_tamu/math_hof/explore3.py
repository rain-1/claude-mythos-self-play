import numpy as np
M=4194304
raw=np.fromfile('arr22.bin',dtype=np.int32)
c=raw[:M+1].astype(np.int64); a=raw[M+1:].astype(np.int64)
g=np.load('g22.npy').astype(np.int64)
n=np.arange(M+1)
A2=2*c-n; b2=2*g-n; S=A2-b2
for k in range(4,22):
    lo,hi=2**k,2**(k+1)
    s=S[lo:hi]; A=A2[lo:hi]; b=b2[lo:hi]
    i=np.argmax(A); j=np.argmax(b)
    print(k,"max2A",A.max(),"at t=%.4f"%(i/2**k),"max2b",b.max(),"at t=%.4f"%(j/2**k),"ratio %.4f"%(b.max()/A.max()),"max slack2",s.max(),"slack/2^(k/2) %.3f"%(s.max()/2**(k/2)), "maxA/2^(k/2)... %.3f"%(A.max()/2**k*np.sqrt(k)) )
eq=np.nonzero(S[1:]==0)[0]+1
for k in range(3,9):
    e=eq[(eq>=2**k)&(eq<2**(k+1))]
    print(k,[ (int(x)-2**k, int(A2[x])) for x in e])
