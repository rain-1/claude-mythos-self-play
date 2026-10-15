import numpy as np
R=1500; W=2*R+1
A=np.fromfile('g0_big.bin',dtype=np.int64).reshape(W,W)
sig=lambda v: np.where(v>0,2*v-1,-2*v)
S=sig(A)
for name,tx,ty in [('row0',S[R,:],S[:,R])]:
    T=np.bitwise_xor.outer(ty,tx)  # [y,x]
    print('frac sigma(f)=tau(x)^tau(y):',(T==S).mean())
tau=S[R,:]  # tau(x)=sigma f(x,0)
print('tau(x) for x=-8..8:',tau[R-8:R+9].tolist())
print('tau col(y) for y=-8..8:',S[R-8:R+9,R].tolist())
print('sorted tau check bijection onto 0..W-1?',sorted(tau.tolist())==list(range(W)))
