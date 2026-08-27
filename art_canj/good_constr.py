"""Test the Mersenne zigzag construction 1, p-1, p, p-3, p-2, ..., 2, 3
for all Mersenne numbers p=2^m-1, m=2..13, and record ALL violation
window lengths (not just the first). Hypothesis:
  - construction is good  <=>  p = 2^m-1 with p prime
  - for composite p, the SET of violating lengths relates to prime factors of p.
Also: which lengths kill for NON-Mersenne odd p (dyadic death)?
"""
import sympy

def constr(p):
    a = [1]
    x = p - 1
    while x >= 2:
        a += [x, x + 1]
        x -= 2
    return a

def violating_lengths(a):
    n = len(a)
    pre = [0]
    for v in a:
        pre.append(pre[-1] + v)
    bad = {}
    for L in range(2, n):
        for i in range(0, n - L + 1):
            if (pre[i + L] - pre[i]) % L == 0:
                bad.setdefault(L, []).append(i)
    return bad

for m in range(2, 14):
    p = 2**m - 1
    fac = sympy.factorint(p)
    a = constr(p)
    bad = violating_lengths(a)
    tag = 'PRIME' if sympy.isprime(p) else 'composite ' + str(dict(fac))
    if not bad:
        print(f"m={m:2d} p={p:5d} {tag:28s} GOOD")
    else:
        Ls = sorted(bad)
        summ = ', '.join(f"L={L} (x{len(bad[L])}, first i={bad[L][0]})" for L in Ls[:6])
        print(f"m={m:2d} p={p:5d} {tag:28s} BAD at {summ}" + (' ...' if len(Ls) > 6 else ''))

print()
print("non-Mersenne odd p, first violations (dyadic death expected):")
for p in [5, 9, 11, 13, 17, 19, 21, 23, 25, 29, 33, 45, 61, 95]:
    a = constr(p)
    bad = violating_lengths(a)
    if not bad:
        print(f"p={p} GOOD (!!)")
    else:
        L0 = min(bad)
        print(f"p={p:3d} first bad L={L0} (i={bad[L0][0]})  all bad L's={sorted(bad)[:8]}")
