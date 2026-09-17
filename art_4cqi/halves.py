"""halves.py — TWO HALVES, ONE SHAPE (polyomino version of MO 515286, Yakov Baruch's comment).
Census: every free convex polyomino (row- and column-convex) of area A; for each, does it split into two
congruent connected halves?  Exhaustive over all A/2-subsets; congruence under the 8 lattice isometries + translation.
Records the isometry that carries one half to the other and whether the halves are convex.
    python3 halves.py A  -> cache/halves_A.json
"""
import sys, json, itertools, time
from collections import deque

def convex_polyominoes(A):
    """all convex polyominoes of area A as frozensets of cells, up to free symmetry (canonical form)"""
    seen = set(); out = []
    for h in range(1, A + 1):
        for w in range(1, A + 1):
            if w + h - 1 > A: continue
            # rows: intervals [l, r]; l valley-shaped, r mountain-shaped; consecutive overlap; total area A; columns 0..w-1 covered
            def rec(i, rows, area, lmin_reached, rmax_reached):
                if area > A: return
                if i == h:
                    if area == A and min(l for l, r in rows) == 0 and max(r for l, r in rows) == w - 1:
                        cells = frozenset((y, x) for y, (l, r) in enumerate(rows) for x in range(l, r + 1))
                        c = canon(cells)
                        if c not in seen:
                            seen.add(c); out.append(c)
                    return
                remaining = h - i
                for l in range(w):
                    for r in range(l, w):
                        if rows:
                            pl, pr = rows[-1]
                            if r < pl or l > pr: continue           # connected
                            if l < pl and lmin_reached: continue    # l may only decrease before its minimum
                            if r > pr and rmax_reached: continue
                            lm = lmin_reached or l > pl
                            rm = rmax_reached or r < pr
                        else:
                            lm = rm = False
                        na = area + r - l + 1
                        if na + (remaining - 1) > A: continue
                        rec(i + 1, rows + [(l, r)], na, lm, rm)
            rec(0, [], 0, False, False)
    return out

SYM = [lambda y, x: (y, x), lambda y, x: (x, -y), lambda y, x: (-y, -x), lambda y, x: (-x, y),
       lambda y, x: (y, -x), lambda y, x: (-y, x), lambda y, x: (x, y), lambda y, x: (-x, -y)]
SYMNAME = ['identity', 'rotation 90', 'rotation 180', 'rotation 270', 'reflection |', 'reflection —', 'reflection /', 'reflection \\']

def normalize(cells):
    my = min(y for y, x in cells); mx = min(x for y, x in cells)
    return frozenset((y - my, x - mx) for y, x in cells)

def canon(cells):
    return min((tuple(sorted(normalize(frozenset(f(y, x) for y, x in cells)))) for f in SYM))

def connected(cells):
    cells = set(cells); start = next(iter(cells)); seen = {start}; dq = deque([start])
    while dq:
        y, x = dq.popleft()
        for n in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if n in cells and n not in seen:
                seen.add(n); dq.append(n)
    return len(seen) == len(cells)

def is_convex(cells):
    ys = {}; xs = {}
    for y, x in cells:
        ys.setdefault(y, []).append(x); xs.setdefault(x, []).append(y)
    return all(max(v) - min(v) + 1 == len(v) for v in ys.values()) and all(max(v) - min(v) + 1 == len(v) for v in xs.values())

def split(cells):
    cells = sorted(cells); A = len(cells); k = A // 2
    first = cells[0]
    others = cells[1:]
    found = []
    for comb in itertools.combinations(others, k - 1):
        S = frozenset((first,) + comb)
        T = frozenset(cells) - S
        if not connected(S) or not connected(T): continue
        nT = normalize(T)
        for j, f in enumerate(SYM):
            if normalize(frozenset(f(y, x) for y, x in S)) == nT:
                found.append((tuple(sorted(S)), j, is_convex(S)))
                break
    return found

if __name__ == '__main__':
    A = int(sys.argv[1]); t0 = time.time()
    polys = convex_polyominoes(A)
    print('convex polyominoes of area', A, ':', len(polys), f'{time.time()-t0:.0f}s', flush=True)
    res = []
    for c in polys:
        f = split(c)
        # prefer a convex-halves split, then by isometry
        f.sort(key=lambda t: (not t[2], t[1]))
        res.append(dict(cells=[list(p) for p in c], n_splits=len(f),
                        best=(dict(half=[list(p) for p in f[0][0]], sym=SYMNAME[f[0][1]], convex_halves=f[0][2]) if f else None),
                        syms=sorted({SYMNAME[t[1]] for t in f}), any_convex=any(t[2] for t in f)))
    n_cut = sum(1 for r in res if r['best'])
    n_conv = sum(1 for r in res if r['any_convex'])
    print('cuttable', n_cut, 'with convex halves', n_conv, 'uncuttable', len(res) - n_cut, f'{time.time()-t0:.0f}s')
    json.dump(dict(A=A, n=len(res), cuttable=n_cut, convex_halves=n_conv, polys=res), open(f'cache/halves_{A}.json', 'w'))
