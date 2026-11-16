"""Independent check of the window lemma: list ALL unique-cycle deletion sets (hc search) and
confirm every L0 consecutive columns hold a deleted vertex."""
import subprocess, sys
L0 = {3: 3, 5: 4, 6: 5, 7: 5, 9: 5}
for m, n, d in [(3, 11, 3), (3, 12, 4), (3, 13, 5), (5, 8, 4), (5, 9, 5), (5, 10, 4), (6, 9, 4), (7, 8, 4), (7, 10, 4), (9, 6, 4)]:
    if n <= L0[m]: continue
    out = subprocess.run(['./hc', 'search', str(m), str(n), str(d)], capture_output=True, text=True).stdout.strip().splitlines()
    sols = [[tuple(map(int, t.split(','))) for t in l.split()] for l in out[:-1]]
    bad = 0
    for s in sols:
        cols = {c for r, c in s}
        if any(not (cols & set(range(a, a + L0[m]))) for a in range(0, n - L0[m] + 1)): bad += 1
    print(f'{m}x{n}, {d} deleted: {len(sols)} unique-cycle sets, {bad} violate the lemma', flush=True)
