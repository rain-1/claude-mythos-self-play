"""PIECE 3 (2560^2), ATLAS PIECE 41: 'The Debt of Channel Seventeen'
Z[sqrt2] equal-gap l=5 fence census to 1e11. Channels ordered by opening depth:
a staircase of boreholes descending into the deep; channel 17 = the void shaft
that owes the model E fences. Run AFTER census."""
import numpy as np, re, json, math
from scipy.ndimage import gaussian_filter
from artlib import save, bake_text, star, polyline

S = 2560
TOP, BOT = 240, 330
H = S - TOP - BOT

def parse_rungap(path):
    out = {}
    for line in open(path):
        m = re.match(r"l=(\d+) g=(\d+) maximal_runs=(\d+) first_start=(\d+)", line)
        if m:
            l, g, c, f = map(int, m.groups())
            out[(l, g)] = (c, f)
    return out

new = parse_rungap("deep_rungap.txt")
old32 = parse_rungap("prev_deep_rungap.txt")
old4 = parse_rungap("cert_4e9_rungap.txt")
meta = json.load(open("atlas41_data.json"))
XMAX = meta["X"]
E17 = meta["E17"]
SPOKE17 = new.get((5, 17), (0, 0))[0] > 0
LOGMIN, LOGMAX = 2.4, math.log10(XMAX)

def ydepth(X):
    return TOP + (math.log10(max(X, 300)) - LOGMIN) / (LOGMAX - LOGMIN) * H

# order by opening depth; 17 second-from-right before far channels
speak = [(g, new[(5, g)][1]) for g in [1, 2, 4, 7, 8, 9, 14, 15, 16, 18] if (5, g) in new]
speak.sort(key=lambda t: t[1])
order = [g for g, _ in speak] + [17] + [23, 24, 25]
NCH = len(order)
LM, RM = 170, 90
pitch = (S - LM - RM) / NCH
xpos = {g: LM + pitch * (i + 0.5) for i, g in enumerate(order)}

buf = np.zeros((S, S, 3), np.float32)
rng = np.random.default_rng(41)
noise = gaussian_filter(rng.normal(0, 1, (S // 8, S // 8)), 6)
noise = np.kron(noise, np.ones((8, 8)))[:S, :S]
noise = (noise - noise.min()) / max(np.ptp(noise), 1e-9)
rock = (0.014 + 0.018 * noise)[:, :, None] * np.array([1.05, 0.92, 0.80])[None, None, :]
rock *= np.linspace(1.10, 0.72, S)[:, None, None]
buf += rock.astype(np.float32)
del rock, noise

AMBER = np.array([1.00, 0.70, 0.24])
COLD = np.array([0.45, 0.70, 1.00])
GOLD = (1.0, 0.86, 0.45)
yy = np.arange(S, dtype=np.float32)
ybot = ydepth(XMAX)

def cum(g, table):
    return table.get((5, g), (0, 0))[0]

for g in order:
    x0 = xpos[g]
    hw = pitch * 0.32
    cN, first = new.get((5, g), (0, 0))
    if cN == 0:
        # silent channel: cold void shaft, full depth
        if g == 17:
            hw = pitch * 0.40
        xs = np.arange(S)
        lat = np.clip(1 - np.abs(xs - x0) / hw, 0, 1) ** 1.5
        prof = np.where((yy > TOP) & (yy < ybot), 0.16, 0).astype(np.float32)
        field = np.outer(prof, lat).astype(np.float32)
        amp = 1.6 if g == 17 else 0.30
        for ch in range(3):
            buf[..., ch] += field * COLD[ch] * amp * 0.5
        continue
    # speaking shaft: density profile from checkpoints
    Xs = [first, 4e9, 3.2e10, XMAX]
    Cs = [1, cum(g, old4), cum(g, old32), cN]
    dens = np.zeros(S, np.float32)
    for (Xa, Ca), (Xb, Cb) in zip(zip(Xs, Cs), zip(Xs[1:], Cs[1:])):
        if Xb <= Xa:
            continue
        ya, yb = ydepth(Xa), ydepth(Xb)
        if yb <= ya + 1:
            continue
        dens[(yy >= ya) & (yy < yb)] = max(Cb - Ca, 0) / (yb - ya)
    if dens.max() > 0:
        dens /= dens.max()
    dens = gaussian_filter(dens, 7)
    prof = (0.20 + 0.80 * dens ** 0.5).astype(np.float32)
    prof[yy < ydepth(first)] = 0
    prof[yy > ybot] = 0
    glow = 0.45 + 0.16 * math.log10(max(cN, 1))
    xs = np.arange(S)
    lat = np.clip(1 - np.abs(xs - x0) / hw, 0, 1) ** 1.5
    field = np.outer(prof, lat).astype(np.float32) * 0.5 * glow
    for ch in range(3):
        buf[..., ch] += field * AMBER[ch]
    star(buf, x0, ydepth(first), (1.0, 0.92, 0.62), amp=1.25, rad=4.0)

# channel 17 ghost debt rungs (model): E(X) = E17 * X / XMAX, rung at each integer
if not SPOKE17:
    x0, hw = xpos[17], pitch * 0.38
    for k in range(1, int(E17) + 1):
        Xk = k / E17 * XMAX
        yk = ydepth(Xk)
        if yk < TOP + 10:
            continue
        npts = 40
        xs_r = np.linspace(x0 - hw, x0 + hw, npts)
        polyline(buf, np.stack([xs_r, np.full(npts, yk)], 1), tuple(COLD), amp=1.0)

# wall lines
for X, amp in [(4e9, 0.16), (3.2e10, 0.16), (XMAX, 0.40)]:
    yl = ydepth(X)
    polyline(buf, np.array([[LM - 60, yl], [S - 50, yl]]), GOLD, amp=amp)

for ch in range(3):
    small = buf[::4, ::4, ch]
    buf[..., ch] += 0.30 * np.kron(gaussian_filter(small, 3.5),
                                   np.ones((4, 4), np.float32))[:S, :S]

img = 1.0 - np.exp(-1.6 * np.clip(buf, 0, None))
img = np.clip(img, 0, 1) ** 0.92

texts = [
    (LM - 60, 70, "THE  DEBT  OF  CHANNEL  SEVENTEEN", 54, (0.92, 0.88, 0.78), True, "ls"),
    (LM - 60, 134, "ATLAS PIECE 41 - Z[sqrt2]:  l=5 equal-gap fences of consecutive members, census to 10^11   -   |S| = %s   -   channels ordered by opening depth" % f"{meta['S']:,}", 27, (0.62, 0.60, 0.58), False, "ls"),
    (LM - 60, 176, "each channel opens deeper than the last: 574,  4892,  2.0x10^5, ...,  2.1x10^9,  5.3x10^9 - and then the staircase breaks", 27, (0.62, 0.60, 0.58), False, "ls"),
]
for X, lab in [(4e9, "4x10^9  (piece 39)"), (3.2e10, "3.2x10^10  (piece 40)"), (XMAX, "10^11  THIS CENSUS")]:
    texts.append((S - 55, ydepth(X) - 12, lab, 24, (0.75, 0.68, 0.50), False, "rs"))
for g in order:
    c, f = new.get((5, g), (0, 0))
    col = (0.85, 0.80, 0.70) if c else (0.60, 0.78, 1.00)
    texts.append((xpos[g], ybot + 40, f"g={g}", 28, col, True, "ms"))
    texts.append((xpos[g], ybot + 78, f"{c}", 24, col, False, "ms"))
    if c:
        lab = f"{f:,}" if f < 1e7 else f"{f:.2e}".replace("e+0", "e")
        texts.append((xpos[g], ydepth(f) - 16, lab, 20, (0.85, 0.78, 0.60), False, "ms"))
if not SPOKE17:
    texts += [
        (xpos[17], TOP - 44, "E = %.0f fences owed" % E17, 25, (0.65, 0.85, 1.0), True, "ms"),
        (xpos[17], TOP - 12, "P(silence) = %.0e" % math.exp(-E17), 25, (0.65, 0.85, 1.0), False, "ms"),
    ]
texts += [
    (LM - 60, S - 186, ("gap-scaling theorem (piece 40): R(17) = R(1) EXACTLY - the 2-adic tower does not disfavor gap 17; yet all %.0f fences the calibrated model expects below 10^11 are missing" % E17) if not SPOKE17 else "CHANNEL 17 SPOKE (factor-certified witness in atlas41_notes.md)", 27, (0.62, 0.60, 0.58), False, "ls"),
    (LM - 60, S - 140, "ghost rungs = the model's expected fence depths for channel 17 (E(X) grows ~ linearly in X, so the debt accrues at the bottom); the void is the data", 27, (0.55, 0.53, 0.51), False, "ls"),
    (LM - 60, S - 94, "channels 23, 24, 25: open in the 2-adic tower, silent as expected (model E < 1)   -   l = 6: ZERO below 10^11 (theorem: an l=6 fence needs 24 | gap)", 27, (0.55, 0.53, 0.51), False, "ls"),
    (LM - 60, S - 48, "rig: segmented full-factorization sieve (piece 40), re-certified: |S|(4x10^9) = 601,376,078 exact; word-scan run pass; every first fence factor-certified", 27, (0.50, 0.48, 0.46), False, "ls"),
]
img = bake_text(img, texts, S)
save(img, "debt17_2560.png", dither=True)
print("saved debt17_2560.png; SPOKE17 =", SPOKE17)
