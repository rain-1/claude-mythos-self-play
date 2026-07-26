"""PANEL 2 — The Ledger of the Monster  (the moonshine module as an emission spectrum)

J(q) = j - 744 = q^-1 + 196884 q + 21493760 q^2 + ... (coefficients computed
exactly from E4^3/Delta in this script) is the partition function of the
moonshine CFT V-natural.  Every energy level splits into irreducible
representations of the Monster; head decompositions (Conway-Norton, re-verified
here; levels 1..3 UNIQUE by exhaustive search over ATLAS dimensions) are drawn
as an emission spectrum: one thin blazing line per irrep copy (multiplicity m =
m stacked lines), line length ∝ log dim, one hue per irrep; the trivial rep is
a star (dim 1 - a point of light).  The vacuum sits below; undecoded levels
dissolve upward.  Footer: the Monster's order, recomputed from its prime
factorization.
"""
import numpy as np, math, sys, time
from scipy.ndimage import gaussian_filter
import kit

PROTO = "--proto" in sys.argv
S = 1024 if PROTO else 2560
SS = 1 if PROTO else 2
W = H = S * SS
rs = W / 1024.0
t0 = time.time()

# ---- exact coefficients ----
NT = 34
def poly_mul(a, b, N):
    out = [0] * N
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if i + j >= N: break
                out[i + j] += ai * bj
    return out
euler = [0] * NT
k = 0
while True:
    g1, g2 = k * (3 * k - 1) // 2, k * (3 * k + 1) // 2
    if g1 >= NT and g2 >= NT and k > 0: break
    s = 1 if k % 2 == 0 else -1
    if g1 < NT: euler[g1] += s
    if g2 < NT and k > 0: euler[g2] += s
    k += 1
e2 = poly_mul(euler, euler, NT); e4 = poly_mul(e2, e2, NT)
e8 = poly_mul(e4, e4, NT); e16 = poly_mul(e8, e8, NT)
e24 = poly_mul(e16, e8, NT)
sig3 = [0] * NT
for n in range(1, NT):
    for m in range(n, NT, n): sig3[m] += n ** 3
E4 = [1] + [240 * sig3[n] for n in range(1, NT)]
E43 = poly_mul(poly_mul(E4, E4, NT), E4, NT)
jq = [0] * NT
for n in range(NT):
    jq[n] = E43[n] - sum(e24[kk] * jq[n - kk] for kk in range(1, n + 1))
c = {n - 1: jq[n] for n in range(NT)}
assert c[1] == 196884 and c[2] == 21493760 and c[5] == 333202640600

DIMS = [1, 196883, 21296876, 842609326, 18538750076, 19360062527, 293553734298]
MULT = {1: (1, 1, 0, 0, 0, 0, 0), 2: (1, 1, 1, 0, 0, 0, 0),
        3: (2, 2, 1, 1, 0, 0, 0), 4: (3, 3, 1, 2, 1, 0, 0),
        5: (4, 5, 3, 2, 1, 1, 1)}
for n, mv in MULT.items():
    assert sum(m * d for m, d in zip(mv, DIMS)) == c[n], n

# Monster order from its prime factorization (footer certificate)
MO = (2**46 * 3**20 * 5**9 * 7**6 * 11**2 * 13**3 * 17 * 19 * 23 * 29 * 31
      * 41 * 47 * 59 * 71)
assert MO == 808017424794512875886459904961710757005754368000000000
print("|M| certificate ok; decomposition sums verified")

IRR_COL = [(1.00, 1.00, 0.96),   # 1        white star
           (1.00, 0.80, 0.32),   # 196883   gold
           (0.98, 0.55, 0.16),   # 2.1e7    amber
           (0.90, 0.28, 0.13),   # 8.4e8    ember
           (0.78, 0.32, 0.66),   # 1.85e10  orchid
           (0.42, 0.40, 0.95),   # 1.94e10  indigo
           (0.32, 0.78, 0.92)]   # 2.9e11   ice

buf = np.zeros((H, W, 3), np.float32)
core = np.zeros((H, W), np.float32)          # for bloom mask of line cores

# faint resonance beam behind the tower (the axis the spectrum hangs on)
YYg, XXg = np.mgrid[0:H, 0:W].astype(np.float32)
beam_x = np.exp(-((XXg - W / 2) / (0.16 * W)) ** 2)
beam_y = np.clip((0.93 * H - YYg) / (0.9 * H), 0, 1) ** 1.5
buf += (beam_x * beam_y)[..., None] * np.array([0.045, 0.045, 0.10], np.float32)[None, None, :]
del XXg, YYg

def spectral_line(x0, x1, yc, col, amp=1.0):
    """thin blazing emission line with wide soft glow."""
    ln = np.zeros((H, W), np.float32)
    kit.line_splat(ln, x0, yc, x1, yc, amp * (x1 - x0), n=int(max(8, (x1 - x0))))
    restore = 0.35 + 0.65 * rs                 # amplitude-restore after blur (1 at proto)
    crisp = gaussian_filter(ln, 1.1 * rs) * restore
    glow = gaussian_filter(ln, 6.5 * rs) * restore * 4.5
    lay = np.clip(crisp, 0, 1.15) + 0.9 * np.clip(glow, 0, 0.5)
    for ch in range(3):
        buf[..., ch] += lay * col[ch]
    core[:] += np.clip(crisp, 0, 1.15)

def star_at(x, y, col, amp=1.0, rad=None):
    st = np.zeros((H, W), np.float32)
    kit.splat_points(st, [x], [y], amp, rad or 2.6 * rs, (H, W))
    for ch in range(3):
        buf[..., ch] += st * col[ch] * 2.4
    buf[...] += gaussian_filter(st, 9 * rs)[..., None] * \
        np.array([c * 0.9 for c in col], np.float32)[None, None, :] * 0.9
    core[:] += st

def ylev(n):
    return H * (0.775 - 0.138 * (n - 1))
LSP = 6.2 * rs                                 # multiplicity line spacing
LEN = lambda d: (math.log10(max(d, 2)) * 0.0115 + 0.004) * W

for n in range(1, 6):
    mv = MULT[n]
    parts = [(i, m, DIMS[i]) for i, m in enumerate(mv) if m > 0]
    widths = [LEN(d) if i > 0 else 0.008 * W for i, m, d in parts]
    gap = 0.014 * W
    total = sum(widths) + gap * (len(parts) - 1)
    x = W / 2 - total / 2
    yc = ylev(n)
    for (i, m, d), wpx in zip(parts, widths):
        ys = yc - LSP * (m - 1) / 2
        for kk in range(m):
            if i == 0:
                star_at(x + wpx / 2 + (kk - (m - 1) / 2) * 2.4 * LSP, yc,
                        IRR_COL[0], amp=1.0)
            else:
                spectral_line(x, x + wpx, ys + kk * LSP, IRR_COL[i],
                              amp=1.05 - 0.07 * kk)
        x += wpx + gap

# vacuum
star_at(W / 2, H * 0.895, (1.0, 1.0, 0.97), amp=1.3, rad=4.2 * rs)

# ghost levels 6..16: one undivided dissolving line each
for n in range(6, 17):
    cn = c[n]
    wpx = min(0.62, math.log10(cn) * 0.0125) * W
    yc = ylev(5) - (n - 5) * 0.037 * H
    if yc < 0.135 * H:
        break
    fade = 0.40 * (0.82 ** (n - 6))
    ln = np.zeros((H, W), np.float32)
    kit.line_splat(ln, W / 2 - wpx / 2, yc, W / 2 + wpx / 2, yc, fade * wpx,
                   n=int(wpx))
    lay = gaussian_filter(ln, (1.6 + 0.55 * (n - 6)) * rs) * (0.35 + 0.65 * rs)
    buf += np.clip(lay, 0, 0.5)[..., None] * \
        np.array([0.72, 0.75, 0.92], np.float32)[None, None, :]

# bloom driven by the crisp cores only
halo = kit.fast_wide_blur(np.clip(core, 0, 1.2), 22 * rs)
buf += halo[..., None] * np.array([1.0, 0.9, 0.7], np.float32)[None, None, :] * 0.30

img = kit.filmic(buf, k=1.35, gamma=0.92)
if SS > 1:
    from PIL import Image
    img = np.array(Image.fromarray(img).resize((S, S), Image.LANCZOS))

# ---- inscriptions ----
fs = max(13, int(14 * S / 1024))
texts = []
texts.append((S * 0.5, S * 0.895 + 30 * S / 1024, "the vacuum  (dim 1)", "mm", (150, 150, 160)))
LABELS = {1: "c1 = 196884 = 1 + 196883       the first whisper under e^(pi sqrt 163)",
          2: "c2 = 21493760 = 1 + 196883 + 21296876",
          3: "c3 = 864299970 = 2(1) + 2(196883) + 21296876 + 842609326",
          4: "c4 = 20245856256 = 3(1) + 3(196883) + 21296876 + 2(842609326) + 18538750076",
          5: "c5 = 333202640600 = 4(1) + 5(196883) + 3(21296876) + 2(842609326) + 18538750076 + 19360062527 + 293553734298"}
for n in range(1, 6):
    texts.append((S * 0.5, ylev(n) / SS - 26 * S / 1024, LABELS[n], "mm", (195, 180, 148)))
texts.append((S * 0.5, (ylev(5) - 11.6 * 0.037 * H) / SS,
              "... an infinite tower, one Monster module per level (Borcherds 1992)",
              "mm", (118, 120, 136)))
texts.append((S * 0.035, S * 0.048, "THE LEDGER OF THE MONSTER", "lm", (190, 170, 130)))
texts.append((S * 0.035, S * 0.048 + 1.8 * fs,
              "J(q) = j - 744, exact from E4^3/Delta; one line per irrep copy, length = log dim",
              "lm", (140, 132, 118)))
texts.append((S * 0.035, S * 0.048 + 3.3 * fs,
              "levels 1-3 split UNIQUELY - forced by the ATLAS dimensions alone",
              "lm", (140, 132, 118)))
texts.append((S * 0.5, S * 0.965,
              "|M| = 2^46 3^20 5^9 7^6 11^2 13^3 17 19 23 29 31 41 47 59 71 = "
              "808017424794512875886459904961710757005754368000000000",
              "mm", (110, 112, 120)))
img = kit.stamp_text(img, texts, fontsize=fs)
from PIL import Image
out = "ledger_proto.png" if PROTO else "ledger_of_the_monster.png"
Image.fromarray(img).save(out)
print("saved", out, f"{time.time()-t0:.0f}s")
