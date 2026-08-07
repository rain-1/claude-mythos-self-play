"""Piece 2: THE HOLDOUT (2560^2) — AP-obstruction atlas piece 41.
Channel 17 of the Z[sqrt2] country: gap-17 length-5 fences (5 consecutive
members of S in arithmetic progression, gap 17). Piece 40 found E≈5-6
expected below 3.2e10 under the independence model, observed 0, P < 1%.

This piece: the anomaly dissected.
 top    THE FENCE — the 5 posts + 64 window slots; candle height = P(slot
        occupied | posts in S) from the 4e9 census (40,647 patterns).
        Frozen slots (q = 0 exactly) = ice stubs. All patterns share ONE
        rigid 2-adic class: n ≡ 14 mod 48, n ≡ 2 mod 9 (mod 32 splits 14/30).
 middle THE CONSPIRACY — occupancy histogram observed vs the EXACT
        Poisson-binomial independence law (same marginals): underdispersed
        (var 5.08 vs 6.03), zero-class suppressed ~5x — measured on the
        speaking neighbours: g=15 deficit 5.2x (104 vs 542), g=16 5.0x.
 bottom THE VERDICT RAIL — depth 4e9 -> 1.6e11: E_indep ghost curve,
        conspiracy-corrected E band (f in [4,7]), piece-40 shoreline,
        neighbours' first fences, and the deep hunt's verdict."""
import numpy as np, json, sys, re
from artlib import (canvas, star, bloom, tonemap, save, bake_text,
                    _splat_points, polyline)

PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"
VERDICT_FENCES = []          # filled from hunt alarms at final render
try:
    for line in open("hunt_alarms_20000000000_160000000000.txt"):
        m = re.match(r'FIRST l=(\d+) g=17 start=(\d+)', line)
        if m: VERDICT_FENCES.append(int(m.group(2)))
except FileNotFoundError:
    pass

FINAL = 1280 if PREVIEW else 2560
SS = 1 if PREVIEW else 2
S = FINAL * SS
rs = S / 1280.0
rng = np.random.default_rng(41)

GOLD = np.array([1.00, 0.80, 0.38])
EMBER= np.array([1.00, 0.55, 0.28])
ICE  = np.array([0.60, 0.85, 1.00])
CYAN = np.array([0.45, 0.92, 1.00])
SILV = np.array([0.60, 0.66, 0.80])
VIOL = np.array([0.58, 0.42, 0.90])
WHT  = np.array([1.0, 0.97, 0.9])

# ---------- data ----------
prof = np.loadtxt("diag17_prof_g17.txt")
offs, q = prof[:, 0].astype(int), prof[:, 2]
cls = json.load(open("g17_class_profiles.json"))
hist17 = {}
for line in open("diag17_out.txt"):
    if line.startswith("g=17"): cur = True; continue
    if 'cur' in dir() and cur and line.strip().startswith("occ_hist"):
        hist17 = dict((int(a), int(b)) for a, b in
                      (p.split(':') for p in line.split()[1:]))
        cur = False
C5 = 40647

# exact Poisson-binomial with marginals q
pb = np.array([1.0])
for qq in q:
    pb = np.convolve(pb, [1-qq, qq])

buf = canvas(S)

# ============ TOP: THE FENCE ============
fx0, fx1 = 0.07*S, 0.93*S
fy = 0.255*S
def fence_x(j):  # offset 0..68
    return fx0 + j/68.0*(fx1-fx0)
# ground line
polyline(buf, [(fx0-0.02*S, fy), (fx1+0.02*S, fy)], SILV*0.7, amp=0.35*rs)
# posts
for k in range(5):
    xp = fence_x(17*k)
    polyline(buf, [(xp, fy), (xp, fy-0.150*S)], GOLD, amp=1.5*rs)
    star(buf, xp, fy-0.150*S, GOLD, amp=1.4, rad=4.8*rs)
# window candles
qmax = q.max()
for j, qq in zip(offs, q):
    xp = fence_x(j)
    if qq == 0.0:
        polyline(buf, [(xp, fy), (xp, fy-0.012*S)], ICE, amp=0.75*rs)
        star(buf, xp, fy-0.012*S, ICE, amp=0.28, rad=1.5*rs)
    else:
        h = 0.015*S + 0.085*S*(qq/qmax)
        col = EMBER if qq > 0.25 else EMBER*0.55 + SILV*0.45
        polyline(buf, [(xp, fy), (xp, fy-h)], col, amp=0.55*rs)
        star(buf, xp, fy-h, col, amp=0.5+0.5*qq/qmax, rad=(1.3+2.2*qq/qmax)*rs)
# twin class barcodes beneath (mod 32: n=14 and n=30)
for row, key in enumerate(["32_14", "32_30"]):
    qc = np.array(cls[key]["q"]); yb = fy + (0.020 + 0.022*row)*S
    for j, qq in zip(offs, qc):
        xp = fence_x(j)
        if qq == 0: col, a = ICE, 0.18
        else: col, a = EMBER, 0.22 + 0.8*qq
        _splat_points(buf, np.array([xp]), np.array([yb]), a*2.6*rs, col, 1)
# conspiracy arcs: strongest slot-pair correlations (ice = rivals, ember = allies)
pairs = json.load(open("g17_pairs.json"))
def arc(j1, j2, col, aa, depth):
    x1, x2 = fence_x(j1), fence_x(j2)
    xm_ = (x1+x2)/2; wd = abs(x2-x1)
    t = np.linspace(0, np.pi, 160)
    xs = xm_ + (wd/2)*np.cos(t)
    ys = fy + 0.062*S + depth*min(wd*0.16, 0.042*S)*np.sin(t)
    polyline(buf, np.stack([xs, ys], 1), col, amp=aa*rs)
for (a, b, c) in pairs["neg"][:8]:
    arc(a, b, ICE, 0.20+1.6*abs(c), 1.0)
for (a, b, c) in pairs["pos"][:6]:
    arc(a, b, EMBER, 0.20+1.4*abs(c), 0.72)
# reflection glow
polyline(buf, [(fx0, fy+0.004*S), (fx1, fy+0.004*S)], GOLD*0.25, amp=0.5*rs)

# ============ MIDDLE: THE CONSPIRACY ============
hx0, hx1 = 0.10*S, 0.55*S
hy0, hy1 = 0.600*S, 0.435*S     # y down->up
kmax = 22
def hxm(k): return hx0 + k/kmax*(hx1-hx0)
def hym(logp):                   # log10 P from -6.2 .. -0.4
    return hy0 + (logp + 6.2)/(6.2-0.4)*(hy1-hy0)
# observed bars as grain stacks
for k in range(kmax+1):
    c = hist17.get(k, 0)
    if c == 0: continue
    p = c/C5
    ytop = hym(np.log10(p))
    npts = int(60 + 40*np.log10(max(c, 1)))
    gx = hxm(k) + rng.normal(0, 1.7*rs, npts)
    gy = rng.uniform(ytop, hy0, npts)
    _splat_points(buf, gx, gy, 0.13*rs, EMBER, 1)
    star(buf, hxm(k), ytop, EMBER, amp=0.55, rad=1.8*rs)
# independence Poisson-binomial curve (ghost)
ks = np.arange(0, kmax+1)
pbk = np.array([pb[k] if k < len(pb) else 0 for k in ks])
pts = np.stack([hxm(ks[pbk > 1e-8]), hym(np.log10(pbk[pbk > 1e-8]))], 1)
polyline(buf, pts, ICE*0.85, amp=0.42*rs)
# the zero-class gap: vertical accusing arrow at k=0
star(buf, hxm(0), hym(np.log10(pb[0])), ICE, amp=1.0, rad=3.0*rs)
polyline(buf, [(hxm(0), hym(np.log10(pb[0]))), (hxm(0), hy0+0.012*S)],
         ICE*0.6, amp=0.30*rs)

# deficit chips (calibrators) right of histogram
chips = [("g=15", 542.5, 104), ("g=16", 64.6, 13), ("g=18", 2.6, 1)]
for i, (lab, Ei, obs) in enumerate(chips):
    cx0, cy0 = 0.62*S, 0.455*S + i*0.048*S
    L = 0.115*S
    polyline(buf, [(cx0, cy0), (cx0+L, cy0)], ICE*0.7, amp=0.5*rs)
    polyline(buf, [(cx0, cy0), (cx0+L*obs/Ei, cy0)], EMBER, amp=1.0*rs)

# ============ BOTTOM: THE VERDICT RAIL ============
rx0, rx1 = 0.08*S, 0.92*S
ry = 0.865*S
lX0, lX1 = np.log10(4e9), np.log10(1.6e11)
def rxm(X): return rx0 + (np.log10(X)-lX0)/(lX1-lX0)*(rx1-rx0)
def rym(E):  # log axis: E from 0.12 .. 50
    E = np.clip(E, 0.12, 50.0)
    return ry - (np.log10(E)-np.log10(0.12))/(np.log10(50)-np.log10(0.12))*0.155*S
polyline(buf, [(rx0, ry), (rx1, ry)], SILV*0.8, amp=0.4*rs)
G = lambda X: X/np.log(X)**2.5
Xs = np.geomspace(4e9, 1.6e11, 300)
E_ind = 1.09*G(Xs)/G(4e9)
pts = np.stack([rxm(Xs), rym(E_ind)], 1)
polyline(buf, pts, ICE*0.75, amp=0.35*rs)
for f, aa in [(4.0, 0.5), (5.0, 0.9), (7.0, 0.5)]:
    Ec = E_ind/f
    pts = np.stack([rxm(Xs), rym(Ec)], 1)
    polyline(buf, pts, GOLD, amp=aa*0.5*rs)
# piece-40 shoreline
xs40 = rxm(3.2e10)
polyline(buf, [(xs40, ry+0.012*S), (xs40, ry-0.165*S)], VIOL*0.8, amp=0.5*rs)
# neighbours' first fences (depth ticks)
for lab, X in [("15", 1.1934e8), ("16", 1.0183e8), ("18", 2.1428e9),
               ("14", 5.341738436e9)]:
    if X < 4e9: continue
    xt = rxm(X)
    star(buf, xt, ry, CYAN, amp=0.8, rad=2.4*rs)
polyline(buf, [(rx0, rym(1.0)), (rx1, rym(1.0))], SILV*0.35, amp=0.22*rs)
# verdict
if VERDICT_FENCES:
    for Xf in VERDICT_FENCES:
        xt = rxm(Xf)
        polyline(buf, [(xt, ry), (xt, ry-0.09*S)], GOLD, amp=1.3*rs)
        star(buf, xt, ry-0.09*S, WHT, amp=1.6, rad=5.0*rs)
else:
    # cold channel exiting right edge
    polyline(buf, [(rxm(1.5e11), ry-0.002*S), (rx1+0.02*S, ry-0.002*S)],
             ICE*0.5, amp=0.8*rs)

buf = bloom(buf, sigmas=(2*rs, 8*rs, 26*rs), weights=(1.0, 0.30, 0.14), thresh=0.55)
img = tonemap(buf, k=1.30, gamma=0.90)

fs = int(14*rs); fs2 = int(12*rs)
verdict_txt = (f"VERDICT: channel 17 speaks — first fence at n = {VERDICT_FENCES[0]:,}"
               if VERDICT_FENCES else
               "VERDICT: silence to 1.6×10¹¹ — the corrected model itself now refuted (P < 0.4%)")
texts = [
 (0.05*S, 0.032*S, "THE HOLDOUT", int(30*rs), (1, 0.92, 0.72), True, "la"),
 (0.05*S, 0.032*S+int(40*rs),
  "atlas of AP obstructions, piece 41 — ℤ[√2]: the channel that refused to speak",
  fs, (0.80, 0.82, 0.90), False, "la"),
 (0.05*S, 0.032*S+int(60*rs),
  "S = {n: v_p(n) even for all p ≡ 3,5 mod 8} — five consecutive members, equal gap 17: expected ≈5 by 3.2×10¹⁰, found 0",
  fs2, (0.65, 0.68, 0.78), False, "la"),
 (0.083*S, 0.098*S, "the five posts", fs2, (0.95, 0.8, 0.45), False, "la"),
 (0.07*S, 0.352*S, "64 window slots — candle = P(occupied | posts ∈ S), census of all 40,647 patterns at 4×10⁹",
  fs2, (0.75, 0.60, 0.45), False, "la"),
 (0.07*S, 0.352*S+int(18*rs),
  "ice stubs = frozen slots (q = 0 exactly) · ONE rigid 2-adic family: n ≡ 14 mod 48, n ≡ 2 mod 9 — no mixture to blame",
  fs2, (0.62, 0.75, 0.85), False, "la"),
 (0.07*S, 0.352*S+int(36*rs), "twin dot-rows: the two neighbourhood versions (n ≡ 14 / 30 mod 32) · arcs: the camps — ice rivals {14,54}↔{6,30,38,62}, ember allies",
  fs2, (0.55, 0.58, 0.68), False, "la"),
 (0.10*S, 0.408*S, "THE CONSPIRACY — how often k of the 64 slots are occupied",
  fs, (1, 0.85, 0.5), False, "la"),
 (0.10*S, 0.408*S+int(19*rs),
  "ember = census · ice curve = independence with the SAME marginals — underdispersed: var 5.08 vs 6.03",
  fs2, (0.65, 0.68, 0.78), False, "la"),
 (0.62*S, 0.415*S, "the neighbours calibrate the conspiracy:", fs2, (0.65, 0.68, 0.78), False, "la"),
 (0.745*S, 0.452*S, "g=15: found 104 of 542 expected  (×5.2)", fs2, (0.85, 0.6, 0.4), False, "la"),
 (0.745*S, 0.500*S, "g=16: found 13 of 65  (×5.0)", fs2, (0.85, 0.6, 0.4), False, "la"),
 (0.745*S, 0.548*S, "g=18: found 1 of 2.6", fs2, (0.85, 0.6, 0.4), False, "la"),
 (0.62*S, 0.575*S, "emptiness is ~5× harder than independence claims —",
  fs2, (0.65, 0.68, 0.78), False, "la"),
 (0.62*S, 0.575*S+int(17*rs), "for EVERY wide channel; the anomaly dissolves: corrected E(3.2×10¹⁰) ≈ 1.4, P(silence) ≈ 25%",
  fs2, (0.65, 0.68, 0.78), False, "la"),
 (0.08*S, 0.665*S, "THE RAIL — expected fences vs depth", fs, (1, 0.85, 0.5), False, "la"),
 (0.08*S, 0.665*S+int(19*rs),
  "ice = independence model · gold band = conspiracy-corrected (÷4…7) · violet = piece-40 shoreline · cyan = neighbours' first fences",
  fs2, (0.65, 0.68, 0.78), False, "la"),
 (0.08*S, 0.94*S, verdict_txt, int(16*rs), (1, 0.9, 0.6), True, "la"),
 (0.093*S, rym(1.0)-int(14*rs), "E = 1", fs2, (0.5,0.53,0.62), False, "la"),
 (hxm(0), hy0+0.022*S, "k=0: 0 observed", fs2, (0.62,0.75,0.85), False, "ma"),
 (0.92*S, 0.885*S, "depth 1.6×10¹¹", fs2, (0.55, 0.58, 0.68), False, "ra"),
 (0.08*S, 0.885*S, "4×10⁹", fs2, (0.55, 0.58, 0.68), False, "la"),
]
img = bake_text(img, texts, S)
save(img, "holdout_preview.png" if PREVIEW else "holdout_2560.png", final=FINAL)
print("saved", "fences:", VERDICT_FENCES)
