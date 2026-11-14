"""Ponds: the field s(u) of a set M (union of convex pieces) drawn as graded indigo bands.

s(u) = the first moment u is covered when every piece of M swells towards the whole hull K
(piece P at time s is (1-s)P + sK).  The last point to be covered gives Schneider's index
c = s*/(1-s*).
"""
import sys, json, numpy as np
sys.path.insert(0, "math_schneider")
from convex_union import build, nfold, prune, field_owner, sstar
from batik import *


class Pond:
    def __init__(self, pieces, n=1):
        self.pieces = [np.asarray(p, float).reshape(-1, 2) for p in pieces]
        self.NU, H, self.hK, self.V = build(self.pieces)
        self.H1 = H
        self.n = n
        self.H = prune(nfold(H, n))
        self.s, self.ux, self.uy = sstar(self.NU, self.H, self.hK, self.V, res=500, ncand=10, iters=24)
        self.c = self.s / (1 - self.s); self.a = n * self.c
        # centres of the pieces of (1/n) nM  (support rows -> a representative point)
        lo, hi = self.V.min(0), self.V.max(0)
        self.lo, self.hi = lo, hi

    def fit(self, box):
        """affine map K -> cloth units inside box (x0,y0,x1,y1), y up"""
        x0, y0, x1, y1 = box
        w = self.hi - self.lo
        sc = min((x1 - x0) / w[0], (y1 - y0) / w[1])
        ox = (x0 + x1) / 2 - sc * (self.lo[0] + self.hi[0]) / 2
        oy = (y0 + y1) / 2 + sc * (self.lo[1] + self.hi[1]) / 2
        self.sc, self.ox, self.oy = sc, ox, oy
        return self

    def to_cloth(self, p):
        p = np.asarray(p, float)
        return np.stack([self.ox + self.sc * p[..., 0], self.oy - self.sc * p[..., 1]], -1)

    def raster(self, C, box):
        """field and owner over the pixel window of box; returns (slice_y, slice_x, F, own)"""
        S = C.S
        x0, y0, x1, y1 = [int(v * S) for v in box]
        px = np.arange(x0, x1); py = np.arange(y0, y1)
        xs = ((px + 0.5) / S - self.ox) / self.sc
        ys = -((py + 0.5) / S - self.oy) / self.sc
        F, own = field_owner(xs, ys, self.NU, self.H, self.hK)
        return slice(y0, y1), slice(x0, x1), F, own

    def active(self, tol=2e-4):
        """indices of pieces tied at the last-covered point"""
        from convex_union import s_at
        out = []
        for i in range(len(self.H)):
            v = s_at(self.ux, self.uy, self.NU, self.H[i:i + 1], self.hK)
            if v < self.s + tol: out.append(i)
        return out

    def piece_point(self, i):
        """a point of piece i of the n-fold set (its support polygon's centroid-ish), by least squares"""
        A = self.NU; b = self.H[i]
        # minimise sum (max(0, A x - b))^2 + tiny * distance to the box centre  -> a point inside
        x = np.linalg.lstsq(A, b, rcond=None)[0]
        for _ in range(60):
            r = A @ x - b
            j = np.argmax(r)
            if r[j] <= 1e-12: break
            x = x - r[j] * A[j]
        return x
