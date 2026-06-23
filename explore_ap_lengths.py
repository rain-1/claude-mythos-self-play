"""
Confirm the AP-length consequence in Z[sqrt-2]:
  - even da  -> long arithmetic progressions of prime-norm points exist
  - odd  da  -> essentially none (length <= 2), as predicted
Also pin down the Z[omega] mod-3 good-step condition precisely.
"""
import numpy as np

def sieve(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            s[i*i::i] = False
    return s

# ---------- longest AP search in Z[sqrt-2], norm a^2 + 2 b^2 ----------------
W = 600
aa, bb = np.mgrid[-W:W+1, -W:W+1]
norm = aa*aa + 2*bb*bb
NMAX = int(norm.max())
isp = sieve(NMAX)
prime = (norm >= 2) & isp[np.clip(norm, 0, NMAX)]

def longest_ap_for_step(prime, da, db, kmax=40):
    """max k such that some (a,b) has all of (a+i*da, b+i*db) prime, i=0..k-1."""
    running = prime.copy()
    best = 1
    for k in range(1, kmax):
        sh = np.roll(np.roll(prime, -k*da, 0), -k*db, 1)
        # invalidate wrapped rows/cols
        if k*da != 0:
            if k*da > 0: sh[-k*da:, :] = False
            else:        sh[:-k*da, :] = False
        if k*db != 0:
            if k*db > 0: sh[:, -k*db:] = False
            else:        sh[:, :-k*db] = False
        running = running & sh
        if not running.any():
            break
        best = k + 1
    return best

print("Z[sqrt-2]  longest AP (terms) per step (da,db):")
for (da, db) in [(2, 0), (0, 1), (2, 2), (4, 0), (2, 1), (0, 2),
                 (1, 0), (1, 1), (3, 0), (1, 2)]:
    L = longest_ap_for_step(prime, da, db)
    tag = "EVEN da (good)" if da % 2 == 0 else "ODD da (blocked)"
    print(f"  step ({da:+d},{db:+d}) : {L:2d} terms   [{tag}]")

# ---------- Z[omega] mod-3 good-step condition ------------------------------
W2 = 260
a2, b2 = np.mgrid[-W2:W2+1, -W2:W2+1]
n2 = a2*a2 - a2*b2 + b2*b2
NM2 = int(n2.max()); isp2 = sieve(NM2)
pr2 = (n2 >= 2) & isp2[np.clip(n2, 0, NM2)]
R = 6
print("\nZ[omega]  pair-correlation by (da,db) mod 3 class (mean count):")
bucket = {}
for da in range(-R, R+1):
    for db in range(-R, R+1):
        sh = np.roll(np.roll(pr2, -da, 0), -db, 1)
        m = pr2 & sh
        if da > 0: m[-da:, :] = False
        elif da < 0: m[:-da, :] = False
        if db > 0: m[:, -db:] = False
        elif db < 0: m[:, :-db] = False
        bucket.setdefault((da % 3, db % 3), []).append(m.sum())
for key in sorted(bucket):
    vals = bucket[key]
    print(f"  (da,db) mod3 = {key} : mean pair-corr {np.mean(vals):8.0f}")
