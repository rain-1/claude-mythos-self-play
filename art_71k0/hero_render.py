"""HERO: THE SYNTHESIS (4096^2) -- MO 513971.
Alternating lexicographic row/column sorting of a random n x n 0/1 matrix:
the number of sorts T until both orders agree.

Composition (chart-as-nightscape):
  x = log2 n  (n = 2 .. 16384),  y = T (1 at bottom .. 13)
  - aurora strata: P(T = k | n) as luminous ribbons (MC, 300k+ trials)
  - grain: actual Monte-Carlo samples as dust inside each ribbon
  - gold pillars at n = 2..7: EXACT weighted distributions (2^{n^2} census
    via the row-multiset reduction), diamonds with area = exact probability
  - silver thread: mu_n; gold thread: fitted law  mu = a + b ln ln n
  - ice wall: the adversarial ceiling T = 2n-3 (worst case, attained for
    every n <= 7 by census; construction for all n) exits the frame
  - witness glyph: the n=7 extremal matrix (T = 11)
  - right margin: the terminal distribution at the largest n
"""
import numpy as np, json, sys, re
from scipy.interpolate import PchipInterpolator
from artlib import canvas, star, bloom, tonemap, save, bake_text, _splat_points, polyline

PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"
FINAL = 1024 if PREVIEW else 4096
SS = 1 if PREVIEW else 2
S = FINAL * SS
rs = S / 1024.0
rng = np.random.default_rng(7)

# ---------------- data ----------------
def parse_exact(fn):
    mu = None; dist = {}; maxT = None; witness = None
    for line in open(fn):
        m = re.match(r'mu_(\d+) = (\d+) / 2\^(\d+)\s+=\s+([\d.]+)', line)
        if m: mu = (int(m.group(2)), int(m.group(3)), float(m.group(4)))
        m = re.match(r'maxT = (\d+).*witness rows: (.*)', line)
        if m: maxT = int(m.group(1)); witness = [int(x) for x in m.group(2).split()]
        m = re.match(r'\s+T=\s*(\d+)\s+(\d+)\s+\(([\d.e+-]+)\)', line)
        if m: dist[int(m.group(1))] = float(m.group(3))
    return mu, dist, maxT, witness

exact = {}
for n in [2, 3, 4, 5, 6, 7]:
    try:
        mu, dist, maxT, wit = parse_exact(f"exact{n}.txt")
        if mu and dist: exact[n] = (mu, dist, maxT, wit)
    except FileNotFoundError:
        pass
print("exact ns:", sorted(exact))

mc = {}
for fn in ["mc_mu.json", "mc_mu2.json"]:
    try:
        for k, v in json.load(open(fn)).items(): mc[int(k)] = v
    except FileNotFoundError: pass
print("mc ns:", sorted(mc))

# anchors: (n, {k: P}, mu)
anchors = []
for n in sorted(exact):
    mu, dist, _, _ = exact[n]
    anchors.append((n, dist, mu[2]))
for n in sorted(mc):
    if n in exact: continue
    d = mc[n]; tot = d['trials']
    anchors.append((n, {k: c/tot for k, c in enumerate(d['dist']) if c > 0}, d['mu']))
anchors.sort()
ns = np.array([a[0] for a in anchors], float)
mus = np.array([a[2] for a in anchors])

# law fit on n >= 32 MC anchors
fit_ns = np.array([n for n in ns if n >= 512])
fit_mu = np.array([m for n, m in zip(ns, mus) if n >= 512])
A = np.vstack([np.ones_like(fit_ns), np.log(np.log(fit_ns))]).T
coef, *_ = np.linalg.lstsq(A, fit_mu, rcond=None)
a_fit, b_fit = coef
print(f"law fit: mu = {a_fit:.3f} + {b_fit:.3f} ln ln n")

# ---------------- chart mapping ----------------
X0, X1 = 0.075, 0.945
Y_BOT, Y_TOP = 0.775, 0.115
LMIN, LMAX = 1.0, 14.1
TMAX = 13.0
def xm(n):  return (X0 + (np.log2(n) - LMIN)/(LMAX - LMIN)*(X1 - X0)) * S
def ym(T):  return (Y_BOT + (T - 1.0)/(TMAX - 1.0)*(Y_TOP - Y_BOT)) * S

# stratum palette: cool ramp by k
def strat_color(k):
    t = np.clip((k - 2.5)/6.0, 0, 1)
    c0 = np.array([0.30, 0.85, 1.00]); c1 = np.array([0.42, 0.40, 1.00])
    c2 = np.array([0.95, 0.35, 0.75])
    return (1-t)*c0 + t*c1 if t < 0.55 else (1-(t-0.55)/0.45)*c1 + (t-0.55)/0.45*c2

GOLD = np.array([1.00, 0.80, 0.38])
ICE  = np.array([0.62, 0.86, 1.00])
WHT  = np.array([1.00, 0.97, 0.90])

buf = canvas(S)

# ---------------- aurora strata ----------------
lg = np.log2(ns)
xg = np.linspace(LMIN, LMAX, 900)          # dense grid in log2 n
cols = (X0 + (xg - LMIN)/(LMAX - LMIN)*(X1 - X0)) * S
for k in range(1, 14):
    P = np.array([a[1].get(k, 0.0) for a in anchors])
    if P.max() <= 0: continue
    # pchip in log2 n on sqrt-scale (keeps small tails visible, no negative)
    interp = PchipInterpolator(lg, np.sqrt(P), extrapolate=False)
    Pg = np.nan_to_num(interp(xg))**2
    col = strat_color(k)
    y0 = ym(k)
    yy = np.arange(int(y0 - 26*rs), int(y0 + 26*rs))
    yy = yy[(yy >= 0) & (yy < S)]
    prof = np.exp(-0.5*((yy - y0)/(7.5*rs))**2)
    band = (Pg**0.85)[None, :] * prof[:, None]
    # deposit: iterate rows (few) -- vectorized per row over x columns
    xi = np.clip(cols.astype(int), 0, S-1)
    for j, y in enumerate(yy):
        w = band[j] * 0.55
        np.add.at(buf[y], xi, w[:, None]*col[None, :])

# grain dust: MC samples inside ribbons
for n, dist, mu in anchors:
    if n in exact: continue
    xc = xm(n)
    wcol = (X1 - X0)/(LMAX - LMIN)*S * 0.30
    for k, P in dist.items():
        if P <= 0: continue
        ng = int(min(900, 2600*P))
        if ng == 0: continue
        gx = xc + rng.normal(0, wcol*0.55, ng)
        gy = ym(k) + rng.normal(0, 4.6*rs, ng)
        _splat_points(buf, gx, gy, 0.075*rs, strat_color(k)*0.9 + 0.1, 1)

# ---------------- exact pillars ----------------
frac_labels = {2: "21/16", 3: "105/64", 4: "125387/2¹⁶",
               5: "36573599/2²⁴", 6: "168401367693/2³⁶", 7: ""}
for n in sorted(exact):
    mu, dist, maxT, wit = exact[n]
    xc = xm(n)
    polyline(buf, [(xc, ym(0.6)), (xc, ym(min(maxT + 0.7, TMAX)))], GOLD*0.35,
             amp=0.10*rs)
    for k, P in dist.items():
        r = 1.2*rs + 6.0*rs*np.sqrt(P)
        star(buf, xc, ym(k), GOLD, amp=0.42 + 0.38*np.sqrt(P), rad=r)

# ---------------- threads ----------------
# law thread (gold, dashed): mu = a + b lnln n
xs = np.linspace(LMIN + 0.35, LMAX, 700)
nn = 2**xs
law = a_fit + b_fit*np.log(np.log(nn))
pts = np.stack([ (X0 + (xs-LMIN)/(LMAX-LMIN)*(X1-X0))*S, ym(law) ], 1)
for i in range(0, len(pts)-8, 12):
    polyline(buf, pts[i:i+7], GOLD, amp=0.16*rs)
# mu thread (silver, solid through anchors)
interp = PchipInterpolator(lg, mus)
xs2 = np.linspace(lg[0], lg[-1], 900)
mu2 = interp(xs2)
pts2 = np.stack([ (X0 + (xs2-LMIN)/(LMAX-LMIN)*(X1-X0))*S, ym(mu2) ], 1)
polyline(buf, pts2, WHT*0.85, amp=0.14*rs)

# ---------------- adversarial ceiling ----------------
xs3 = np.linspace(1.0, np.log2((TMAX + 3)/2 + 1.6), 500)
Tc = 2*(2**xs3) - 3
keep = (Tc >= 1) & (Tc <= TMAX + 0.9)
pts3 = np.stack([ (X0 + (xs3[keep]-LMIN)/(LMAX-LMIN)*(X1-X0))*S, ym(Tc[keep]) ], 1)
polyline(buf, pts3, ICE, amp=0.5*rs)
for n in sorted(exact):
    mu, dist, maxT, wit = exact[n]
    star(buf, xm(n), ym(maxT), ICE, amp=0.85, rad=2.6*rs)   # attained ceiling

# witness glyph: largest exact n's extremal matrix, doubly-sorted end state
nw = max(exact)
wit = exact[nw][3]
if wit:
    gx0, gy0 = 0.265*S, 0.185*S
    cell = 5.2*rs
    Wm = np.array([[(r >> (nw-1-j)) & 1 for j in range(nw)] for r in wit])
    for i in range(nw):
        for j in range(nw):
            if Wm[i, j]:
                yy0, xx0 = int(gy0 + i*cell), int(gx0 + j*cell)
                buf[yy0:yy0+int(cell*0.8), xx0:xx0+int(cell*0.8)] += \
                    ICE[None, None, :]*0.55
            else:
                yy0, xx0 = int(gy0 + i*cell), int(gx0 + j*cell)
                buf[yy0:yy0+int(cell*0.8), xx0:xx0+int(cell*0.8)] += \
                    np.array([0.05, 0.07, 0.10])[None, None, :]

# right margin: terminal distribution bars at largest n
nbig = int(ns[-1])
dbig = anchors[-1][1]
for k, P in dbig.items():
    if P <= 0: continue
    x0 = 0.952*S; L = P*0.038*S
    yy = ym(k)
    polyline(buf, [(x0, yy), (x0 + L, yy)], strat_color(k), amp=0.9*rs)

buf *= (1.0 if PREVIEW else 1.8)   # FINAL_BOOST: thin-line loss at LANCZOS downscale
buf = bloom(buf, sigmas=(2*rs, 7*rs, 24*rs), weights=(1.0, 0.30, 0.13), thresh=0.55)
img = tonemap(buf, k=1.35, gamma=0.92)

fs = int(12.5*rs); fs2 = int(11*rs)
mu_strs = " · ".join(f"μ{n}={frac_labels[n]}" for n in sorted(exact) if frac_labels.get(n))
# axis ticks
for ntick in [4, 16, 64, 256, 1024, 4096, 16384]:
    polyline(buf, [(xm(ntick), 0.782*S), (xm(ntick), 0.792*S)], WHT*0.5, amp=0.3*rs)
buf_ticks_done = True
texts = [
 (0.075*S, 0.028*S, "THE SYNTHESIS", int(30*rs), (1, 0.92, 0.72), True, "la"),
 (0.075*S, 0.028*S+int(38*rs),
  "two orders take turns imposing themselves on one random 0/1 matrix — rows sort, then columns, then rows —",
  fs, (0.80, 0.82, 0.90), False, "la"),
 (0.075*S, 0.028*S+int(56*rs),
  "until one day nothing moves.  T = the length of the argument.   MO 513971 · aurora = P(T = k | n), ~390,000 matrices",
  fs, (0.80, 0.82, 0.90), False, "la"),
 (0.945*S, 0.028*S, f"law (fit n ≥ 512):  μ(n) ≈ {a_fit:.2f} + {b_fit:.2f}·ln ln n",
  fs, (1, 0.85, 0.5), False, "ra"),
 (0.945*S, 0.028*S+int(18*rs), "conjecture: μ(n) = ln ln n + C — the local slope falls 2 → ≈1.1 across the data",
  fs, (1, 0.85, 0.5), False, "ra"),


 (0.075*S, 0.83*S, "gold pillars: EXACT census (all 2^{n²} matrices via row-multiset reduction) — " + mu_strs,
  fs2, (0.95, 0.80, 0.45), False, "la"),
 (0.075*S, 0.83*S+int(18*rs),
  "μ7 exact; worst case T = 2n−3 (ice wall) attained at every n ≤ 7 — the crafted quarrel outlives every random one",
  fs2, (0.70, 0.85, 0.95), False, "la"),
 (0.075*S, 0.83*S+int(36*rs),
  "average argument: five sentences at n = 8192 — and thesis-first vs antithesis-first agree in law, differ on 60% of matrices (corr ≈ 0)",
  fs2, (0.62, 0.65, 0.75), False, "la"),
 (0.263*S, 0.155*S, f"the crafted matrix, n={max(exact)}: T = {2*max(exact)-3}",
  fs2, (0.70, 0.85, 0.95), False, "la"),
]
for ntick in [4, 16, 64, 256, 1024, 4096, 16384]:
    texts.append((xm(ntick), 0.797*S, f"{ntick}", fs2, (0.55,0.58,0.68), False, "ma"))
texts.append((0.068*S, 0.80*S, "n", fs2, (0.55,0.58,0.68), False, "ra"))
for kt in [2, 4, 6, 8, 10, 12]:
    texts.append((0.068*S, ym(kt), f"T={kt}", fs2, (0.5,0.53,0.62), False, "rm"))
texts.append((0.952*S, ym(dbig and max(dbig)+1 or 8), f"P(T=k)\nn={nbig}", fs2, (0.5,0.53,0.62), False, "la"))
img = bake_text(img, texts, S)
save(img, "synthesis_preview.png" if PREVIEW else "synthesis_4096.png", final=FINAL)
print("saved")
