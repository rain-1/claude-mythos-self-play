"""Independent verifier: given lines + an edge list forming a claimed
simple polygon, check EVERYTHING from scratch (no trust in the reduction):
  1. every side lies on one of the n lines (residual < 1e-9)
  2. consecutive sides on different lines
  3. all corners distinct
  4. it is a single closed cycle of the claimed length
  5. NO two sides intersect except consecutive ones at their shared corner
     (exact segment-segment intersection tests)
  6. each unordered line-pair adjacent at most once (poster's constraint)
"""
import numpy as np, sys
from itertools import combinations
from polylib import forced_graph, drop_triangle_graph, crossings, vid

def cycle_from_edges(edges):
    nbr = {}
    for u, v in edges:
        nbr.setdefault(u, []).append(v)
        nbr.setdefault(v, []).append(u)
    for v, ns in nbr.items():
        assert len(ns) == 2, f"vertex {v} degree {len(ns)}"
    v0 = next(iter(nbr)); cyc = [v0]; prev = None; v = v0
    while True:
        a, b = nbr[v]
        nxt = a if a != prev else b
        if nxt == v0: break
        cyc.append(nxt); prev, v = v, nxt
    return cyc

def seg_intersect(p, q, a, b, eps=1e-12):
    """Do segments pq and ab intersect (excluding exact shared endpoints)?"""
    d1 = np.cross(q-p, a-p); d2 = np.cross(q-p, b-p)
    d3 = np.cross(b-a, p-a); d4 = np.cross(b-a, q-a)
    if (d1*d2 < -eps) and (d3*d4 < -eps): return True
    # touching / collinear cases: check if any endpoint lies strictly inside other seg
    for (u, s, t) in ((a,p,q),(b,p,q),(p,a,b),(q,a,b)):
        L = t-s
        cr = np.cross(L, u-s)
        if abs(cr) < 1e-9*np.linalg.norm(L):
            dot = np.dot(u-s, L)/np.dot(L, L)
            if 1e-9 < dot < 1-1e-9: return True
    return False

def verify(theta, r, edges, expected_k):
    n = len(theta)
    ct, st = np.cos(theta), np.sin(theta)
    X, Y, T = crossings(theta, r)
    P = {}
    for i in range(n):
        for j in range(i+1, n):
            P[i*n+j] = np.array([X[i,j], Y[i,j]])
    cyc = cycle_from_edges(edges)
    assert len(cyc) == expected_k == len(edges), \
        f"cycle length {len(cyc)} != {expected_k}"
    pts = [P[v] for v in cyc]
    # 3: corners distinct
    arr = np.array(pts)
    d = np.linalg.norm(arr[:,None,:]-arr[None,:,:], axis=2) + np.eye(len(arr))
    assert d.min() > 1e-7, "duplicate corners"
    k = len(cyc)
    lines_of = []
    for a in range(k):
        p, q = pts[a], pts[(a+1) % k]
        # 1: side on a line
        res = np.abs(ct*(p[0]) + st*(p[1]) - r) + np.abs(ct*(q[0]) + st*(q[1]) - r)
        li = int(np.argmin(res))
        assert res[li] < 1e-8, f"side {a} not on any line (res {res.min():.2e})"
        lines_of.append(li)
    # 2: consecutive sides on different lines
    for a in range(k):
        assert lines_of[a] != lines_of[(a+1) % k], f"consecutive sides {a} same line"
    # 6: each line pair adjacent at most once
    adjpairs = set()
    for a in range(k):
        pr = tuple(sorted((lines_of[a], lines_of[(a+1)%k])))
        assert pr not in adjpairs, f"pair {pr} adjacent twice"
        adjpairs.add(pr)
    # 5: no two non-consecutive sides intersect; consecutive share only corner
    for a in range(k):
        for b in range(a+1, k):
            p, q = pts[a], pts[(a+1)%k]
            u, v = pts[b], pts[(b+1)%k]
            if b == a+1 or (a == 0 and b == k-1):
                continue  # consecutive: share exactly one endpoint by construction
            assert not seg_intersect(p, q, u, v), f"sides {a},{b} intersect"
    return lines_of, cyc

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "full":
        n = int(sys.argv[2])
        theta = np.load(f"win_n{n}_theta.npy"); r = np.load(f"win_n{n}_r.npy")
        comps, edges, _ = forced_graph(theta, r)
        assert comps == [n*(n-1)//2], comps
        verify(theta, r, edges, n*(n-1)//2)
        print(f"n={n}: VERIFIED simple {n*(n-1)//2}-gon, all sides on the {n} lines,"
              f" all {n*(n-1)//2} crossings used, no self-intersection.")
    elif mode == "drop":
        n = int(sys.argv[2])
        theta = np.load(f"win18_n{n}_theta.npy"); r = np.load(f"win18_n{n}_r.npy")
        tri = tuple(np.load(f"win18_n{n}_tri.npy"))
        comps, edges = drop_triangle_graph(theta, r, tri)
        k = n*(n-1)//2 - 3
        assert comps == [k], comps
        verify(theta, r, edges, k)
        print(f"n={n}: VERIFIED simple {k}-gon (dropped triangle {tri}), no self-intersection.")
