import numpy as np
M=4194304
raw=np.fromfile('arr22.bin',dtype=np.int32)
c=raw[:M+1].astype(np.int64); a=raw[M+1:].astype(np.int64)
g=np.load('g22.npy').astype(np.int64)
def oc(n): return n.bit_length()-1
cnt=0
for n in range(5,M+1):
    k=oc(n); x=g[n-1]
    gr = g[x]+g[n-x] if k%2==0 else g[x+1]+g[n-1-x]
    if gr!=g[n]:
        cnt+=1
        if cnt<40: print(n,bin(n),k, "a(n-1)=",a[n-1],"n-a(n-1)=",n-a[n-1], "g=",g[n],"gr=",gr)
print(cnt)
