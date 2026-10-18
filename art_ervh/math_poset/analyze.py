"""Post-process raw/n*.txt (output of genposet_f) -> optimal.json + table.
Independently recomputes e(P) (DP over down-sets) and #Aut(P) (brute-force
search over permutations with pruning) in Python, and describes each poset by
its connected components (recognising fences)."""
import json, sys, itertools, re
from fractions import Fraction
from functools import lru_cache
from math import factorial

def parse(fn):
    ranks = []
    for line in open(fn):
        if line.startswith('RANK'):
            t = line.split()
            ranks.append(dict(e=int(t[3]), aut=int(t[5]), count=int(t[7]), posets=[]))
        elif line.startswith('POSET'):
            covers = [tuple(map(int, x.split(','))) for x in line.split()[1:]]
            ranks[-1]['posets'].append(covers)
    return ranks

def closure(n, covers):
    up = [0]*n
    for a, b in sorted(covers, key=lambda c: -c[0]):
        pass
    adj = [[] for _ in range(n)]
    for a, b in covers: adj[a].append(b)
    for i in reversed(range(n)):          # topological labelling: a<b for covers
        u = 0
        for j in adj[i]: u |= (1 << j) | up[j]
        up[i] = u
    dn = [0]*n
    for i in range(n):
        for j in range(n):
            if up[i] >> j & 1: dn[j] |= 1 << i
    return up, dn

def linext(n, covers):
    up, dn = closure(n, covers)
    cur = {0: 1}
    for _ in range(n):
        nxt = {}
        for m, v in cur.items():
            for j in range(n):
                if not m >> j & 1 and dn[j] & ~m == 0:
                    nxt[m | 1 << j] = nxt.get(m | 1 << j, 0) + v
        cur = nxt
    return cur[(1 << n) - 1]

def autsize(n, covers):
    up, dn = closure(n, covers)
    inv = [(bin(up[i]).count('1'), bin(dn[i]).count('1')) for i in range(n)]
    cnt = 0
    img = [-1]*n; used = [False]*n
    def bt(i):
        nonlocal cnt
        if i == n: cnt += 1; return
        for v in range(n):
            if used[v] or inv[v] != inv[i]: continue
            if all(((up[k] >> i) & 1) == ((up[img[k]] >> v) & 1) and
                   ((up[i] >> k) & 1) == ((up[v] >> img[k]) & 1) for k in range(i)):
                used[v] = True; img[i] = v; bt(i+1); used[v] = False
    bt(0)
    return cnt

def components(n, covers):
    par = list(range(n))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for a, b in covers: par[f(a)] = f(b)
    comps = {}
    for i in range(n): comps.setdefault(f(i), []).append(i)
    return list(comps.values())

def describe_comp(comp, covers):
    """Return a name for a connected component."""
    s = set(comp)
    cv = [(a, b) for a, b in covers if a in s]
    k = len(comp)
    if k == 1: return 'pt', 'point'
    deg = {v: 0 for v in comp}
    for a, b in cv: deg[a] += 1; deg[b] += 1
    if len(cv) == k - 1 and max(deg.values()) <= 2:
        # path in the Hasse diagram whose edges alternate direction = fence
        ends = [v for v in comp if deg[v] == 1]
        adj = {v: [] for v in comp}
        for a, b in cv: adj[a].append((b, 'up')); adj[b].append((a, 'dn'))
        path = [ends[0]]; dirs = []; prev = None
        while len(path) < k:
            for w, d in adj[path[-1]]:
                if w != prev:
                    prev = path[-1]; path.append(w); dirs.append(d); break
        if all(dirs[i] != dirs[i+1] for i in range(len(dirs)-1)):
            if k == 2: return 'Z2', 'chain2'
            if k % 2 == 0: return 'Z%d' % k, 'fence%d' % k
            # odd: count minimal elements
            mins = sum(1 for v in comp if all(b != v for a, b in cv))
            if mins > k // 2: return 'Z%d' % k, 'fence%d(W: %d minima)' % (k, mins)
            return 'Z%d*' % k, 'fence%d(M: %d maxima, dual)' % (k, k - mins)
        if all(d == 'up' for d in dirs) or all(d == 'dn' for d in dirs):
            return 'C%d' % k, 'chain%d' % k
    rel = ' '.join('%d<%d' % c for c in cv)
    if len(cv) == k - 1:
        t = describe_tree(comp, cv)
        if t: return 'T%d' % k, '%s[%s]' % (t, rel)
    return 'X%d' % k, 'other%d[%s]' % (k, rel)

def describe_tree(comp, cv):
    """Hasse diagram is a tree: try 'zigzag spine + pendant leaves'."""
    import itertools
    adj = {v: set() for v in comp}
    for a, b in cv: adj[a].add(b); adj[b].add(a)
    below = {(a, b) for a, b in cv}
    def bfs(s):
        par = {s: None}; q = [s]
        for x in q:
            for y in adj[x]:
                if y not in par: par[y] = x; q.append(y)
        return q[-1], par
    far, _ = bfs(comp[0]); far2, par = bfs(far)
    path = [far2]
    while par[path[-1]] is not None: path.append(par[path[-1]])
    dirs = ['u' if (path[i], path[i+1]) in below else 'd' for i in range(len(path)-1)]
    zig = all(dirs[i] != dirs[i+1] for i in range(len(dirs)-1))
    rest = [v for v in comp if v not in path]
    if zig and all(len(adj[v]) == 1 for v in rest):
        leaves = []
        for v in rest:
            (w,) = adj[v]; i = path.index(w)
            kind = 'min' if (v, w) in below else 'max'
            leaves.append('%d(%s %s)' % (i + 1, 'pendant', kind))
        return 'zigzag%d+leaves@%s' % (len(path), ','.join(sorted(leaves, key=lambda x: int(x.split('(')[0]))))
    h = 'height2' if all(not any((b, c) in below for c in comp) or not any((x, a) in below for x in comp) for a, b in cv) else 'height>2'
    return 'tree-%s' % h

def describe(n, covers):
    parts = [describe_comp(c, covers) for c in components(n, covers)]
    parts.sort(key=lambda p: (-int(re.sub(r'\D', '', p[0]) or 1), p[0]))
    is_fu = all(p[0] == 'pt' or p[0].startswith('Z') for p in parts)
    return ' ⊔ '.join(p[1] for p in parts), is_fu

def main():
    out = {}
    rows = []
    for n in range(1, 13):
        try: ranks = parse('raw/n%d.txt' % n)
        except FileNotFoundError: continue
        if not ranks or not ranks[0]['posets']: continue
        res = []
        for rk, r in enumerate(ranks):
            plist = []
            for cov in r['posets']:
                e = linext(n, cov)
                a = autsize(n, cov)
                desc, fu = describe(n, cov)
                plist.append(dict(covers=[list(c) for c in cov], desc=desc, e=e, aut=a, fence_union=fu))
            fs = {Fraction(p['e'], p['aut']) for p in plist}
            assert len(fs) == 1, (n, rk, fs)
            assert fs == {Fraction(r['e'], r['aut'])}
            g = fs.pop()
            res.append(dict(g=str(g), posets=plist, count=r['count']))
        gv = Fraction(res[0]['g']); out[n] = dict(g=int(gv) if gv.denominator == 1 else res[0]['g'], proven=True, method='full enumeration of all unlabeled posets (nauty genposetg + plugin), cross-checked in Python', posets=res[0]['posets'],
                      runners_up=[dict(f=x['g'], posets=x['posets']) for x in res[1:]])
        rows.append((n, res[0]['g'], [p['desc'] for p in res[0]['posets']],
                     all(p['fence_union'] for p in res[0]['posets']),
                     [(x['g'], [p['desc'] for p in x['posets']]) for x in res[1:3]]))
    json.dump(out, open('optimal.json', 'w'), indent=1, ensure_ascii=False)
    for r in rows:
        print(r[0], r[1], r[3], r[2])
        for x in r[4]: print('     runner-up', x)

if __name__ == '__main__':
    main()
