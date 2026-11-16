"""Rigid windows for unique Hamiltonian cycles in grid graphs (MO 516913).

A WINDOW is m rows x L full columns with no deleted vertex.  A Hamiltonian cycle of the
big graph meets it in a PATH SYSTEM: vertex-disjoint paths covering all m*L vertices,
every path end leaving through the left or the right side.  Its INTERFACE is
(left exits, right exits, which exit is joined to which).

window(m, L) returns {interface: number of path systems}.
An interface is a tuple of 2m labels: left side rows 0..m-1, then right side rows 0..m-1;
0 = no exit, equal labels = the two ends of one path.
"""
import sys, itertools, json
from collections import defaultdict

def canon(t):
    mp = {0: 0}; out = []
    for x in t:
        if x not in mp: mp[x] = len(mp)
        out.append(mp[x])
    return tuple(out)

def window(m, L):
    # state = left labels (m) + h plugs (m) + v plug (1)
    cur = defaultdict(int)
    for S in range(1 << m):
        lab = [0] * m; k = 0
        for r in range(m):
            if S >> r & 1: k += 1; lab[r] = k
        cur[tuple(lab) + tuple(lab) + (0,)] += 1
    for c in range(L):
        for r in range(m):
            nxt = defaultdict(int)
            last = (r == m - 1)
            for st, n in cur.items():
                a = st[m + r]; b = st[2 * m]
                s = list(st)
                if a == 0 and b == 0:
                    if not last:
                        x = max(st) + 1
                        s[m + r] = x; s[2 * m] = x
                        nxt[canon(s)] += n
                elif a == 0 or b == 0:
                    x = a or b
                    s[m + r] = x; s[2 * m] = 0
                    nxt[canon(s)] += n
                    if not last:
                        s[m + r] = 0; s[2 * m] = x
                        nxt[canon(s)] += n
                elif a != b:
                    s[m + r] = 0; s[2 * m] = 0
                    s = [a if x == b else x for x in s]
                    nxt[canon(s)] += n
            cur = nxt
    return {st[:2 * m]: n for st, n in cur.items()}

def nc_matchings(pts):
    """non-crossing perfect matchings of an ordered list of points"""
    if not pts: yield (); return
    a = pts[0]
    for j in range(1, len(pts), 2):
        for A in nc_matchings(pts[1:j]):
            for B in nc_matchings(pts[j + 1:]):
                yield ((a, pts[j]),) + A + B

def single_cycle(pi_pairs, tau_pairs, npts):
    adj = defaultdict(list)
    for a, b in pi_pairs: adj[a].append(b); adj[b].append(a)
    for a, b in tau_pairs: adj[a].append(b); adj[b].append(a)
    start = pi_pairs[0][0]; prev = None; x = start; steps = 0
    while True:
        nb = adj[x]
        y = nb[0] if nb[0] != prev or (nb[0] == nb[1]) and steps % 1 == 0 and prev is None else nb[1]
        if prev is not None and nb[0] == prev and nb[1] == prev:
            y = prev
        prev, x = x, y; steps += 1
        if x == start: break
        if steps > 4 * npts: return False
    return steps == npts

def pairs_of(iface):
    d = defaultdict(list)
    for i, x in enumerate(iface):
        if x: d[x].append(i)
    return [tuple(v) for v in d.values()]

def analyse(m, L, verbose=False):
    W = window(m, L)
    rigid = [s for s, n in W.items() if n == 1]
    by_exits = defaultdict(list)
    for s, n in W.items():
        by_exits[tuple(1 if x else 0 for x in s)].append((s, n))
    poss = []
    for s in rigid:
        ex = tuple(1 if x else 0 for x in s)
        Lp = [i for i in range(m) if ex[i]]; Rp = [m + i for i in range(m) if ex[m + i]]
        if len(Lp) % 2 or len(Rp) % 2: continue
        pp = pairs_of(s); npts = len(Lp) + len(Rp)
        if npts == 0: continue
        others = [(pairs_of(t), n) for t, n in by_exits[ex]]
        for tl in nc_matchings(Lp):
            for tr in nc_matchings(Rp):
                tau = tl + tr
                if not single_cycle(pp, tau, npts): continue
                N = sum(n for q, n in others if single_cycle(q, tau, npts))
                if N == 1:
                    poss.append((s, tau))
    return W, rigid, poss

if __name__ == '__main__':
    m = int(sys.argv[1]); Lmax = int(sys.argv[2])
    for L in range(1, Lmax + 1):
        W, rigid, poss = analyse(m, L)
        print(f'm={m} L={L}: interfaces {len(W)}, path systems {sum(W.values())}, '
              f'rigid {len(rigid)}, possibly-unique (interface,closure) {len(poss)}, '
              f'distinct interfaces {len(set(p[0] for p in poss))}', flush=True)
        if poss and len(sys.argv) > 3:
            for s in sorted(set(p[0] for p in poss))[:12]: print('   ', s[:m], s[m:])
