"""Stage 1 of the 51-fiber verdict sky: enumerate fibers z/t = p/q,
factor M = 51 q^4 - p^4, record conic + D_M local verdicts."""
import json, math
from math import gcd
from sympy import factorint
from fiberlib import conic_soluble, d_locally_soluble

QMAX = 96
out = []
n_conic_dead = n_local_dead = n_surv = 0
for q in range(1, QMAX + 1):
    pmax = int((51 ** 0.25) * q) + 1
    for p in range(0, pmax + 1):
        if p == 0 and q != 1:
            continue
        if p > 0 and gcd(p, q) != 1:
            continue
        M = 51 * q**4 - p**4
        if M <= 0:
            continue
        fac = factorint(M)
        cs, cw = conic_soluble(M, fac)
        ds, dw = d_locally_soluble(M, fac)
        if cs and not ds:
            verdict, wit = 'local_dead', dw     # deeper wall than conic
            n_local_dead += 1
        elif not cs:
            verdict, wit = 'conic_dead', cw
            n_conic_dead += 1
        else:
            verdict, wit = 'survivor', None
            n_surv += 1
        out.append(dict(p=p, q=q, M=int(M), verdict=verdict, wit=str(wit),
                        fac={str(k): int(v) for k, v in fac.items()}))
    print(f'q={q} done', flush=True)

json.dump(out, open('fibers_stage1.json', 'w'))
print('fibers:', len(out), 'conic_dead:', n_conic_dead,
      'local_dead:', n_local_dead, 'survivors:', n_surv)
# consistency: conic-dead should imply D-dead (same p==3 mod 4 odd-order wall)
incons = [f for f in out if f['verdict'] == 'conic_dead'
          and d_locally_soluble(f['M'])[0]]
print('conic_dead but D-soluble (should be 0):', len(incons))
