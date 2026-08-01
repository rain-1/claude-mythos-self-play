"""Final analysis on the 75k census:
1. verify golden-window laws on new blocks k=22,23
2. signature-automaton saturation diagnosis
"""
import pickle
from detlib import zeck

d = pickle.load(open("dets75024.pkl", "rb"))
FIB = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597,
       2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025]

print("nonzero total:", sum(1 for v in d.values() if v != 0))
for k in (22, 23):
    flo, fhi = FIB[k - 1], FIB[k]
    nz = [n for n in range(flo, min(fhi, 75025)) if d.get(n, 0) != 0]
    pred_first = FIB[k - 1] + FIB[k - 6]
    # last = 1000(10)*: F_k + F_{k-4} + F_{k-6} + ... down to F_2 or F_3
    last = FIB[k - 1] + FIB[k - 5]
    idx = k - 7
    while idx >= 0:
        last += FIB[idx]
        idx -= 2
    print(f"block k={k}: first nz {min(nz)} (predicted {pred_first}) "
          f"{'OK' if min(nz)==pred_first else 'MISMATCH'}; "
          f"last nz {max(nz)} (predicted {last}) "
          f"{'OK' if max(nz)==last else 'MISMATCH'}; zeck(last)={zeck(max(nz))}")

# u_k check in census: per=1 positions have det != 0; also check det value at
u = [1, 2, 3, 5, 9, 15, 24, 39, 64, 104, 168, 272, 441, 714, 1155, 1869,
     3025, 4895, 7920, 12815, 20736, 33552, 54288]
print("det at u_k:", [(n, d.get(n)) for n in u if n <= 75024])

# saturation: states discovered vs max prefix length (signature depth 6)
from functools import lru_cache

F2 = [0, 1, 2]
while len(F2) < 40:
    F2.append(F2[-1] + F2[-2])


def value(word):
    m = len(word)
    return sum(F2[m - i] for i, dig in enumerate(word) if dig)


@lru_cache(maxsize=None)
def suffixes(last, maxlen):
    out = [()]
    frontier = [((), last)]
    for _ in range(maxlen):
        nf = []
        for (w, prev) in frontier:
            for a in (0, 1):
                if prev == 1 and a == 1:
                    continue
                w2 = w + (a,)
                out.append(w2)
                nf.append((w2, a))
        frontier = nf
    return out


KS = 6
MAXLEN = 23   # words up to F_24-1
sigs_by_len = {}
prefixes = []
frontier = [((1,), 1)]
while frontier:
    nf = []
    for (w, prev) in frontier:
        prefixes.append(w)
        if len(w) < MAXLEN - KS:
            for a in (0, 1):
                if prev == 1 and a == 1:
                    continue
                nf.append((w + (a,), a))
    frontier = nf

seen = set()
growth = {}
for p in sorted(prefixes, key=len):
    last = p[-1]
    sig = (last, tuple(d[value(p + s)] for s in suffixes(last, KS)))
    if sig not in seen:
        seen.add(sig)
    growth[len(p)] = len(seen)
print("state discovery by prefix length (k*=6):")
for L in sorted(growth):
    print(" len<=", L, "states:", growth[L])
