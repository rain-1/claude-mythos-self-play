"""Trace the alternating sort on one 4096x4096 random binary matrix.
Record: per-pass change masks (which cells flipped value), last-change pass,
change count, row/col permutation displacement per pass; save everything."""
import numpy as np
from sort_lib import _row_keys, _lex_argsort, rows_sorted

n = 4096
rng = np.random.default_rng(513971)          # seed = the MO question number
A0 = rng.integers(0, 2, (n, n), dtype=np.int8).astype(np.uint8)

A = A0.copy()
last_change = np.zeros((n, n), np.int16)     # 0 = never changed
change_count = np.zeros((n, n), np.int16)
masks = []
perms = []                                    # (pass, 'R'/'C', permutation applied)
t = 0
while True:
    t += 1
    if t % 2 == 1:
        K = _row_keys(A)
        p = _lex_argsort(K)
        B = A[p]
        perms.append(('R', p.astype(np.int32)))
    else:
        K = _row_keys(np.ascontiguousarray(A.T))
        p = _lex_argsort(K)
        B = A[:, p]
        perms.append(('C', p.astype(np.int32)))
    m = A != B
    masks.append(m)
    nm = int(m.sum())
    disp = int(np.abs(p - np.arange(n)).sum())
    print(f"pass {t} ({'R' if t%2 else 'C'}): changed cells={nm}  perm displacement={disp}",
          flush=True)
    last_change[m] = t
    change_count += m
    A = B
    if rows_sorted(A) and rows_sorted(np.ascontiguousarray(A.T)):
        break
print("T =", t)
np.savez_compressed("hero_trace.npz",
                    A0=A0, A_final=A, last_change=last_change,
                    change_count=change_count, T=t,
                    masks=np.array([m for m in masks], dtype=bool),
                    perm_kinds=np.array([k for k, _ in perms]),
                    perm_arrays=np.array([p for _, p in perms]))
print("saved")
