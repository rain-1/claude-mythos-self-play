"""Fast evaluators for the MO 513798 polygon-on-lines search (odd n).

Vertices: index pair (i,j), i<j -> vid = i*n+j (sparse). Forced graph:
on each line sort crossings, match consecutive pairs (0,1)(2,3)...
Drop-triangle variant: remove the 3 mutual crossings of a line triple,
match the remaining sorted corners; reject if two matched segments both
strictly contain a dropped point (they'd cross there).
"""
import numpy as np

def crossings(theta, r):
    """Return pts[i][j] = (x,y) param arrays; None if near-degenerate."""
    n = len(theta)
    ct, st = np.cos(theta), np.sin(theta)
    D = ct[:,None]*st[None,:] - ct[None,:]*st[:,None]
    if np.min(np.abs(D + np.eye(n))) < 1e-9: return None, None, None
    X = (r[:,None]*st[None,:] - r[None,:]*st[:,None])
    Y = (ct[:,None]*r[None,:] - ct[None,:]*r[:,None])
    np.fill_diagonal(D, 1.0)
    X, Y = X/D, Y/D          # X[i,j]=x coord of line i ^ line j  (i!=j)
    # param of crossing (i,j) along line i: t = -st_i*x + ct_i*y
    T = -st[:,None]*X + ct[:,None]*Y
    return X, Y, T

def forced_graph(theta, r):
    """Return (C, edges, cyc_of_vertex) for the forced matching graph,
    or (None,None,None) if degenerate. edges = list of (vidA, vidB)."""
    n = len(theta)
    X, Y, T = crossings(theta, r)
    if T is None: return None, None, None
    nbr = {}   # vid -> [vid, vid]
    edges = []
    for i in range(n):
        js = np.array([j for j in range(n) if j != i])
        order = js[np.argsort(T[i, js])]
        # check distinct params (no concurrence)
        ts = np.sort(T[i, js])
        if np.min(np.diff(ts)) < 1e-9: return None, None, None
        for a in range(0, n-1, 2):
            u = vid(i, order[a], n); v = vid(i, order[a+1], n)
            edges.append((u, v))
            nbr.setdefault(u, []).append(v)
            nbr.setdefault(v, []).append(u)
    return _cycles(nbr), edges, nbr

def vid(i, j, n):
    return (i*n+j) if i < j else (j*n+i)

def _cycles(nbr):
    seen = set(); comps = []
    for v0 in nbr:
        if v0 in seen: continue
        c = 0; prev = None; v = v0
        while v not in seen:
            seen.add(v); c += 1
            a, b = nbr[v]
            nxt = a if a != prev else b
            prev, v = v, nxt
        comps.append(c)
    return sorted(comps)

def ncomp(theta, r):
    c, _, _ = forced_graph(theta, r)
    return None if c is None else len(c)

def drop_triangle_graph(theta, r, tri):
    """Graph after dropping the 3 mutual crossings of lines tri=(a,b,c).
    Returns (comps, edges) or (None, None) if degenerate/self-crossing."""
    n = len(theta)
    X, Y, T = crossings(theta, r)
    if T is None: return None, None
    a, b, c = tri
    dropped = {vid(a,b,n), vid(b,c,n), vid(a,c,n)}
    nbr = {}; edges = []
    # containment[p] = set of lines whose matched segment strictly contains dropped pt p
    contain = {p: [] for p in dropped}
    for i in range(n):
        js = np.array([j for j in range(n) if j != i])
        ts = T[i, js]
        if np.min(np.diff(np.sort(ts))) < 1e-9: return None, None
        keep = [(t, j) for t, j in zip(ts, js) if vid(i, j, n) not in dropped]
        drop_here = [(T[i, j], j) for j in js if vid(i, j, n) in dropped]
        keep.sort()
        m = len(keep)
        if m % 2: return None, None
        for k in range(0, m, 2):
            (t0, j0), (t1, j1) = keep[k], keep[k+1]
            u, v = vid(i, j0, n), vid(i, j1, n)
            edges.append((u, v))
            nbr.setdefault(u, []).append(v)
            nbr.setdefault(v, []).append(u)
            for (tp, jp) in drop_here:
                if t0 < tp < t1:
                    contain[vid(i, jp, n)].append(i)
    for p, lines_thru in contain.items():
        if len(lines_thru) >= 2:
            return None, None      # two sides cross at the dropped point
    return _cycles(nbr), edges
