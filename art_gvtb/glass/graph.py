"""One maximal planar graph, several straight-line drawings.

Faces are kept as oriented vertex triples so the same face can be
coloured identically in every drawing.
"""
import numpy as np, itertools, json, sys


def random_triangulation(n, seed, flips=400, mindeg=4):
    rng = np.random.default_rng(seed)
    faces = [(0, 1, 2), (0, 2, 1)]  # two faces of a triangle on the sphere
    for v in range(3, n):
        k = rng.integers(len(faces))
        a, b, c = faces.pop(k)
        faces += [(a, b, v), (b, c, v), (c, a, v)]
    # random edge flips toward degree balance (sphere triangulation)
    for _ in range(flips):
        faces = flip_random(faces, rng)
    return faces


def edge_map(faces):
    m = {}
    for i, f in enumerate(faces):
        for j in range(3):
            m[(f[j], f[(j + 1) % 3])] = i
    return m


def degrees(faces):
    d = {}
    for f in faces:
        for v in f:
            d[v] = d.get(v, 0) + 1
    return d


def flip_random(faces, rng):
    em = edge_map(faces)
    deg = degrees(faces)
    i = rng.integers(len(faces))
    f = faces[i]
    j = rng.integers(3)
    a, b = f[j], f[(j + 1) % 3]
    c = f[(j + 2) % 3]
    g = faces[em[(b, a)]]
    d = [x for x in g if x not in (a, b)][0]
    if (c, d) in em or (d, c) in em or c == d:
        return faces
    # flip a-b -> c-d if it improves degree variance
    before = (deg[a] - 6) ** 2 + (deg[b] - 6) ** 2 + (deg[c] - 6) ** 2 + (deg[d] - 6) ** 2
    after = (deg[a] - 7) ** 2 + (deg[b] - 7) ** 2 + (deg[c] - 5) ** 2 + (deg[d] - 5) ** 2
    if after > before and rng.random() > 0.15:
        return faces
    if deg[a] <= 4 or deg[b] <= 4:
        return faces
    k = em[(b, a)]
    new = [f for t, f in enumerate(faces) if t not in (i, k)]
    new += [(a, d, c), (b, c, d)]
    # orientation: original f = (a,b,c) ccw, g = (b,a,d)
    return new


def neighbours(faces, n):
    nb = [set() for _ in range(n)]
    for f in faces:
        for j in range(3):
            nb[f[j]].add(f[(j + 1) % 3])
            nb[f[(j + 1) % 3]].add(f[j])
    return nb


def tutte(faces, n, outer, weights=None):
    nb = neighbours(faces, n)
    pos = np.zeros((n, 2))
    ang = np.pi / 2 + np.array([0, 2, 4]) * np.pi / 3
    for t, v in enumerate(outer):
        pos[v] = np.cos(ang[t]), np.sin(ang[t])
    inner = [v for v in range(n) if v not in outer]
    idx = {v: i for i, v in enumerate(inner)}
    A = np.zeros((len(inner), len(inner)))
    B = np.zeros((len(inner), 2))
    for v in inner:
        i = idx[v]
        for u in nb[v]:
            w = 1.0 if weights is None else weights(u, v)
            A[i, i] += w
            if u in idx:
                A[i, idx[u]] -= w
            else:
                B[i] += w * pos[u]
    X = np.linalg.solve(A, B)
    for v in inner:
        pos[v] = X[idx[v]]
    return pos


def koebe(faces, n, outer, iters=4000):
    """Circle packing (Collins-Stephenson); boundary angle sums = pi/3."""
    nb = neighbours(faces, n)
    em = edge_map(faces)
    r = np.ones(n)
    # flower of each vertex: faces containing v
    fl = [[] for _ in range(n)]
    for f in faces:
        if set(f) == set(outer):
            continue
        for j in range(3):
            fl[f[j]].append((f[(j + 1) % 3], f[(j + 2) % 3]))

    def angsum(v, rv):
        s = 0.0
        for u, w in fl[v]:
            a, b, c = rv + r[u], rv + r[w], r[u] + r[w]
            s += np.arccos(np.clip((a * a + b * b - c * c) / (2 * a * b), -1, 1))
        return s

    for it in range(iters):
        for v in range(n):
            target = np.pi / 3 if v in outer else 2 * np.pi
            lo, hi = 1e-6, 1e3
            for _ in range(50):
                mid = np.sqrt(lo * hi)
                if angsum(v, mid) > target:
                    lo = mid
                else:
                    hi = mid
            r[v] = np.sqrt(lo * hi)
        r /= r.max()
    # layout: place outer triangle, then BFS
    pos = {}
    a, b, c = outer
    pos[a] = np.array([0.0, 0.0])
    pos[b] = np.array([r[a] + r[b], 0.0])
    # orient so that remaining faces are ccw
    placed = {a, b}
    q = [(a, b)]
    fl_all = {}
    for f in faces:
        for j in range(3):
            fl_all[(f[j], f[(j + 1) % 3])] = f[(j + 2) % 3]
    # third vertex of face to the left of directed edge (u,w)
    def place(u, w, x):
        du, dw = r[u] + r[x], r[w] + r[x]
        d = np.linalg.norm(pos[w] - pos[u])
        ca = (du * du + d * d - dw * dw) / (2 * du * d)
        ang = np.arccos(np.clip(ca, -1, 1))
        e = (pos[w] - pos[u]) / d
        rot = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
        return pos[u] + du * rot @ e
    while q:
        u, w = q.pop()
        for (s, t) in ((u, w), (w, u)):
            x = fl_all.get((s, t))
            if x is None or x in pos:
                continue
            if set((s, t, x)) == set(outer):
                continue
            pos[x] = place(s, t, x)
            q += [(s, x), (x, t)]
    P = np.array([pos[v] for v in range(n)])
    return P, r


def schnyder(faces, n, outer):
    """Schnyder realizer via canonical ordering; coordinates by face counts."""
    nb = neighbours(faces, n)
    a1, a2, a3 = outer
    # canonical order: peel vertices from boundary starting at a3 side
    # Use standard: remove vertices one at a time from outer cycle (excluding a1,a2)
    # with no chords. Order of removal reversed = canonical ordering.
    boundary = [a1, a3, a2]  # path from a1 to a2 through a3 (outer cycle minus edge a1a2)
    removed = []
    alive = set(range(n))
    while len(alive) > 2:
        cand = None
        for i in range(1, len(boundary) - 1):
            v = boundary[i]
            # chord check: v must not be adjacent to boundary vertices other than neighbours on boundary
            ok = True
            bset = set(boundary)
            for u in nb[v]:
                if u in alive and u in bset and u not in (boundary[i - 1], boundary[i + 1]):
                    ok = False
                    break
            if ok:
                cand = i
                break
        v = boundary[cand]
        alive.remove(v)
        removed.append(v)
        left, right = boundary[cand - 1], boundary[cand + 1]
        rot = rotation(faces, v)
        def arc(a, b, step):
            j = rot.index(a); out = []
            while True:
                j = (j + step) % len(rot)
                if rot[j] == b:
                    return out
                out.append(rot[j])
        newmid = []
        for step in (1, -1):
            m = arc(left, right, step)
            if m and all(u in alive for u in m):
                newmid = m
        boundary = boundary[:cand] + newmid + boundary[cand + 1:]
    order = [a1, a2] + removed[::-1]
    rank = {v: i for i, v in enumerate(order)}
    return order, rank


def rotation(faces, v):
    nxt = {}
    for f in faces:
        if v in f:
            j = f.index(v)
            nxt[f[(j + 1) % 3]] = f[(j + 2) % 3]
    start = next(iter(nxt))
    out = [start]
    while True:
        u = nxt[out[-1]]
        if u == start:
            break
        out.append(u)
    return out


def shift_drawing(faces, n, outer):
    """de Fraysseix-Pach-Pollack shift method on the (2n-4)x(n-2) grid."""
    a1, a2, _ = outer
    order, rank = schnyder(faces, n, outer)
    nb = neighbours(faces, n)
    x = np.zeros(n, int); y = np.zeros(n, int)
    v3 = order[2]
    x[a1], y[a1] = 0, 0
    x[v3], y[v3] = 1, 1
    x[a2], y[a2] = 2, 0
    contour = [a1, v3, a2]
    L = {a1: {a1}, v3: {v3}, a2: {a2}}
    for k in range(3, n):
        v = order[k]
        idxs = [i for i, u in enumerate(contour) if u in nb[v]]
        p, q = idxs[0], idxs[-1]
        # shift
        for i in range(p + 1, q):
            for w in L[contour[i]]:
                x[w] += 1
        for i in range(q, len(contour)):
            for w in L[contour[i]]:
                x[w] += 2
        wp, wq = contour[p], contour[q]
        x[v] = (x[wp] + x[wq] + y[wq] - y[wp]) // 2
        y[v] = (x[wq] - x[wp] + y[wq] + y[wp]) // 2
        L[v] = {v}.union(*[L[contour[i]] for i in range(p + 1, q)])
        contour = contour[:p + 1] + [v] + contour[q:]
    return np.stack([x, y], 1).astype(float)


def check_planar(P, faces, outer):
    # all inner faces positively oriented and nondegenerate
    sgn = []
    for f in faces:
        if set(f) == set(outer):
            continue
        a, b, c = P[list(f)]
        sgn.append(np.cross(b - a, c - a))
    sgn = np.array(sgn)
    return (sgn > 1e-12).all() or (sgn < -1e-12).all(), np.abs(sgn).min() / np.abs(sgn).max()


if __name__ == '__main__':
    n = int(sys.argv[1]); seed = int(sys.argv[2])
    F = random_triangulation(n, seed)
    print(len(F), sorted(degrees(F).values()))
