# Turn shapes + fair 3-partitions (piece polygons) into petit-four rows for petit.py.
import numpy as np

def shape_row(kind, prims, cx, cy, H, ab=None):
    row = np.zeros(64)
    row[0], row[1], row[2] = cx, cy, H
    if kind == 'ellipse':
        row[3] = 1; row[5], row[6] = ab
        return row
    row[4] = len(prims)
    for j, p in enumerate(prims):
        row[5 + 4*j: 9 + 4*j] = p
    return row

def poly_prims(V):
    """convex polygon (ccw) -> half-plane prims (type 0)"""
    V = np.asarray(V, float); out = []
    for i in range(len(V)):
        a, b = V[i], V[(i+1) % len(V)]
        e = b - a; n = np.array([e[1], -e[0]]); n /= np.linalg.norm(n)
        out.append([0, n[0], n[1], n @ a])
    return out

def cut_lines(poly, inside, tol=1e-3):
    """edges of a convex piece polygon that run through the shape's interior = the knife cuts.
    returns list of (n, c) with outward normal n (piece is n.x <= c)."""
    P = np.asarray(poly, float)
    if np.cross(P[1] - P[0], P[2] - P[0]) < 0 or _area(P) < 0:
        P = P[::-1]
    lines = []
    for i in range(len(P)):
        a, b = P[i], P[(i+1) % len(P)]
        L = np.linalg.norm(b - a)
        if L < 1e-6:
            continue
        m = 0.5 * (a + b)
        if inside(m) < -tol:
            e = (b - a) / L; n = np.array([e[1], -e[0]])
            c = n @ a
            if not any(abs(n @ n2 - 1) < 1e-6 and abs(c - c2) < 1e-6 for n2, c2 in lines):
                lines.append((n, c))
    return lines

def _area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)

def piece_rows(pieces, inside, gap, colours, pearl=0.0):
    """pieces: 3 polygons (shape-local coords). returns (3, 9) rows."""
    rows = np.zeros((3, 12))
    cen_all = np.mean([np.mean(np.asarray(p), 0) for p in pieces], 0)
    for k, poly in enumerate(pieces):
        ls = cut_lines(poly, inside)
        if len(ls) > 2:
            # keep the two longest-separated distinct cut lines (convex piece of a 3-cut has <= 2)
            ls = ls[:2]
        while len(ls) < 2:
            ls.append((np.array([0.0, 0.0]), 1.0))
        (n1, c1), (n2, c2) = ls
        # nudge: away from the other pieces, along the sum of the cut normals (inward = -n)
        v = -(n1 + n2)
        if np.linalg.norm(v) < 1e-9:
            v = np.mean(np.asarray(poly), 0) - cen_all
        v = v / (np.linalg.norm(v) + 1e-12)
        Pp = np.asarray(poly, float); x, y = Pp[:, 0], Pp[:, 1]
        cr = x*np.roll(y, -1) - np.roll(x, -1)*y; A = cr.sum()/2
        cen = np.array([((x + np.roll(x, -1))*cr).sum(), ((y + np.roll(y, -1))*cr).sum()])/(6*A)
        rows[k] = [n1[0], n1[1], c1, n2[0], n2[1], c2, gap * v[0], gap * v[1], colours[k], cen[0], cen[1], pearl]
    return rows
