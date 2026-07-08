"""BORROMEAN PRIMES — 13, 61, 937: pairwise strangers, triply bound.

Take any two of the primes 13, 61, 937: each is a quadratic residue
modulo the other (all six Legendre symbols are +1 -- verified below). In
Mazur's dictionary that reads: every pair is UNLINKED, mod 2. Yet the
triple is not free: the Rédei symbol [13, 61, 937] = -1 (Vogel 2005), the
arithmetic analogue of the Milnor triple linking number that detects the
Borromean rings -- remove any one ring and the other two fall apart, yet
all three together cannot be separated.

The rings are drawn as the standard Borromean configuration: three
ellipses in mutually orthogonal planes (a genuine Borromean embedding for
b < 1 < a...); over/under comes from true 3-D depth, not hand-drawn
crossings.

Verified in code: the six Legendre symbols. Cited, not computed: the
Rédei symbol value (Vogel, "On the object of triple linking numbers of
primes"; also Morishita, Knots and Primes ch. 8).
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

P3 = [13, 61, 937]


def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def verify():
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            assert legendre(P3[i], P3[j]) == 1, (P3[i], P3[j])
    # all three are 1 mod 4, so p* = p and reciprocity is plain symmetry
    for p in P3:
        assert p % 4 == 1
    print("VERIFIED: all six Legendre symbols among {13, 61, 937} equal +1 "
          "(pairwise 'unlinked'); all three primes are 1 mod 4")


def ring_points(which, a=1.0, b=0.58, m=4000):
    t = np.linspace(0, 2 * np.pi, m, endpoint=False)
    ca, sb = a * np.cos(t), b * np.sin(t)
    z0 = np.zeros_like(t)
    if which == 0:
        pts = np.stack([ca, sb, z0], axis=1)
    elif which == 1:
        pts = np.stack([z0, ca, sb], axis=1)
    else:
        pts = np.stack([sb, z0, ca], axis=1)
    return pts


def rot(axis, ang):
    c, s = np.cos(ang), np.sin(ang)
    if axis == 0:
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == 1:
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


COLS = [np.array([1.00, 0.76, 0.28]),    # 13   gold
        np.array([0.30, 0.72, 1.00]),    # 61   ice
        np.array([1.00, 0.40, 0.22])]    # 937  ember


def render(S=2560, SS=2, out="borromean_primes_2560.png"):
    verify()
    W = H = S * SS
    canvas = np.zeros((H, W, 3))
    canvas[:] = np.array([0.016, 0.015, 0.028])

    Rview = rot(0, 0.42) @ rot(1, 0.35) @ rot(2, 0.12)
    scale = W * 0.30
    cx, cy = W / 2, H / 2 - 0.02 * H
    tube = W * 0.020

    # ---- sample rings, detect the 6 projected crossings from geometry
    M = 3000
    rings = []
    for k in range(3):
        pts = ring_points(k, m=M) @ Rview.T
        rings.append(dict(x=cx + scale * pts[:, 0], y=cy + scale * pts[:, 1],
                          z=pts[:, 2]))
    crossings = {0: [], 1: [], 2: []}   # ring -> list of (idx, over?)
    for i in range(3):
        for j in range(i + 1, 3):
            dx = rings[i]["x"][:, None] - rings[j]["x"][None, ::5]
            dy = rings[i]["y"][:, None] - rings[j]["y"][None, ::5]
            dd = dx * dx + dy * dy
            close = dd < (tube * 2.0) ** 2
            # cluster contacts along ring i's parameter
            idxs = np.where(close.any(axis=1))[0]
            assert len(idxs) > 0
            splits = np.where(np.diff(idxs) > 30)[0]
            clusters = np.split(idxs, splits + 1)
            # merge wrap-around cluster
            if len(clusters) > 1 and clusters[0][0] == 0 and clusters[-1][-1] == M - 1:
                clusters[0] = np.concatenate([clusters[-1], clusters[0]])
                clusters.pop()
            assert len(clusters) in (2, 4), f"pair {i}{j}: {len(clusters)} crossings"
            for cl in clusters:
                ci = cl[len(cl) // 2]
                jj = np.argmin(dd[ci]) * 5
                over_i = rings[i]["z"][ci] > rings[j]["z"][jj]
                crossings[i].append((int(ci), bool(over_i)))
                crossings[j].append((int(jj), not over_i))
    ncross = sum(len(v) for v in crossings.values()) // 2
    print(f"projected crossings detected: {ncross} "
          f"(per ring: {[len(crossings[k]) for k in range(3)]})")

    # ---- cut each ring into 4 arcs at midpoints between crossings
    arcs = []
    for k in range(3):
        cr = sorted(crossings[k])
        nc = len(cr)
        idxs = [c[0] for c in cr]
        cuts = sorted(((idxs[a] + (idxs[(a + 1) % nc] + (M if a == nc - 1 else 0)))
                       // 2) % M for a in range(nc))
        for a in range(nc):
            c0, c1 = cuts[a], cuts[(a + 1) % nc] + (M if a == nc - 1 else 0)
            sel = np.arange(c0, c1 + 1) % M
            inside = [(ci, ov) for ci, ov in cr
                      if (c0 <= ci <= c1) or (c0 <= ci + M <= c1)]
            assert len(inside) == 1, (k, a, inside)
            zkey = 1.0 if inside[0][1] else -1.0
            arcs.append(dict(k=k, sel=sel, zkey=zkey, gid=len(arcs)))

    # ---- sprite masks
    r_o = tube * 0.92
    r_b = tube * 0.86
    r_s = tube * 0.20
    span = int(np.ceil(tube * 1.35)) + 2
    yy, xx = np.mgrid[-span:span + 1, -span:span + 1].astype(np.float64)

    def disk(r, ox=0.0, oy=0.0):
        return (xx - ox) ** 2 + (yy - oy) ** 2 <= r * r

    m_out = disk(r_o)
    m_body = disk(r_b)
    m_spec = disk(r_s, -0.30 * tube, -0.30 * tube) & m_body
    m_shadow = disk(tube * 1.26)
    rr = np.sqrt((xx + 0.25 * tube) ** 2 + (yy + 0.25 * tube) ** 2) / (r_b + 1e-9)
    shade = np.clip(1.10 - 0.52 * rr, 0.36, 1.10)
    out_col = np.array([0.02, 0.02, 0.045])
    spec_col = np.array([1.0, 0.98, 0.92])

    zall = np.concatenate([r["z"] for r in rings])
    zmin, zmax = zall.min(), zall.max()
    spacing = tube * 0.14
    for arc in sorted(arcs, key=lambda a: (a["zkey"], a["gid"])):
        rg = rings[arc["k"]]
        x = rg["x"][arc["sel"]]; y = rg["y"][arc["sel"]]; z = rg["z"][arc["sel"]]
        d = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
        L = d[-1]
        nn = max(4, int(L / spacing))
        tt = np.linspace(0, L, nn)
        xs = np.interp(tt, d, x); ys = np.interp(tt, d, y)
        zz = np.interp(tt, d, z)
        xi = np.round(xs).astype(int); yi = np.round(ys).astype(int)
        ok = (xi >= span) & (xi < W - span) & (yi >= span) & (yi < H - span)
        xi, yi, zz = xi[ok], yi[ok], zz[ok]
        dp = (zz - zmin) / (zmax - zmin + 1e-9)
        if arc["zkey"] > 0:                 # over-arc casts a shadow
            for x0, y0 in zip(xi[::5], yi[::5]):
                patch = canvas[y0 - span:y0 + span + 1, x0 - span:x0 + span + 1]
                patch[m_shadow] *= 0.86
        for x0, y0 in zip(xi, yi):
            canvas[y0 - span:y0 + span + 1, x0 - span:x0 + span + 1][m_out] = out_col
        for x0, y0, d1 in zip(xi, yi, dp):
            colv = COLS[arc["k"]] * (0.60 + 0.40 * d1)
            canvas[y0 - span:y0 + span + 1, x0 - span:x0 + span + 1][m_body] = \
                colv[None, :] * shade[m_body][:, None]
        for x0, y0 in zip(xi, yi):
            patch = canvas[y0 - span:y0 + span + 1, x0 - span:x0 + span + 1]
            patch[m_spec] = patch[m_spec] * 0.72 + 0.28 * spec_col

    # gentle bloom of the whole emblem
    lum = canvas.sum(axis=2)
    glow = gaussian_filter(lum, tube * 1.6)
    canvas += 0.12 * glow[..., None] * np.array([1.0, 0.9, 0.75])[None, None, :] / (glow.max() + 1e-9)

    img = (np.clip(canvas, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(img).resize((S, S), Image.LANCZOS)

    draw = ImageDraw.Draw(im)
    fp = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    fpb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    f_t = ImageFont.truetype(fpb, int(S * 0.026))
    f_s = ImageFont.truetype(fp, int(S * 0.013))
    f_p = ImageFont.truetype(fpb, int(S * 0.020))
    draw.text((S / 2, S * 0.055), "BORROMEAN PRIMES", font=f_t,
              fill=(235, 228, 210), anchor="mm")
    sub1 = ("every pair a quadratic residue of the other — six Legendre symbols +1, "
            "pairwise unlinked (verified)")
    sub2 = ("yet the Rédei symbol [13, 61, 937] = −1 — the triple cannot be pulled apart "
            "(Vogel 2005 · Milnor  μ̄₁₂₃  ↔  Rédei)")
    draw.text((S / 2, S * 0.905), sub1, font=f_s, fill=(158, 158, 180), anchor="mm")
    draw.text((S / 2, S * 0.928), sub2, font=f_s, fill=(158, 158, 180), anchor="mm")
    # prime labels near each ring
    lab_pos = {0: (0.845, 0.415), 1: (0.565, 0.155), 2: (0.295, 0.545)}
    for k, p in enumerate(P3):
        col = tuple(int(255 * v) for v in COLS[k])
        x, y = lab_pos[k]
        draw.text((S * x, S * y), str(p), font=f_p, fill=col, anchor="mm")
    im.save(out)
    print("saved", out, im.size)


if __name__ == "__main__":
    render(S=1024, SS=2, out="borromean_proto.png")
