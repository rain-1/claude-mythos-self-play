"""Zagier's one-sentence proof of Fermat's two-squares theorem, verified.
S = {(x,y,z) in Z+^3 : x^2 + 4yz = p}.  Involution zeta (the 'windmill' map) has
exactly one fixed point => |S| odd => the swap (x,y,z)->(x,z,y) has a fixed point
=> p = x^2 + (2y)^2."""
import sys

def solutions(p):
    S = []
    x = 1
    while x*x < p:
        r = p - x*x
        if r % 4 == 0:
            m = r//4
            y = 1
            while y*y <= m:
                if m % y == 0:
                    S.append((x, y, m//y))
                    if y != m//y: S.append((x, m//y, y))
                y += 1
        x += 2
    return S

def zeta(t):
    x, y, z = t
    if x < y - z:   return (x + 2*z, z, y - x - z)
    elif x < 2*y:   return (2*y - x, y, x - y + z)
    else:           return (x - 2*y, x - y + z, y)

def swap(t): return (t[0], t[2], t[1])

def verify(p):
    S = solutions(p)
    Sset = set(S)
    assert len(Sset) == len(S)
    # zeta is an involution on S
    fz = []
    for t in S:
        u = zeta(t)
        assert u in Sset, (t, u)
        assert zeta(u) == t, (t, u)
        if u == t: fz.append(t)
    assert len(fz) == 1 and fz[0] == (1, 1, (p-1)//4)
    fs = [t for t in S if swap(t) == t]
    assert len(S) % 2 == 1
    assert len(fs) >= 1
    reps = sorted(set((t[0], 2*t[1]) for t in fs))
    for a, b in reps: assert a*a + b*b == p
    return S, fz[0], fs, reps

# orbit structure of swap . zeta : paths and cycles; the path joining the two fixed points
def orbits(S, p):
    Sset = set(S)
    # build the "grand involution graph": edges from zeta-matching and swap-matching
    # follow the alternating path from the zeta-fixed point
    start = (1, 1, (p-1)//4)
    path = [start]; cur = start; use_swap = True
    while True:
        nxt = swap(cur) if use_swap else zeta(cur)
        if nxt == cur: break
        path.append(nxt); cur = nxt; use_swap = not use_swap
    return path

for p in [13, 29, 101, 1009, 2029, 4001, 8009, 20021+8, 39916801%10000]:
    # ensure p prime and 1 mod 4
    def isp(n):
        if n < 2: return False
        i = 2
        while i*i <= n:
            if n % i == 0: return False
            i += 1
        return True
    if not (isp(p) and p % 4 == 1): continue
    S, zfix, sfix, reps = verify(p)
    path = orbits(S, p)
    print(f"p={p:6d}: |S|={len(S):5d} (odd), zeta-fixed={zfix}, swap-fixed={len(sfix)}, p={reps[0][0]}^2+{reps[0][1]}^2, alt-path len={len(path)}")
