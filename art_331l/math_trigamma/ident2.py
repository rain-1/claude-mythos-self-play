from mpmath import *
mp.dps = 95
T = mpf('-0.48197675632314710911170383198462159135973534627147351787027133860811921057804351843257443137939329739')
L = loggamma(mpf(1)/4); G=catalan; g=euler; l2=log(2); lp=log(pi); A=log(glaisher)
names=['T','1','pi','1/pi','g','l2','lp','L','G','G/pi','A','z3/pi^2','pi^2','g*pi','l2*pi','lp*pi','L*pi']
vals=[T,1,pi,1/pi,g,l2,lp,L,G,G/pi,A,zeta(3)/pi**2,pi**2,g*pi,l2*pi,lp*pi,L*pi]
r = pslq(vals, maxcoeff=10**4, maxsteps=10**7)
print(r and list(zip(names,r)))
