import numpy as np
M=4194304
raw=np.fromfile('arr22.bin',dtype=np.int32)
c=raw[:M+1].astype(np.int64); a=raw[M+1:].astype(np.int64)
g=np.load('g22.npy').astype(np.int64)
n=np.arange(M+1); A2=2*c-n; b2=2*g-n
def Phi(f2,k,e):
    # f2: dict-like array over full index (2*profile), only octave k-1 used; returns D2 on [2^k,2^(k+1)]
    lo=2**k; D=np.zeros(lo+1,dtype=np.int64)
    for i in range(1,lo+1):
        nn=lo+i; sp=D[i-1]+e; L=(nn+sp)//2; T=nn-L
        def F(x):
            if x==lo+1: return -1
            assert lo//2<=x<=lo, (k,nn,x)
            return f2[x]
        D[i]=F(L)+F(T)
    return D
ok=True
for k in []:
    lo=2**k; Ak=A2[lo:2*lo+1]; bk=b2[lo:2*lo+1]
    e = -1 if k%2==0 else 1
    try:
        r1=Phi(A2,k,-1); r2=Phi(b2,k,e); r3=Phi(A2,k,+1); r4=Phi(b2,k,-1)
    except AssertionError as er: print("assert",er); continue
    print(k,"Conway reproduced",np.array_equal(r1,Ak),"g reproduced",np.array_equal(r2,bk),
          "Phi(A,+1)<=A:",bool((r3<=Ak).all()),"Phi(b,-1)<=A:",bool((r4<=Ak).all()),"Phi(b,+1)<=Phi(b,-1):",bool((Phi(b2,k,1)<=r4).all()))
print("--- reflection tests")
def R(f2,k):  # reflect octave k-1 portion: indices [2^(k-1),2^k]
    h=2**(k-1); out=f2.copy(); seg=f2[h:2*h+1]; out[h:2*h+1]=seg[::-1]; return out
for k in range(3,15):
    lo=2**k; bk=b2[lo:2*lo+1]; Ak=A2[lo:2*lo+1]
    p1=Phi(b2,k,1); p2=Phi(R(b2,k),k,-1)[::-1]; p3=Phi(R(b2,k),k,1)[::-1]
    print(k,"Phi(b,+1)==R Phi(Rb,-1):",np.array_equal(p1,p2),"==R Phi(Rb,+1):",np.array_equal(p1,p3),
      " A vs R Phi(R A,-1):",np.array_equal(Ak,Phi(R(A2,k),k,-1)[::-1]), " A vs RPhi(RA,+1):",np.array_equal(Ak,Phi(R(A2,k),k,1)[::-1]),
      " b symmetric?",np.array_equal(bk,bk[::-1]))
