"""Independent certificate for a claimed gap-g length-5 fence at start n:
the 5 posts n, n+g, ..., n+4g must be in S (all bad-prime valuations even),
and all 4g-4 window values must be OUT of S — via sympy.factorint, no sieve.
Usage: python3 certify_fence.py <n> <g>"""
import sys
from sympy import factorint

def in_S(m):
    if m <= 0: return False
    f = factorint(m)
    return all(v % 2 == 0 for p, v in f.items() if p % 8 in (3, 5)), f

def fmt(f):
    return "·".join(f"{p}^{v}" if v > 1 else f"{p}" for p, v in sorted(f.items()))

n, g = int(sys.argv[1]), int(sys.argv[2])
ok = True
for k in range(5):
    m = n + k*g
    member, f = in_S(m)
    print(f"POST  {m} = {fmt(f)}   {'IN S' if member else 'NOT IN S  <-- FAIL'}")
    ok &= member
empty = True
for j in range(1, 4*g):
    if j % g == 0: continue
    m = n + j
    member, f = in_S(m)
    if member:
        print(f"WINDOW {m} (+{j}) = {fmt(f)}  IN S  <-- FAIL (window not empty)")
        empty = False
print("CERTIFIED FENCE" if ok and empty else "NOT A FENCE", f"(start {n}, gap {g})")
