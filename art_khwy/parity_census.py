"""Big census: parity of #components of the forced graph vs n mod 8.
Conjecture: (-1)^(V-C) = Jacobi(-2|n), V=n(n-1)/2. Equivalently
single cycle possible only n = 3,5 mod 8."""
import numpy as np, sys
from collections import Counter
from polylib import forced_graph

def jacobi(a, m):
    a %= m; t = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if m % 8 in (3, 5): t = -t
        a, m = m, a
        if a % 4 == 3 and m % 4 == 3: t = -t
        a %= m
    return t if m == 1 else 0

rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
trials = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
print("n  V  trials  parity-histogram (C mod 2)  predicted-C-parity  agree")
for n in range(3, 20, 2):
    V = n*(n-1)//2
    cnt = Counter(); minc = 99
    got = 0
    while got < trials:
        theta = rng.uniform(0, np.pi, n)
        r = rng.uniform(-1, 1, n)
        # mix in structured samples: near-regular fans
        if got % 5 == 4:
            theta = (np.pi*np.arange(n)/n + rng.normal(0, 0.02, n)) % np.pi
            r = 1.0 + rng.normal(0, 0.15, n)
        comps, _, _ = forced_graph(theta, r)
        if comps is None: continue
        got += 1
        cnt[len(comps) % 2] += 1
        minc = min(minc, len(comps))
    # predicted parity of C: (-1)^(V-C) = jacobi(-2, n) => C = V - [jacobi==-1] mod 2
    pred = (V - (0 if jacobi(-2, n) == 1 else 1)) % 2
    obs = set(cnt)
    print(f"{n:2d} {V:3d} {got:6d}  {dict(cnt)}  minC={minc}  pred={pred}  "
          f"agree={obs == {pred}}")
