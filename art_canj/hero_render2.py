"""HERO 4096x4096 — THE CROWN AND THE WOUND
Left pyramid:  Z_127 (Mersenne prime) — every proper window's clearance from
               divisibility; the crown stands with no zero anywhere.
Right pyramid: Z_63 (composite Mersenne number) — same object, wounded at
               prefix lengths exactly {3,7,9,21} = the divisors of 63.
Materials: even interior windows = steel-blue fabric (clearance 1/2);
odd interior = ember rising to gold (clearance 1/L -> heat grows with L);
prefix column = cyan arithmetic stripe;  wounds = white-gold ruptures.
Below each: the zigzag itself as a glowing thread.  Bottom: the census shore
(exhaustive counts for all odd n <= 63).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SS = 2
W = H = 4096
Ws, Hs = W * SS, H * SS
buf = np.zeros((Hs, Ws, 3), np.float32)

def splat(x, y, sigma, color, amp):
    """additive gaussian in local bbox"""
    r = int(3 * sigma) + 1
    x0, y0 = int(x) - r, int(y) - r
    x1, y1 = int(x) + r + 1, int(y) + r + 1
    if x1 <= 0 or y1 <= 0 or x0 >= Ws or y0 >= Hs:
        return
    xa, ya = max(x0, 0), max(y0, 0)
    xb, yb = min(x1, Ws), min(y1, Hs)
    gy = np.arange(ya, yb) - y
    gx = np.arange(xa, xb) - x
    g = np.exp(-(gy[:, None] ** 2 + gx[None, :] ** 2) / (2 * sigma ** 2))
    for k in range(3):
        buf[ya:yb, xa:xb, k] += amp * color[k] * g

def soft_rect(xc, yc, wx, wy, color, amp):
    """soft-edged rectangle splat (separable smoothstep profile)"""
    pad = int(max(wx, wy) * 0.8) + 2
    x0, y0 = int(xc - wx / 2 - pad), int(yc - wy / 2 - pad)
    x1, y1 = int(xc + wx / 2 + pad) + 1, int(yc + wy / 2 + pad) + 1
    xa, ya = max(x0, 0), max(y0, 0)
    xb, yb = min(x1, Ws), min(y1, Hs)
    if xb <= xa or yb <= ya:
        return
    gx = np.arange(xa, xb) + 0.5 - xc
    gy = np.arange(ya, yb) + 0.5 - yc
    fx = np.clip((wx / 2 + wx * 0.30 - np.abs(gx)) / (wx * 0.60), 0, 1)
    fy = np.clip((wy / 2 + wy * 0.30 - np.abs(gy)) / (wy * 0.60), 0, 1)
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    g = fy[:, None] * fx[None, :]
    for k in range(3):
        buf[ya:yb, xa:xb, k] += amp * color[k] * g

def line_glow(p0, p1, color, amp, width, n_samp=None):
    d = np.hypot(p1[0] - p0[0], p1[1] - p0[1])
    if n_samp is None:
        n_samp = max(int(d / (width * 0.5)), 2)
    ts = np.linspace(0, 1, n_samp)
    for t in ts:
        splat(p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]),
              width, color, amp / n_samp * d / width * 0.7)

# ---------------- palette ----------------
BG        = np.array([0.012, 0.016, 0.030])
STEEL     = np.array([0.30, 0.48, 0.66])
EMBER     = np.array([1.00, 0.68, 0.26])
GOLD      = np.array([1.00, 0.82, 0.42])
CYAN      = np.array([0.42, 0.88, 0.94])
WOUNDC    = np.array([1.00, 0.92, 0.72])
THREAD    = np.array([1.00, 0.76, 0.34])
COLD      = np.array([0.35, 0.45, 0.60])

def constr(p):
    a = [1]
    x = p - 1
    while x >= 2:
        a += [x, x + 1]
        x -= 2
    return a

def draw_pyramid(p, x_left, x_right, y_base, y_apex, crown=True):
    T = np.load(f'hero_tri_{p}.npz')['T']
    wspan = x_right - x_left
    hspan = y_base - y_apex
    cw = wspan / p * SS_adjust           # cell pitch in x
    ch = hspan / (p - 2)
    cells = []
    for (i, L, c, pf) in T:
        i, L = int(i), int(L)
        xc = x_left + (i + L / 2.0) / p * wspan
        yc = y_base - (L - 2) / (p - 2.0) * hspan
        cells.append((xc, yc, L, c, pf))
    # interior: the weave.  even rows = steel fabric at rest (clearance 1/2);
    # odd rows = ember cells whose sum is +1 or -1 (mod L) by start parity:
    # render the ±1 alternation as a two-tone weave, heat rising with L.
    for (xc, yc, L, c, pf) in cells:
        if pf != 0:
            continue
        if abs(c - 0.5) < 1e-9:
            soft_rect(xc, yc, cw * 0.94, ch * 0.55, STEEL, 0.16 * (p / 63.0) ** 0.7)
    # need start parity: recompute from T directly
    T = np.load(f'hero_tri_{p}.npz')['T']
    for (i, L, c, pf) in T:
        i, L = int(i), int(L)
        if pf == 1 or abs(c - 0.5) < 1e-9:
            continue
        xc = x_left + (i + L / 2.0) / p * wspan
        yc = y_base - (L - 2) / (p - 2.0) * hspan
        heat = np.log(1.0 / c) / np.log(p + 2.0)
        plus = (i % 2 == 0)          # start parity -> sum ≡ +1 or −1 (mod L)
        base = EMBER if plus else EMBER * 0.34 + STEEL * 0.62
        col = base * (0.65 + 0.35 * heat) + GOLD * 0.34 * heat ** 2
        dens = (p / 63.0) ** 0.7     # ink balance across pyramid scales
        soft_rect(xc, yc, cw * 0.94, ch * 0.55, col,
                  dens * ((0.11 + 0.85 * heat ** 2.2) * (1.0 if plus else 0.62)))
    # apex crown: only for the good zigzag
    if crown:
        x_apex = x_left + 0.5 * wspan
        splat(x_apex, y_apex, ch * 1.2, GOLD, 2.2)
        splat(x_apex, y_apex, ch * 3.2, EMBER, 0.7)
    # prefix stripe (cyan arithmetic edge), enlarged
    for (xc, yc, L, c, pf) in cells:
        if pf == 1 and c > 1e-9:
            closeness = np.log(0.5 / max(c, 1.0 / (2 * p))) / np.log(p)
            soft_rect(xc - cw * 0.25, yc, cw * 1.5, ch * 0.72, CYAN,
                      0.30 + 1.25 * np.clip(closeness, 0, 1) ** 1.5)
    # wounds: tight white-gold ruptures
    wounds = []
    for (xc, yc, L, c, pf) in cells:
        if c <= 1e-9:
            wounds.append((xc, yc, L))
            splat(xc - cw * 0.25, yc, ch * 0.5, WOUNDC, 2.6)
            splat(xc - cw * 0.25, yc, ch * 1.3, EMBER, 0.8)
    return wounds

SS_adjust = 1.0

def draw_zigzag(p, x_left, x_right, y_top, y_bot, wounded_L=()):
    """the zigzag's true anatomy: after the founding 1, even positions ride
    the rail p+1-i and odd positions the rail p+3-i — two descending
    diagonals of beads, joined by the sawtooth thread."""
    a = constr(p)
    xs = x_left + (np.arange(p) + 0.5) / p * (x_right - x_left)
    ys = y_bot - (np.array(a) - 1) / (p - 1) * (y_bot - y_top)
    tcol = THREAD if not wounded_L else COLD
    for i in range(p - 1):
        line_glow((xs[i], ys[i]), (xs[i + 1], ys[i + 1]), tcol,
                  amp=0.30, width=1.3 * SS)
    for i in range(p):
        col = GOLD if (i % 2 == 1) else CYAN * 0.85
        splat(xs[i], ys[i], 3.0 * SS, col, 2.6)
    # founding gesture: the 1 at position 1
    splat(xs[0], ys[0], 6 * SS, GOLD, 6.5)
    splat(xs[0], ys[0], 14 * SS, EMBER, 1.2)
    # wounds: the violating prefixes end at position L-1 (0-based): star them
    for L in wounded_L:
        splat(xs[L - 1], ys[L - 1], 4.5 * SS, WOUNDC, 4.5)
        splat(xs[L - 1], ys[L - 1], 11 * SS, EMBER, 1.1)

# ---------------- layout ----------------
M = SS
title_y = 330 * M

# pyramids
LX0, LX1 = 150 * M, 2080 * M
RX0, RX1 = 2280 * M, 3950 * M
PY_BASE, PY_APEX = 2810 * M, 480 * M

w1 = draw_pyramid(127, LX0, LX1, PY_BASE, PY_APEX)
w2 = draw_pyramid(63, RX0, RX1, PY_BASE, PY_APEX, crown=False)
print("wounds:", len(w1), len(w2))

# zigzag threads
draw_zigzag(127, LX0, LX1, 2930 * M, 3160 * M)
draw_zigzag(63, RX0, RX1, 2930 * M, 3160 * M, wounded_L=(3, 7, 9, 21))

# ---------------- census shore ----------------
# (n, count, log10 nodes searched) from this run's exhaustive engines
census = [(3,2,0.5),(5,0,0.7),(7,4,1.1),(9,0,1.4),(11,0,1.8),(13,0,2.1),
          (15,0,2.4),(17,0,2.8),(19,0,3.1),(21,0,3.4),(23,0,3.7),(25,0,4.0),
          (27,0,4.2),(29,0,4.6),(31,4,4.6),(33,0,5.1),(35,0,4.3),(37,0,4.1),
          (39,0,3.9),(41,0,4.0),(43,0,4.1),(45,0,4.1),(47,0,4.6),(49,0,5.0),
          (51,0,5.5),(53,0,5.8),(55,0,6.2),(57,0,6.6),(59,0,7.0),(61,0,7.5),
          (63,0,7.9)]
SH_Y0, SH_Y1 = 3900 * M, 3560 * M     # base, max top
SH_X0, SH_X1 = 290 * M, 3810 * M
for (n, cnt, lgn) in census:
    x = SH_X0 + (n - 3) / 60.0 * (SH_X1 - SH_X0)
    h = (lgn / 8.0) * (SH_Y0 - SH_Y1)
    ytop = SH_Y0 - h
    allones = (n & (n + 1)) == 0
    colc = GOLD if cnt > 0 else (CYAN * 0.8 if allones else STEEL * 0.8)
    # column
    nseg = max(int(h / (3 * M)), 2)
    for t in np.linspace(0, 1, nseg):
        y = SH_Y0 - t * h
        splat(x, y, 5.2 * M, colc, 0.75 * (0.35 + 0.65 * t))
    # reflection below baseline
    for t in np.linspace(0, 0.4, max(int(nseg * 0.3), 2)):
        y = SH_Y0 + t * h * 0.45
        splat(x, y, 5.0 * M, colc, 0.18 * (0.4 - t))
    if cnt > 0:      # crown star
        splat(x, ytop - 16 * M, 8 * M, GOLD, 7.0)
        splat(x, ytop - 16 * M, 22 * M, EMBER, 1.3)
    elif allones:    # the all-ones towers that die: 15, 63
        splat(x, ytop - 12 * M, 5.5 * M, WOUNDC, 2.4)

# horizon glow
gy = np.arange(Hs)
horiz = np.exp(-((gy - SH_Y0) / (46 * M)) ** 2)
buf += 0.10 * horiz[:, None, None] * np.array([0.25, 0.36, 0.5])[None, None, :]

# ---------------- background + bloom + tone ----------------
buf += BG[None, None, :]

from scipy.ndimage import gaussian_filter, zoom as ndzoom
lum = buf.mean(2)
thr = np.percentile(lum, 99.2)
mask = np.clip((lum - thr) / (lum.max() - thr + 1e-9), 0, 1)
hot = buf * mask[:, :, None]
small = hot[::4, ::4]
bl = np.stack([gaussian_filter(small[:, :, k], 14) for k in range(3)], 2)
bloom = ndzoom(bl, (4, 4, 1), order=1)[:Hs, :Ws]
buf = buf + 1.15 * bloom

img = 1 - np.exp(-1.55 * buf)
img = np.clip(img, 0, 1) ** (1 / 1.9)
img = img + (np.random.rand(Hs, Ws, 1) - 0.5) / 255.0
img8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
im = Image.fromarray(img8).resize((W, H), Image.LANCZOS)

# ---------------- annotation (after bloom/tone) ----------------
def load_font(names, size):
    for nm in names:
        try:
            return ImageFont.truetype(nm, size)
        except Exception:
            pass
    return ImageFont.load_default()

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_title = load_font([FB], 118)
f_sub   = load_font([FR], 46)
f_lab   = load_font([FB], 56)
f_cap   = load_font([FR], 38)
f_small = load_font([FR], 33)

d = ImageDraw.Draw(im)
gold = (255, 214, 140); dim = (150, 168, 195); cyn = (150, 216, 228)
def ctext(x, y, s, font, fill):
    bb = d.textbbox((0, 0), s, font=font)
    d.text((x - (bb[2] - bb[0]) / 2, y), s, font=font, fill=fill)

ctext(W/2, 84, "THE CROWN AND THE WOUND", f_title, gold)
ctext(W/2, 232, "every consecutive stretch must miss its average — a law only the complete primes can carry   ·   MO 514690", f_sub, dim)

ctext((150+2080)/2/1, 388, "Z₁₂₇  ·  2⁷−1 prime — the crown", f_lab, gold)
ctext((2280+3950)/2, 388, "Z₆₃  ·  2⁶−1 = 3²·7 — the wound", f_lab, (200, 190, 170))

# per-pyramid caption
ctext((150+2080)/2, 3210, "each tile = one window (position × length); brightness = how close its sum comes to divisibility", f_cap, dim)
ctext((150+2080)/2, 3262, "odd interior windows miss by exactly 1/L — the crown burns hotter as it rises;  even windows rest at ½", f_cap, dim)
ctext((2280+3950)/2, 3210, "the same zigzag at 63: its prefix sums strike zero exactly at L ∈ {3, 7, 9, 21} — the divisors of 63", f_cap, cyn)
ctext((2280+3950)/2, 3262, "the permutation factors its own length: the wounds name the factors", f_cap, cyn)

# theorem + census captions
ctext(W/2, 3396, "THEOREM (this run): the zigzag 1, p−1, p, p−3, p−2, … is good  ⇔  p is a Mersenne prime;  its violating window lengths are exactly the nontrivial divisors of p", f_cap, gold)
ctext(W/2, 3448, "interior windows are safe forever:  odd length ⇒ sum ≡ ±1 (mod L),  even length ⇒ sum ≡ L/2 (mod L)", f_small, dim)

ctext(W/2, 3944, "the census shore: exhaustive search over every odd n ≤ 63 — good permutations exist only at n = 3, 7, 31 (Mersenne primes), and only 2 / 4 / 4 of them: the zigzag and its reflections", f_small, dim)
ctext(W/2, 3990, "column height = log₁₀ nodes searched · gold stars = the three crowns · pale marks = the all-ones numbers 15 and 63, killed by their own factors", f_small, (110, 125, 150))
for (nn, lab) in [(3,"3"),(7,"7"),(15,"15"),(31,"31"),(63,"63")]:
    xx = (290 + (nn - 3) / 60.0 * (3810 - 290))
    ctext(xx, 3906, lab, f_small, dim)
for (nn, cc) in [(3,"2"),(7,"4"),(31,"4")]:
    xx = (290 + (nn - 3) / 60.0 * (3810 - 290))
    hh = {3:0.5,7:1.1,31:4.6}[nn] / 8.0 * (3900 - 3560)
    ctext(xx, 3900 - hh - 78, cc, f_lab, gold)

im.save('good_hero_4096.png')
print("saved good_hero_4096.png")
