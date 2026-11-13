import numpy as np
from fast import one, primes_upto
from rec import run, isprime
pr=primes_upto(400000)
for n in range(2,6001):
    a,c,last,nf=run(n)
    A,C,L,F,G,P=one(n,pr)
    assert (a,c,last,nf)==(A,C,L,F),(n,(a,c,last,nf),(A,C,L,F))
    assert bool(isprime(a))==(P==1),n
print('fast == brute for n<=6000')
