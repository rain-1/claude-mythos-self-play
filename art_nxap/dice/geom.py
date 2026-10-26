"""Convex polyhedral dice: vertices, faces (CCW from outside), mass properties."""
import numpy as np


def prism(n, L, R=1.0):
    """Right prism over a regular n-gon (circumradius R), length L along z."""
    t = 2 * np.pi * np.arange(n) / n + np.pi / n
    ring = np.stack([R * np.cos(t), R * np.sin(t)], 1)
    V = np.concatenate([np.c_[ring, np.full(n, -L / 2)], np.c_[ring, np.full(n, L / 2)]])
    F = [list(range(n))[::-1], list(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        F.append([i, j, n + j, n + i])
    return V, F


def _hull(P):
    from scipy.spatial import ConvexHull
    h = ConvexHull(P)
    # merge coplanar triangles into faces
    faces = {}
    for simp, eq in zip(h.simplices, h.equations):
        key = tuple(np.round(eq, 6))
        faces.setdefault(key, set()).update(simp.tolist())
    F = []
    for key, vs in faces.items():
        nrm = np.array(key[:3])
        vs = list(vs)
        c = P[vs].mean(0)
        a = np.cross(nrm, [1, 0, 0] if abs(nrm[0]) < 0.9 else [0, 1, 0]); a /= np.linalg.norm(a)
        b = np.cross(nrm, a)
        ang = [np.arctan2((P[v] - c) @ b, (P[v] - c) @ a) for v in vs]
        F.append([vs[k] for k in np.argsort(ang)])
    return P, F


def platonic(name):
    p = (1 + 5 ** 0.5) / 2
    if name == 'cube':
        P = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
    elif name == 'tet':
        P = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float)
    elif name == 'oct':
        P = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
    elif name == 'ico':
        P = []
        for a in (-1, 1):
            for b in (-1, 1):
                P += [[0, a, b * p], [a, b * p, 0], [b * p, 0, a]]
        P = np.array(P, float)
    elif name == 'dod':
        P = [[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        for a in (-1, 1):
            for b in (-1, 1):
                P += [[0, a / p, b * p], [a / p, b * p, 0], [b * p, 0, a / p]]
        P = np.array(P, float)
    P = P / np.linalg.norm(P, axis=1).max()
    return _hull(P)


def bipyramid(n, H, R=1.0):
    t = 2 * np.pi * np.arange(n) / n
    P = np.c_[R * np.cos(t), R * np.sin(t), np.zeros(n)]
    P = np.vstack([P, [0, 0, H], [0, 0, -H]])
    return _hull(P)


def trapezohedron(n, R=1.0):
    """n-gonal trapezohedron (antiprism dual): 2n kite faces. Built as hull of two
    twisted rings + apexes with the standard kite-planarity height."""
    # vertices: apex ±h0, rings at ±z1 twisted by pi/n
    a = np.pi / n
    # derive via planarity numerically: pick ring z=±c, apex h so kite is planar
    c = 0.1 * R
    t = 2 * np.pi * np.arange(n) / n
    top = np.c_[R * np.cos(t), R * np.sin(t), np.full(n, c)]
    bot = np.c_[R * np.cos(t + a), R * np.sin(t + a), np.full(n, -c)]
    # kite: apex(0,0,h), top[0], bot[0], top[1] planar -> solve h
    A, B, C = top[0], bot[0], top[1]
    nrm = np.cross(B - A, C - A)
    h = A[2] + (nrm[0] * A[0] + nrm[1] * A[1]) / nrm[2]
    P = np.vstack([top, bot, [0, 0, h], [0, 0, -h]])
    return _hull(P)


def mass_props(V, F):
    """Volume, centroid, inertia tensor (about centroid, unit density)."""
    vol = 0.0
    cen = np.zeros(3)
    C = np.zeros((3, 3))
    Can = np.array([[2, 1, 1], [1, 2, 1], [1, 1, 2]]) / 120.0
    for f in F:
        for k in range(1, len(f) - 1):
            A = np.array([V[f[0]], V[f[k]], V[f[k + 1]]]).T  # columns
            d = np.linalg.det(A)
            vol += d / 6
            cen += d / 24 * A.sum(1)
            C += d * A @ Can @ A.T
    cen /= vol
    C = C - vol * np.outer(cen, cen)
    I = np.trace(C) * np.eye(3) - C
    return vol, cen, I


def face_normals(V, F):
    N = []
    c0 = V.mean(0)
    for f in F:
        P = V[f]
        n = np.zeros(3)
        for k in range(len(f)):
            n += np.cross(P[k], P[(k + 1) % len(f)])
        n /= np.linalg.norm(n)
        if (P.mean(0) - c0) @ n < 0:
            n = -n
        N.append(n)
    return np.array(N)


def planes(V, F):
    N = face_normals(V, F)
    d = np.array([N[i] @ V[F[i][0]] for i in range(len(F))])
    return N, d
