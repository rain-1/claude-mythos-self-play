import numpy as np
M=4194304
raw=np.fromfile('arr22.bin',dtype=np.int32)
c=raw[:M+1].astype(np.int64); d=raw[M+1:].astype(np.int64)
n=np.arange(M+1)
k=np.zeros(M+1,dtype=np.int64); k[1:]=np.floor(np.log2(n[1:])).astype(np.int64)
# fix log2 precision
k[1:]=np.array([int(x).bit_length()-1 for x in range(1,M+1)]) if False else k[1:]
g=np.where(k%2==0,d,n-d); g[0]=0
print("g first 70:",g[1:70].tolist())
# test hofstadter-like recurrences on g
for name,f in [("g(g(n-1))+g(n-g(n-1))",lambda m: g[g[m-1]]+g[m-g[m-1]]),
               ("n-g(g(n-1))-g(n-g(n-1))",lambda m: m-g[g[m-1]]-g[m-g[m-1]])]:
    m=np.arange(3,M+1); r=f(m); bad=np.nonzero(r!=g[3:])[0]
    print(name,"mismatches",len(bad), (bad[:10]+3).tolist())
print("dg in",set(np.diff(g[1:]).tolist()))
e=c-g; print("e=c-g first:",e[1:80].tolist()); print("min e",e[1:].min())
print("dE in", set(np.diff(e[1:]).tolist()))
# d(n)=c+c*-n, e=c-c*
D=c+d-n; E=c-d
print("D:",D[1:60].tolist()); print("E:",E[1:60].tolist())
np.save('g22.npy',g.astype(np.int32))
