"""pell_analyze.py — global statistics + theorem tripwires over the 1e8 census."""
import numpy as np

OUT = "/tmp/claude-0/-home-user-claude-mythos-self-play/adf44c3e-737f-5218-82c7-9c74bc24d1b1/scratchpad/pell1e8"
N = 100_000_000

flags = np.fromfile(f"{OUT}/flags.u8", dtype=np.uint8)
period = np.fromfile(f"{OUT}/period.u32", dtype=np.uint32)
reg = np.fromfile(f"{OUT}/reg.f32", dtype=np.float32)

proc = (flags & 4) != 0
elig = (flags & 2) != 0
odd = (period & 1) == 1
print(f"processed (squarefree nonsquare): {proc.sum():,}")
print(f"eligible among processed: {(proc & elig).sum():,}")

# THEOREM TRIPWIRE: odd period => eligible (negative Pell needs all odd p|d to be 1 mod 4)
bad = proc & odd & ~elig
print(f"TRIPWIRE odd-period-but-ineligible count (must be 0): {bad.sum()}")
assert bad.sum() == 0

npell = proc & odd
print(f"negative Pell solvable: {npell.sum():,} "
      f"({npell.sum()/proc.sum()*100:.3f}% of all squarefree)")
ef = npell.sum() / (proc & elig).sum()
print(f"fraction among ELIGIBLE at 1e8: {ef:.5f}  (Stevenhagen limit 1-alpha = 0.58058)")

# running fraction in log windows
d = np.arange(N + 1, dtype=np.int64)
edges = np.unique(np.logspace(np.log10(100), 8, 200).astype(np.int64))
eligc = np.cumsum(proc & elig)
oddc = np.cumsum(npell)
print("\ncumulative fraction among eligible at d = 1e3..1e8:")
for D in (10**3, 10**4, 10**5, 10**6, 10**7, 10**8):
    print(f"  d<={D:>12,}: {oddc[D]/eligc[D]:.5f}   (n_elig={eligc[D]:,})")

# period stats
P = period[proc].astype(np.int64)
print(f"\nperiod: max = {P.max():,} at d = {np.argmax(period)}, mean = {P.mean():.1f}")
R = reg[proc].astype(np.float64)
print(f"regulator: max = {R.max():.2f} at d = {np.argmax(reg)}, min = {R.min():.4f}")
imax = np.argmax(reg)
print(f"  record-regulator d = {imax}: period {period[imax]:,}, R = {reg[imax]:.2f}")
print(f"  -> fundamental solution has ~{reg[imax]/np.log(10):.0f} decimal digits")

# roads: smallest regulators at large d
big = proc & (d > 9e7)
Rbig = np.where(big, reg, np.inf)
small_idx = np.argsort(Rbig)[:12]
print("\nsmallest regulators for d > 9e7 (the roads):")
for i in small_idx:
    m = int(np.round(np.sqrt(i)))
    print(f"  d={i}  P={period[i]}  R={reg[i]:.3f}  d-m^2={i-m*m} (m={m}) "
          f"{'ELIG' if flags[i]&2 else 'inel'} {'ODD' if period[i]&1 else 'even'}")

# distribution of R/sqrt(d) at the top end
sel = proc & (d > 5e7)
ratio = reg[sel] / np.sqrt(d[sel])
print(f"\nR/sqrt(d) for d>5e7: mean {ratio.mean():.3f}, median {np.median(ratio):.3f}, "
      f"p99 {np.percentile(ratio,99):.3f}, max {ratio.max():.3f}")

# period parity fractions among eligible in windows (drift view)
print("\nwindowed (not cumulative) fraction among eligible:")
for lo, hi in [(10**6, 2*10**6), (10**7, 2*10**7), (5*10**7, 10**8)]:
    w = proc & elig & (d >= lo) & (d < hi)
    print(f"  [{lo:.0e},{hi:.0e}): {(w & odd).sum()/w.sum():.5f}")
