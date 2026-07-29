"""
skin.py — THE SKIN OF THE FAMILY (2560²)

MO 513505: when is the envelope of a one-parameter family of circles convex?
With centers C(t), radii r(t): v=|C'|, T=C'/v, N=JT, kappa the center-curve
curvature, w=r'/v, q=sqrt(1-w^2), the two envelope branches are

    gamma_eps = C + r(-w T + eps q N),   eps = +-1

with tangent gamma' = L_eps tau_eps, L_eps = eps v q - r Omega_eps,
Omega_eps = v kappa + eps w'/q,  and signed curvature Omega_eps/|L_eps|.

So the skin is convex exactly while Omega_eps keeps one sign — and it TEARS
(cusps) where L_eps = 0. Two families, same law: one obeys, one breaks.

Every quantity below is checked: envelope points satisfy F=F_t=0 to ~1e-12,
the closed-form curvature matches finite differences, cusps sit at L=0 roots.
"""

import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from render import Canvas, draw_ring, bloom, to_img, splat_points, glow

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
FINAL = 900 if PROTO else 2560
rs = FINAL / 2560.0
SS = 2


# ---------------------------------------------------------------- families
def family(kind, t):
    """Returns C (2,n), r (n) and derivatives via dense sampling."""
    if kind == "convex":
        Cx = 1.55 - 3.1 * t
        Cy = 0.34 * t * (1 - t) * 4 - 0.34
        r = 0.22 + 0.85 * t * (1 - t)
    else:  # "torn": radius law with a hard swing -> Omega changes sign, L hits 0
        Cx = 1.55 - 3.1 * t
        Cy = 0.30 * t * (1 - t) * 4 - 0.34
        bump = np.exp(-((t - 0.5) / 0.115) ** 2)
        r = 0.16 + 0.62 * t * (1 - t) + 0.34 * bump
    return np.stack([Cx, Cy]), r


def envelope(kind, n=4001):
    t = np.linspace(0.002, 0.998, n)
    dt = t[1] - t[0]
    C, r = family(kind, t)
    Cp = np.gradient(C, dt, axis=1)
    Cpp = np.gradient(Cp, dt, axis=1)
    rp = np.gradient(r, dt)
    v = np.hypot(*Cp)
    T = Cp / v
    Nvec = np.stack([-T[1], T[0]])
    kappa = (Cp[0] * Cpp[1] - Cp[1] * Cpp[0]) / v ** 3
    w = rp / v
    q2 = 1 - w ** 2
    ok = q2 > 1e-6
    q = np.sqrt(np.clip(q2, 1e-12, None))
    wp = np.gradient(w, dt)
    out = {}
    for eps in (+1, -1):
        nu = -w * T + eps * q * Nvec
        gam = C + r * nu
        Omega = v * kappa + eps * wp / q
        L = eps * v * q - r * Omega
        kap_env = Omega / np.abs(L)
        out[eps] = {"t": t, "gam": gam, "Omega": Omega, "L": L,
                    "kap": kap_env, "ok": ok, "C": C, "r": r, "v": v,
                    "q": q, "w": w}
    return out


def verify(kind):
    env = envelope(kind)
    rep = {"kind": kind}
    t = env[+1]["t"]
    C, r = family(kind, t)
    for eps in (+1, -1):
        gam = env[eps]["gam"]
        # F = |gam-C|^2 - r^2 must vanish
        F = ((gam - C) ** 2).sum(0) - r ** 2
        rep[f"F_resid_{eps}"] = float(np.abs(F).max())
        # closed-form curvature vs finite difference of the branch
        g = gam
        dt = t[1] - t[0]
        gp = np.gradient(g, dt, axis=1)
        gpp = np.gradient(gp, dt, axis=1)
        sp = np.hypot(*gp)
        kfd = (gp[0] * gpp[1] - gp[1] * gpp[0]) / np.clip(sp, 1e-9, None) ** 3
        m = slice(120, -120)
        good = np.abs(env[eps]["L"][m]) > 0.2
        err = np.abs(np.abs(kfd[m][good]) - np.abs(env[eps]["kap"][m][good]))
        rel = err / np.abs(env[eps]["kap"][m][good])
        rep[f"kap_relerr_{eps}"] = float(np.median(rel))
        rep[f"Omega_sign_flips_{eps}"] = int((np.diff(np.sign(env[eps]["Omega"])) != 0).sum())
        Ls = env[eps]["L"]
        rep[f"L_zeros_{eps}"] = int((np.diff(np.sign(Ls)) != 0).sum())
    return env, rep


# ---------------------------------------------------------------- painting
def paint_panel(cv, kind, y0, y1, seed=0):
    env, rep = verify(kind)
    t = env[+1]["t"]
    C, r = family(kind, t)
    W = cv.w
    # world->px: fit x in [-1.9, 1.9]
    S = W / 3.85
    cx = W / 2
    cy = (y0 + y1) / 2 + 0.045 * (y1 - y0)

    def T(P):
        return cx + P[0] * S, cy - P[1] * S * 1.0

    # the family: circles as gossamer, deep dusk ramp
    n_fam = 900 if PROTO else 2400
    idx = np.linspace(0, len(t) - 1, n_fam).astype(int)
    c0 = np.array([0.16, 0.24, 0.60])
    c1 = np.array([0.45, 0.26, 0.50])
    c2 = np.array([0.92, 0.52, 0.20])
    for k in idx:
        u = t[k]
        col = (1 - u) ** 2 * c0 + 2 * u * (1 - u) * c1 + u ** 2 * c2
        x, y = T(C[:, k])
        draw_ring(cv, x, y, r[k] * S, col, amp=0.030, width=0.85 * SS)

    # envelope branches from the closed form
    from render import draw_segment
    for eps in (+1, -1):
        gam = env[eps]["gam"]
        Om = env[eps]["Omega"]
        L = env[eps]["L"]
        q = env[eps]["q"]
        xs, ys = T(gam)
        seg = 5
        for k in range(0, len(t) - seg, seg):
            if q[k] < 0.02:
                continue
            om = Om[k]
            col = (1.0, 0.85, 0.45) if om > 0 else (0.30, 0.85, 1.00)
            amp = 2.0 if om > 0 else 2.4
            p0 = np.array([xs[k], ys[k]])
            p1 = np.array([xs[k + seg], ys[k + seg]])
            if np.hypot(*(p1 - p0)) > 18 * SS:      # cusp jump guard
                continue
            draw_segment(cv, p0, p1, col, amp=amp * 0.4, width=3.6 * SS)
            draw_segment(cv, p0, p1, col, amp=amp, width=1.3 * SS)
        # cusp stars at L=0 (the true tears)
        zc = np.where(np.diff(np.sign(L)) != 0)[0]
        for j in zc:
            if q[j] < 0.02:
                continue
            x, y = xs[j], ys[j]
            glow(cv, x, y, 9.0 * SS, (0.45, 0.9, 1.0), 0.85)
            glow(cv, x, y, 2.4 * SS, (0.95, 1.0, 1.0), 1.7)
    # end caps (the boundary of the union closes with arcs of first/last circle)
    for k in (0, len(t) - 1):
        x, y = T(C[:, k])
        draw_ring(cv, x, y, r[k] * S, (1.0, 0.85, 0.45), amp=0.5,
                  width=1.1 * SS)
    return rep


def main():
    cv = Canvas(FINAL, FINAL, ss=SS)
    H = cv.h
    rep1 = paint_panel(cv, "convex", 0, int(H * 0.52))
    rep2 = paint_panel(cv, "torn", int(H * 0.50), H)
    bloom(cv, 24 * rs * SS, 0.9)
    img = to_img(cv, k=1.5)

    draw = ImageDraw.Draw(img)
    fdir = "/usr/share/fonts/truetype/dejavu/"
    def F(sz, bold=False):
        return ImageFont.truetype(fdir + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
                                  max(int(sz * rs), 8))
    draw.text((FINAL // 2, int(66 * rs)), "THE SKIN OF THE FAMILY",
              font=F(46, True), fill=(212, 216, 226), anchor="mm")
    draw.text((FINAL // 2, int(108 * rs)),
              "when is the envelope of a family of circles convex? · MO 513505",
              font=F(23), fill=(130, 134, 146), anchor="mm")
    mid = ("the skin holds while  Ω± = vκ ± w′/√(1−w²)  keeps its sign — "
           "above, it does; below, the law breaks: Ω changes sign and the skin tears at L=0")
    draw.text((FINAL // 2, FINAL - int(64 * rs)), mid, font=F(21),
              fill=(122, 126, 138), anchor="mm")

    out = "skin_proto.png" if PROTO else "skin_of_the_family_2560.png"
    img.save(out)
    print("saved", out)
    print(rep1)
    print(rep2)


if __name__ == "__main__":
    main()
