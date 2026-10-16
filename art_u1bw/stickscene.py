# stickscene.py — a tray of broken sticks.  Each trial breaks a glass stick of length S at five uniform points.
# The six pieces either lie flat as a closed CYCLIC HEXAGON (in stick order) or, when they can, stand up as a
# TETRAHEDRON (max-volume assignment), resting on its most stable face.  Writes scene.bin for sticks.c.
import numpy as np, itertools, struct, colorsys, json, sys

EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
def _reps():
    syms = []
    for vp in itertools.permutations(range(4)):
        syms.append([EDGES.index(tuple(sorted((vp[a], vp[b])))) for a, b in EDGES])
    seen, reps = set(), []
    for p in itertools.permutations(range(6)):
        key = min(tuple(p[s[i]] for i in range(6)) for s in syms)
        if key not in seen: seen.add(key); reps.append(p)
    return reps
REPS = _reps()

def cm_vol2(e):   # e: 6 edge lengths (01,02,03,12,13,23); 288 V^2 = CM det
    d = np.asarray(e) ** 2
    M = np.ones((5, 5)); M[0, 0] = 0
    M[1:, 1:] = 0
    for k, (i, j) in enumerate(EDGES): M[i + 1, j + 1] = M[j + 1, i + 1] = d[k]
    return np.linalg.det(M) / 288.0

def tri(a, b, c): return a < b + c and b < a + c and c < a + b
def tetra_ok(e):
    return (tri(e[0], e[1], e[3]) and tri(e[0], e[2], e[4]) and tri(e[1], e[2], e[5]) and tri(e[3], e[4], e[5])
            and cm_vol2(e) > 0)

def best_assign(L):
    best, nv = None, 0
    for p in REPS:
        e = [L[i] for i in p]
        if tetra_ok(e):
            nv += 1; v = cm_vol2(e)
            if best is None or v > best[0]: best = (v, p)
    return (best[1] if best else None), nv

def tetra_coords(e):
    d01, d02, d03, d12, d13, d23 = e
    p0 = np.zeros(3); p1 = np.array([d01, 0, 0])
    x2 = (d01 ** 2 + d02 ** 2 - d12 ** 2) / (2 * d01); y2 = np.sqrt(max(d02 ** 2 - x2 ** 2, 0)); p2 = np.array([x2, y2, 0])
    x3 = (d01 ** 2 + d03 ** 2 - d13 ** 2) / (2 * d01)
    y3 = (d02 ** 2 - d03 ** 2 + d23 ** 2 - (x2 - x3) ** 2 - y2 ** 2 + x3 ** 2 - x3 ** 2) / 1.0
    # solve |p3-p2|^2 = d23^2 with p3=(x3,y3,z3), |p3|^2=d03^2
    y3 = (d03 ** 2 - d23 ** 2 + (x2 ** 2 + y2 ** 2) - 2 * x2 * x3) / (2 * y2)
    z3 = np.sqrt(max(d03 ** 2 - x3 ** 2 - y3 ** 2, 0)); p3 = np.array([x3, y3, z3])
    return np.array([p0, p1, p2, p3])

def rest_on_face(P, rng, tall=False):
    c = P.mean(0); best = None
    for f in itertools.combinations(range(4), 3):
        A, B, C = P[list(f)]; n = np.cross(B - A, C - A); area = np.linalg.norm(n) / 2; n /= np.linalg.norm(n)
        o = [k for k in range(4) if k not in f][0]
        if np.dot(P[o] - A, n) > 0: n = -n            # n points away from the apex (down)
        # centroid projection inside the face?
        q = c - np.dot(c - A, n) * n
        def same(p1, p2, a, b): return np.dot(np.cross(b - a, p1 - a), np.cross(b - a, p2 - a)) >= 0
        inside = same(q, A, B, C) and same(q, B, A, C) and same(q, C, A, B)
        hgt = abs(np.dot(P[o] - A, n))
        key = hgt if tall else area
        if inside and (best is None or key > best[0]): best = (key, f, n)
    _, f, n = best
    # rotate n to -z
    z = np.array([0, 0, -1.0]); v = np.cross(n, z); s = np.linalg.norm(v); cth = np.dot(n, z)
    if s < 1e-9: R = np.eye(3) if cth > 0 else np.diag([1, -1, -1])
    else:
        K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]) / s
        th = np.arctan2(s, cth); R = np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K
    Q = (P - c) @ R.T
    ang = rng.uniform(0, 2 * np.pi); Rz = np.array([[np.cos(ang), -np.sin(ang), 0], [np.sin(ang), np.cos(ang), 0], [0, 0, 1]])
    Q = Q @ Rz.T; Q[:, 2] -= Q[:, 2].min()
    Q[:, :2] -= Q[:, :2].mean(0)
    return Q

def cyclic_hexagon(L):
    L = np.asarray(L); m = L.max(); i = L.argmax()
    def total(R, skip=None):
        return sum(2 * np.arcsin(min(1, x / (2 * R))) for k, x in enumerate(L) if k != skip)
    # case 1: centre inside — sum of central angles = 2pi
    lo, hi = m / 2, 1e3 * L.sum()
    if total(lo) >= 2 * np.pi:
        for _ in range(200):
            mid = (lo + hi) / 2
            if total(mid) > 2 * np.pi: lo = mid
            else: hi = mid
        R = (lo + hi) / 2; angs = [2 * np.arcsin(min(1, x / (2 * R))) for x in L]
    else:   # centre outside: longest chord's angle = 2pi - (others) ... solve sum others = 2 arcsin(m/2R)
        lo, hi = m / 2, 1e3 * L.sum()
        f = lambda R: total(R, skip=i) - 2 * np.arcsin(min(1, m / (2 * R)))
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(mid) > 0: hi = mid
            else: lo = mid
        R = (lo + hi) / 2; angs = [2 * np.arcsin(min(1, x / (2 * R))) for x in L]; angs[i] = -angs[i]
    th = np.concatenate([[0], np.cumsum(angs)])[:6]
    V = np.c_[R * np.cos(th), R * np.sin(th)]
    return V - V.mean(0)

def pastel(h, s=0.55, v=1.0): return np.array(colorsys.hsv_to_rgb(h % 1, s, v))

def build(seed=7, cols=11, rows=13, S=24.0, pitch=10.2, rr=0.17, rb=0.40, gap=0.32, out='scene.bin', meta='meta.json',
          absk=0.55, sat=0.62, huefn=None, force=None):
    rng = np.random.default_rng(seed)
    sph, cap = [], []
    trials = []
    for r in range(rows):
        for c in range(cols):
            cx = (c - (cols - 1) / 2) * pitch + (pitch / 2 if r % 2 else 0); cy = (r - (rows - 1) / 2) * pitch * np.sqrt(3) / 2
            cuts = np.sort(rng.random(5)); L = np.diff(np.r_[0, cuts, 1]) * S
            a, nv = best_assign(L)
            mids = (np.r_[0, cuts] + np.r_[cuts, 1]) / 2
            hue = [(0.98 - 0.86 * m) if huefn is None else huefn(m) for m in mids]
            if a is not None:
                e = [L[i] for i in a]; P = rest_on_face(tetra_coords(e), rng)
                P[:, :2] += [cx, cy]; P[:, 2] += rb
                verts = P; segs = [(EDGES[k], a[k]) for k in range(6)]
            else:
                V = cyclic_hexagon(L); ang = rng.uniform(0, 2 * np.pi)
                Rz = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]]); V = V @ Rz.T + [cx, cy]
                verts = np.c_[V, np.full(6, rb)]; segs = [((k, (k + 1) % 6), k) for k in range(6)]
            trials.append(dict(r=r, c=c, x=cx, y=cy, L=L.tolist(), ok=a is not None, nv=nv))
            for v in verts: sph.append([*v, rb, 1, 0.985, 0.965, 0.94, 0])
            for (i, j), piece in segs:
                A, B = verts[i], verts[j]; u = B - A; ln = np.linalg.norm(u); u /= ln
                if ln < 2 * gap + 0.05: continue
                t = pastel(hue[piece], sat); col = -np.log(np.clip(t, 1e-3, 1)) * absk
                cap.append([*(A + u * gap), *(B - u * gap), rr, 0, *col, 0])
    with open(out, 'wb') as f:
        f.write(struct.pack('ii', len(sph), len(cap)))
        f.write(np.array(sph, dtype=np.float64).tobytes()); f.write(np.array(cap, dtype=np.float64).tobytes())
    json.dump(trials, open(meta, 'w'))
    return trials

if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    T = build(seed)
    print(sum(t['ok'] for t in T), 'of', len(T), 'stand up')

def build_rows(seed=3, nrows=22, per=3, S=18.0, dy=3.1, dxgap=2.2, rr=0.2, rb=0.36, gap=0.13, out='scene.bin', meta='meta.json',
               absk=0.55, sat=0.62, tilt=0.02, beadcol=(0.985, 0.965, 0.94), hue0=0.98, hue1=0.12, beadmat=1, flatbeads=False, tall=False):
    rng = np.random.default_rng(seed)
    sph, cap, trials = [], [], []
    W = per * S + (per - 1) * dxgap
    for r in range(nrows):
        y = (r - (nrows - 1) / 2) * dy
        x0 = -W / 2 + rng.uniform(-1.5, 1.5)
        for c in range(per):
            cuts = np.sort(rng.random(5)); L = np.diff(np.r_[0, cuts, 1]) * S
            mids = (np.r_[0, cuts] + np.r_[cuts, 1]) / 2
            hue = [hue0 - (hue0 - hue1 + 1) % 1 * m if False else hue0 + ((hue1 - hue0)) * m for m in mids]
            a, nv = best_assign(L)
            xs = x0 + c * (S + dxgap)
            th = rng.normal(0, tilt)
            cx, cy = xs + S / 2, y
            if a is not None:
                e = [L[i] for i in a]; P = rest_on_face(tetra_coords(e), rng, tall)
                P[:, :2] += [cx, cy]; P[:, 2] += rb
                for v in P: sph.append([*v, rb, beadmat, *beadcol, 0.15])
                off = rb * 0.6 if beadmat != 0 else rb + rr + 0.01
                for k, (i, j) in enumerate(EDGES):
                    A, B = P[i], P[j]; u = B - A; ln = np.linalg.norm(u); u /= ln
                    t = pastel(hue[a[k]], sat); col = -np.log(np.clip(t, 1e-3, 1)) * absk
                    if ln > 2 * off + 0.02: cap.append([*(A + u * off), *(B - u * off), rr, 0, *col, 0])
            else:
                d = np.array([np.cos(th), np.sin(th)]); nrm_ = np.array([-d[1], d[0]])
                for k in range(6):
                    s0, s1 = (np.r_[0, cuts][k]) * S, (np.r_[cuts, 1][k]) * S
                    if s1 - s0 < 2 * gap + 0.02: continue
                    jit = rng.normal(0, 0.06); ph = rng.normal(0, 0.012)
                    dd = np.array([np.cos(th + ph), np.sin(th + ph)])
                    m = np.array([xs, y]) + d * (s0 + s1) / 2 + nrm_ * jit
                    hl = (s1 - s0) / 2 - gap - rr
                    if hl < 0.01: hl = 0.01
                    A = m - dd * hl; B = m + dd * hl
                    t = pastel(hue[k], sat); col = -np.log(np.clip(t, 1e-3, 1)) * absk
                    cap.append([A[0], A[1], rr, B[0], B[1], rr, rr, 0, *col, 0])
            trials.append(dict(r=r, c=c, x=cx, y=cy, L=L.tolist(), ok=a is not None, nv=nv))
    with open(out, 'wb') as f:
        f.write(struct.pack('ii', len(sph), len(cap)))
        if sph: f.write(np.array(sph, dtype=np.float64).tobytes())
        f.write(np.array(cap, dtype=np.float64).tobytes())
    json.dump(trials, open(meta, 'w'))
    return trials
