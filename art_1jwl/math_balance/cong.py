# congruence obstructions: residues mod M reachable by ±1^k ± ... ± n^k
import sys, numpy as np
def obstructed(k, nmax, M):
    r = np.zeros(M, bool); r[0] = True
    out = []
    for n in range(1, nmax+1):
        w = pow(n, k, M)
        r = np.roll(r, w) | np.roll(r, -w)
        par = (n*(n+1)//2) % 2
        ok = r[0] if par == 0 else (r[1] or r[M-1])
        if not ok: out.append(n)
    return out
if __name__ == "__main__":
    for k in range(1, 41):
        res = {}
        for M in (2**12, 3**6, 5**4, 7**4, 11**3, 13**3, 17**3):
            o = obstructed(k, 400, M)
            if o: res[M] = o
        print(k, {m: (v if len(v) < 40 else v[:12] + ['...'] + v[-12:]) for m, v in res.items()})
