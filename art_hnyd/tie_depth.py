"""Mechanism measurement: how deep do the ties go at each pass?
For each pass t, reconstruct the matrix state before the pass and measure the
common-prefix length (in the current key order) of each swapped adjacent pair."""
import numpy as np

z = np.load("hero_trace.npz")
A0 = z['A0']
kinds = z['perm_kinds']
perms = z['perm_arrays']
n = A0.shape[0]
T = int(z['T'])

rowp = np.arange(n)
colp = np.arange(n)
state_perms = [(rowp.copy(), colp.copy())]
for t in range(T):
    p = perms[t]
    if kinds[t] == 'R':
        rowp = rowp[p]
    else:
        colp = colp[p]
    state_perms.append((rowp.copy(), colp.copy()))

def common_prefix(u, v):
    d = np.nonzero(u != v)[0]
    return int(d[0]) if len(d) else len(u)

print("pass | axis | #adjacent-swaps | common-prefix length of swapped pairs (median, mean, max)")
for t in range(T):
    rp, cp = state_perms[t]                     # state BEFORE pass t+1
    A = A0[rp][:, cp]
    p = perms[t]
    adj = [i for i in np.nonzero(p != np.arange(n))[0]
           if p[i] == i + 1 and i + 1 < n and p[i + 1] == i]
    if not adj:
        print(f"  {t+1}  | {kinds[t]} | 0 swaps")
        continue
    if kinds[t] == 'R':
        cpls = [common_prefix(A[i], A[i + 1]) for i in adj]
    else:
        At = A.T
        cpls = [common_prefix(At[i], At[i + 1]) for i in adj]
    cpls = np.array(cpls)
    print(f"  {t+1}  | {kinds[t]} | {len(adj):5d} | median {np.median(cpls):7.0f}  mean {cpls.mean():8.1f}  max {cpls.max()}")

# baseline: adjacent rows of the SORTED random matrix (pass-1 output) typical tie depth
A1 = A0[state_perms[1][0]][:, state_perms[1][1]]
cpl0 = np.array([common_prefix(A1[i], A1[i + 1]) for i in range(n - 1)])
print(f"\nbaseline: adjacent rows after pass 1: median cpl {np.median(cpl0):.0f}, "
      f"mean {cpl0.mean():.2f}, max {cpl0.max()} (~log2 n = {np.log2(n):.0f})")
