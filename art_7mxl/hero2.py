"""HERO v2: 'The Casting Vote' — nightscape of the Fibonacci-sum parliament.

Ground: skyline over n = 1..987; column height = log10 per(n) (number of
permutations with every i+pi(i) Fibonacci); colour by det M_n:
ember-gold +1, ice -1, dim slate 0 (the tied parliaments). Water below the
baseline reflects. per(n)=1 chasms marked by a lone star at the floor.
Sky: the self-similar law — rows k = Fibonacci blocks [F_k, F_{k+1}) of the
FULL census to 28656, sparks at relative position for det != 0, coloured by
sign: the aurora of the Zeckendorf automaton.
"""
import numpy as np
import pickle
import sys
import math
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, zoom

S = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS = 2
W = H = S * SS
rs = S / 1024.0

NMAX = 987
Y_HORIZON = 0.780   # baseline (water line) as fraction of H
Y_TOP_SKYLINE = 0.315  # top of tallest column
SKY_LO, SKY_HI = 0.045, 0.68   # aurora band (rows live here, upper part)

pers = pickle.load(open("pers1597.pkl", "rb"))
dets = pickle.load(open("dets28656.pkl", "rb"))

FIB = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597,
       2584, 4181, 6765, 10946, 17711, 28657]

C_GOLD = np.array([1.00, 0.78, 0.30])
C_ICE = np.array([0.42, 0.72, 1.00])
C_SLATE = np.array([0.34, 0.36, 0.46])
C_HAZE = np.array([0.55, 0.48, 0.62])


def splat_pts(buf, xs, ys, ws):
    h, w = buf.shape[:2]
    x0 = np.floor(xs).astype(np.int64)
    y0 = np.floor(ys).astype(np.int64)
    fx = xs - x0
    fy = ys - y0
    for dx, dy, wt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                       (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xi = x0 + dx
        yi = y0 + dy
        ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
        if buf.ndim == 2:
            np.add.at(buf, (yi[ok], xi[ok]), ws[ok] * wt[ok])


def main():
    rng = np.random.default_rng(20260801)
    # separate colour-family buffers
    b_gold = np.zeros((H, W), np.float32)
    b_ice = np.zeros((H, W), np.float32)
    b_slate = np.zeros((H, W), np.float32)
    b_star = np.zeros((H, W), np.float32)
    b_sky_g = np.zeros((H, W), np.float32)
    b_sky_i = np.zeros((H, W), np.float32)
    b_pillar = np.zeros((H, W), np.float32)

    x_lo, x_hi = 0.045 * W, 0.965 * W
    colw = (x_hi - x_lo) / NMAX
    logmax = math.log10(float(pers[NMAX]))
    y0 = Y_HORIZON * H
    ytop = Y_TOP_SKYLINE * H

    def xpos(n):
        return x_lo + (n - 0.5) * colw

    def ycol(lp):
        return y0 - (lp / logmax) * (y0 - ytop)

    # ---- skyline columns
    for n in range(1, NMAX + 1):
        lp = math.log10(float(pers[n])) if pers[n] > 0 else 0.0
        d = dets[n]
        buf = b_gold if d > 0 else (b_ice if d < 0 else b_slate)
        yc = ycol(lp)
        x = xpos(n)
        npts = max(6, int((y0 - yc) / (1.1)))
        ys = np.linspace(yc, y0, npts)
        # column body: brightest at cap, fading to base; det!=0 brighter
        base_w = 1.0 if d != 0 else 0.42
        grad = np.linspace(1.0, 0.35, npts)
        xs = np.full(npts, x)
        # slight width: 3 sub-strands
        for off in (-0.30, 0.0, 0.30):
            splat_pts(buf, xs + off * colw, ys, base_w * grad * 0.5)
        # cap spark
        capw = 5.0 if d != 0 else 1.4
        th = rng.normal(size=(2, 60))
        splat_pts(buf, x + th[0] * 0.9 * rs * SS,
                  yc + th[1] * 0.9 * rs * SS, np.full(60, capw / 60 * 4))
        # water reflection (dimmer, stretched, blur later)
        yr = y0 + (y0 - ys) * 0.32
        for off in (-0.30, 0.0, 0.30):
            splat_pts(buf, xs + off * colw, yr, base_w * grad * 0.13)
        # lone-voice chasm: per == 1
        if pers[n] == 1 and n > 1:
            th = rng.normal(size=(2, 5000))
            splat_pts(b_star, x + th[0] * 2.6 * rs * SS,
                      y0 - 4 * rs * SS + th[1] * 2.6 * rs * SS,
                      np.full(5000, 0.012))

    # ---- Fibonacci pillars on the ground axis
    for f in FIB:
        if f > NMAX:
            break
        x = xpos(f)
        ys = np.linspace(ytop - 0.06 * H, y0 + 0.10 * H, 800)
        splat_pts(b_pillar, np.full(800, x), ys, np.full(800, 0.010))

    # ---- skyline silhouette (for aurora clipping)
    xs_cols = np.array([xpos(n) for n in range(1, NMAX + 1)])
    ys_cols = np.array([ycol(math.log10(float(pers[n])) if pers[n] > 0
                             else 0.0) for n in range(1, NMAX + 1)])
    xgrid = np.arange(W, dtype=np.float64)
    sil_top = np.interp(xgrid, xs_cols, ys_cols,
                        left=y0, right=ys_cols[-1])

    def behind(xs, ys, margin=10 * rs * SS):
        idx = np.clip(xs.astype(np.int64), 0, W - 1)
        return np.where(ys < sil_top[idx] - margin, 1.0, 0.10)

    # ---- aurora sky: Fibonacci blocks of the full census
    KMIN, KMAX = 7, 21  # blocks [F_k, F_{k+1})  (1-indexed into FIB)
    nrows = KMAX - KMIN + 1
    b_thread = np.zeros((H, W), np.float32)
    for ki, k in enumerate(range(KMAX, KMIN - 1, -1)):
        flo, fhi = FIB[k - 1], FIB[k]
        fr = ki / (nrows - 1)          # 0 = KMAX (bottom) .. 1 = KMIN (top)
        yrow = (SKY_LO + (SKY_HI - SKY_LO) * (1 - fr) ** 0.80) * H
        nz = [(n, dets[n]) for n in range(flo, fhi) if dets[n] != 0]
        if not nz:
            continue
        # faint continuous row thread
        tx = np.arange(int(x_lo), int(x_hi), 2)
        tw = np.full(len(tx), 0.028) * behind(tx.astype(np.float64),
                                              np.full(len(tx), yrow))
        splat_pts(b_thread, tx.astype(np.float64),
                  np.full(len(tx), yrow), tw)
        ink = 30.0 / max(len(nz), 1)  # equal ink per row
        for n, d in nz:
            rel = (n - flo) / (fhi - flo)
            x = x_lo + rel * (x_hi - x_lo)
            buf = b_sky_g if d > 0 else b_sky_i
            up = 1.0 if d > 0 else -1.0
            m = 34
            ys = yrow - up * np.abs(rng.normal(size=m)) * 3.4 * rs * SS
            xs = x + rng.normal(size=m) * 0.45 * rs * SS
            fac = behind(xs, ys)
            splat_pts(buf, xs, ys, np.full(m, ink / m * 28) * fac)

    # ---- golden meridians + forbidden haze in the sky band
    y_sky_top = (SKY_LO + 0.0) * H
    y_sky_bot = (SKY_LO + (SKY_HI - SKY_LO)) * H + 0.012 * H
    PHI = (1 + 5 ** 0.5) / 2
    for relm, wgt in ((1 / PHI ** 4, 0.050), (1 / PHI ** 2, 0.082)):
        xm = x_lo + relm * (x_hi - x_lo)
        ysm = np.linspace(y_sky_top, y_sky_bot, 900)
        fac = behind(np.full(900, xm), ysm)
        splat_pts(b_pillar, np.full(900, xm), ysm, np.full(900, wgt * 2.2) * fac)
    # cold haze over the forbidden golden section (rel > 1/phi^2)
    x_f = x_lo + (x_hi - x_lo) / PHI ** 2
    xx = np.arange(W, dtype=np.float32)[None, :]
    yy2 = np.arange(H, dtype=np.float32)[:, None]
    hz = (1.0 / (1.0 + np.exp(-(xx - x_f) / (14 * rs * SS))))
    vert = np.where(yy2 > y_sky_bot,
                    np.clip(1 - (yy2 - y_sky_bot) / (0.05 * H), 0, 1),
                    1.0)
    haze = (hz * vert).astype(np.float32) * 0.085
    # keep haze out of the mountain: multiply by behind-factor per pixel
    behind_px = (yy2 < sil_top[None, :] - 10 * rs * SS)
    haze *= np.where(behind_px, 1.0, 0.10).astype(np.float32)
    # fade at the right frame edge and outside the plot span
    edge = np.clip((x_hi + 0.01 * W - xx) / (0.025 * W), 0, 1) *         np.clip((xx - x_lo) / (0.05 * W), 0, 1)
    haze *= edge.astype(np.float32)

    # ---- compose
    img = np.zeros((H, W, 3), np.float32)

    def nz_pct(a, p):
        m = a[a > 1e-9]
        return np.percentile(m, p) if len(m) else 1.0

    def tone(x, k, g):
        return np.power(np.clip(1 - np.exp(-k * x), 0, 1), g)

    # gentle blur of water region
    water = slice(int(y0) + int(2 * rs * SS), H)
    for b in (b_gold, b_ice, b_slate):
        b[water] = gaussian_filter(b[water], (4.5 * rs, 1.6 * rs)) * 0.75

    sky_blur = (0.9 * rs, 0.9 * rs)
    b_sky_g[:] = gaussian_filter(b_sky_g, sky_blur)
    b_sky_i[:] = gaussian_filter(b_sky_i, sky_blur)

    img += tone(b_gold / nz_pct(b_gold, 99.3), 1.8, 0.62)[..., None] * C_GOLD
    img += tone(b_ice / nz_pct(b_ice, 99.3), 1.8, 0.62)[..., None] * C_ICE
    img += tone(b_slate / nz_pct(b_slate, 99.0), 1.5, 0.68)[..., None] * C_SLATE
    img += tone(b_star / nz_pct(b_star, 99.5), 2.6, 0.60)[..., None] * C_GOLD
    img += tone(b_sky_g / nz_pct(b_sky_g, 99.0), 1.5, 0.66)[..., None] * (C_GOLD * 0.85)
    img += tone(b_sky_i / nz_pct(b_sky_i, 99.0), 1.5, 0.66)[..., None] * (C_ICE * 0.85)
    img += tone(b_pillar / nz_pct(b_pillar, 99.0), 1.6, 0.70)[..., None] * (C_HAZE * 0.5)
    img += tone(b_thread / nz_pct(b_thread, 99.0), 1.3, 0.75)[..., None] * (C_HAZE * 0.35)
    img += haze[..., None] * np.array([0.30, 0.42, 0.62])

    # horizon glow
    yy = np.arange(H)[:, None].astype(np.float32)
    glow = np.exp(-((yy - y0) / (26 * rs * SS)) ** 2) * 0.10
    img += glow[..., None] * np.array([0.45, 0.40, 0.55])

    # bloom
    lum = img.sum(2)
    thr = np.percentile(lum, 99.3)
    mask = np.clip(lum - thr, 0, None)[..., None] * img / (lum[..., None] + 1e-9)
    ds = max(1, int(6 * rs))
    small = mask[::ds, ::ds]
    bl = gaussian_filter(small, (13 * rs / ds, 13 * rs / ds, 0))
    bloom = zoom(bl, (mask.shape[0] / small.shape[0],
                      mask.shape[1] / small.shape[1], 1), order=1)[:H, :W]
    img += 0.9 * np.clip(bloom, 0, None)

    img = np.clip(img, 0, 1)
    pil = Image.fromarray((img * 255).astype(np.uint8)).resize((S, S), Image.LANCZOS)
    arr = np.asarray(pil).astype(np.float32) / 255.0
    arr = np.clip(arr + (rng.random(arr.shape) - 0.5) / 255.0, 0, 1)
    out = Image.fromarray((arr * 255).astype(np.uint8))

    if S >= 2048:
        fs1 = int(S * 0.0120)
        fs2 = int(S * 0.0085)
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", fs1)
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fs2)
        dr = ImageDraw.Draw(out)
        y = int(0.925 * S)
        dr.text((int(0.045 * S), y), "THE CASTING VOTE", fill=(235, 208, 152), font=f1)
        cap = ("(M_n)ij = 1 iff i+j is Fibonacci (MO 513340)   ·   skyline n = 1..987: height = log10 #{permutations π with every i+π(i) Fibonacci}, "
               "0 up to 10^105   ·   gold det = +1, ice det = −1, slate det = 0")
        dr.text((int(0.045 * S), y + int(fs1 * 1.55)), cap, fill=(152, 154, 160), font=f2)
        cap2 = ("n = 97: 333,973,125 permutations — 166,986,563 even vs 166,986,562 odd: carried by ONE vote   ·   "
                "gold stars on the floor: n = 2, 3, 5, 9, 15, 24, 39, 64, 104, 168, 272, 441, 714 — a single permutation (Zeckendorf 1(0001)*)")
        dr.text((int(0.045 * S), y + int(fs1 * 2.55)), cap2, fill=(152, 154, 160), font=f2)
        cap3 = ("sky: the sign law across every n ≤ 28,656, one row per Fibonacci block [F_k, F_{k+1}) — verdicts live only in the golden window "
                "[1/φ⁴, 1/φ²] of each block (meridians); beyond the second meridian, every parliament ties: det = 0")
        dr.text((int(0.045 * S), y + int(fs1 * 3.55)), cap3, fill=(152, 154, 160), font=f2)
    out.save(f"hero2_{S}.png")
    print("saved", f"hero2_{S}.png")


if __name__ == "__main__":
    main()
