"""fold.py — flat-folding a convex figure along straight creases.

A fold along a line reflects the part on one side across the line: a distance-non-increasing map
(1-Lipschitz).  For the unit disc F the image of every such map fits in a congruent copy of F
(|f(x) - f(0)| <= |x| <= 1), which is the property MathOverflow 7016 asks whether only the disc has.

State: a list of LAYERS; each layer is a convex polygon in the current plane plus the isometry
(2x2 orthogonal + offset) taking current coordinates back to the original sheet, so any texture
painted on the original sheet can be looked up exactly through the stack.  Creases are hinge
segments in current coordinates; they get folded along with the paper.
"""
import numpy as np


def clip_half(poly, q, n):
    """Sutherland–Hodgman: keep the part of convex polygon `poly` with (p - q)·n <= 0.
    Returns (kept, other) polygons (either may be empty)."""
    P = np.asarray(poly, float)
    s = (P - q) @ n
    kept, other = [], []
    m = len(P)
    for i in range(m):
        a, b = P[i], P[(i + 1) % m]
        sa, sb = s[i], s[(i + 1) % m]
        if sa <= 0:
            kept.append(a)
        else:
            other.append(a)
        if (sa <= 0) != (sb <= 0):
            t = sa / (sa - sb)
            x = a + t * (b - a)
            kept.append(x); other.append(x)
    return np.array(kept), np.array(other)


def poly_area(P):
    if len(P) < 3:
        return 0.0
    x, y = P[:, 0], P[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def reflect_pts(P, q, n):
    s = (P - q) @ n
    return P - 2 * s[:, None] * n[None, :]


class Folded:
    def __init__(self, poly):
        poly = np.asarray(poly, float)
        # layer: (poly, R (2x2), t (2,)) with original = R @ p + t
        self.layers = [(poly, np.eye(2), np.zeros(2))]
        self.creases = []   # (x0,y0,x1,y1, weight)
        self.centre_img = np.zeros(2)   # where the original centre (0,0) is now
        self.lines = []

    def total_area(self):
        return sum(poly_area(P) for P, _, _ in self.layers)

    def hull_pts(self):
        return np.vstack([P for P, _, _ in self.layers])

    def fold(self, q, n):
        """fold along the line through q with unit normal n: the side n·(p-q) > 0 flips over."""
        q = np.asarray(q, float); n = np.asarray(n, float); n = n / np.linalg.norm(n)
        new = []
        hinges = []
        for P, R, t in self.layers:
            kept, other = clip_half(P, q, n)
            if len(kept) >= 3:
                new.append((kept, R, t))
            if len(other) >= 3:
                Pr = reflect_pts(other, q, n)
                # original = R @ p_old + t, p_old = reflect(p_new) = p_new - 2((p_new - q)·n) n
                #          = R @ (I - 2 n n^T) p_new + R @ (2 (q·n) n) + t
                Rr = R @ (np.eye(2) - 2 * np.outer(n, n))
                tr = R @ (2 * (q @ n) * n) + t
                new.append((Pr, Rr, tr))
                if len(kept) >= 3:
                    # hinge = the chord of this layer on the line: the shared edge; take the two new points
                    s = (P - q) @ n
                    pts = []
                    m = len(P)
                    for i in range(m):
                        a, b = P[i], P[(i + 1) % m]
                        sa, sb = s[i], s[(i + 1) % m]
                        if (sa <= 0) != (sb <= 0):
                            tt = sa / (sa - sb)
                            pts.append(a + tt * (b - a))
                    if len(pts) >= 2:
                        hinges.append((pts[0], pts[-1]))
        self.layers = new
        # fold the existing creases
        cr = []
        for (x0, y0, x1, y1, w) in self.creases:
            a = np.array([x0, y0]); b = np.array([x1, y1])
            sa = (a - q) @ n; sb = (b - q) @ n
            if sa <= 0 and sb <= 0:
                cr.append((x0, y0, x1, y1, w))
            elif sa > 0 and sb > 0:
                a2 = reflect_pts(a[None], q, n)[0]; b2 = reflect_pts(b[None], q, n)[0]
                cr.append((a2[0], a2[1], b2[0], b2[1], w))
            else:
                tt = sa / (sa - sb); x = a + tt * (b - a)
                if sa <= 0:
                    cr.append((a[0], a[1], x[0], x[1], w))
                    b2 = reflect_pts(b[None], q, n)[0]
                    cr.append((x[0], x[1], b2[0], b2[1], w))
                else:
                    cr.append((x[0], x[1], b[0], b[1], w))
                    a2 = reflect_pts(a[None], q, n)[0]
                    cr.append((a2[0], a2[1], x[0], x[1], w))
        for (a, b) in hinges:
            cr.append((a[0], a[1], b[0], b[1], 1.0))
        self.creases = cr
        # centre image
        c = self.centre_img
        if (c - q) @ n > 0:
            self.centre_img = reflect_pts(c[None], q, n)[0]
        self.lines.append((q.copy(), n.copy()))

    def check_lipschitz(self, rng, m=2000):
        """sample pairs of original points; map forward through the folds; distances never grow."""
        pts = rng.standard_normal((m, 2)); pts /= np.linalg.norm(pts, axis=1)[:, None]
        pts *= np.sqrt(rng.uniform(0, 1, m))[:, None]
        cur = pts.copy()
        for q, n in self.lines:
            s = (cur - q) @ n
            flip = s > 0
            cur[flip] = cur[flip] - 2 * s[flip][:, None] * n[None, :]
        d0 = np.linalg.norm(pts[:m // 2] - pts[m // 2:], axis=1)
        d1 = np.linalg.norm(cur[:m // 2] - cur[m // 2:], axis=1)
        return float((d1 - d0).max()), cur

    def forward(self, pts):
        cur = np.asarray(pts, float).copy()
        for q, n in self.lines:
            s = (cur - q) @ n
            flip = s > 0
            cur[flip] = cur[flip] - 2 * s[flip][:, None] * n[None, :]
        return cur


def disc_polygon(m=1440, r=1.0):
    th = np.linspace(0, 2 * np.pi, m, endpoint=False)
    return np.c_[r * np.cos(th), r * np.sin(th)]


def random_fold_sequence(fig, k, rng, frac=(0.10, 0.38), tries=200, schedule=None):
    """k folds; each flips over between frac[0] and frac[1] of the current (union) area, choosing
    lines at random orientation and depth. The flipped side is the smaller one."""
    fig.snaps = [[P.copy() for P, _, _ in fig.layers]]
    fig.snap_lines = []
    for i in range(k):
        fr = schedule[i] if schedule is not None else frac
        pts = fig.hull_pts()
        c = pts.mean(0)
        A = fig.total_area()
        ok = False
        for _ in range(tries):
            th = rng.uniform(0, 2 * np.pi)
            n = np.array([np.cos(th), np.sin(th)])
            proj = (pts - c) @ n
            lo, hi = proj.min(), proj.max()
            d = rng.uniform(lo + 0.15 * (hi - lo), hi - 0.15 * (hi - lo))
            q = c + d * n
            # area on the + side
            ap = 0.0
            for P, _, _ in fig.layers:
                kept, other = clip_half(P, q, n)
                ap += poly_area(other) if len(other) >= 3 else 0.0
            f = ap / A
            if f > 0.5:
                n = -n; f = 1 - f
            if fr[0] <= f <= fr[1]:
                ok = True; break
        if not ok:
            continue
        fig.fold(q, n)
        fig.snaps.append([P.copy() for P, _, _ in fig.layers])
        fig.snap_lines.append((q.copy(), n.copy()))
    return fig
