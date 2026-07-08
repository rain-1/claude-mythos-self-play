"""THE NURSERY OF NUMBERS — Conway's surreal numbers as a birthday cascade.

Day 0: a single number, 0 = { | }, born from nothing at all.
Day n: every sign-expansion of length n is a new number. Integers march
outward forever; dyadic rationals weave the interior ever finer. The days
are spaced geometrically so day omega -- where the full real continuum
(and omega itself, and the infinitesimals) is born -- is an actual line
in the image: the shoreline the whole cascade converges to.

Famous non-dyadic reals (1/3, sqrt2-1, e-2, pi-3, phi-1...) are drawn as
continuous threads: they descend through every generation but only touch
existence at the shore.

Verification: the sign-expansion value rule is checked against brute-force
{L|R} simplicity-rule birth order for all numbers born by day 6.
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (splat_points, splat_quad_bezier, bloom, filmic, save,
                 lerp_palette)
from scipy.ndimage import gaussian_filter
from fractions import Fraction


# ----------------------------------------------------------------------
# The mathematics: sign expansions and their values
# ----------------------------------------------------------------------
def children(v, mag, changed, first):
    """Vectorized: value/step-magnitude/changed-flag/first-sign arrays of one
    generation -> the two children of each node (left = minus, right = plus)."""
    outs = []
    for sgn in (-1.0, +1.0):
        # halving starts at the first sign that differs from the first sign
        newly_changed = (~changed) & (sgn != first)
        ch = changed | newly_changed
        newmag = np.where(ch, mag * 0.5, mag)  # mag stays 1 during integer march
        vv = v + sgn * newmag
        outs.append((vv, newmag, ch, first.copy()))
    return outs


def brute_force_birthdays(maxday=6):
    """Ground truth: iterate 'a number is {L|R} of earlier numbers, value =
    simplest in the gap' (Conway's simplicity rule) day by day."""
    born = [Fraction(0)]
    day = {Fraction(0): 0}
    for d in range(1, maxday + 1):
        s = sorted(born)
        new = []
        # gaps: below min, between consecutive, above max
        new.append(s[0] - 1)
        for a, b in zip(s, s[1:]):
            # simplest dyadic strictly between a and b
            new.append(simplest_between(a, b))
        new.append(s[-1] + 1)
        for x in new:
            if x not in day:
                day[x] = d
                born.append(x)
    return day


def simplest_between(a, b):
    """Simplest dyadic rational strictly between a and b (Conway simplicity)."""
    # smallest denominator 2^k that admits an integer strictly between
    k = 0
    while True:
        scale = 2 ** k
        lo = int(np.floor(float(a * scale))) + 1
        hi = int(np.ceil(float(b * scale))) - 1
        if lo <= hi:
            # integer with smallest absolute value wins (simplicity)
            cands = [lo, hi, 0]
            best = None
            for c in range(lo, hi + 1):
                if best is None or abs(c) < abs(best):
                    best = c
            return Fraction(best, scale)
        k += 1


def verify(maxday=6):
    truth = brute_force_birthdays(maxday)
    # generate via sign expansions
    got = {0.0: 0}
    v = np.array([0.0]); mag = np.array([1.0])
    ch = np.array([False]); fs = np.array([0.0])
    # day1 children of root: +1/-1, mag stays 1, first sign set
    for d in range(1, maxday + 1):
        if d == 1:
            v = np.array([-1.0, 1.0]); mag = np.array([1.0, 1.0])
            ch = np.array([False, False]); fs = np.array([-1.0, 1.0])
        else:
            (lv, lm, lc, lf), (rv, rm, rc, rf) = children(v, mag, ch, fs)
            v = np.concatenate([lv, rv]); mag = np.concatenate([lm, rm])
            ch = np.concatenate([lc, rc]); fs = np.concatenate([lf, rf])
        for x in v:
            if x not in got:
                got[x] = d
    truth_f = {float(k): dd for k, dd in truth.items()}
    assert got == truth_f, "sign-expansion values disagree with simplicity rule"
    print(f"VERIFIED: sign-expansion birth order == {{L|R}} simplicity rule "
          f"through day {maxday} ({len(truth)} numbers)")


def sign_expansion_of(x, depth):
    """Sign expansion (list of +-1) of an arbitrary real x, plus the value
    path (approximants after each sign)."""
    v, mag, changed, first = 0.0, 1.0, False, 0.0
    signs, path = [], []
    for i in range(depth):
        s = 1.0 if x > v else -1.0
        if i == 0:
            first = s
            v = v + s * mag
        else:
            if (not changed) and s != first:
                changed = True
            if changed:
                mag *= 0.5
            v = v + s * mag
        signs.append(s)
        path.append(v)
    return signs, path


# ----------------------------------------------------------------------
# The rendering
# ----------------------------------------------------------------------
def render(S=1024, SS=2, DEPTH=19, r=0.80, A=2.0,
           edge_gain=1.0, thread_gain=1.0, out="nursery_proto.png",
           k_tone=1.15, depth_decay=0.82, shore_gain=1.15, acc_blur=0.0):
    W = H = S * SS
    scl = S / 1024.0          # resolution scale: glow sizes follow the canvas
    rng = np.random.default_rng(7)

    def X(v):
        return (0.5 + 0.485 * v / (A + np.abs(v))) * W

    # day -> y pixel: geometric convergence to the shore
    y_shore = 0.845 * H
    y_top = 0.075 * H

    def Y(d):
        return y_top + (y_shore - y_top) * (1 - r ** d)

    acc = [np.zeros((H, W)) for _ in range(3)]  # rgb accumulators

    # ---- palette along depth: white-gold birth -> amber -> violet -> cyan-blue
    def depth_color(d):
        t = 1 - r ** d
        return lerp_palette(np.full(1, t), [
            (0.00, (1.00, 0.97, 0.88)),
            (0.18, (1.00, 0.82, 0.45)),
            (0.42, (0.95, 0.55, 0.30)),
            (0.65, (0.62, 0.35, 0.72)),
            (0.85, (0.30, 0.45, 0.95)),
            (1.00, (0.42, 0.75, 1.00)),
        ])[0]

    # ---- the cascade
    v = np.array([0.0]); mag = np.array([1.0])
    ch = np.array([False]); fs = np.array([0.0])
    node_days = [(np.array([0.0]), 0)]
    for d in range(DEPTH):
        if d == 0:
            nv = np.array([-1.0, 1.0]); nm = np.array([1.0, 1.0])
            nc = np.array([False, False]); nf = np.array([-1.0, 1.0])
            pv = np.array([0.0, 0.0])
        else:
            (lv, lm, lc, lf), (rv, rm, rc, rf) = children(v, mag, ch, fs)
            nv = np.concatenate([lv, rv]); nm = np.concatenate([lm, rm])
            nc = np.concatenate([lc, rc]); nf = np.concatenate([lf, rf])
            pv = np.concatenate([v, v])
        # draw edges parent(day d) -> child(day d+1) as hanging beziers
        x1 = X(pv); y1 = np.full_like(x1, Y(d))
        x2 = X(nv); y2 = np.full_like(x2, Y(d + 1))
        cx = x1 + 0.12 * (x2 - x1)
        cy = y1 + 0.75 * (y2 - y1)
        col = depth_color(d + 1)
        # per-edge mass: proportional to length so long integer-march edges
        # glow; decays with depth but the 2^d count keeps total level light up
        L = np.hypot(x2 - x1, y2 - y1)
        wgt = edge_gain * (L / (SS * 18.0) + 0.16) * (depth_decay ** d)
        for c in range(3):
            splat_quad_bezier(acc[c], x1, y1, cx, cy, x2, y2, wgt * col[c],
                              samples_per_px=1.25 / SS + 0.75)
        v, mag, ch, fs = nv, nm, nc, nf
        node_days.append((nv, d + 1))
        if (d + 1) % 5 == 0:
            print(f"  day {d+1}: {len(v)} numbers")

    # ---- birth stars for the first days (the root blazes)
    for nv, d in node_days:
        if d > 7:
            break
        col = depth_color(d)
        amp = 3.0 * (0.55 ** d) * edge_gain
        xs = X(nv); ys = np.full_like(xs, Y(d))
        for c in range(3):
            g = np.zeros_like(acc[0])
            splat_points(g, xs, ys, np.full_like(xs, amp))
            acc[c] += gaussian_filter(g, 1.9 * SS * scl) * (1.9 * SS * scl) ** 2 * 6.28 * col[c] * 0.05

    # ---- the integer spine marches on to omega: continue the real edges
    # n -> n+1 (day n -> n+1) far beyond DEPTH, fading toward the shore glow
    n_ext = np.arange(DEPTH, 4000, dtype=np.float64)
    for sgn in (-1.0, 1.0):
        xs1 = X(sgn * n_ext); ys1 = Y(n_ext)
        xs2 = X(sgn * (n_ext + 1)); ys2 = Y(n_ext + 1)
        keep = np.hypot(xs2 - xs1, ys2 - ys1) > 0.15
        if keep.sum() == 0:
            continue
        Lx = np.hypot(xs2 - xs1, ys2 - ys1)[keep]
        wsp = edge_gain * (Lx / (SS * 18.0) + 0.16) * (depth_decay ** 13) \
            * np.linspace(1.0, 0.30, keep.sum())
        colsp = np.array([1.0, 0.85, 0.55])
        from kit import splat_segments
        for c in range(3):
            splat_segments(acc[c], xs1[keep], ys1[keep], xs2[keep], ys2[keep],
                           wsp * colsp[c], samples_per_px=1.4)

    # soften the cascade weave into a GRADED fog: sharp filigree up top,
    # dissolving toward the shore where generations pass below pixel scale
    if acc_blur > 0:
        yy_col = np.arange(H)[:, None]

        def smoothstep(a, b, x):
            t = np.clip((x - a) / (b - a), 0, 1)
            return t * t * (3 - 2 * t)

        extra = np.log2((S * SS) / 2048.0)  # fog starts deeper at higher res
        w2 = smoothstep(Y(12 + extra), Y(19 + extra), yy_col)            # deep fog
        w1 = smoothstep(Y(7.5 + extra), Y(13 + extra), yy_col) * (1 - w2)  # mid haze
        w0 = 1 - w1 - w2
        for c in range(3):
            b1 = gaussian_filter(acc[c], 1.1 * SS * scl ** 0.7)
            b2 = gaussian_filter(acc[c], 2.8 * SS * scl ** 0.7)
            sharp = gaussian_filter(acc[c], acc_blur * SS * scl ** 0.3)
            acc[c] = w0 * sharp + w1 * b1 + w2 * b2
    # arrival density of the CASCADE ONLY (threads/pegs must not hijack the max)
    cascade_sum = acc[0] + acc[1] + acc[2]

    # ---- famous latecomer threads (born only at day omega)
    latecomers = [
        (1 / 3, (1.00, 0.45, 0.22)),                  # ember
        (np.sqrt(2) - 1, (1.00, 0.60, 0.25)),
        (np.e - 2, (1.00, 0.38, 0.30)),
        (np.pi - 3, (1.00, 0.52, 0.18)),
        ((np.sqrt(5) - 1) / 2, (1.00, 0.68, 0.30)),   # phi - 1
        (-1 / 3, (1.00, 0.45, 0.22)),
        (-(np.e - 2), (1.00, 0.38, 0.30)),
        (np.log(2), (1.00, 0.55, 0.35)),
        (-(np.sqrt(3) - 1), (1.00, 0.48, 0.25)),
    ]
    THREAD_DEPTH = max(DEPTH + 14, 34)
    for xval, col in latecomers:
        _, path = sign_expansion_of(xval, THREAD_DEPTH)
        pts = [(X(np.array([0.0]))[0], Y(0))]
        for i, pv_ in enumerate(path):
            pts.append((X(np.array([pv_]))[0], Y(i + 1)))
        pts.append((X(np.array([xval]))[0], y_shore))
        pts = np.array(pts)
        # smooth polyline -> bezier chain
        x1 = pts[:-1, 0]; y1 = pts[:-1, 1]
        x2 = pts[1:, 0]; y2 = pts[1:, 1]
        cx = x1; cy = 0.5 * (y1 + y2)
        wgt = thread_gain * (np.hypot(x2 - x1, y2 - y1) / (SS * 6.0) + 0.34 * scl)
        colv = np.array(col)
        for c in range(3):
            splat_quad_bezier(acc[c], x1, y1, cx, cy, x2, y2, wgt * colv[c],
                              samples_per_px=1.4)
        # the number is finally BORN at the shore: a bright peg
        g = np.zeros_like(acc[0])
        splat_points(g, np.array([X(np.array([xval]))[0]]),
                     np.array([y_shore]), np.array([thread_gain * 2.4]))
        g = gaussian_filter(g, 1.8 * SS * scl) * (1.8 * SS * scl) ** 2 * 6.28
        for c in range(3):
            acc[c] += g * colv[c] * 0.35

    rgb = np.stack(acc, axis=-1)

    # ---- the shore: horizontal glow where the continuum is born
    shore = np.zeros((H, W))
    yy = np.arange(H)[:, None]
    band = np.exp(-((yy - y_shore) / (2.4 * SS * scl)) ** 2)
    # shore brightness follows the arrival density of the cascade itself
    arrive = gaussian_filter(cascade_sum, 3 * SS)
    arr_row = arrive[int(y_shore) - 6 * SS:int(y_shore) - 1 * SS, :].mean(axis=0)
    arr_row = gaussian_filter(arr_row, 2.0 * SS)
    arr_row = arr_row / (arr_row.max() + 1e-12)
    arr_row = arr_row ** 0.6
    shore = band * arr_row[None, :]
    shore_col = np.array([0.75, 0.88, 1.0])
    rgb += shore_gain * shore[..., None] * shore_col[None, None, :]

    # ---- below the shore: the sea of the continuum — a dim reflection of the
    # whole cascade (the tree gazing into what it converges to), plus the
    # mist of infinitesimals hugging the shoreline
    ys_i = int(y_shore)
    refl = gaussian_filter(rgb, (4.0 * SS * scl, 1.2 * SS * scl, 0))
    rows_below = np.arange(ys_i + 1, H)
    src = 2 * ys_i - rows_below
    ok = (src >= 0) & (src < H)
    fade = np.exp(-(rows_below - ys_i) / (0.09 * H))
    rgb[rows_below[ok]] += (0.22 * fade[ok, None, None]
                            * refl[src[ok]] * np.array([0.55, 0.75, 1.0]))
    mist = np.exp(-np.clip((yy - y_shore), 0, None) / (0.035 * H)) * (yy > y_shore)
    rgb += 0.10 * mist[..., None] * arr_row[None, :, None] * shore_col[None, None, :]
    for sgn in (-1, 1):
        xo = 0.5 * W + sgn * 0.492 * W
        gx = np.exp(-((np.arange(W) - xo) / (9.0 * SS * scl)) ** 2)
        gy = np.exp(-((np.arange(H) - y_shore) / (7.0 * SS * scl)) ** 2)
        rgb += 2.2 * (gy[:, None] * gx[None, :])[..., None] * np.array([1.0, 0.85, 0.55])[None, None, :]

    rgb = bloom(rgb, sigma=2.5 * SS * scl, amount=0.30, thresh=0.55)
    rgb = filmic(rgb, k=k_tone, gamma=0.88)
    save(rgb, out, down=SS)
    print("saved", out)


if __name__ == "__main__":
    verify(6)
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--size", type=int, default=1024)
    p.add_argument("--ss", type=int, default=2)
    p.add_argument("--depth", type=int, default=19)
    p.add_argument("--out", default="nursery_proto.png")
    a = p.parse_args()
    render(S=a.size, SS=a.ss, DEPTH=a.depth, out=a.out)
