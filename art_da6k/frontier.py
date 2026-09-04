"""frontier.py — the zero frontier sigma* of Z(s) via Bohr's possible worlds.

sup Re(zeros of Z) = sup { sigma : exists a character theta of the prime torus with Z_theta(sigma)=0 }
(Kronecker: t -> (t log p mod 2pi)_p is dense; Hurwitz: a zero in a limit function forces zeros
of Z nearby).  We minimise |Z_theta(sigma)| over theta and bisect on sigma.
"""
import numpy as np, json, sys, time
from math import log, pi
from zeta_g import gseq, torus_setup, torus_min

N = int(sys.argv[1]) if len(sys.argv) > 1 else 160
restarts = int(sys.argv[2]) if len(sys.argv) > 2 else 40
g = gseq(N)
primes, V = torus_setup(N, g)
lg = np.array([log(x) for x in g[:N]])
print(f'N={N} terms, {len(primes)} primes; smallest term g^-1 = {np.exp(-lg[-1]):.2e}')
sys.stdout.flush()

out = {}
theta = None
for sigma in [1.06, 1.04, 1.02, 1.00, 0.98, 0.96, 0.94, 0.92, 0.90]:
    t0 = time.time()
    m, theta = torus_min(sigma, V, lg, restarts=restarts, seed=1, theta0=theta)
    # world description: phases of the first few primes
    desc = {str(p): round(float(np.mod(theta[i], 2 * pi)), 4) for i, p in enumerate(primes[:8])}
    print(f'sigma={sigma:.3f}  min|Z_theta| = {m:.3e}   ({time.time()-t0:.1f}s)  theta(2,3,5,7,11,13..)={desc}')
    sys.stdout.flush()
    out[str(sigma)] = dict(min=float(m), theta=[float(x) for x in theta])
json.dump(dict(N=N, primes=primes, results=out), open(f'frontier_N{N}.json', 'w'))
