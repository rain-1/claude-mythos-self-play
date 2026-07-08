"""THE RECIPROCITY LOOM — quadratic reciprocity woven as literal fabric.

Mazur's dictionary: the mod-2 linking number of two prime-knots is the
Legendre symbol, lk2(q, p) defined by (q*/p) = (-1)^lk2, q* = (-1)^((q-1)/2) q.
Here every odd prime up to 101 runs once as a warp thread and once as a
weft thread; at each intersection the q-thread passes OVER the p-thread
exactly when (q*/p) = +1 (q "splits over" p -- unlinked, so it lifts
above). Gauss's golden theorem (q*/p) = (p/q) is then a statement about
cloth: the weave is symmetric across the diagonal. On the diagonal
itself, a prime meets its own ramification: a bead of light.

Threads are dyed by residue class mod 4 -- gold for p = 1 (mod 4), cyan
for p = 3 (mod 4) -- since q* = q exactly for the golden threads.

Verified: Euler's criterion against brute-force QR search for p <= 23;
the reciprocity identity (q*/p) = (p/q) for all 300 pairs (this equality
IS quadratic reciprocity, and IS the fabric's symmetry).
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont

PRIMES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
          61, 67, 71, 73, 79, 83, 89, 97, 101]


def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return 1 if r == 1 else -1


def star(q):
    return q if q % 4 == 1 else -q


def verify():
    # Euler criterion vs brute force
    for p in [3, 5, 7, 11, 13, 17, 19, 23]:
        squares = {(x * x) % p for x in range(1, p)}
        for a in range(1, p):
            assert (legendre(a, p) == 1) == (a in squares)
    # quadratic reciprocity in the q* form: (q*/p) = (p/q)
    for p in PRIMES:
        for q in PRIMES:
            if p == q:
                continue
            assert legendre(star(q), p) == legendre(p, q), (p, q)
    print("VERIFIED: Euler criterion (p<=23, brute force); "
          "(q*/p) = (p/q) for all 600 ordered pairs -- quadratic reciprocity")


def render(S=2560, SS=2, out="reciprocity_loom_2560.png"):
    verify()
    N = len(PRIMES)
    W = H = S * SS
    marg = int(0.075 * W)
    span_px = (W - 2 * marg) / N
    tube = span_px * 0.16
    canvas = np.zeros((H, W, 3))
    canvas[:] = np.array([0.017, 0.016, 0.030])

    GOLD1 = np.array([0.98, 0.78, 0.36])     # p = 1 mod 4
    CYAN3 = np.array([0.42, 0.78, 0.95])     # p = 3 mod 4

    def thread_color(p):
        base = GOLD1 if p % 4 == 1 else CYAN3
        # slight per-prime variation so neighbouring threads separate
        f = 0.88 + 0.24 * ((p * 0.6180339887) % 1)
        return np.clip(base * f, 0, 1)

    def pos(k):
        return marg + (k + 0.5) * span_px

    # ---- sprite masks
    r_o = tube * 0.95
    r_b = tube * 0.84
    r_s = tube * 0.30
    span = int(np.ceil(tube * 1.3)) + 2
    yy, xx = np.mgrid[-span:span + 1, -span:span + 1].astype(np.float64)

    def disk(r, ox=0.0, oy=0.0):
        return (xx - ox) ** 2 + (yy - oy) ** 2 <= r * r

    m_out = disk(r_o)
    m_body = disk(r_b)
    m_spec = disk(r_s, -0.30 * tube, -0.30 * tube) & m_body
    m_shadow = disk(tube * 1.28)
    rr = np.sqrt((xx + 0.25 * tube) ** 2 + (yy + 0.25 * tube) ** 2) / (r_b + 1e-9)
    shade = np.clip(1.08 - 0.50 * rr, 0.38, 1.08)
    out_col = np.array([0.02, 0.02, 0.045])
    spec_col = np.array([1.0, 0.98, 0.92])

    # ---- build groups: one per (thread, cell); z from the Legendre rule
    groups = []
    for ri, p in enumerate(PRIMES):        # horizontal thread of prime p
        yc = pos(ri)
        for ci, q in enumerate(PRIMES):
            if p == q:
                z = 0.0
            else:
                z = -1.0 if legendre(star(q), p) == 1 else 1.0
            groups.append(dict(axis="h", fixed=yc, k0=marg + ci * span_px,
                               k1=marg + (ci + 1) * span_px, z=z,
                               col=thread_color(p), gid=len(groups)))
    for ci, q in enumerate(PRIMES):        # vertical thread of prime q
        xc = pos(ci)
        for ri, p in enumerate(PRIMES):
            if p == q:
                z = 0.0
            else:
                z = 1.0 if legendre(star(q), p) == 1 else -1.0
            groups.append(dict(axis="v", fixed=xc, k0=marg + ri * span_px,
                               k1=marg + (ri + 1) * span_px, z=z,
                               col=thread_color(q), gid=len(groups)))

    spacing = tube * 0.16
    for g in sorted(groups, key=lambda g: (g["z"], g["gid"])):
        L = g["k1"] - g["k0"]
        nsm = max(6, int(L / spacing))
        t = np.linspace(0, 1, nsm)
        ks = g["k0"] + t * L
        # z-bump: over/under threads bow across the cell
        mid = pos(0)  # dummy
        bump = np.sin(np.pi * t)
        if g["axis"] == "h":
            xs = ks
            ys = np.full_like(ks, g["fixed"])
        else:
            xs = np.full_like(ks, g["fixed"])
            ys = ks
        xi = np.round(xs).astype(int)
        yi = np.round(ys).astype(int)
        ok = (xi >= span) & (xi < W - span) & (yi >= span) & (yi < H - span)
        xi, yi = xi[ok], yi[ok]
        bu = bump[ok]
        if g["z"] > 0.5:
            # cast shadow near cell centre
            for x0, y0, b in zip(xi[::3], yi[::3], bu[::3]):
                if b < 0.45:
                    continue
                patch = canvas[y0 - span:y0 + span + 1, x0 - span:x0 + span + 1]
                patch[m_shadow] *= 0.72
        for x0, y0 in zip(xi, yi):
            canvas[y0 - span:y0 + span + 1, x0 - span:x0 + span + 1][m_out] = out_col
        body = g["col"][None, :] * shade[m_body][:, None]
        for x0, y0 in zip(xi, yi):
            canvas[y0 - span:y0 + span + 1, x0 - span:x0 + span + 1][m_body] = body
        for x0, y0 in zip(xi, yi):
            patch = canvas[y0 - span:y0 + span + 1, x0 - span:x0 + span + 1]
            patch[m_spec] = patch[m_spec] * 0.55 + 0.45 * spec_col

    # ---- diagonal ramification beads
    from scipy.ndimage import gaussian_filter
    delta = np.zeros((H, W))
    for k, p in enumerate(PRIMES):
        x0, y0 = int(pos(k)), int(pos(k))
        delta[y0, x0] = 1.0
    bead = gaussian_filter(delta, tube * 0.55) * (tube * 0.55) ** 2 * 6.28
    canvas += 1.5 * bead[..., None] * np.array([1.0, 0.95, 0.80])[None, None, :]
    halo = gaussian_filter(delta, tube * 2.2) * (tube * 2.2) ** 2 * 6.28
    canvas += 0.30 * halo[..., None] * np.array([1.0, 0.88, 0.55])[None, None, :]

    img = (np.clip(canvas, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(img).resize((S, S), Image.LANCZOS)

    # ---- labels
    draw = ImageDraw.Draw(im)
    fp = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    fpb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    f_lab = ImageFont.truetype(fp, int(S * 0.014))
    f_t = ImageFont.truetype(fpb, int(S * 0.024))
    f_s = ImageFont.truetype(fp, int(S * 0.0125))
    dimc = (155, 155, 178)
    for k, p in enumerate(PRIMES):
        c = tuple(int(255 * v) for v in
                  ((0.98, 0.78, 0.36) if p % 4 == 1 else (0.42, 0.78, 0.95)))
        draw.text((pos(k) / SS, marg / SS - S * 0.021), str(p), font=f_lab,
                  fill=c, anchor="mm")
        draw.text((marg / SS - S * 0.024, pos(k) / SS), str(p), font=f_lab,
                  fill=c, anchor="mm")
    draw.text((S / 2, S - S * 0.040), "THE RECIPROCITY LOOM", font=f_t,
              fill=(235, 228, 210), anchor="mm")
    draw.text((S / 2, S - S * 0.018),
              "q rises over p  ⇔  (q*∕p) = +1  ·  lk₂(p,q) ↔ Legendre  ·  "
              "the cloth is symmetric because (q*∕p) = (p∕q): quadratic reciprocity",
              font=f_s, fill=dimc, anchor="mm")
    im.save(out)
    print("saved", out, im.size)


if __name__ == "__main__":
    render(S=1024, SS=2, out="fabric_proto.png")
