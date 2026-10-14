from mpmath import *
mp.dps = 50
T = mpf('-0.48197675632314710911170383198462159135973534627147351787027133860811921057804351843257443137939329739')
a = 1/sqrt(2)
def q(u):
    return u/abs(expm1(mpc(a,-a)*u))**2
K = quad(lambda u: q(u)-1/u, [0,0.5,1]) + quad(q,[1,5,20,inf])
print('K',K)
d = T-2*K
print('T-2K', d)
print(pslq([d,1,euler,log(2),pi,log(pi)],maxcoeff=1000,maxsteps=10**6))
