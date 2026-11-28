"""P[X1+X2+X3 < 2 X4] for the nested law at finite eps (Monte Carlo, 4e7 hands), and lion counts."""
import numpy as np
rng=np.random.default_rng(5); p=0.47434645545490369; N=10_000_000
def draw(eps,size):
    G=rng.geometric(1-p,size)-1; U=rng.random(size)
    return eps**G*(1-eps**U)
for eps in [0.5,0.3,0.2,0.1,0.03,0.01,1e-3,1e-5]:
    c=np.zeros(5); 
    for rep in range(4):
        X=draw(eps,(N,4)); S=X.sum(1,keepdims=True); L=(3*X>S).sum(1); c+=np.bincount(L,minlength=5)
    c/=4*N; print('eps=%g  P=%.5f  lions 0/1/2: %.4f %.4f %.4f'%(eps,(c*np.arange(5)).sum()/4,c[0],c[1],c[2]))
q=1-p; z=1-p**4
print('limit: k=1..4 tops:',[round(v,5) for v in (4*q*p**3/z,6*q*q*p*p/z,4*q**3*p/z,q**4/z)])
print('limit lions 0/1/2:',q**4/z,4*q*p**3/z,(6*q*q*p*p+4*q**3*p)/z,' T=',(4*q*p**3+2*(6*q*q*p*p+4*q**3*p))/z/4)
