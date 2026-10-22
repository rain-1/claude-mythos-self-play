#!/usr/bin/env python3
"""Independent verifier for incremental cyclic Latin squares.
L[i][j] = (i + q[j]) mod n.  Property (0-based values): for every c = 1..n the cells with
L <= c-1 hold exactly c coins in each row and column and at most c coins on every ordinary
(non-wrapping) diagonal i+j=const and i-j=const.
Usage: python3 verify.py [squares.json]      -> checks every q in the file
       python3 verify.py --brute N           -> brute-force count of valid q over all N! perms
"""
import json, sys, itertools
from collections import Counter

def is_incremental_cyclic(q):
    n = len(q)
    if sorted(q) != list(range(n)):
        return False, "q is not a permutation"
    L = [[(i + q[j]) % n for j in range(n)] for i in range(n)]
    for c in range(1, n + 1):
        coins = [(i, j) for i in range(n) for j in range(n) if L[i][j] < c]
        rows = Counter(i for i, _ in coins); cols = Counter(j for _, j in coins)
        if any(rows[i] != c for i in range(n)) or any(cols[j] != c for j in range(n)):
            return False, f"row/col count wrong at c={c}"
        s = Counter(i + j for i, j in coins); d = Counter(i - j for i, j in coins)
        if max(s.values()) > c or max(d.values()) > c:
            return False, f"diagonal overfull at c={c}"
    return True, "ok"

def is_linear(q):
    n = len(q)
    if n < 2: return True
    a = (q[1] - q[0]) % n
    return all(q[j] == (a * j + q[0]) % n for j in range(n))

def is_toroidal_layer0(q):
    n = len(q); r = [(-x) % n for x in q]
    return len({(r[j] + j) % n for j in range(n)}) == n and len({(r[j] - j) % n for j in range(n)}) == n

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--brute":
        N = int(sys.argv[2])
        print(N, sum(is_incremental_cyclic(list(p))[0] for p in itertools.permutations(range(N))))
        sys.exit()
    data = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "squares.json"))
    bad = 0
    for n, qs in sorted(data.items(), key=lambda t: int(t[0])):
        for q in qs:
            ok, msg = is_incremental_cyclic(q)
            assert len(q) == int(n)
            kind = "linear" if is_linear(q) else ("toroidal-nonlinear" if is_toroidal_layer0(q) else "non-toroidal")
            print(f"n={n:>2} {kind:<19} {msg}  q={q}")
            bad += not ok
    print("ALL OK" if bad == 0 else f"{bad} FAILURES")
