import numpy as np
M=4194304
raw=np.fromfile('arr22.bin',dtype=np.int32)
c=raw[:M+1].astype(np.int64); d=raw[M+1:].astype(np.int64)
g=np.load('g22.npy').astype(np.int64)
fc=np.bincount(c[1:]); fg=np.bincount(g[1:]); fd=np.bincount(d[1:])
# values up to M/2 complete
V=M//2
for k in range(1,6):
    lo,hi=2**(k-1)+1,2**k+1
    print(k,"c:",fc[lo:hi].tolist()); print(k,"g:",fg[lo:hi].tolist()); print(k,"c*:",fd[lo:hi].tolist())
for k in range(1,22):
    lo,hi=2**(k-1)+1,2**k+1
    a=sorted(fc[lo:hi]); b=sorted(fg[lo:hi])
    print(k, "multiset equal" if a==b else "differ", "maxfreq c,g", max(a),max(b))
