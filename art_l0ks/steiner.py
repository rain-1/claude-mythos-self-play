#!/usr/bin/env python3
"""Steiner minimal trees for the vertices of a regular n-gon (circumradius 1).

Structure: chain DP over contiguous full components (valid for convex/cocircular
terminals; validated for n<=7 against full enumeration over ALL leaf orders).
Full component on s consecutive vertices: enumerate the Catalan(s-2) planar full
topologies (rooted at last leaf), optimize Steiner points by Weiszfeld + BFGS.
"""
import numpy as np, math, json, itertools, sys
from scipy.optimize import minimize

def shapes(lo, hi):
    """All binary merge trees over ordered leaves lo..hi (inclusive). Leaf = int."""
    if lo == hi:
        return [lo]
    out = []
    for m in range(lo, hi):
        for L in shapes(lo, m):
            for R in shapes(m+1, hi):
                out.append((L, R))
    return out

def topology_edges(shape, s):
    """Unrooted full topology: shape over leaves 0..s-2, root Steiner joins shape-top and leaf s-1.
    Returns (edges, n_steiner). Nodes: 0..s-1 terminals, s..2s-3 Steiner."""
    edges = []
    counter = [s]
    def build(node):
        if isinstance(node, int):
            return node
        a = build(node[0]); b = build(node[1])
        sp = counter[0]; counter[0] += 1
        edges.append((sp, a)); edges.append((sp, b))
        return sp
    if s == 2:
        return [(0, 1)], 0
    top = build(shape)
    # top is the root Steiner point of the merge over 0..s-2; if shape is a single
    # leaf (s==2 handled) else top is Steiner; join it to leaf s-1:
    edges.append((top, s-1))
    return edges, counter[0]-s

def opt_topology(term_xy, edges, ns, iters=400, polish=True):
    """Minimize total edge length over Steiner point positions."""
    s = len(term_xy)
    if ns == 0:
        L = 0.0
        for a, b in edges:
            L += np.linalg.norm(term_xy[a]-term_xy[b])
        return L, np.zeros((0, 2))
    # adjacency of steiner points
    nbrs = [[] for _ in range(ns)]
    for a, b in edges:
        if a >= s: nbrs[a-s].append(b)
        if b >= s: nbrs[b-s].append(a)
    # init: each steiner point at mean of terminal set beneath it (approx: mean of all)
    P = np.zeros((ns, 2))
    ctr = term_xy.mean(axis=0)
    for i in range(ns):
        ts = [x for x in nbrs[i] if x < s]
        P[i] = (term_xy[ts].mean(axis=0)*0.7 + ctr*0.3) if ts else ctr
    def pos(idx, P):
        return term_xy[idx] if idx < s else P[idx-s]
    eps = 1e-12
    for _ in range(iters):
        for i in range(ns):
            num = np.zeros(2); den = 0.0
            for q in nbrs[i]:
                v = pos(q, P) - P[i]
                d = math.hypot(v[0], v[1]) + eps
                num += pos(q, P)/d; den += 1.0/d
            if den > 0 and np.isfinite(den):
                P[i] = num/den
    P[~np.isfinite(P).all(axis=1)] = ctr + 1e-6
    def length(flat):
        Q = flat.reshape(ns, 2)
        L = 0.0
        for a, b in edges:
            pa = term_xy[a] if a < s else Q[a-s]
            pb = term_xy[b] if b < s else Q[b-s]
            L += math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2 + 1e-24)
        return L
    if polish:
        res = minimize(length, P.ravel(), method='BFGS',
                       options={'gtol': 1e-12, 'maxiter': 500})
        if res.fun < length(P.ravel()):
            P = res.x.reshape(ns, 2)
    return length(P.ravel()), P

def full_component(term_xy):
    """Best full Steiner topology over ordered terminals (convex arc)."""
    s = len(term_xy)
    if s == 2:
        return np.linalg.norm(term_xy[0]-term_xy[1]), [(0, 1)], np.zeros((0, 2))
    best = (np.inf, None, None)
    for sh in shapes(0, s-2):
        edges, ns = topology_edges(sh, s)
        L, P = opt_topology(term_xy, edges, ns)
        if L < best[0]:
            best = (L, edges, P)
    return best

def census(n, cap=8):
    """Chain DP for regular n-gon, returns dict with geometry."""
    ang = 2*np.pi*np.arange(n)/n
    V = np.stack([np.cos(ang), np.sin(ang)], axis=1)
    # FC[s] = best full component over s consecutive vertices 0..s-1 (rotation-invariant)
    FC = {}
    for s in range(2, min(cap, n)+1):
        FC[s] = full_component(V[:s])
    # DP over the cut line 0..n-1
    W = np.full(n, np.inf); W[0] = 0.0
    choice = [None]*n
    for j in range(1, n):
        for s in range(2, min(cap, j+1)+1):
            c = W[j-(s-1)] + FC[s][0]
            if c < W[j]:
                W[j] = c; choice[j] = s
    # reconstruct components (as (start_index, s))
    comps = []
    j = n-1
    while j > 0:
        s = choice[j]
        comps.append((j-(s-1), s))
        j -= s-1
    return {'n': n, 'V': V, 'FC': FC, 'len': W[n-1], 'comps': comps,
            'rim': (n-1)*2*math.sin(math.pi/n), 'star': float(n)}

def enum_all_full(term_xy):
    """Validation: ALL unrooted binary topologies over ALL leaf labelings ((2n-5)!!)."""
    n = len(term_xy)
    trees = [[(0, 1), (0, 2), (1, 2)]]  # placeholder; build via leaf insertion on edges
    # canonical: start with star on {0,1,2} via one steiner point
    # representation: edge list over nodes: 0..n-1 terminals, n.. steiner
    base_edges = [(0, n), (1, n), (2, n)]
    trees = [(base_edges, 1)]
    for leaf in range(3, n):
        new = []
        for edges, ns in trees:
            for ei in range(len(edges)):
                a, b = edges[ei]
                sp = n + ns
                e2 = edges[:ei] + edges[ei+1:] + [(a, sp), (b, sp), (leaf, sp)]
                # renumber: steiner indices must be >= n; existing ones are n..n+ns-1 ok
                new.append((e2, ns+1))
        trees = new
    best = np.inf
    for edges, ns in trees:
        # remap steiner ids to be contiguous s..s+ns-1 with s=n
        L, _ = opt_topology(term_xy, edges, ns, iters=250, polish=True)
        best = min(best, L)
    return best

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'census'
    if mode == 'validate':
        for n in [3, 4, 5, 6, 7]:
            c = census(n)
            ref = None
            if n == 3: ref = 3.0
            if n == 4: ref = math.sqrt(2)*(1+math.sqrt(3))
            fe = enum_all_full(c['V']) if n <= 7 else None
            print(f"n={n}: DP={c['len']:.10f} rim={c['rim']:.10f} "
                  f"full-enum={fe:.10f}" + (f" ref={ref:.10f}" if ref else ""))
    else:
        out = {}
        for n in range(3, 41):
            c = census(n)
            best_s = {s: c['FC'][s][0] for s in c['FC']}
            out[n] = {'len': c['len'], 'rim': c['rim'], 'star': c['star'],
                      'comps': c['comps'],
                      'fc': {str(s): float(v) for s, v in best_s.items()}}
            tag = 'RIM' if abs(c['len']-c['rim']) < 1e-9 else 'STEINER'
            print(f"n={n:2d}  SMT={c['len']:.9f}  rim={c['rim']:.9f}  "
                  f"ratio={c['len']/c['rim']:.6f}  comps={c['comps']}  {tag}", flush=True)
        json.dump(out, open('steiner_census.json', 'w'), indent=1)
