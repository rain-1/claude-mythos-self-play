"""PIECE 2 (2560^2): 'The Ledger of Signs' — iterated structured rank-one downdate
M <- M - (Mx)(Mx)^T/(x^T M x); each replacement retires exactly one sign-unit of
inertia into the null space (MO 513954, answered YES). Spectral-flow waterfall."""
import numpy as np
from scipy.ndimage import gaussian_filter
from artlib import save, bake_text, star, polyline

S = 2560
z = np.load("cascade_flow.npz")
E, signs, inert = z['E'], z['signs'], z['inert']       # E: (108, 61, 120)
NST, NS, n = E.shape

L, R, TOP, BOT = 150, 90, 150, 380
W, H = S - L - R, S - TOP - BOT
YS = 0.35
VMAX = float(np.abs(E).max()) * 1.03

def ymap(lam):
    v = np.arcsinh(lam / YS) / np.arcsinh(VMAX / YS)   # [-1, 1]
    return TOP + H * (0.5 - 0.5 * v)

def xmap(tau):
    return L + W * tau / NST

buf = np.zeros((S, S, 3), np.float32)
hot = np.zeros((S, S, 3), np.float32)

AMBER = np.array([1.00, 0.68, 0.22])
TEAL = np.array([0.26, 0.82, 0.92])
GHOST = np.array([0.52, 0.48, 0.70])
tol = 1e-6

# threads: for each sorted index, the full trajectory (dim ensemble)
tau_grid = np.concatenate([k + np.linspace(0, 1, NS) for k in range(NST)])
for i in range(n):
    lam = E[:, :, i].ravel()                            # (NST*NS,)
    xs = xmap(tau_grid)
    ys = ymap(lam)
    alive = np.abs(lam) > 40 * tol
    sgn = np.sign(lam)
    state = np.where(~alive, 0, np.where(sgn > 0, 1, -1)).astype(np.int8)
    brk = np.nonzero(np.diff(state))[0]
    starts = np.concatenate([[0], brk + 1])
    ends = np.concatenate([brk + 1, [len(lam)]])
    for a, b in zip(starts, ends):
        if b - a < 2:
            continue
        st = state[a]
        if st == 0:
            continue                                    # shore pile drawn separately
        elif st == 1:
            col, amp = AMBER, 0.26
        else:
            col, amp = TEAL, 0.30
        polyline(buf, np.stack([xs[a:b], ys[a:b]], 1), tuple(col), amp=amp, step=0.8)

# the dying thread of each stage: white-hot comet (amp ramps along the stage)
for k in range(NST):
    lam0, lam1 = E[k, 0, :], E[k, -1, :]
    cand = np.nonzero((np.abs(lam0) > 40 * tol) & (np.abs(lam1) <= 40 * tol))[0]
    if len(cand) == 0:
        continue
    i = cand[0] if signs[k] < 0 else cand[-1]
    lam = E[k, :, i]
    xs = xmap(k + np.linspace(0, 1, NS))
    ys = ymap(lam)
    base_col = np.array([1.0, 0.88, 0.55]) if signs[k] > 0 else np.array([0.72, 0.95, 1.0])
    ramp = 0.25 + 0.95 * np.linspace(0, 1, NS - 1) ** 2
    pts = np.stack([xs, ys], 1)
    for a in range(NS - 1):
        polyline(hot, pts[a:a + 2], tuple(base_col), amp=0.75 * ramp[a], step=0.7)

# the shore fills: kernel-count glow band at y=0, brightness ramps with n0(t)
n0_path = inert[:, 2].astype(np.float32)                # per stage boundary
xs_band = np.arange(L - 10, S - R + 10)
tau_b = np.clip((xs_band - L) / W * NST, 0, NST)
n0_interp = np.interp(tau_b, np.arange(NST + 1), n0_path)
band_amp = 0.015 + 0.22 * (n0_interp / n) ** 1.2
yc = ymap(0.0)
for dy, wgt in [(-2, 0.35), (-1, 0.8), (0, 1.0), (1, 0.8), (2, 0.35)]:
    for ch, cv in enumerate(GHOST * 1.25):
        np.add.at(buf[..., ch], (np.full_like(xs_band, int(round(yc)) + dy), xs_band),
                  band_amp * wgt * cv)

# death flares: end of each stage, the newly-zero eigenvalue
for k in range(NST):
    sg = signs[k]
    col = (1.0, 0.85, 0.45) if sg > 0 else (0.75, 0.95, 1.0)
    star(hot, xmap(k + 1.0), ymap(0.0), col, amp=1.05, rad=3.4)
    # delta-sign tick at top
    tcol = AMBER if sg > 0 else TEAL
    polyline(buf, np.array([[xmap(k + 0.5), TOP - 46], [xmap(k + 0.5), TOP - 24]]),
             tuple(tcol), amp=0.5)

# initial-zero ghosts already on the line: mark their birth
for _ in range(int(inert[0][2])):
    pass  # they are drawn as ghost threads already

# inertia ledger strip (stacked bars per stage boundary)
y0 = S - 292
hstrip = 68
for k in range(NST + 1):
    npos, nneg, nzer = inert[k]
    x = xmap(min(k, NST) * 1.0)
    yy = y0 + hstrip
    for hgt, col, aa in [(hstrip * npos / n, AMBER, 0.5), (hstrip * nneg / n, TEAL, 0.55),
                         (hstrip * nzer / n, GHOST, 0.30)]:
        if hgt < 0.5:
            yy -= hgt
            continue
        polyline(buf, np.array([[x, yy], [x, yy - hgt]]), tuple(col), amp=aa, step=0.6)
        polyline(buf, np.array([[x + 1.2, yy], [x + 1.2, yy - hgt]]), tuple(col), amp=aa, step=0.6)
        yy -= hgt

# shore line (y=0) faint base
polyline(buf, np.array([[L - 20, ymap(0)], [S - R + 20, ymap(0)]]), (0.8, 0.75, 0.9),
         amp=0.05)

# bloom
hb = np.empty_like(hot)
for ch in range(3):
    hb[..., ch] = gaussian_filter(hot[..., ch], 2.5)
buf += hot + 1.0 * hb
for ch in range(3):
    small = buf[::4, ::4, ch]
    buf[..., ch] += 0.22 * np.kron(gaussian_filter(small, 4.0),
                                   np.ones((4, 4), np.float32))[:S, :S]

img = 1.0 - np.exp(-1.5 * np.clip(buf, 0, None))
img = np.clip(img, 0, 1) ** 0.93
base = np.array([0.014, 0.015, 0.030], np.float32)
img = img + base[None, None, :] * (1 - img)

texts = [
    (L, S - 190, "THE  LEDGER  OF  SIGNS", 56, (0.92, 0.88, 0.78), True, "ls"),
    (L, S - 122, "M ← M − (Mx)(Mx)ᵀ/(xᵀMx):  every replacement retires exactly one sign-unit of inertia into the null space  (MO 513954: YES, one Sylvester congruence)", 30, (0.62, 0.60, 0.58), False, "ls"),
    (L, S - 74, "a signature-(66, 42, 12) operator dies in exactly 108 replacements: amber = positive spectrum, teal = negative — magnitudes are flung wildly, only the COUNT is conserved", 30, (0.62, 0.60, 0.58), False, "ls"),
    (L, S - 26, "flares = the moment each direction is handed over  ·  strip = the inertia ledger (n₊, n₋, n₀)  ·  law verified exactly in ℚ (380 trials) and in float to n = 400", 30, (0.50, 0.48, 0.46), False, "ls"),
]
img = bake_text(img, texts, S)
save(img, "ledger_2560.png", dither=True)
print("saved ledger_2560.png")
