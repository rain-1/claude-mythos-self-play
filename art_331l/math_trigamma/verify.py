from mpmath import *
mp.dps = 60
T = mpf('-0.48197675632314710911170383198462159135973534627147351787027133860811921057804351843257443137939329739')
q = lambda x: 2*x/abs(expm1(mpc(1,1)*x))**2 - exp(-x)/x
I = quad(q,[0,0.25,1,4,16,inf])
Tint = 2*I + log(2) - 2*euler
print('T (lattice) ', T)
print('T (integral)', Tint, ' diff', T-Tint)
# check Mellin link at w=3: int_0^inf u^2/|e^{wu}-1|^2 du = Gamma(3) w^{-3} Z(3)
mp.dps = 30
om = exp(-1j*pi/4)
lhs = quad(lambda u: u**2/abs(expm1(om*u))**2,[0,1,4,16,inf])
Z3 = nsum(lambda n: zeta(3, mpc(1,n)), [1,inf])
print('Mellin check', lhs, 2*om**-3*Z3)
mp.dps = 98
Tm = T
r = pslq([Tm,1,euler,log(2),log(pi),pi,1/pi,sqrt(2),log(1+sqrt(2)),pi*sqrt(2),loggamma(mpf(1)/4),catalan,catalan/pi,sqrt(2)*log(1+sqrt(2))],maxcoeff=10**4,maxsteps=10**7)
print(r)
