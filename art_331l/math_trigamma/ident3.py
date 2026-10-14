from mpmath import *
mp.dps = 98
T = mpf('-0.48197675632314710911170383198462159135973534627147351787027133860811921057804351843257443137939329739')
L = loggamma(mpf(1)/4)
base = {'1':1,'g':euler,'l2':log(2),'lp':log(pi),'L':L,'A':log(glaisher)}
names=['T']; vals=[T]
for kn,kv in [('',1),('pi*',pi),('/pi*',1/pi),('pi^2*',pi**2)]:
    for bn,bv in base.items():
        names.append(kn+bn); vals.append(kv*bv)
names += ['G','G/pi','z3','z3/pi','z3/pi^2']; vals += [catalan,catalan/pi,zeta(3),zeta(3)/pi,zeta(3)/pi**2]
print(len(vals))
r = pslq(vals, maxcoeff=3000, maxsteps=10**7)
print(r and [(n,c) for n,c in zip(names,r) if c])
