"""Exact-ish geometry for MO 515908 'Pizza slices on a plate'.
A slice = circular sector of radius 1, apex a, centre direction th, half-angle ph.
Plate = disc of radius r = 1 - eps about the origin."""
import numpy as np
from shapely.geometry import Polygon
from shapely.strtree import STRtree

def sector_poly(a, th, ph, n=48):
    t = np.linspace(th - ph, th + ph, n)
    pts = [(a[0], a[1])] + list(zip(a[0] + np.cos(t), a[1] + np.sin(t)))
    return Polygon(pts)

def far_dist(a, th, ph):
    """max distance from origin over the sector (apex or arc)."""
    A = np.hypot(*a)
    if A < 1e-15:
        return 1.0
    g = np.arctan2(a[1], a[0])
    dpsi = (g - th + np.pi) % (2 * np.pi) - np.pi      # angle from th to arg a
    dpsi = np.clip(dpsi, -ph, ph)
    return max(A, np.sqrt(A * A + 1 + 2 * A * np.cos(g - (th + dpsi))))

def check(slices, r, tol=1e-10, n=64):
    """slices: list of (ax, ay, th, ph). Returns (ok, worst_out, worst_overlap)."""
    out = max(far_dist((s[0], s[1]), s[2], s[3]) - r for s in slices)
    polys = [sector_poly((s[0], s[1]), s[2], s[3], n) for s in slices]
    tree = STRtree(polys)
    ov = 0.0
    for i, p in enumerate(polys):
        for j in tree.query(p):
            if j > i:
                ov = max(ov, p.intersection(polys[j]).area)
    return (out <= tol and ov <= tol), out, ov

def fan(apex, th0, k, ph, sign=1):
    """k slices sharing an apex; first slice centred at th0 + sign*ph, then onward."""
    return [(apex[0], apex[1], th0 + sign * (2 * j + 1) * ph, ph) for j in range(k)]

def five_sixths(N, eps, grid=24, ph=None):
    """Half-pizza fan from (d,0) facing left + two side fans hanging from the rim.
    Side-fan apex at x = xa on the rim, first leaf rotated t0 from vertical; small grid search."""
    r = 1 - eps
    ph = np.pi / (2 * N) if ph is None else ph
    d = np.sqrt(1 - r * r)
    W = np.arccos(d) - 1e-9
    k1 = int(np.floor(W / ph + 1e-12))
    big = fan((d, 0.0), np.pi - k1 * ph, k1, ph)
    best = (0, big)
    def side(xa, t0, k2):
        ya = np.sqrt(r * r - xa * xa)
        top = fan((xa, ya), -np.pi / 2 + t0, k2, ph)
        bot = [(x, -y, -th, p) for (x, y, th, p) in top]
        return top + bot
    for xa in np.linspace(d, d + 0.12, grid):
        for t0 in np.linspace(0, 0.25, grid):
            # quick upper bound on k2 from containment of the last slice
            ya = np.sqrt(r * r - xa * xa)
            T = np.arccos(1 / (2 * r)) - np.arcsin(xa / r)
            kmax = int(np.floor((T - t0) / (2 * ph) + 1e-9)) + 1
            if 2 * kmax <= best[0] - 0: continue
            for k2 in range(kmax, 0, -1):
                if 2 * k2 <= best[0]: break
                S2 = side(xa, t0, k2)
                if max(far_dist((q[0], q[1]), q[2], q[3]) for q in S2) > r + 1e-12: continue
                ok, o, v = check(big + S2, r, n=40)
                if ok:
                    best = (2 * k2, big + S2)
                    break
    S = best[1]
    ok, o, v = check(S, r)
    assert ok, (o, v)
    return S

if __name__ == "__main__":
    import sys
    for eps in [1e-2, 1e-3, 1e-4, 1e-5]:
        for N in [12, 24, 48, 96]:
            S = five_sixths(N, eps)
            ok, o, v = check(S, 1 - eps)
            print(f"eps={eps:g} N={N}: {len(S)}/{2*N} = {len(S)/(2*N):.4f} ok={ok}")

# ---------------------------------------------------------------- strict verifier
def _depth(px, py, s):
    """signed depth of points inside sector s (positive = interior)."""
    ax, ay, th, ph = s
    u = px - ax; v = py - ay
    lx = u * np.cos(th) + v * np.sin(th); ly = -u * np.sin(th) + v * np.cos(th)
    return np.minimum(np.minimum(1 - np.hypot(lx, ly), lx * np.sin(ph) - ly * np.cos(ph)),
                      lx * np.sin(ph) + ly * np.cos(ph))

def _boundary(s, n=4000):
    ax, ay, th, ph = s
    t = np.linspace(0, 1, n)
    e1 = (ax + np.cos(th - ph) * t, ay + np.sin(th - ph) * t)
    e2 = (ax + np.cos(th + ph) * t, ay + np.sin(th + ph) * t)
    a = np.linspace(th - ph, th + ph, n)
    arc = (ax + np.cos(a), ay + np.sin(a))
    return np.concatenate([e1[0], e2[0], arc[0]]), np.concatenate([e1[1], e2[1], arc[1]])

def strict_check(slices, r, n=4000):
    """max over pairs of the depth of one sector's boundary inside the other (sampled at
    spacing <= 1/n; overlaps of depth > ~1/(2n) cannot hide), and max radius."""
    worst = -1.0
    out = max(far_dist((s[0], s[1]), s[2], s[3]) for s in slices) - r
    B = []
    for s in slices:
        bx, by = _boundary(s, n)
        ax, ay, th, ph = s                     # plus interior samples (catches nested/coincident)
        rr, aa = np.meshgrid(np.linspace(0.05, 0.95, 12), np.linspace(-0.9, 0.9, 9))
        ix = ax + rr.ravel() * np.cos(th + aa.ravel() * ph); iy = ay + rr.ravel() * np.sin(th + aa.ravel() * ph)
        B.append((np.concatenate([bx, ix]), np.concatenate([by, iy])))
    for i, s in enumerate(slices):
        for j, t in enumerate(slices):
            if i == j: continue
            if np.hypot(s[0] - t[0], s[1] - t[1]) > 2.01: continue
            worst = max(worst, _depth(B[i][0], B[i][1], t).max())
    return out, worst

def rect_fill(o, u, L, ph):
    """Alternating slices filling the rectangle o + [0,1]u + [0,L]u_perp exactly (leaf length 1)."""
    ux, uy = u; vx, vy = -uy, ux
    th = np.arctan2(uy, ux)
    out = []
    y = np.sin(ph)
    while True:
        if y + np.sin(ph) > L + 1e-12: break
        out.append((o[0] + y * vx, o[1] + y * vy, th, ph))
        yb = y + np.tan(ph)
        if yb + np.sin(ph) > L + 1e-12: break
        out.append((o[0] + ux + yb * vx, o[1] + uy + yb * vy, th + np.pi, ph))
        y += 2 * np.tan(ph)
    return out

def cross(N, eps):
    """Jonathan Love's cross: bar of height 1 across, two stubs of width 1 (MO 515908)."""
    r = 1 - eps
    ph = np.pi / (2 * N)
    h = np.sqrt(r * r - 0.25)
    S = rect_fill((-h, -0.5), (0.0, 1.0), 2 * h, ph)            # bar: leaves vertical, wait: u = leaf dir
    # bar: rectangle x in [-h,h], y in [-1/2,1/2]; leaves vertical (u=(0,1)), stacked along x
    S = rect_fill((h, -0.5), (0.0, 1.0), 2 * h, ph)              # u_perp = (-1,0): stacks toward -x
    S += rect_fill((-0.5, 0.5), (1.0, 0.0), h - 0.5, ph)         # top stub: leaves horizontal, stack up
    S += rect_fill((0.5, -0.5), (-1.0, 0.0), h - 0.5, ph)        # bottom stub: u=(-1,0), perp=(0,-1)
    return S

def fan_order(S, N):
    """Return the list of 2N positions in the original pizza: slices of S (or None for leftovers),
    ordered big fan (ccw), bottom fan, leftovers, top fan reversed - so hue = original position."""
    big = sorted([s for s in S if abs(s[1]) < 1e-9], key=lambda s: s[2])
    top = sorted([s for s in S if s[1] > 1e-9], key=lambda s: s[2])
    bot = sorted([s for s in S if s[1] < -1e-9], key=lambda s: -s[2])
    return big + bot + [None] * (2 * N - len(S)) + top[::-1]
