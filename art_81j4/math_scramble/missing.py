import numpy as np,sys
fn,R=sys.argv[1],int(sys.argv[2]); W=2*R+1
A=np.fromfile(fn,dtype=np.int64).reshape(W,W)
for k in range(-6,7):
    d=np.diagonal(A,-k)  # A[y,x] with x-y=k -> diagonal offset x-y = k : np.diagonal(A,offset) gives A[i,i+offset] => x-y=offset
    d=np.diagonal(A,k)
    s=set(d.tolist()); miss=[v for v in range(-60,61) if v not in s]
    print(k,len(d),miss)
