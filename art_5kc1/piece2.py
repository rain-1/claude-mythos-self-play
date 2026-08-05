#!/usr/bin/env python3
"""THE SCALE MODEL — 2560^2.  MO 513938.
phi_a : j -> q_j = (a^j - 1)/2^v2(a-1), odd j.  Theorem (one line of LTE):
|q_x - q_y|_2 = 2^-(beta-1) |x - y|_2,  beta = v2(a+1) — a 2-adic SIMILARITY.
Image of the odd ball = the single ball q_1 + 2^beta Z_2 (radius 2^-beta).
Chart: Monna map (bit-reversal) on both axes.  x = Monna(odd j), y = Monna(q_j
mod 2^R).  The image is ONE horizontal strip of height exactly 2^-beta placed at
the Monna address of q_1; inside, the carpet is a self-affine spectral weave.
Six worlds: a = 5 (beta=1, isometry) then a = 3, 7, 15, 31, 63 (beta = 2..6):
each panel's lit country is half as tall as the one before."""
import sys, numpy as np
from artlib import canvas, star, bloom, tonemap, save, bake_text, _splat_points, polyline

PREVIEW = "--preview" in sys.argv
S = 1024 if PREVIEW else 2560
SS = 1 if PREVIEW else 2
R = S * SS
rs = R / 1024.0
rng = np.random.default_rng(7)
buf = canvas(R)

C_GOLD = np.array([1.00, 0.78, 0.30])
C_ICE  = np.array([0.55, 0.88, 1.00])
C_DIM  = np.array([0.30, 0.40, 0.60])

TB = 17              # j over odd residues mod 2^TB -> 2^(TB-1) = 32768 points/panel
RB = 30              # y resolution bits

def monna_frac(vals, bits):
    """bit-reversal to [0,1): value b0 + b1*2 + ... -> b0/2 + b1/4 + ..."""
    v = np.asarray(vals, np.uint64).copy()
    out = np.zeros(len(v), np.float64)
    f = 0.5
    for _ in range(bits):
        out += (v & 1) * f
        v >>= np.uint64(1)
        f *= 0.5
    return out

def qvals(a, TB, RB):
    al = ((a - 1) & -(a - 1)).bit_length() - 1     # v2(a-1)
    M = 1 << (RB + al)
    js = np.arange(1, 1 << TB, 2, dtype=np.int64)
    # pow chain: a^j mod M for odd j: a^1, then multiply by a^2 each step
    qs = np.empty(len(js), np.uint64)
    cur = a % M
    step = pow(a, 2, M)
    mask = (1 << RB) - 1
    for i in range(len(js)):
        qs[i] = ((cur - 1) >> al) & mask
        cur = (cur * step) % M
    return js, qs

panels = [5, 3, 7, 15, 31, 63]
marg = 0.052
pw = (1.0 - 4 * marg) / 3.0          # 3 cols
ph = pw
row_y = [0.185, 0.185 + ph + 0.105]
col_x = [marg, 2 * marg + pw, 3 * marg + 2 * pw]

# spectral ramp gold->rose->ice for x-position hue
def ramp(t):
    t = np.asarray(t)[..., None]
    c0 = np.array([1.00, 0.72, 0.25]); c1 = np.array([0.95, 0.45, 0.40])
    c2 = np.array([0.55, 0.60, 0.95]); c3 = np.array([0.45, 0.90, 1.00])
    seg = np.clip(t * 3, 0, 3)
    out = np.where(seg < 1, c0 + (c1 - c0) * seg,
          np.where(seg < 2, c1 + (c2 - c1) * (seg - 1), c2 + (c3 - c2) * (seg - 2)))
    return out

texts = []
fsS = S / 1024.0
law_checked = 0
for pi, a in enumerate(panels):
    r_, c_ = divmod(pi, 3)
    x0, y0 = col_x[c_] * R, row_y[r_] * R
    W = pw * R
    be = ((a + 1) & -(a + 1)).bit_length() - 1     # v2(a+1)
    sh = be - 1
    js, qs = qvals(a, TB, RB)
    # verify the law on random pairs inside this panel (live tripwire)
    for _ in range(200):
        i1, i2 = rng.integers(0, len(js), 2)
        if i1 == i2: continue
        d = int(qs[i1]) - int(qs[i2])
        v2d = ((d & -d).bit_length() - 1) if d % (1 << RB) else RB
        dj = int(js[i1] - js[i2]); v2j = (dj & -dj).bit_length() - 1
        want = v2j + sh
        assert v2d == want or want >= RB, (a, js[i1], js[i2], v2d, want)
        law_checked += 1
    mx = monna_frac((js >> 1), TB - 1)             # odd j -> index (j-1)/2
    my = monna_frac(qs, RB)
    # ghost frame = the full unit square (the country before the map)
    fr = np.array([[x0, y0], [x0 + W, y0], [x0 + W, y0 + W], [x0, y0 + W]])
    polyline(buf, np.vstack([fr, fr[:1]]), C_DIM, amp=0.09 * rs)
    # the strip the theorem allows: y in [Monna(q1 ball address), +2^-be)
    q1 = int(qs[0])
    strip_y0 = monna_frac([q1 & ((1 << be) - 1)], be)[0]
    ys0, ys1 = y0 + strip_y0 * W, y0 + (strip_y0 + 2.0 ** (-be)) * W
    # soft strip wash
    iy0, iy1 = int(ys0), max(int(ys0) + 1, int(ys1))
    buf[iy0:iy1, int(x0):int(x0 + W)] += (0.028 * np.array([0.16, 0.30, 0.44], np.float32))
    for yv in (ys0, ys1):
        xs = np.linspace(x0, x0 + W, int(W / rs))
        _splat_points(buf, xs, np.full_like(xs, yv), 0.05 * rs, C_ICE * 0.8, 1)
    # the carpet: points colored by x-position spectral ramp
    px = x0 + mx * W
    py = y0 + my * W
    cols = ramp(mx)
    # per-panel ink normalization: strip is 2^-be of the square; keep total light equal
    strip_px = (W / rs) * (W / rs) * 2.0 ** (-be)   # strip area in proto px
    amp = 0.85 * rs * strip_px / len(js)
    # true per-point colored splat (chunked to keep memory sane)
    CH = 8192
    for s0 in range(0, len(px), CH):
        sl = slice(s0, s0 + CH)
        c3 = cols[sl]
        for ci in range(3):
            _splat_points(buf, px[sl], py[sl], amp * c3[:, ci], np.array([1., 0, 0]) if ci == 0 else (np.array([0, 1., 0]) if ci == 1 else np.array([0, 0, 1.])), 1)
    # labels
    texts.append(((x0 + 0.5 * W) / R, (y0 - 30 * rs) / R,
                  f"a = {a}     beta = v2(a+1) = {be}     ratio 1 : 2^{sh}" if sh else f"a = {a}     beta = 1     ISOMETRY (ratio 1:1)",
                  13, (0.72, 0.76, 0.86), False, "mm"))
    texts.append(((x0 + 0.5 * W) / R, (y0 + W + 16 * rs) / R,
                  f"the whole image: one ball, height 2^-{be}", 11, (0.5, 0.75, 0.9), False, "mm"))

buf = bloom(buf, sigmas=(1.6 * rs, 6 * rs, 20 * rs), weights=(1.0, 0.35, 0.16), thresh=0.62)
img = tonemap(buf, k=1.5, gamma=0.94)
if SS > 1:
    from PIL import Image
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((S, S), Image.LANCZOS)
    img = np.asarray(im).astype(np.float32) / 255.0

heads = [
    (0.040, 0.028, "THE SCALE MODEL", 30, (0.93, 0.88, 0.78), True, "la"),
    (0.040, 0.066, "j  ->  q_j = (a^j - 1) / 2^v2(a-1)   on odd j:   |q_x - q_y|_2  =  2^-(beta-1) |x-y|_2,   beta = v2(a+1)",
     14, (0.62, 0.66, 0.78), False, "la"),
    (0.040, 0.092, "the normalized Lucas map redraws the odd integers as a perfect scale model - each panel: Monna chart of the graph;",
     12, (0.52, 0.56, 0.68), False, "la"),
    (0.040, 0.112, "the lit country is ONE 2-adic ball, and it is half as tall each time beta climbs   -   MO 513938, verified + proved via LTE",
     12, (0.52, 0.56, 0.68), False, "la"),
    (0.960, 0.966, f"x = Monna(j),  y = Monna(q_j mod 2^{RB}),  {1 << (TB - 1)} odd j per panel;  hue = position of j", 11, (0.5, 0.54, 0.66), False, "ra"),
]
T = [(hx * S, hy * S, s_, int(sz * fsS), col, b, an) for (hx, hy, s_, sz, col, b, an) in heads]
T += [(tx * S, ty * S, s_, int(sz * fsS), col, b, an) for (tx, ty, s_, sz, col, b, an) in texts]
img = bake_text(img, T, S)
out = "piece2_preview.png" if PREVIEW else "scale_model_2560.png"
save(img, out, dither=True)
print("saved", out, "| law checks:", law_checked)
