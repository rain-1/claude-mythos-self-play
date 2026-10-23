"""General backtracking search for plane integral drawings of a triangulation on the lattice
Z x sqrt(k) Z (point (x,y) means (x, y*sqrt(k))), squared distance dx^2 + k dy^2.
Vertices are placed in a given order; each new vertex is p_nb + w with w a short "Pythagorean" vector,
then must be at integer distance from all placed neighbours, keep all completed faces CCW and create
no crossings. Solutions are scored by min angle; best kept per max-edge value.
"""
import math, json, sys
import numpy as np
from numba import njit

@njit(cache=True)
def isq(n):
    if n < 0: return -1
    r = int(math.sqrt(n))
    while r*r > n: r -= 1
    while (r+1)*(r+1) <= n: r += 1
    return r if r*r == n else -1

@njit(cache=True)
def orient(ax,ay,bx,by,cx,cy,k):
    v = (bx-ax)*(cy-ay) - (by-ay)*(cx-ax)
    return 1 if v > 0 else (-1 if v < 0 else 0)

@njit(cache=True)
def onseg(ax,ay,bx,by,cx,cy):
    return min(ax,bx) <= cx <= max(ax,bx) and min(ay,by) <= cy <= max(ay,by)

@njit(cache=True)
def seg_conflict(ax,ay,bx,by,cx,cy,dx,dy):
    o1 = orient(ax,ay,bx,by,cx,cy,1); o2 = orient(ax,ay,bx,by,dx,dy,1)
    o3 = orient(cx,cy,dx,dy,ax,ay,1); o4 = orient(cx,cy,dx,dy,bx,by,1)
    if o1*o2 < 0 and o3*o4 < 0: return True
    if o1 == 0 and onseg(ax,ay,bx,by,cx,cy): return True
    if o2 == 0 and onseg(ax,ay,bx,by,dx,dy): return True
    if o3 == 0 and onseg(cx,cy,dx,dy,ax,ay): return True
    if o4 == 0 and onseg(cx,cy,dx,dy,bx,by): return True
    return False

@njit(cache=True)
def place_ok(t, X, Y, order_pos, E, adjm, n, k, L, FF):
    # vertex v = order[t] just placed; check vs placed (order_pos < t) stuff
    v = -1
    for u in range(n):
        if order_pos[u] == t: v = u
    x = X[v]; y = Y[v]
    # distinct and distances
    for u in range(n):
        if order_pos[u] < t:
            if X[u] == x and Y[u] == y: return False
            if adjm[u, v]:
                d2 = (X[u]-x)**2 + k*(Y[u]-y)**2
                if d2 > L*L or isq(d2) < 0: return False
    # faces completed now
    for f in range(FF.shape[0]):
        a = FF[f,0]; b = FF[f,1]; c = FF[f,2]
        if (a == v or b == v or c == v) and order_pos[a] <= t and order_pos[b] <= t and order_pos[c] <= t:
            if orient(X[a],Y[a],X[b],Y[b],X[c],Y[c],k) <= 0: return False
    # new vertex on old edge
    for e in range(E.shape[0]):
        a = E[e,0]; b = E[e,1]
        if a == v or b == v: continue
        if order_pos[a] < t and order_pos[b] < t:
            if orient(X[a],Y[a],X[b],Y[b],x,y,1) == 0 and onseg(X[a],Y[a],X[b],Y[b],x,y): return False
    # new edges vs old edges / old vertices on new edges
    for e in range(E.shape[0]):
        a = E[e,0]; b = E[e,1]
        if not (a == v or b == v): continue
        w = a if b == v else b
        if order_pos[w] >= t: continue
        for u in range(n):
            if u == v or u == w or order_pos[u] > t: continue
            if orient(X[w],Y[w],x,y,X[u],Y[u],1) == 0 and onseg(X[w],Y[w],x,y,X[u],Y[u]): return False
        for e2 in range(E.shape[0]):
            c = E[e2,0]; d = E[e2,1]
            if order_pos[c] > t or order_pos[d] > t: continue
            if c == v or d == v or c == w or d == w: continue
            if seg_conflict(X[w],Y[w],x,y,X[c],Y[c],X[d],Y[d]): return False
    return True

@njit(cache=True)
def minang(X, Y, FF, k):
    best = 10.0
    sk = math.sqrt(k)
    for f in range(FF.shape[0]):
        for t in range(3):
            o = FF[f,t]; p = FF[f,(t+1)%3]; q = FF[f,(t+2)%3]
            ux = X[p]-X[o]; uy = (Y[p]-Y[o])*sk; vx = X[q]-X[o]; vy = (Y[q]-Y[o])*sk
            c = (ux*vx+uy*vy)/math.sqrt((ux*ux+uy*uy)*(vx*vx+vy*vy))
            c = min(1.0, max(-1.0, c))
            a = math.acos(c)
            if a < best: best = a
    return best

@njit(cache=True)
def search(n, order, nbref, E, adjm, FF, PVx, PVy, k, L, B, best_ang, best_sol, maxnodes, angmin_prune):
    order_pos = np.full(n, 10**6, np.int64)
    for t in range(n): order_pos[order[t]] = t
    X = np.zeros(n, np.int64); Y = np.zeros(n, np.int64)
    idx = np.zeros(n, np.int64)
    npv = PVx.shape[0]
    t = 1
    idx[1] = 0
    nodes = 0; nsol = 0
    X[order[0]] = 0; Y[order[0]] = 0
    while t >= 1:
        if nodes > maxnodes: break
        v = order[t]; r = order[nbref[t]]
        placed = False
        while idx[t] < npv:
            w = idx[t]; idx[t] += 1
            if t == 1 and not (PVy[w] > 0 or (PVy[w] == 0 and PVx[w] > 0)): continue
            x = X[r] + PVx[w]; y = Y[r] + PVy[w]
            if abs(x) > B or abs(y) > B: continue
            X[v] = x; Y[v] = y
            nodes += 1
            # temporarily treat order_pos
            if place_ok(t, X, Y, order_pos, E, adjm, n, k, L, FF):
                placed = True; break
        if not placed:
            t -= 1
            continue
        if t == n-1:
            # solution
            nsol += 1
            mx = 0
            for e in range(E.shape[0]):
                a = E[e,0]; b = E[e,1]
                d = isq((X[a]-X[b])**2 + k*(Y[a]-Y[b])**2)
                if d > mx: mx = d
            ang = minang(X, Y, FF, k)
            if ang > best_ang[mx]:
                best_ang[mx] = ang
                for u in range(n):
                    best_sol[mx, 2*u] = X[u]; best_sol[mx, 2*u+1] = Y[u]
            continue
        t += 1
        idx[t] = 0
    return nsol, nodes

def make_pv(k, L):
    pv = []
    for dy in range(-int(L/math.sqrt(k))-1, int(L/math.sqrt(k))+2):
        for dx in range(-L, L+1):
            d2 = dx*dx + k*dy*dy
            if 0 < d2 <= L*L and math.isqrt(d2)**2 == d2:
                pv.append((math.isqrt(d2), dx, dy))
    pv.sort()
    return np.array([p[1] for p in pv], np.int64), np.array([p[2] for p in pv], np.int64)

def run(n, edges, faces, order, k, L, B, maxnodes=10**9):
    """faces: CCW-oriented bounded faces (any consistent orientation; mirror solutions are also found
    because the first edge direction covers a half-plane only modulo rotation by 180 degrees... we try both
    orientations by also running with reversed faces)."""
    E = np.array(edges, np.int64)
    adjm = np.zeros((n, n), np.bool_)
    for a, b in edges: adjm[a, b] = adjm[b, a] = True
    pos = {v: i for i, v in enumerate(order)}
    nbref = [0]*n
    for t in range(1, n):
        v = order[t]
        prev = [u for u in order[:t] if adjm[u, v]]
        assert prev, "order must be connected"
        nbref[t] = pos[prev[0]]
    PVx, PVy = make_pv(k, L)
    results = {}
    tot = 0
    for sign in (1, -1):
        FF = np.array([f if sign == 1 else (f[0], f[2], f[1]) for f in faces], np.int64)
        best_ang = np.zeros(L+1); best_sol = np.zeros((L+1, 2*n), np.int64)
        nsol, nodes = search(n, np.array(order, np.int64), np.array(nbref, np.int64), E, adjm, FF,
                             PVx, PVy, k, L, B, best_ang, best_sol, maxnodes, 0.0)
        tot += nsol
        for mx in range(L+1):
            if best_ang[mx] > 0 and best_ang[mx] > results.get(mx, (0,))[0]:
                results[mx] = (best_ang[mx], best_sol[mx].reshape(n, 2).tolist())
    return tot, results
