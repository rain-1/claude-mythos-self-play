"""MO 514690: 'good' permutations of {1..n} (n odd): every proper consecutive
block of length >=2 has sum NOT divisible by its length.

Small-n exhaustive census + construction tests + dyadic-lemma verification.
"""
import sys
from itertools import permutations

def is_good(a):
    n = len(a)
    pre = [0]*(n+1)
    for i, v in enumerate(a):
        pre[i+1] = pre[i] + v
    for L in range(2, n):          # proper blocks only
        for i in range(0, n-L+1):
            if (pre[i+L] - pre[i]) % L == 0:
                return False
    return True

def first_violation(a):
    n = len(a)
    pre = [0]*(n+1)
    for i, v in enumerate(a):
        pre[i+1] = pre[i] + v
    for L in range(2, n):
        for i in range(0, n-L+1):
            if (pre[i+L] - pre[i]) % L == 0:
                return (i, L, pre[i+L]-pre[i])
    return None

def dfs_count(n, cap=None, collect=False):
    """Exhaustive DFS with incremental window checks."""
    used = [False]*(n+1)
    a = []
    pre = [0]
    out = []
    cnt = 0
    def rec():
        nonlocal cnt
        i = len(a)
        if i == n:
            cnt += 1
            if collect:
                out.append(tuple(a))
            return cnt >= (cap or float('inf'))
        for v in range(1, n+1):
            if used[v]:
                continue
            s = pre[-1] + v
            ok = True
            # windows ending at position i+1 (1-based), length L=2..min(i+1, n-1)
            for L in range(2, min(i+1, n-1)+1):
                if (s - pre[i+1-L]) % L == 0:
                    ok = False
                    break
            if not ok:
                continue
            used[v] = True
            a.append(v)
            pre.append(s)
            stop = rec()
            a.pop()
            pre.pop()
            used[v] = False
            if stop:
                return True
        return False
    rec()
    return cnt, out

def mersenne_construction(p):
    """1, p-1, p, p-3, p-2, ..., 2, 3  (poster's construction)."""
    a = [1]
    x = p - 1
    while x >= 2:
        a += [x, x+1]
        x -= 2
    assert sorted(a) == list(range(1, p+1)), a
    return a

if __name__ == '__main__':
    print("== construction sanity ==")
    for p in [3, 7, 15, 31, 63, 127, 255, 511, 1023]:
        a = mersenne_construction(p)
        fv = first_violation(a)
        print(f"p={p:5d} construction good: {fv is None}",
              f"first violation (i,L,sum)={fv}" if fv else "")

    print("\n== exhaustive census small odd n ==")
    for n in range(3, 16, 2):
        cnt, _ = dfs_count(n)
        print(f"n={n:3d}  #good = {cnt}")
        sys.stdout.flush()
