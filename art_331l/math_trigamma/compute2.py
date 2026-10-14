from mpmath import *
import sys
mp.dps = int(sys.argv[1]); N=int(sys.argv[2]); K=int(sys.argv[3])
def f(n):
    n = mpf(n)
    return -2*psi(1, mpc(1,n)).imag - 2/n
s = fsum(f(n) for n in range(1, N))
tail = fsum(2*(-1)**k*bernoulli(2*k)*zeta(2*k+1, N) for k in range(1, K))
print(s+tail)
