#!/usr/bin/env python3
"""THE LAST STEP — 4096^2 hero (v2: nebula field + bowed final-jump arcs).
N = 2^(n-1)+3, LL orbit s0=4, s_{k+1}=s_k^2-2 mod N; verdict = where s(n-2) lands.
Columns n=3..1027; y = s/N: floor p=0 = target 14/N (odd n, gold), ceiling p=1 =
(N-4)/N (even n, ice).  Field = occupation fog of all orbits (towers thicken with
height); one bowed hairline arc per column = the last step, from s(n-3) to the
verdict bead; exact landings blaze on the rails = the primes (necessity proven).
Basement: liar-scan ledger."""
import sys, numpy as np
from scipy.ndimage import gaussian_filter, zoom
from artlib import canvas, polyline, star, bloom, tonemap, save, bake_text, _splat_points

PREVIEW = "--preview" in sys.argv
S = 1024 if PREVIEW else 4096
SS = 1 if PREVIEW else 2
R = S * SS
rs = R / 1024.0

rng = np.random.default_rng(5)
buf = canvas(R)

d = np.load("hero_orbits.npz")
pos, offs, meta = d["pos"], d["offs"], d["meta"]
ns = meta[:, 0].astype(int); isprime = meta[:, 2].astype(bool); dist = meta[:, 3]

XL, XR = 42 * rs, 995 * rs
YTOP, YBOT = 96 * rs, 850 * rs
BY0, BY1 = 892 * rs, 972 * rs
NMIN, NMAX = 3, ns.max()
def xcol(n): return XL + (n - NMIN) / (NMAX - NMIN) * (XR - XL)
def ypos(p): return YBOT - p * (YBOT - YTOP)

C_DUST  = np.array([0.28, 0.40, 0.62])
C_BOLT  = np.array([0.55, 0.68, 0.90])
C_GOLD  = np.array([1.00, 0.78, 0.30])
C_ICE   = np.array([0.55, 0.88, 1.00])
C_AMBER = np.array([1.00, 0.52, 0.20])
C_STEEL = np.array([0.60, 0.70, 0.88])

# ---- background wash: faint indigo gradient for depth ----
yy = np.linspace(0, 1, R, dtype=np.float32)[:, None]
wash = (0.030 * np.exp(-((yy - 0.08) / 0.35) ** 2))[..., None] * np.array([0.10, 0.13, 0.30], np.float32)
buf += wash

# ---- occupation nebula (coarse hist -> blur -> upsample) ----
GW, GH = 512, 420
H = np.zeros((GH, GW), np.float32)
gx_all, gy_all = [], []
for i, n in enumerate(ns):
    orb = pos[offs[i]:offs[i + 1]][:-1]
    if len(orb) == 0: continue
    x01 = (xcol(n) - XL) / (XR - XL)
    gx_all.append(np.full(len(orb), x01 * (GW - 1)) + rng.normal(0, 1.3, len(orb)))
    gy_all.append((1.0 - orb) * (GH - 1) + rng.normal(0, 0.7, len(orb)))
gx = np.clip(np.concatenate(gx_all), 0, GW - 1).astype(np.int32)
gy = np.clip(np.concatenate(gy_all), 0, GH - 1).astype(np.int32)
np.add.at(H, (gy, gx), 1.0)
H = gaussian_filter(H, (2.2, 1.4))
H = H / max(H.max(), 1e-9)
H = H ** 0.62                                 # lift the thin left
win = np.ones(GW, np.float32)
e = int(GW * 0.03)
win[:e] = np.linspace(0, 1, e); win[-e:] = np.linspace(1, 0, e)
H *= win[None, :]
neb = zoom(H, ((YBOT - YTOP) / GH, (XR - XL) / GW), order=1)
neb = np.clip(neb, 0, None)
y0i, x0i = int(YTOP), int(XL)
h, w = neb.shape
for c in range(3):
    buf[y0i:y0i + h, x0i:x0i + w, c] += 0.42 * neb * C_DUST[c]

# ---- rails ----
for (yy_, col) in ((YBOT, C_GOLD), (YTOP, C_ICE)):
    xs = np.linspace(XL - 16 * rs, XR + 16 * rs, int(2400 * rs))
    _splat_points(buf, xs, np.full_like(xs, yy_), 0.14 * rs, col, 1)
    _splat_points(buf, xs, np.full_like(xs, yy_ + (1.6 * rs if yy_ == YBOT else -1.6 * rs)), 0.05 * rs, col * 0.6, 1)

# ---- final-jump arcs + verdict beads ----
near_rank = np.argsort(dist)
amber = {}
r_i = 0
for i in near_rank:
    if not isprime[i] and r_i < 20:
        amber[i] = 1.0 - r_i / 20.0; r_i += 1

for i, n in enumerate(ns):
    orb = pos[offs[i]:offs[i + 1]]
    x = xcol(n)
    p_prev = orb[-2] if len(orb) >= 2 else orb[-1]
    p_end = orb[-1]
    y0_, y1_ = ypos(p_prev), ypos(p_end)
    par_col = C_GOLD if (n % 2) else C_ICE
    bow = (12 * rs) * (1 if n % 2 else -1)
    tt = np.linspace(0, 1, 48)[:, None]
    p0 = np.array([x, y0_]); p2 = np.array([x, y1_])
    p1 = np.array([x + bow, 0.5 * (y0_ + y1_)])
    bez = (1 - tt) ** 2 * p0 + 2 * (1 - tt) * tt * p1 + tt ** 2 * p2
    bc = C_BOLT * 0.7 + par_col * 0.3
    amp_arc = 0.040 * rs if not isprime[i] else 0.10 * rs
    if isprime[i]: bc = par_col
    polyline(buf, bez, bc, amp=amp_arc)
    # small bead where the arc starts (the penultimate value)
    star(buf, x, y0_, C_BOLT, amp=0.5, rad=0.75 * rs)
    if isprime[i]:
        star(buf, x, y1_, par_col, amp=3.6, rad=3.4 * rs)
        star(buf, x, y1_, np.array([1, 1, 1.]), amp=1.1, rad=1.0 * rs)
        ysg = np.linspace(YTOP, YBOT, int(800 * rs))
        _splat_points(buf, np.full_like(ysg, x), ysg, 0.011 * rs, par_col, 1)
    else:
        wgt = amber.get(i, 0.0)
        col = C_STEEL * (1 - wgt) + C_AMBER * wgt
        star(buf, x, y1_, col, amp=0.55 + 1.5 * wgt, rad=(0.95 + 1.0 * wgt) * rs)

# ---- basement ledger ----
try:
    L = np.loadtxt("liars_final.txt")
    have_scan = L.ndim == 2 and len(L) > 100
except Exception:
    have_scan = False
if have_scan:
    Ln, Lq, Ldist = L[:, 0].astype(int), L[:, 2].astype(bool), L[:, 4]
    NSC = Ln.max()
    def xsc(n): return XL + (n - 3) / (NSC - 3) * (XR - XL)
    close = np.clip(-np.log10(np.maximum(Ldist, 1e-12)) / 10.0, 0.03, 1.0)
    comp = ~Lq
    xs = xsc(Ln[comp].astype(np.float64))
    hs = (BY1 - BY0) * (0.06 + 0.80 * close[comp])
    for x, h, c_ in zip(xs, hs, close[comp]):
        ys = np.linspace(BY1 - h, BY1, max(3, int(h / rs * 1.5)))
        _splat_points(buf, np.full_like(ys, x), ys, 0.09 * rs * (0.2 + 0.8 * c_), C_DUST, 1)
    for n_ in Ln[Lq]:
        x = xsc(n_)
        ys = np.linspace(BY0 - 4 * rs, BY1, int(160 * rs))
        cc = C_GOLD if n_ % 2 else C_ICE
        _splat_points(buf, np.full_like(ys, x), ys, 0.13 * rs, cc, 1)
        star(buf, x, BY0 - 6 * rs, cc, amp=2.4, rad=2.0 * rs)
    xs2 = np.linspace(XL - 16 * rs, XR + 16 * rs, int(2000 * rs))
    _splat_points(buf, xs2, np.full_like(xs2, BY1 + 2 * rs), 0.035 * rs, C_STEEL, 1)

# ---- finish ----
buf = bloom(buf, sigmas=(2 * rs, 7 * rs, 26 * rs), weights=(1.0, 0.42, 0.24), thresh=0.5)
img = tonemap(buf, k=1.3, gamma=0.92)
if SS > 1:
    from PIL import Image
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((S, S), Image.LANCZOS)
    img = np.asarray(im).astype(np.float32) / 255.0

fs = S / 1024.0
texts = [
    (0.040 * S, 0.020 * S, "THE LAST STEP", int(34 * fs), (0.93, 0.88, 0.78), True, "la"),
    (0.040 * S, 0.058 * S, "N = 2^(n-1) + 3      s(0)=4,  s(k+1) = s(k)^2 - 2  (mod N)      one column per n = 3..1027      the verdict is where the orbit lands",
     int(14 * fs), (0.60, 0.64, 0.76), False, "la"),
    (0.958 * S, 0.078 * S, "ceiling: s(n-2) = -4, the even-n primes  (3 a residue: the tower closes in GF(N))",
     int(13 * fs), (0.55, 0.82, 0.95), False, "ra"),
    (0.958 * S, 0.845 * S, "floor: s(n-2) = 14, the odd-n primes  (3 a non-residue: the tower needs GF(N^2))",
     int(13 * fs), (0.95, 0.78, 0.42), False, "ra"),
    (0.040 * S, 0.862 * S, "the deep ledger, n <= 20000:  tick height = how near each composite came to lying  -  every exact landing is prime",
     int(13 * fs), (0.55, 0.60, 0.72), False, "la"),
    (0.958 * S, 0.980 * S, "MO 513606  -  necessity proven;  no Lucas-Lehmer liar below n = 20000",
     int(12 * fs), (0.58, 0.61, 0.70), False, "ra"),
]
for i, n in enumerate(ns):
    if isprime[i] and n in (29, 68, 85, 229, 391, 785):
        lx = xcol(n) * (S / R)
        yl = (0.806 if n % 2 else 0.104) * S
        texts.append((lx, yl, str(n), int(12 * fs), (0.85, 0.75, 0.55) if n % 2 else (0.6, 0.85, 0.95), False, "ma"))
img = bake_text(img, texts, S)
out = "hero_preview.png" if PREVIEW else "hero_4096.png"
save(img, out, dither=True)
print("saved", out)
