"""
rattle.py — THE RATTLE (2560²) · positions without difference

The n=5 coin set that comes closest to being held: it fits — with a slack
measured in parts per ten thousand — and therefore it is never held at all.
Hard-disk MCMC over the feasible configurations at s=1, quotiented by the
tray's rotation: every position in the fog is reachable, and no contact,
no force, no physically possible process inside the tray distinguishes
one from another. (Phil.SE: are two states distinct if no possible
process can tell them apart?)

Gold skeleton: the same coins jammed rigid in the tray shrunk by 1/s_max —
the world in which they would be held.

Usage: rattle.py [proto]
"""

import json
import math
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from render import (Canvas, draw_ring, draw_segment, glow, bloom, to_img,
                    splat_points, PAL, GHOST)
from search_jam import best_s, maximize_s
from engine import contact_data, first_order_flex

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
FINAL = 900 if PROTO else 2560
rs = FINAL / 2560.0
SS = 2

MULTISET = (1, 3, 1, 3)          # {1/2, 1/3 x3, 1/4, 1/5 x3} — closest floppy fit (refined sweep)
SWEEPS = 4000 if PROTO else 26000
SAMPLE_EVERY = 4


def radii_of(ms):
    r = []
    for m, p in zip(ms, (2, 3, 4, 5)):
        r += [1.0 / p] * m
    return np.array(sorted(r, reverse=True))


def mcmc(radii, x0, sweeps, step0=0.004, seed=1):
    """Hard-disk MCMC at s=1 in unit tray; gauge-fix collective rotation so
    the largest coin keeps its initial polar angle. Returns samples list and
    near-contact events."""
    rng = np.random.default_rng(seed)
    N = len(radii)
    x = x0.copy()
    cap = 1 - radii                       # max |center|
    samples = []
    contacts = []
    step = step0
    acc_hist = []
    ang0 = math.atan2(x[0, 1], x[0, 0])
    for sw in range(sweeps):
        acc = 0
        for i in rng.permutation(N):
            prop = x[i] + rng.normal(0, step, 2)
            if prop @ prop > cap[i] ** 2:
                continue
            d = x - prop
            d[i] = 1e9
            rr = radii + radii[i]
            if (np.einsum('ij,ij->i', d, d) < rr * rr).any():
                continue
            x[i] = prop
            acc += 1
        acc_hist.append(acc / N)
        # adapt step
        if sw % 50 == 49:
            a = np.mean(acc_hist[-50:])
            step *= 1.25 if a > 0.55 else (0.8 if a < 0.25 else 1.0)
            step = min(max(step, 5e-4), 0.02)
        # gauge: Procrustes — rotate to best-align with the initial config
        cross = float(np.sum(x0[:, 0] * x[:, 1] - x0[:, 1] * x[:, 0]))
        dot = float(np.sum(x0[:, 0] * x[:, 0] + x0[:, 1] * x[:, 1]))
        da = -math.atan2(cross, dot)
        ca, sa = math.cos(da), math.sin(da)
        x = x @ np.array([[ca, sa], [-sa, ca]])
        if sw % SAMPLE_EVERY == 0:
            samples.append(x.copy())
            # near contacts
            for i in range(N):
                for j in range(i + 1, N):
                    dd = np.hypot(*(x[i] - x[j])) - (radii[i] + radii[j])
                    if dd < 8e-4:
                        t = radii[i] / (radii[i] + radii[j])
                        contacts.append(x[i] + (x[j] - x[i]) * t)
                ddt = (1 - radii[i]) - np.hypot(*x[i])
                if ddt < 8e-4:
                    contacts.append(x[i] * (1 + (radii[i] + ddt) / (np.hypot(*x[i]) + 1e-12)))
    return np.array(samples), np.array(contacts) if contacts else np.zeros((0, 2))


def main():
    radii = radii_of(MULTISET)
    N = len(radii)
    print("multiset", MULTISET, "N =", N, "area =", np.pi * (radii ** 2).sum())

    # find the jammed local max (best over restarts)
    smax, xjam, locs = best_s(radii, restarts=250, seed=42)
    print(f"s_max = {smax:.9f}  slack = {smax-1:.3e}")
    assert smax > 1

    # start MCMC from the jam config (feasible at s=1 with slack)
    samples, cts = mcmc(radii, xjam.copy(), SWEEPS, seed=3)
    print(f"samples {len(samples)}, near-contact events {len(cts)}")

    # flex verification at a dense-contact config: strict first-order flex exists
    cd = contact_data(xjam, radii * smax / 1.0000001, tol=1e-6)
    tflex, _ = first_order_flex(xjam, radii * smax, cd)
    print(f"at jammed config (scaled radii): contacts={len(cd)}, strict flex LP t={tflex:.3e}")

    # rattle area per coin (MC hull estimate): std-ellipse area proxy
    areas = []
    for i in range(N):
        pts = samples[:, i, :]
        cov = np.cov(pts.T)
        areas.append(np.pi * np.sqrt(max(np.linalg.det(cov), 0)) * 4)
    order = np.argsort(radii)[::-1]

    # ---------------- render ----------------
    cv = Canvas(FINAL, FINAL, ss=SS)
    cx = FINAL * SS * 0.385
    cy = FINAL * SS * 0.475
    R = FINAL * SS * 0.335

    # tray
    draw_ring(cv, cx, cy, R, PAL[-1], amp=0.9, width=1.3 * SS)

    # fog: per-coin center density, half-res bincount
    HW = FINAL * SS // 2
    for i in range(N):
        p = int(round(1 / radii[i]))
        col = PAL[p]
        pts = samples[:, i, :]
        xs = (cx + pts[:, 0] * R) / 2
        ys = (cy + pts[:, 1] * R) / 2
        h = np.zeros((HW, HW), np.float32)
        xi = np.clip(xs.astype(int), 0, HW - 1)
        yi = np.clip(ys.astype(int), 0, HW - 1)
        np.add.at(h, (yi, xi), 1.0)
        h = gaussian_filter(h, 2.2)
        h /= h.max() + 1e-12
        h = h ** 0.62                       # lift the tails
        big = np.kron(h, np.ones((2, 2), np.float32))
        amp = 1.5 if p == 5 else 1.05
        for c in range(3):
            cv.buf[..., c] += big * col[c] * amp * 0.5

    # faint glass fills
    from render import draw_disc
    for i in range(N):
        p = int(round(1 / radii[i]))
        m = samples[:, i, :].mean(0)
        draw_disc(cv, cx + m[0] * R, cy + m[1] * R, radii[i] * R, PAL[p],
                  amp=0.028)

    # dwell-density rim bands: every 5th sampled rim accumulated — the band's
    # width IS the local rattle amplitude, its brightness the dwell measure
    sub = samples[::5]
    for i in range(N):
        p = int(round(1 / radii[i]))
        col = PAL[p]
        acc = Canvas(FINAL, FINAL, ss=SS)      # reuse structure for one layer
        for k in range(len(sub)):
            x, y = sub[k, i]
            draw_ring(acc, cx + x * R, cy + y * R, radii[i] * R,
                      (1.0, 1.0, 1.0), amp=1.0, width=0.8 * SS)
        lay = acc.buf[..., 0]
        lay /= (lay.max() + 1e-9)
        lay = lay ** 0.6
        boost = 1.5 if p == 5 else 1.0
        for c in range(3):
            cv.buf[..., c] += lay * col[c] * 1.15 * boost
        del acc

    # near-contact sparks
    if len(cts):
        splat_points(cv, cx + cts[:, 0] * R, cy + cts[:, 1] * R,
                     np.full(len(cts), 0.007 * SS), (1.0, 0.9, 0.6),
                     sigma_px=0.9 * SS)

    # the jammed skeleton: the same coins rigid in the tray shrunk by 1/smax
    draw_ring(cv, cx, cy, R / smax, (1.0, 0.85, 0.45), amp=0.4,
              width=1.0 * SS)
    for i in range(N):
        x, y = xjam[i] / smax
        draw_ring(cv, cx + x * R, cy + y * R, radii[i] * R, (1.0, 0.85, 0.45),
                  amp=0.28, width=1.0 * SS)

    # ---------------- displacement roses (magnified) ----------------
    # pick: the 1/2, the loosest 1/4, the loosest 1/5
    picks = []
    for target in (0.5, 0.25, 0.2):
        cand = [i for i in range(N) if abs(radii[i] - target) < 1e-9]
        picks.append(max(cand, key=lambda i: areas[i]))
    rose_R = FINAL * SS * 0.105
    rose_x = FINAL * SS * 0.855
    rose_ys = [FINAL * SS * (0.22 + 0.28 * k) for k in range(3)]
    frac = {0.5: "½", 0.25: "¼", 0.2: "⅕"}
    for k, i in enumerate(picks):
        pts = samples[:, i, :] - samples[:, i, :].mean(0)
        rms = np.sqrt((pts ** 2).sum(1).mean())
        mag = 0.62 * rose_R / (3 * rms)
        p = int(round(1 / radii[i]))
        col = PAL[p]
        # frame
        draw_ring(cv, rose_x, rose_ys[k], rose_R, (0.4, 0.42, 0.5),
                  amp=0.5, width=1.0 * SS)
        xs = rose_x + pts[:, 0] * mag
        ys = rose_ys[k] + pts[:, 1] * mag
        keep = (xs - rose_x) ** 2 + (ys - rose_ys[k]) ** 2 < (0.94 * rose_R) ** 2
        splat_points(cv, xs[keep], ys[keep],
                     np.full(int(keep.sum()), 0.38 * SS), col, sigma_px=2.0 * SS)
        # leader line from the coin to its rose
        ci = samples[:, i, :].mean(0)
        p0 = np.array([cx + ci[0] * R, cy + ci[1] * R])
        p1 = np.array([rose_x - rose_R * 1.12, rose_ys[k]])
        draw_segment(cv, p0, p1, (0.35, 0.37, 0.45), amp=0.30, width=1.0 * SS)
        labels_extra = getattr(main, "_rose_labels", [])
        labels_extra.append((rose_x, rose_ys[k] + rose_R + 26 * rs * SS,
                             f"{frac[radii[i]]}  ·  wander ×{mag/(R):.0f}"))
        main._rose_labels = labels_extra

    bloom(cv, 26 * rs * SS, 0.9)
    img = to_img(cv, k=1.35)

    # ---------------- text ----------------
    draw = ImageDraw.Draw(img)
    fdir = "/usr/share/fonts/truetype/dejavu/"
    def F(sz, bold=False):
        return ImageFont.truetype(fdir + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
                                  max(int(sz * rs), 8))
    draw.text((FINAL // 2, int(70 * rs)), "THE RATTLE", font=F(46, True),
              fill=(210, 214, 224), anchor="mm")
    draw.text((FINAL // 2, int(112 * rs)),
              "positions without difference", font=F(24),
              fill=(130, 134, 146), anchor="mm")
    for (lx, ly, txt) in getattr(main, "_rose_labels", []):
        draw.text((lx / SS, ly / SS), txt, font=F(22), fill=(140, 144, 156),
                  anchor="mm")
    sub = (f"coins ½, three ⅓, ¼ and three ⅕ in the unit tray — they fit, with slack {smax-1:.1e} — "
           f"and so they are never held: {len(samples)} configurations, all feasible, none distinguishable. "
           f"gold: the tray smaller by {(1-1/smax):.2e} in which the same coins jam rigid.")
    draw.text((FINAL // 2, FINAL - int(74 * rs)), sub, font=F(21),
              fill=(120, 124, 136), anchor="mm")

    out = "rattle_proto.png" if PROTO else "the_rattle_2560.png"
    img.save(out)
    print("saved", out)
    json.dump({"multiset": list(MULTISET), "s_max": smax,
               "slack": smax - 1, "n_samples": len(samples),
               "flex_lp": tflex, "rattle_areas": list(map(float, areas))},
              open("rattle_stats.json", "w"))


if __name__ == "__main__":
    main()
