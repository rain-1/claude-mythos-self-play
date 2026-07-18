"""THE SAME SHADOW -- homometric constellations, 2560^2.

Two bodies A = U+V, B = U-V: provably non-congruent, yet with exactly equal
difference multisets and diffraction |F|^2. The silk behind everything IS the
shared diffraction pattern (k-origin at the heart of the shared Patterson
mandala, which is drawn in cyan beads: multiplicity = brightness).  The two
bodies wear the same gold: no measurement of distances or scattering can say
which is which. Only the drawing knows.
"""
import numpy as np, time
from collections import Counter
from scipy.ndimage import gaussian_filter
from PIL import Image
import homo_build as hb

FINAL = 2560
SS = 2
S = FINAL * SS


def fourier_silk(A, B, center, kscale):
    """|F(k)|^2 field over the whole canvas, k = (px-center)*kscale."""
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float64)
    KX = (xs - center[0]) * kscale
    KY = (ys - center[1]) * kscale
    FA = np.zeros((S, S), dtype=np.complex128)
    for (x, y) in A:
        FA += np.exp(1j * (KX * x + KY * y))
    I = (FA.real ** 2 + FA.imag ** 2)
    # verify equality against B on a subsampled grid (full grid is expensive)
    sub = np.s_[:: 40, :: 40]
    FB = np.zeros_like(KX[sub], dtype=np.complex128)
    for (x, y) in B:
        FB += np.exp(1j * (KX[sub] * x + KY[sub] * y))
    err = np.abs((np.abs(FB) ** 2) - I[sub]).max() / I.max()
    print(f"silk |F_A|^2 vs |F_B|^2 max rel err: {err:.2e}")
    return I.astype(np.float32)


def splat_beads(buf, pts, amp, sig):
    H, W, _ = buf.shape
    rad = int(np.ceil(3.2 * sig))
    for (x, y), a in zip(pts, amp):
        x0, x1 = int(x - rad), int(x + rad + 1)
        y0, y1 = int(y - rad), int(y + rad + 1)
        if x1 < 0 or y1 < 0 or x0 >= W or y0 >= H:
            continue
        xs = np.arange(max(x0, 0), min(x1, W))
        ys = np.arange(max(y0, 0), min(y1, H))
        d2 = (xs[None, :] - x) ** 2 + (ys[:, None] - y) ** 2
        g = np.exp(-d2 / (2 * sig * sig))
        core = np.exp(-d2 / (2 * (sig * 0.45) ** 2))
        buf[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1, 0] += a[0] * (g * 0.55 + core)
        buf[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1, 1] += a[1] * (g * 0.55 + core)
        buf[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1, 2] += a[2] * (g * 0.55 + core)


def stroke_polyline(buf, pts, col, width, amp, nsub=40):
    """Additive luminous polyline through pts."""
    pts = np.asarray(pts, float)
    for i in range(len(pts) - 1):
        p, q = pts[i], pts[i + 1]
        ts = np.linspace(0, 1, nsub)
        xy = p[None, :] * (1 - ts[:, None]) + q[None, :] * ts[:, None]
        for (x, y) in xy:
            ix, iy = int(x), int(y)
            r = int(np.ceil(3 * width))
            xs = np.arange(max(ix - r, 0), min(ix + r + 1, buf.shape[1]))
            ys = np.arange(max(iy - r, 0), min(iy + r + 1, buf.shape[0]))
            if len(xs) == 0 or len(ys) == 0:
                continue
            d2 = (xs[None, :] - x) ** 2 + (ys[:, None] - y) ** 2
            g = np.exp(-d2 / (2 * width * width)) * (amp / nsub)
            for c in range(3):
                buf[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1, c] += col[c] * g


def render():
    A, B, dA, spec_err = hb.build()
    print(f"pair verified in-render: spec_err {spec_err:.1e}")
    U, V = hb.U, hb.V
    # ---- geometry: place bodies and shadow
    cA = np.array([0.24 * S, 0.29 * S])
    cB = np.array([0.76 * S, 0.29 * S])
    cP = np.array([0.50 * S, 0.67 * S])
    scale_body = 0.175 * S / 60.0          # constellation units -> px
    scale_pat = 0.17 * S / 100.0
    # ---- silk: shared diffraction, k-origin at the Patterson heart
    kscale = 10.5 / S
    t0 = time.time()
    silk = fourier_silk(A, B, cP, kscale)
    print(f"silk in {time.time()-t0:.0f}s")
    silkN = silk / silk.max()
    # log-soft silk: fabric, not blaze; keep the DC sun at the heart
    fab = np.log1p(silk / (0.02 * silk.max()))
    fab /= fab.max()
    rgb = np.zeros((S, S, 3), dtype=np.float32)
    silk_col = np.array([0.30, 0.34, 0.62])
    sun_col = np.array([0.95, 0.80, 0.55])
    rgb += fab[..., None] * silk_col[None, None, :] * 0.42
    rgb += (silkN ** 1.35)[..., None] * sun_col[None, None, :] * 0.75
    # ---- the two bodies: same gold, opposite-wound arms
    gold = np.array([1.0, 0.82, 0.48])
    gold_core = np.array([1.0, 0.95, 0.82])
    for (c0, sgn) in [(cA, +1), (cB, -1)]:
        body = (A if sgn > 0 else B).astype(float)
        cen = body.mean(0)
        # skeleton web: nearest-neighbour tour through the U-sites
        left = list(range(1, len(U)))
        tour = [0]
        while left:
            u0 = U[tour[-1]]
            j = min(left, key=lambda i: (U[i][0] - u0[0]) ** 2 + (U[i][1] - u0[1]) ** 2)
            tour.append(j)
            left.remove(j)
        vc = V.mean(0)
        web = [(c0[0] + (U[i][0] + sgn * vc[0] - cen[0]) * scale_body,
                c0[1] - (U[i][1] + sgn * vc[1] - cen[1]) * scale_body) for i in tour]
        stroke_polyline(rgb, web, gold * 0.30, 1.3 * SS, 2.6 * SS)
        amber = np.array([1.0, 0.55, 0.18])
        pale = np.array([1.0, 0.96, 0.80])
        for u in U:
            arm = [(c0[0] + (u[0] + sgn * v[0] - cen[0]) * scale_body,
                    c0[1] - (u[1] + sgn * v[1] - cen[1]) * scale_body) for v in V]
            for i in range(len(arm) - 1):
                tt = i / (len(arm) - 2)
                col = (amber * (1 - tt) + pale * tt) * 0.62
                stroke_polyline(rgb, arm[i:i + 2], col, 1.8 * SS, 3.6 * SS)
            # beads: root biggest, fading outward
            for i, (x, y) in enumerate(arm):
                tt = i / (len(arm) - 1)
                sz = (2.9 - 1.1 * tt) * SS
                splat_beads(rgb, [(x, y)], [gold_core * (1.32 - 0.5 * tt)], sz)
        # whisper-beam toward the shared shadow
        stroke_polyline(rgb, [tuple(c0), tuple(cP)],
                        np.array([0.5, 0.55, 0.62]) * 0.10, 9 * SS, 5.5 * SS, nsub=160)
    # ---- the shared Patterson mandala (cyan beads, multiplicity = light)
    cyan = np.array([0.35, 0.95, 0.88])
    dpts, damps = [], []
    mmax = max(dA.values())
    for (dx, dy), mult in dA.items():
        dpts.append((cP[0] + dx * scale_pat, cP[1] - dy * scale_pat))
        a = (mult / mmax) ** 0.5
        damps.append(cyan * (0.24 + 1.8 * a))
    splat_beads(rgb, dpts, damps, 2.0 * SS)
    # ---- bloom + tone
    lum = rgb.mean(-1)
    p = np.percentile(lum, 99.0)
    mask = np.clip(lum / (p + 1e-9) - 0.85, 0, 1)[..., None]
    rgb += 0.55 * gaussian_filter(rgb * mask, (9 * SS, 9 * SS, 0))
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    rr = np.hypot(xx - S / 2, yy - S / 2) / (S * 0.72)
    rgb *= (1 - 0.38 * np.clip(rr, 0, 1) ** 2.2)[..., None]
    bg = np.array([0.010, 0.012, 0.026])
    out = 1 - np.exp(-1.72 * rgb)
    out = np.clip(out + bg[None, None, :], 0, 1) ** 0.90
    img = Image.fromarray((out * 255).astype(np.uint8)).resize((FINAL, FINAL), Image.LANCZOS)
    img.save("same_shadow.png")
    print("saved same_shadow.png")


if __name__ == "__main__":
    render()
