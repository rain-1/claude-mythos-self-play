# survivor density per denominator q after quadratic-residue sieve (texture for piece 2)
import numpy as np
C = [35534992, 3306770731944, 15172317493269316128, 1093490321304049798772416, 18958669594580211381729967107]
mods = [9, 5, 7, 11, 13, 16, 17, 19, 23]
sq = {m: np.array(sorted({(i*i)%m for i in range(m)})) for m in mods}
issq = {m: np.zeros(m, bool) for m in mods}
for m in mods: issq[m][sq[m]] = True
import json
r_lo, r_hi = -43695, -28782
rows = []
for qd in range(1, 361):
    p = np.arange(int(np.floor(r_lo*qd)), int(np.ceil(r_hi*qd))+1, dtype=np.int64)
    # F(p,q) = -(C0 p^4 + C1 p^3 q + C2 p^2 q^2 + C3 p q^3 + C4 q^4)
    surv = np.ones(len(p), bool)
    npts = len(p)
    for m in mods:
        pm = (p % m).astype(np.int64)
        
        qm = qd % m
        Cm = [c % m for c in C]
        val = (-(Cm[0]*pm**4 + Cm[1]*pm**3*qm + Cm[2]*pm**2*qm**2 + Cm[3]*pm*qm**3 + Cm[4]*qm**4)) % m
        surv &= issq[m][val]
        if not surv.any(): break
    rows.append((qd, npts, int(surv.sum())))
    if qd % 60 == 0: print(qd, flush=True)
json.dump(rows, open('sieve_rows.json','w'))
print("done", sum(r[2] for r in rows), "survivors of", sum(r[1] for r in rows))
