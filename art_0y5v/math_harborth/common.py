"""Exact verification utilities (integer / Fraction arithmetic)."""
from fractions import Fraction
from itertools import combinations
import math

def orient(a, b, c):
    v = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    return (v > 0) - (v < 0)

def onseg(a, b, c):
    return min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= c[1] <= max(a[1], b[1])

def is_plane(P, edges):
    """Exact check: distinct points, no vertex on a non-incident edge, no two edges crossing/touching."""
    n = len(P)
    if len(set(map(tuple, P))) != n:
        return False, "coincident"
    for (a, b) in edges:
        for v in range(n):
            if v in (a, b): continue
            if orient(P[a], P[b], P[v]) == 0 and onseg(P[a], P[b], P[v]):
                return False, f"vertex {v} on edge {a}-{b}"
    for (a, b), (c, d) in combinations(edges, 2):
        if len({a, b, c, d}) < 4: continue
        o1, o2 = orient(P[a], P[b], P[c]), orient(P[a], P[b], P[d])
        o3, o4 = orient(P[c], P[d], P[a]), orient(P[c], P[d], P[b])
        if o1*o2 < 0 and o3*o4 < 0:
            return False, f"crossing {a}-{b} x {c}-{d}"
        if (o1 == 0 and onseg(P[a], P[b], P[c])) or (o2 == 0 and onseg(P[a], P[b], P[d])) \
           or (o3 == 0 and onseg(P[c], P[d], P[a])) or (o4 == 0 and onseg(P[c], P[d], P[b])):
            return False, "touching"
    return True, "ok"

def sqrt_q(q):
    """exact sqrt of a nonnegative Fraction, or None."""
    q = Fraction(q)
    n, d = q.numerator, q.denominator
    rn, rd = math.isqrt(n), math.isqrt(d)
    if rn*rn == n and rd*rd == d:
        return Fraction(rn, rd)
    return None

def edge_lengths(P, edges):
    out = []
    for a, b in edges:
        d2 = Fraction(P[a][0]-P[b][0])**2 + Fraction(P[a][1]-P[b][1])**2
        out.append(sqrt_q(d2))
    return out

def faces_from_drawing(P, edges):
    """Bounded triangular faces of a plane straight-line triangulation: 3-cycles with no vertex inside,
    oriented counter-clockwise. Also returns the outer face (convex hull triangle)."""
    adj = {v: set() for v in range(len(P))}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    faces = []
    for a, b, c in combinations(range(len(P)), 3):
        if b in adj[a] and c in adj[a] and c in adj[b]:
            o = orient(P[a], P[b], P[c])
            if o == 0: continue
            tri = (a, b, c) if o > 0 else (a, c, b)
            empty = True
            for v in range(len(P)):
                if v in tri: continue
                if all(orient(P[tri[i]], P[tri[(i+1) % 3]], P[v]) > 0 for i in range(3)):
                    empty = False; break
            if empty:
                faces.append(tri)
    return faces

def min_angle_deg(P, faces):
    best = 180.0
    for f in faces:
        for t in range(3):
            o, p, q = (P[f[t]], P[f[(t+1) % 3]], P[f[(t+2) % 3]])
            ux, uy = float(p[0]-o[0]), float(p[1]-o[1]); vx, vy = float(q[0]-o[0]), float(q[1]-o[1])
            c = (ux*vx+uy*vy)/math.sqrt((ux*ux+uy*uy)*(vx*vx+vy*vy))
            best = min(best, math.degrees(math.acos(max(-1, min(1, c)))))
    return best

def verify(P, edges, nfaces_expected=None):
    """Full exact verification. P: list of (Fraction|int, Fraction|int). Returns dict."""
    P = [(Fraction(x), Fraction(y)) for x, y in P]
    ok, why = is_plane(P, edges)
    L = edge_lengths(P, edges)
    integral = all(l is not None and l.denominator == 1 for l in L)
    rational = all(l is not None for l in L)
    faces = faces_from_drawing(P, edges) if ok else []
    n, m = len(P), len(edges)
    return dict(plane=ok, reason=why, integral=integral, rational=rational, lengths=L,
                faces=faces, euler_ok=(ok and len(faces) + 1 == m - n + 2),
                min_angle=min_angle_deg(P, faces) if ok else None)
