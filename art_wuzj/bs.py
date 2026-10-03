"""bs.py — exact Pythagorean beanstalk B_n by generations, with ALL derivations."""
import numpy as np
from sympy import factorint
from functools import lru_cache

def legs(w):
    """all (x, z) with w^2 + x^2 = z^2, x>0"""
    f = factorint(w)
    divs = [1]
    for p, e in f.items():
        divs = [d * p**k for d in divs for k in range(2 * e + 1)]
    w2 = w * w
    out = []
    for d in divs:
        if d < w:
            D = w2 // d
            if (d ^ D) & 1 == 0:
                out.append(((D - d) // 2, (D + d) // 2))
    return out

def beanstalk(n):
    S = set(range(1, n + 1)); gen = {s: 0 for s in S}
    L = {}
    frontier = sorted(S)
    derivs = {}   # z -> list of (x, y) with x<y, both in final set
    g = 0
    while frontier:
        g += 1; new = []
        for w in frontier:
            for x, z in legs(w):
                if x in S and z not in S and z not in new:
                    new.append(z)
        # elements born this generation: z whose legs exist among gen<g
        for z in new:
            S.add(z); gen[z] = g
        frontier = new
    # all derivations inside the final set
    for z in S:
        pass
    for w in S:
        for x, z in legs(w):
            if x in S and z in S and w < x:
                derivs.setdefault(z, []).append((w, x))
    return S, gen, derivs

if __name__ == '__main__':
    import sys, pickle
    n = int(sys.argv[1])
    S, gen, der = beanstalk(n)
    print(n, max(S), len(S) - n, max(gen.values()))
    pickle.dump((n, S, gen, der), open(f'bs_{n}.pkl', 'wb'))
