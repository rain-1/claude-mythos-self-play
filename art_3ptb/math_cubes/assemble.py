"""Assemble reps.json / height.json from the general (gen) and paired searches.
Every stored representation is verified by exact polynomial expansion."""
import json, glob, re

def expand(polys):
    # polys: list of (A,B); returns coefficients of sum (A x + B)^3 as [x^0..x^3]
    c = [0, 0, 0, 0]
    for A, B in polys:
        c[3] += A**3; c[2] += 3*A*A*B; c[1] += 3*A*B*B; c[0] += B**3
    return c

best = {}   # n -> (height, paired_flag, polys)
def offer(n, polys, paired):
    assert all(A != 0 for A, _ in polys)
    c = expand(polys)
    assert c == [n, 0, 0, 0], (n, polys, c)
    h = max(max(abs(A), abs(B)) for A, B in polys)
    cur = best.get(n)
    key = (h, 0 if paired else 1)
    if cur is None or key < (cur[0], 0 if cur[1] else 1):
        best[n] = (h, paired, polys)

def is_paired(polys):
    # can the 6 polys be split into 3 pairs with opposite x-coefficients?
    def rec(rem):
        if not rem: return True
        a = rem[0]
        for j in range(1, len(rem)):
            if rem[j][0] == -a[0] and rec(rem[1:j] + rem[j+1:]): return True
        return False
    return rec(list(polys))

N_ALL = 5000
for f in sorted(glob.glob('g_H*.txt'), key=lambda s: int(re.findall(r'\d+', s)[0])):
    for line in open(f):
        r = list(map(int, line.split()))
        n = r[0]; p = [(r[1+2*i], r[2+2*i]) for i in range(6)]
        offer(n, p, is_paired(p))
for f in glob.glob('p_H*.txt'):
    for line in open(f):
        r = list(map(int, line.split()))
        n = r[0]; q = r[2:]
        p = []
        for k in range(3):
            A, u, v = q[3*k:3*k+3]
            p += [(A, u), (-A, -v)]
        offer(n, p, True)
offer(0, [(1, 0), (-1, 0)] * 3, True)

# general search is exhaustive up to height 14 (|n|<=5000); paired up to the H of the p_H files
maxgen = 14
height = {n: best[n][0] for n in sorted(best)}
json.dump({str(n): height[n] for n in height}, open('height.json', 'w'), indent=0)
reps = {str(n): [list(pp) for pp in best[n][2]] for n in sorted(best) if abs(n) <= 500}
json.dump(reps, open('reps.json', 'w'), indent=0)
paired_flag = {str(n): best[n][1] for n in sorted(best)}
json.dump(paired_flag, open('paired_flag.json', 'w'))
for N in (100, 500, 1000, 2000):
    miss = [n for n in range(0, N + 1) if n not in best]
    print(N, 'missing (n>=0):', len(miss), miss[:60])
print('stored reps |n|<=500:', len(reps))
import collections
print('height histogram |n|<=500:', sorted(collections.Counter(height[n] for n in height if abs(n) <= 500).items()))
print('non-paired minimal reps |n|<=500:', [n for n in best if abs(n) <= 500 and not best[n][1]][:50])
