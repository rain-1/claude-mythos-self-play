"""Brute-force all symmetric primitive Dyck paths of area 1..40 -> paths.json."""
import json
NMAX = 40
out = {str(n): [] for n in range(1, NMAX + 1)}
def dfs(half, s2):  # half = P_0..P_j, s2 = 2*sum(P_0..P_{j-1})
    m = half[-1]
    if m >= 1 and s2 + m <= NMAX:     # may stop here: h = j
        full = half + half[-2::-1]
        assert sum(full) == s2 + m
        out[str(s2 + m)].append(full)
    for nm in (m - 1, m + 1):
        if nm >= 1 and s2 + 2 * m + nm <= NMAX:
            dfs(half + [nm], s2 + 2 * m)
dfs([0, 1], 0)
for n in out:
    out[n].sort(key=lambda p: (len(p), p))
d = json.load(open("d_upto_6000.json"))
assert all(len(out[str(n)]) == d[n] for n in range(1, NMAX + 1))
for p in sum(out.values(), []):
    L = len(p) - 1
    assert p[0] == p[-1] == 0 and all(x >= 1 for x in p[1:-1]) and p == p[::-1]
    assert all(abs(p[i + 1] - p[i]) == 1 for i in range(L))
json.dump(out, open("paths.json", "w"), separators=(",", ":"))
print("total paths:", sum(len(v) for v in out.values()), [len(out[str(n)]) for n in range(1, NMAX + 1)])
