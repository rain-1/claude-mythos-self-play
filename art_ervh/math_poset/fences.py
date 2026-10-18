"""Theory/optimisation over disjoint unions.

f(P) = e(P)/|Aut P|.  Write h(C) = e(C)/(|C|! |Aut C|) for a connected poset C.
For P = disjoint union with m_C copies of each iso class C:
    e(P) = n! prod_C (e(C)/|C|!)^{m_C},   |Aut P| = prod_C |Aut C|^{m_C} m_C!
so   f(P) = n! * prod_C h(C)^{m_C} / m_C!.
Maximising over unions drawn from a list of connected classes is a knapsack
(DP over n, items = iso classes, multiplicity m costs h^m/m!).

1. Fence unions: classes = point, Z2 (chain), Z_a (a even >=4, self-dual,
   Aut=1), Z_a and Z_a* (a odd >=3, two non-iso duals, Aut=Z/2 each).
2. General components: top-60 connected classes of each size from the full
   enumeration (raw/n*.txt, sizes <= 12) and height-2 trees (raw/trees_k.json).
Outputs fence_unions.json, unions_best.json and prints tables."""
import json, os, re
from fractions import Fraction
from math import factorial, pi

NMAX = 40

def euler_zigzag(N):
    # E_0..E_N via Entringer / boustrophedon
    E = [1]
    row = [1]
    for n in range(1, N + 1):
        new = [0]
        for k in range(n):
            new.append(new[-1] + row[n - 1 - k])
        row = new
        E.append(row[-1])
    return E

E = euler_zigzag(NMAX + 1)   # E[a] = e(fence with a elements)
assert E[:9] == [1, 1, 1, 2, 5, 16, 61, 272, 1385]

def knapsack(items, nmax):
    """items: list of (size, h(Fraction), name). Returns best[n] = (value, multiset)."""
    best = [None] * (nmax + 1)
    best[0] = (Fraction(1), ())
    for (k, h, name) in items:
        new = list(best)
        for n in range(nmax + 1):
            if best[n] is None: continue
            val, ms = best[n]
            p = Fraction(1)
            for m in range(1, (nmax - n) // k + 1):
                p = p * h / m
                t = n + m * k
                cand = val * p
                if new[t] is None or cand > new[t][0]:
                    new[t] = (cand, ms + ((name, m),))
        best = new
    return best

def fence_items(nmax):
    it = [(1, Fraction(1), 'pt'), (2, Fraction(1, 2), 'Z2')]
    for a in range(3, nmax + 1):
        if a % 2 == 0:
            it.append((a, Fraction(E[a], factorial(a)), 'Z%d' % a))
        else:
            h = Fraction(E[a], 2 * factorial(a))
            it.append((a, h, 'Z%d' % a)); it.append((a, h, 'Z%d*' % a))
    return it

def fmt(ms):
    return ' + '.join(('%s' % nm) if m == 1 else ('%d×%s' % (m, nm)) for nm, m in ms)

def load_conn():
    """connected classes from full enumeration: size -> list of (e, aut, covers)"""
    out = {}
    for n in range(1, 13):
        fn = 'raw/n%d.txt' % n
        if not os.path.exists(fn): continue
        L = []
        for line in open(fn):
            if line.startswith('CONN'):
                a, b = line.split(':')
                t = a.split()
                cov = [list(map(int, x.split(','))) for x in b.split()]
                L.append((int(t[2]), int(t[4]), cov))
        if L and any(l.startswith('>Z') for l in open(fn)):
            out[n] = L
    return out

def load_trees():
    out = {}
    for k in range(1, 30):
        fn = 'raw/trees_%d.json' % k
        if os.path.exists(fn): out[k] = json.load(open(fn))
    return out

def main():
    fi = fence_items(NMAX)
    fb = knapsack(fi, NMAX)
    res = {}
    print('n  | best fence union f | components | log(f/n!)/n')
    for n in range(1, NMAX + 1):
        v, ms = fb[n]
        f = v * factorial(n)
        res[n] = dict(f=str(f), f_float=float(f), comps=fmt(ms))
        print(n, f, fmt(ms))
    json.dump(res, open('fence_unions.json', 'w'), indent=1)

    # general components
    conn = load_conn(); trees = load_trees()
    items = []
    names = {}
    for k, L in conn.items():
        for i, (e, a, cov) in enumerate(L):
            nm = 'C%d.%d' % (k, i)
            items.append((k, Fraction(e, a * factorial(k)), nm)); names[nm] = dict(size=k, e=e, aut=a, covers=cov, src='enum')
    otrees = {}
    for k in range(1, 30):
        fn = 'raw/otrees_%d.json' % k
        if os.path.exists(fn) and k not in conn: otrees[k] = json.load(open(fn))
    for k, L in otrees.items():
        for i, (e, a, cov) in enumerate(L):
            nm = 'OT%d.%d' % (k, i)
            items.append((k, Fraction(e, a * factorial(k)), nm)); names[nm] = dict(size=k, e=e, aut=a, covers=cov, src='oriented-tree')
    for k, L in trees.items():
        if k in conn or k in otrees: continue   # enumeration already exact & complete for top-60
        for i, (e, a, nt, cov) in enumerate(L):
            for d in range(nt):
                nm = 'T%d.%d%s' % (k, i, '*' if d else '')
                items.append((k, Fraction(e, a * factorial(k)), nm))
                names[nm] = dict(size=k, e=e, aut=a, covers=cov if d == 0 else [[y, x] for x, y in cov], src='tree')
    # fences larger than what is covered
    kmax_cov = max(list(conn) + list(trees)) if (conn or trees) else 0
    for (k, h, nm) in fi:
        if k > kmax_cov: items.append((k, h, nm)); names[nm] = dict(size=k, src='fence')
    gb = knapsack(items, NMAX)
    out = {}
    print('\nn | best union over (all conn. <=%s) ∪ (all tree-Hasse conn. %s) ∪ (height-2 trees <=%s) ∪ fences | / best fence union'
          % (max(conn) if conn else 0, sorted(otrees), max(trees) if trees else 0))
    for n in range(1, NMAX + 1):
        v, ms = gb[n]
        f = v * factorial(n)
        ff = Fraction(res[n]['f'])
        out[n] = dict(f=str(f), f_float=float(f), comps=fmt(ms), ratio_to_fence=float(f / ff),
                      components={nm: names[nm] for nm, m in ms})
        print(n, f, '%.4f' % float(f / ff), fmt(ms))
    json.dump(out, open('unions_best.json', 'w'), indent=1)

    # asymptotics of h for fences and for best connected per size
    print('\nk | E_k/k! | 2(2/pi)^(k+1) | best connected h(C)·k!·aut... ')
    for k in range(1, 17):
        best = None
        if k in conn: best = max(Fraction(e, a) for e, a, _ in conn[k])
        elif k in otrees: best = max(Fraction(e, a) for e, a, _ in otrees[k])
        elif k in trees: best = max(Fraction(e, a) for e, a, _, _ in trees[k])
        fz = Fraction(E[k], 1 if (k % 2 == 0 or k == 1) else 2)
        print(k, '%.5f' % (E[k] / factorial(k)), '%.5f' % (2 * (2 / pi) ** (k + 1)),
              'fence e/aut=%s' % fz, 'best conn e/aut=%s' % best,
              'ratio %.4f' % (float(best / fz) if best else float('nan')))

if __name__ == '__main__':
    main()
