#!/usr/bin/env python3
"""Render: THE SELF THAT SURVIVES THE SHUFFLE (2560²), from perm_census.json.

Chart: x = digit length n (1..25); y = orbit prime-fraction (share of an
orbit's members that are prime), 0 at the floor, 1 at the gold shore.
Every orbit of every n <= 7 is a rain-point; the richest are drawn as bead
rings (bead = member, gold = prime, slate = composite).  Perfect rings
(every member prime) blaze on the shore — there are twelve, none after
n = 3.  From n = 8 on, {1,3,7,9}-multiset orbits are drawn at their kill
resistance; repunits are singleton beads — the only shore-touchers past
the wall are R19 and R23.  The rising cyan wall is the expectation ledger:
-log10 E[another perfect orbit], the odds against another self.
"""
import numpy as np, json, math, random
import scipy.ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
import sys

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
SIZE = 1280 if PROTO else 2560
SS = 2
S = SIZE * SS
rs = SIZE / 2560.0 * 2   # splat scale vs a 1280 proto

d = json.load(open("perm_census.json"))
phase1, phase2 = d["phase1"], d["phase2"]
ledger = {int(k): v for k, v in d["ledger"].items()}

rng = random.Random(7)
npr = np.random.default_rng(7)

# ---------------------------------------------------------------- layout
MX, MTOP, MBOT = 0.055 * S, 0.10 * S, 0.24 * S
NMAX = 25
def xcol(n):   # column center
    return MX + (n - 0.5) / NMAX * (S - 2 * MX)
CW = (S - 2 * MX) / NMAX
def yfrac(f):  # fraction -> y (shore at top of field)
    return MTOP + (1 - f) * (S - MTOP - MBOT)

# ---------------------------------------------------------------- buffers
warm = np.zeros((S, S), dtype=np.float32)   # gold ink
cold = np.zeros((S, S), dtype=np.float32)   # slate-blue ink
cyan = np.zeros((S, S), dtype=np.float32)   # cyan accents

def splat(buf, x, y, amp, sig):
    x = np.atleast_1d(np.asarray(x, dtype=np.float64))
    y = np.atleast_1d(np.asarray(y, dtype=np.float64))
    amp = np.broadcast_to(np.asarray(amp, dtype=np.float64), x.shape)
    sig = np.broadcast_to(np.asarray(sig, dtype=np.float64), x.shape)
    R = np.maximum((3.0 * sig).astype(int), 2)
    for xi, yi, a, s_, r in zip(x, y, amp, sig, R):
        x0, x1 = int(xi) - r, int(xi) + r + 1
        y0, y1 = int(yi) - r, int(yi) + r + 1
        if x1 < 0 or y1 < 0 or x0 >= S or y0 >= S: continue
        xs = np.arange(max(x0, 0), min(x1, S))
        ys = np.arange(max(y0, 0), min(y1, S))
        gx = np.exp(-0.5 * ((xs - xi) / s_) ** 2)
        gy = np.exp(-0.5 * ((ys - yi) / s_) ** 2)
        buf[np.ix_(ys, xs)] += a * gy[:, None] * gx[None, :]

def splat_fast(buf, x, y, amp):
    """bilinear point splat for fog (then blurred once)"""
    x = np.asarray(x); y = np.asarray(y); amp = np.asarray(amp, dtype=np.float32)
    x0 = np.floor(x).astype(np.int64); y0 = np.floor(y).astype(np.int64)
    fx = (x - x0).astype(np.float32); fy = (y - y0).astype(np.float32)
    fl = buf.ravel()
    for dx, wx in ((0, 1 - fx), (1, fx)):
        for dy, wy in ((0, 1 - fy), (1, fy)):
            xi = np.clip(x0 + dx, 0, S - 1); yi = np.clip(y0 + dy, 0, S - 1)
            np.add.at(fl, yi * S + xi, amp * wx * wy)

# ---------------------------------------------------------------- phase-1 fog
# every orbit: a rain point at (col-jittered x, y=fraction)
fogx, fogy, foga = [], [], []
rings = {n: [] for n in range(1, 8)}   # (f, T, P, key) top orbits
for key, (T, P) in phase1.items():
    n = int(key.split(":")[0])
    f = P / T
    fogx.append(xcol(n) + (rng.random() - 0.5) * CW * 0.82)
    fogy.append(yfrac(f) + (rng.random() - 0.5) * 3 * rs)
    foga.append(1.0)
    rings[n].append((f, T, P, key))
splat_fast(cold, np.array(fogx), np.array(fogy), np.full(len(fogx), 0.55, np.float32))
print(f"[render] fog: {len(fogx)} phase-1 orbits")

# ---------------------------------------------------------------- phase-2 dust
# killed orbits: resistance = tries to find a composite witness
p2x, p2y, p2a = [], [], []
mod3x, mod3y = [], []
repunits = {}
for key, val in phase2.items():
    n = int(key.split(":")[0])
    tag = val[0]
    if tag == "killed":
        tries, T = val[1], val[2]
        f_res = rng.random() * 0.045                   # the dead lie on the floor
        p2x.append(xcol(n) + (rng.random() - 0.5) * CW * 0.82)
        p2y.append(yfrac(f_res) + (rng.random() - 0.5) * 4 * rs)
        p2a.append(0.4 + 0.3 * tries)
    elif tag == "mod3":
        mod3x.append(xcol(n) + (rng.random() - 0.5) * CW * 0.82)
        mod3y.append(yfrac(0.0) + (rng.random() - 0.5) * 4 * rs)
    elif tag in ("SURVIVOR", "composite-orbit1"):
        cnt = key.split(":")[1].split(".")
        if cnt[1] == cnt[2] == cnt[3] == "0":        # repunit
            repunits[n] = (tag == "SURVIVOR")
splat_fast(cold, np.array(p2x), np.array(p2y), np.array(p2a, dtype=np.float32) * 0.5)
splat_fast(cold, np.array(mod3x), np.array(mod3y), np.full(len(mod3x), 0.30, np.float32))
print(f"[render] phase-2 dust: {len(p2x)} killed, {len(mod3x)} mod-3 dead, repunits {sorted(repunits)}")

# blur fogs softly
cold = ndi.gaussian_filter(cold, 1.1 * rs)

# ---------------------------------------------------------------- rings
def draw_ring(cx, cy, radius, T, P, blaze=False):
    """bead ring: T beads, P of them prime(gold), rest slate; fraction-arc for big T"""
    if T == 1:
        if P == 1:
            splat(warm, [cx], [cy], [3.2 if blaze else 2.0], [3.2 * rs])
        else:
            splat(cold, [cx], [cy], [1.6], [2.2 * rs])
        return
    nb = int(min(T, 48))
    th = np.linspace(0, 2 * np.pi, nb, endpoint=False) - np.pi / 2
    bx = cx + radius * np.cos(th)
    by = cy + radius * np.sin(th)
    ngold = int(round(nb * P / T))
    # beads: primes first (gold), then slate — deterministic order around ring
    ga = 2.6 if blaze else 1.15
    if ngold:
        splat(warm, bx[:ngold], by[:ngold], np.full(ngold, ga), np.full(ngold, (2.4 if blaze else 1.7) * rs))
    if nb - ngold:
        splat(cold, bx[ngold:], by[ngold:], np.full(nb - ngold, 0.85), np.full(nb - ngold, 1.6 * rs))
    if blaze:  # halo ring
        th2 = np.linspace(0, 2 * np.pi, 160, endpoint=False)
        splat_fast(warm, cx + radius * np.cos(th2), cy + radius * np.sin(th2),
                   np.full(160, 0.55, np.float32))

ring_labels = []
for n in range(1, 8):
    lst = sorted(rings[n], reverse=True)[:14]
    placed = []
    for f, T, P, key in lst:
        r = np.clip(2.4 * math.sqrt(T) * rs, 4 * rs, CW * 0.40)
        if f == 1.0:
            r = max(r, 13 * rs)
        y = yfrac(f)
        for py, pr in placed:
            if abs(y - py) < (r + pr) * 1.15:
                y = py + (r + pr) * 1.15
        x = xcol(n)
        blaze = (f == 1.0)
        draw_ring(x, y, r, T, P, blaze=blaze)
        placed.append((y, r))
        if blaze:
            digits = key.split(":")[1]
            ring_labels.append((x, y, r, digits.lstrip("0") or digits, T))
print(f"[render] rings drawn; {len(ring_labels)} perfect")

# repunit lane: R_n singleton beads; survivors blaze on the shore
rep_labels = []
for n in range(2, NMAX + 1):
    if n <= 7:
        # repunit orbits live in phase1 already (key n:111..)
        key = f"{n}:{'1' * n}"
        pr = phase1.get(key, [1, 0])[1] > 0
    else:
        pr = repunits.get(n, False)
    x, y = xcol(n), yfrac(1.0 if pr else 0.0)
    if pr:
        splat(warm, [x], [y], [4.0], [3.6 * rs])
        splat(warm, [x], [y], [0.9], [10 * rs])
        if n > 2:
            rep_labels.append((x, y, f"R{n}"))
    else:
        splat(cyan, [x], [y], [1.5], [2.0 * rs])

# specimen register: the twelve perfect orbits, magnified in the desert
SPEC = [("2",), ("3",), ("5",), ("7",), ("11",), ("13", "31"), ("17", "71"),
        ("37", "73"), ("79", "97"), ("113", "131", "311"),
        ("199", "919", "991"), ("337", "373", "733")]
spec_geom = []
sx0, sx1 = 0.40 * S, 0.955 * S
sy0, sy1 = 0.235 * S, 0.685 * S
cols_, rows_ = 4, 3
for i, orb in enumerate(SPEC):
    gi, gj = i % cols_, i // cols_
    cx = sx0 + (gi + 0.5) / cols_ * (sx1 - sx0)
    cy = sy0 + (gj + 0.5) / rows_ * (sy1 - sy0)
    rad = (30 + 7.5 * len(orb)) * rs
    if len(orb) == 1:
        splat(warm, [cx], [cy], [3.4], [4.0 * rs])
        splat(warm, [cx], [cy], [0.8], [12 * rs])
    else:
        th4 = np.linspace(0, 2 * np.pi, 220, endpoint=False)
        splat_fast(warm, cx + rad * np.cos(th4), cy + rad * np.sin(th4),
                   np.full(220, 0.30, np.float32))
        thb = np.linspace(0, 2 * np.pi, len(orb), endpoint=False) - np.pi / 2
        splat(warm, cx + rad * np.cos(thb), cy + rad * np.sin(thb),
              np.full(len(orb), 2.8), np.full(len(orb), 3.4 * rs))
    spec_geom.append((cx, cy, rad, orb))

# ghost ring: the self that never came — faint dashed circle on the shore at n=12
gx, gy, gr = xcol(12), yfrac(1.0), 20 * rs
th3 = np.linspace(0, 2 * np.pi, 90, endpoint=False)
dash = (np.arange(90) // 6) % 2 == 0
splat_fast(cold, gx + gr * np.cos(th3[dash]), gy + gr * np.sin(th3[dash]),
           np.full(int(dash.sum()), 2.2, np.float32))

# the shore itself: thin line at f=1
ysh = yfrac(1.0)
xs_line = np.arange(int(MX * 0.7), int(S - MX * 0.7))
splat_fast(warm, xs_line.astype(float), np.full(len(xs_line), ysh), np.full(len(xs_line), 0.045, np.float32))

# ---------------------------------------------------------------- ledger wall
# bottom strip: -log10 E[another perfect orbit at n] rising into impossibility
led_n = sorted(k for k in ledger if k >= 4)
led_v = np.array([-math.log10(max(ledger[n], 1e-300)) for n in led_n])
ymax_led = led_v.max()
y0_led = S - 0.055 * S
h_led = MBOT - 0.10 * S
for n, v in zip(led_n, led_v):
    x = xcol(n)
    h = v / ymax_led * h_led
    ys2 = np.linspace(y0_led - h, y0_led, max(int(h / (1.5 * rs)), 4))
    splat_fast(cyan, np.full(len(ys2), x), ys2, np.full(len(ys2), 1.7, np.float32))
    splat(cyan, [x], [y0_led - h], [1.5], [2.2 * rs])

# ---------------------------------------------------------------- compose
warm = warm + 0.55 * ndi.gaussian_filter(warm, 5.5 * rs)   # bloom
cyan = cyan + 0.5 * ndi.gaussian_filter(cyan, 4.5 * rs)

img = np.zeros((S, S, 3), dtype=np.float32)
# ground: near-black blue
img[..., 0] = 0.0025; img[..., 1] = 0.0030; img[..., 2] = 0.0080
GOLD = np.array([1.00, 0.80, 0.38]); SLATE = np.array([0.42, 0.52, 0.72]); CY = np.array([0.35, 0.85, 0.90])
for ch in range(3):
    img[..., ch] += GOLD[ch] * (1 - np.exp(-0.9 * warm))
    img[..., ch] += SLATE[ch] * (1 - np.exp(-0.55 * cold)) * 0.85
    img[..., ch] += CY[ch] * (1 - np.exp(-0.8 * cyan)) * 0.9
img = np.clip(img, 0, 1) ** (1 / 2.2)
img8 = np.clip(img * 255 + np.random.uniform(-0.5, 0.5, img.shape), 0, 255).astype(np.uint8)
out = Image.fromarray(img8).resize((SIZE, SIZE), Image.LANCZOS)

# ---------------------------------------------------------------- text
dr = ImageDraw.Draw(out)
def font(sz, bold=False):
    try:
        return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf", sz)
    except Exception:
        return ImageFont.load_default()
sc = SIZE / 2560
ft, fm, fsm = font(int(64 * sc), True), font(int(30 * sc)), font(int(24 * sc))
dr.text((int(0.045 * SIZE), int(0.028 * SIZE)), "THE SELF THAT SURVIVES THE SHUFFLE",
        font=ft, fill=(220, 200, 160))
sub = ("permutable primes, MO 514708  ·  x = digit length 1–25  ·  y = share of the digit-orbit that is prime  ·  "
       "gold ring = every shuffle prime")
dr.text((int(0.045 * SIZE), int(0.028 * SIZE) + int(80 * sc)), sub, font=fsm, fill=(130, 126, 132))
v1 = "census exhaustive to 7 digits (12 perfect orbits, none after 991)  ·  every {1,3,7,9}-multiset to 25 digits killed by a composite witness"
v2 = "except R19 and R23, the repunits — the self that survives every shuffle is the self with no parts to shuffle"
dr.text((int(0.045 * SIZE), int(0.028 * SIZE) + int(112 * sc)), v1, font=fsm, fill=(130, 126, 132))
dr.text((int(0.045 * SIZE), int(0.028 * SIZE) + int(144 * sc)), v2, font=fsm, fill=(130, 126, 132))
# ring labels
bycol = {}
for x, y, r, digits, T in ring_labels:
    bycol.setdefault(round(x), []).append((y, r, digits))
for xr, lst in bycol.items():
    lst.sort()
    lasty = -1e9
    for y, r, digits in lst:
        px = xr / S * SIZE + (r / S * SIZE) + int(10 * sc)
        py = y / S * SIZE - int(12 * sc)
        py = max(py, lasty + int(26 * sc))
        lasty = py
        dr.text((px, py), digits, font=fsm, fill=(196, 172, 128))
for x, y, lab in rep_labels:
    px, py = x / S * SIZE, y / S * SIZE - int(46 * sc)
    w = dr.textlength(lab, font=fm)
    dr.text((px - w / 2, py), lab, font=fm, fill=(226, 206, 150))
# ledger caption
dr.text((int(0.045 * SIZE), int((y0_led / S) * SIZE) + int(14 * sc)),
        "the odds against another self: −log₁₀ E[a new all-prime orbit of length n]  —  "
        f"total expectation past 991: ≈ {sum(ledger[n] for n in led_n):.3f}, past 25 digits: < 10⁻³⁰",
        font=fsm, fill=(96, 150, 156))
fspec = font(int(34 * sc), True)
for cx, cy, rad, orb in spec_geom:
    if len(orb) == 1:
        w = dr.textlength(orb[0], font=fspec)
        dr.text((cx / S * SIZE - w / 2, cy / S * SIZE + int(16 * sc)), orb[0],
                font=fspec, fill=(228, 204, 148))
    else:
        thb = np.linspace(0, 2 * np.pi, len(orb), endpoint=False) - np.pi / 2
        for t_, mem in zip(thb, orb):
            bx = (cx + (rad + 26 * rs) * np.cos(t_)) / S * SIZE
            by = (cy + (rad + 26 * rs) * np.sin(t_)) / S * SIZE
            w = dr.textlength(mem, font=fspec)
            dr.text((bx - w / 2, by - int(15 * sc)), mem, font=fspec, fill=(228, 204, 148))
dr.text((int(sx0 / S * SIZE), int((sy0 / S) * SIZE) - int(40 * sc)),
        "the twelve, magnified — every digit-shuffle of each is prime",
        font=fsm, fill=(150, 138, 118))

gpx, gpy = gx / S * SIZE, gy / S * SIZE
w = dr.textlength("the self that never came", font=fsm)
dr.text((gpx - w / 2, gpy + int(26 * sc)), "the self that never came", font=fsm, fill=(110, 118, 136))
for n in range(1, NMAX + 1):
    px = xcol(n) / S * SIZE
    lab = str(n)
    w = dr.textlength(lab, font=fsm)
    dr.text((px - w / 2, (yfrac(0.0) / S) * SIZE + int(16 * sc)), lab, font=fsm, fill=(88, 88, 100))
for n, txt in ((4, "1 in 23"), (10, "1 in 4×10⁸"), (17, "1 in 10¹⁸"), (25, "1 in 10³²")):
    if n in ledger:
        v = -math.log10(max(ledger[n], 1e-300))
        px = xcol(n) / S * SIZE
        py = (y0_led - v / ymax_led * h_led) / S * SIZE - int(26 * sc)
        w = dr.textlength(txt, font=fsm)
        dr.text((px - w / 2, py), txt, font=fsm, fill=(96, 150, 156))
out.save("perm_proto.png" if PROTO else "perm_2560.png")
print("[render] wrote", "perm_proto.png" if PROTO else "perm_2560.png")
