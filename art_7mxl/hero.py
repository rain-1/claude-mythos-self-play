"""HERO: 'The Casting Vote' — the Fibonacci-sum determinant parliament.

Main harp: n=97 — 333,973,125 Fibonacci permutations; even/odd split
166,986,563 / 166,986,562; det = +1. Sampled matchings drawn as arc fog:
even permutations above the baseline (ember), odd below (ice).
Medallions: n=100 (det 0 — the perfect tie), n=104 (per = 1 — the lone
voice, odd, det = -1).
"""
import numpy as np
import pickle
import sys
from PIL import Image, ImageDraw, ImageFont
from detlib import fibs_upto
from scipy.ndimage import gaussian_filter, zoom

S = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS = 2                       # supersample
W = H = S * SS
rs = S / 1024.0


def splat_pts(buf, xs, ys, ws):
    """Bilinear additive splat of weighted points into 2-D buf."""
    h, w = buf.shape
    x0 = np.floor(xs).astype(np.int64)
    y0 = np.floor(ys).astype(np.int64)
    fx = xs - x0
    fy = ys - y0
    for dx, dy, wt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                       (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xi = x0 + dx
        yi = y0 + dy
        ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
        np.add.at(buf, (yi[ok], xi[ok]), (ws * wt)[ok])


def draw_arc(buf, xa, xb, y0, up, ky, weight):
    """Elliptical arc between rail x-positions xa..xb (pixels)."""
    cx = 0.5 * (xa + xb)
    r = 0.5 * abs(xb - xa)
    if r < 1e-9:
        return
    approx = np.pi * r * max(ky, 0.3)
    npts = max(10, int(approx / 1.2))
    th = np.linspace(0.0, np.pi, npts)
    xs = cx + r * np.cos(th)
    ys = y0 - up * r * ky * np.sin(th)
    splat_pts(buf, xs, ys, np.full(npts, weight * approx / npts))


class Harp:
    def __init__(self, n, x_lo, x_hi, y0, ky=0.52, ky_scale=1.0):
        self.n = n
        self.x_lo = x_lo
        self.x_hi = x_hi
        self.y0 = y0
        self.ky = ky
        self.dx = (x_hi - x_lo) / (n - 1)
        self.ky_eff = ky * ky_scale

    def xpos(self, i):
        """rail position of label i (1..n)."""
        return self.x_lo + (i - 1) * self.dx

    def skeleton(self, buf, weight):
        F = fibs_upto(2 * self.n)
        for q in F:
            i_lo = max(1, q - self.n)
            i_hi = (q - 1) // 2
            for i in range(i_lo, i_hi + 1):
                j = q - i
                if j > self.n or j < 1 or j <= i:
                    continue
                for up in (1, -1):
                    draw_arc(buf, self.xpos(i), self.xpos(j), self.y0, up,
                             self.ky_eff, weight)

    def perm_arcs(self, buf, perm, up, weight):
        """perm 0-indexed tuple; draw arcs i -> perm[i]."""
        drawn = set()
        for i0, j0 in enumerate(perm):
            i, j = i0 + 1, j0 + 1
            a, b = min(i, j), max(i, j)
            if a == b:
                # fixed point: short vertical tick
                x = self.xpos(a)
                ys = self.y0 - up * np.linspace(0, 6 * rs * SS, 8)
                splat_pts(buf, np.full(8, x), ys, np.full(8, weight * 2))
                continue
            key = (a, b)
            mult = 2.0 if key in drawn else 1.0
            drawn.add(key)
            draw_arc(buf, self.xpos(a), self.xpos(b), self.y0, up,
                     self.ky_eff, weight * mult)


def tone(x, k, g=0.62):
    y = 1.0 - np.exp(-k * x)
    return np.power(np.clip(y, 0, 1), g)


def main():
    skel = np.zeros((H, W), np.float32)
    even = np.zeros((H, W), np.float32)
    odd = np.zeros((H, W), np.float32)
    gold = np.zeros((H, W), np.float32)

    # ---- main harp n=97
    n = 97
    harp = Harp(n, 0.06 * W, 0.94 * W, 0.545 * H, ky=0.60)
    harp.skeleton(skel, 1.0)
    samples = pickle.load(open("samples_97.pkl", "rb"))
    ne = sum(1 for _, s in samples if s > 0)
    no = len(samples) - ne
    we = 1.0 / max(ne, 1)
    wo = 1.0 / max(no, 1)
    for perm, sgn in samples:
        if sgn > 0:
            harp.perm_arcs(even, perm, +1, we)
        else:
            harp.perm_arcs(odd, perm, -1, wo)

    # Fibonacci midpoint pillars on the main rail
    F = fibs_upto(2 * n)
    for q in F:
        c = (q) / 2.0
        if c < 1 or c > n:
            continue
        x = harp.xpos(c)
        ys = np.linspace(0.08 * H, 0.985 * H, 600)
        splat_pts(gold, np.full(600, x), ys, np.full(600, 0.006))

    # the casting-vote star: one gold spark on the even side
    xs_star = harp.xpos(n) + 0.018 * W
    y_star = harp.y0 - 0.035 * H
    th = np.random.default_rng(5).normal(size=(2, 4000)) * 2.2 * rs * SS
    splat_pts(gold, xs_star + th[0], y_star + th[1],
              np.full(4000, 0.02))

    # ---- medallions
    m1 = Harp(100, 0.075 * W, 0.435 * W, 0.875 * H, ky=0.55)
    m1.skeleton(skel, 0.55)
    s100 = pickle.load(open("samples_100.pkl", "rb"))
    ne1 = sum(1 for _, s in s100 if s > 0)
    no1 = len(s100) - ne1
    for perm, sgn in s100:
        if sgn > 0:
            m1.perm_arcs(even, perm, +1, 0.85 / max(ne1, 1))
        else:
            m1.perm_arcs(odd, perm, -1, 0.85 / max(no1, 1))

    m2 = Harp(104, 0.565 * W, 0.925 * W, 0.875 * H, ky=0.55)
    m2.skeleton(skel, 0.55)
    s104 = pickle.load(open("samples_104.pkl", "rb"))
    perm104, sgn104 = s104[0]
    assert sgn104 == -1
    # the lone voice: crisp, drawn with extra passes
    for _ in range(3):
        m2.perm_arcs(odd, perm104, -1, 0.55)

    # ---- compose
    img = np.zeros((H, W, 3), np.float32)

    def nz_pct(a, p):
        m = a[a > 0]
        return np.percentile(m, p) if len(m) else 1.0

    sk = tone(skel / nz_pct(skel, 99.0), 1.15, 0.70)
    ev = tone(even / nz_pct(even, 99.5), 2.4, 0.60)
    od = tone(odd / nz_pct(odd, 99.5), 2.4, 0.60)
    gl = tone(gold / nz_pct(gold, 99.5), 2.8, 0.60)

    c_sk = np.array([0.30, 0.37, 0.47])
    c_ev = np.array([1.00, 0.66, 0.26])
    c_od = np.array([0.30, 0.62, 0.95])
    c_gl = np.array([1.00, 0.83, 0.42])
    img += sk[..., None] * c_sk * 0.5
    img += ev[..., None] * c_ev
    img += od[..., None] * c_od
    img += gl[..., None] * c_gl

    # bloom on bright cores
    lum = img.sum(2)
    thr = np.percentile(lum, 99.2)
    mask = np.clip(lum - thr, 0, None)[..., None] * img / (lum[..., None] + 1e-9)
    ds = max(1, int(6 * rs))
    small = mask[::ds, ::ds]
    bl = gaussian_filter(small, (14 * rs / ds, 14 * rs / ds, 0))
    bloom = zoom(bl, (mask.shape[0] / small.shape[0],
                      mask.shape[1] / small.shape[1], 1), order=1)
    bloom = bloom[:H, :W]
    img += 0.85 * np.clip(bloom, 0, None)

    img = np.clip(img, 0, 1)
    # downsample
    pil = Image.fromarray((img * 255).astype(np.uint8))
    pil = pil.resize((S, S), Image.LANCZOS)
    arr = np.asarray(pil).astype(np.float32) / 255.0
    # dither
    arr = np.clip(arr + (np.random.default_rng(1).random(arr.shape) - 0.5) / 255.0, 0, 1)
    out = Image.fromarray((arr * 255).astype(np.uint8))

    # ---- caption card
    if S >= 2048:
        fs1 = int(S * 0.0125)
        fs2 = int(S * 0.0095)
        try:
            f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", fs1)
            f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fs2)
        except OSError:
            f1 = f2 = ImageFont.load_default()
        dr = ImageDraw.Draw(out)
        y = int(0.952 * S)
        dr.text((int(0.06 * S), y), "THE CASTING VOTE", fill=(232, 205, 150), font=f1)
        cap = ("(M)ij = 1 iff i+j is Fibonacci  ·  n = 97:  333,973,125 permutations with every i+π(i) Fibonacci  ·  "
               "166,986,563 even (ember, above)  vs  166,986,562 odd (ice, below)  ·  det = +1: carried by one vote")
        dr.text((int(0.06 * S), y + int(fs1 * 1.5)), cap, fill=(150, 152, 158), font=f2)
        cap2 = ("left: n = 100 — 10,562,500 permutations, 5,281,250 : 5,281,250, det = 0, the perfect tie      "
                "right: n = 104 — one permutation, odd, det = −1, the lone voice")
        dr.text((int(0.06 * S), y + int(fs1 * 2.6)), cap2, fill=(150, 152, 158), font=f2)
        # medallion labels
        dr.text((int(0.075 * S), int(0.905 * S)), "the tie", fill=(120, 128, 140), font=f2)
        dr.text((int(0.565 * S), int(0.905 * S)), "the lone voice", fill=(120, 128, 140), font=f2)

    out.save(f"hero_{S}.png")
    print("saved", f"hero_{S}.png")


if __name__ == "__main__":
    main()
