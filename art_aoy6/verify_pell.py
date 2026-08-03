"""verify_pell.py — independent exact verification of the C census.

For every squarefree nonsquare d <= 2000 (and a random large sample):
  1. Recompute the CF of sqrt(d) in exact integer arithmetic.
  2. Build the convergent p/q at the end of the first period (bigint).
  3. Check p^2 - d q^2 == (-1)^period EXACTLY  (parity law tripwire).
  4. Check the C regulator against ln(p + q*sqrt(d)) (mpmath, 50 dps).
  5. Check flags: squarefree (sympy), eligible (no prime factor 3 mod 4).
Also: OEIS A031396 (negative Pell solvable) prefix check, and the classic
d=61 fundamental solution 29718^2 - 61*3805^2 = -1.
"""
import sys, random, numpy as np
from math import isqrt
import sympy, mpmath
mpmath.mp.dps = 60

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pell_test"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 100000

flags = np.fromfile(f"{OUT}/flags.u8", dtype=np.uint8)
period = np.fromfile(f"{OUT}/period.u32", dtype=np.uint32)
reg = np.fromfile(f"{OUT}/reg.f32", dtype=np.float32)
assert len(flags) == N + 1, (len(flags), N)

def cf_exact(d):
    """CF of sqrt(d): returns (period, p, q) with p,q the convergent at the
    end of the first period, exact ints."""
    a0 = isqrt(d)
    assert a0 * a0 != d
    m, q, a = 0, 1, a0
    pm1, pm2 = a0, 1          # p_{-1}=1? standard: p0=a0, p_{-1}=1
    qm1, qm2 = 1, 0
    P = 0
    while True:
        m = a * q - m
        assert (d - m * m) % q == 0
        q = (d - m * m) // q
        a = (a0 + m) // q
        P += 1
        p_new = a * pm1 + pm2
        q_new = a * qm1 + qm2
        if q == 1:
            # convergent at end of period is p_{P-1}/q_{P-1} = pm1/qm1
            return P, pm1, qm1
        pm2, pm1 = pm1, p_new
        qm2, qm1 = qm1, q_new
        assert P < 10 ** 6

fails = 0
tested = 0
ds = [d for d in range(2, 2001) if flags[d] & 4]
rng = random.Random(20260803)
ds += [d for d in rng.sample(range(2, N + 1), 4000) if flags[d] & 4]
for d in ds:
    P, p, q = cf_exact(d)
    tested += 1
    # parity law: norm of fundamental solution
    norm = p * p - d * q * q
    if norm != (-1) ** P:
        print(f"PARITY FAIL d={d}: P={P} norm={norm}")
        fails += 1
    if P != period[d]:
        print(f"PERIOD MISMATCH d={d}: exact {P} vs C {period[d]}")
        fails += 1
    R = mpmath.log(p + q * mpmath.sqrt(d))
    if abs(float(R) - float(reg[d])) > 1e-4 * max(1.0, float(R)):
        print(f"REG MISMATCH d={d}: exact {R} vs C {reg[d]}")
        fails += 1
    # flags
    sf = sympy.factorint(d)
    is_sqfree = all(e == 1 for e in sf.values())
    elig = all(p_ % 4 != 3 for p_ in sf)
    if bool(flags[d] & 1) != is_sqfree:
        print(f"SQFREE FLAG FAIL d={d}"); fails += 1
    if bool(flags[d] & 2) != elig:
        print(f"ELIG FLAG FAIL d={d}"); fails += 1

# OEIS A031396: d for which x^2 - d y^2 = -1 is solvable (d>1 squarefree part
# ... actual A031396 lists numbers k such that Pell(-1) solvable, incl. 1)
a031396 = [1,2,5,10,13,17,26,29,37,41,50,53,58,61,65,73,74,82,85,89,97,101,
           106,109,113,122,125,130,137,145,149,157,170,173,181,185,193,197,
           202,218,226,229,233,241,250,257,265,269,274,277,281,290,293]
mine = [d for d in range(2, 300) if (flags[d] & 4) and period[d] % 2 == 1]
ref = [k for k in a031396 if 1 < k < 300 and (flags[k] & 1)]  # squarefree ones we census
missing = [k for k in ref if k not in mine]
extra = [k for k in mine if k not in a031396]
print(f"OEIS A031396 (squarefree, <300): ref {len(ref)}, "
      f"missing {missing}, extra-not-in-list {extra}")
if missing: fails += 1
# note: A031396 includes non-squarefree k (50,125,250,290? 290=2*5*29 sqfree);
# 'extra' entries just mean the OEIS slice above is a prefix; check none skipped.

# classic d=61
P61, p61, q61 = cf_exact(61)
print(f"d=61: period={P61}, fundamental {p61} + {q61}*sqrt(61), "
      f"norm={p61*p61-61*q61*q61}")
assert (p61, q61) == (29718, 3805) and p61*p61 - 61*q61*q61 == -1

print(f"tested {tested} d exactly; FAILURES: {fails}")
assert fails == 0, "VERIFICATION FAILED"
print("ALL PELL CHECKS PASSED")
