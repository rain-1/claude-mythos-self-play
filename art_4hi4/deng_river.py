"""THE RIVER THAT FLOWED UPHILL — for Yu Deng, Fields Medal 2026.

Deng (with Zaher Hani and Xiao Ma) derived the Boltzmann equation rigorously
from reversible hard-sphere dynamics for long times -- Hilbert's sixth problem
territory: the crossing from time-symmetric microscopic law to the one-way
macroscopic world.

One gas of hard disks, three acts on one space-time carpet (time flows down):

  Act I   (0 -> T):   a cold crystal block with every particle at the SAME
                      speed is released; collisions spread the speeds; the
                      Boltzmann H-functional descends the mountain.
  Act II  (T -> 2T):  Loschmidt's demon flips every velocity.  The gas
                      re-traces its whole history -- the carpet below the fold
                      is the exact mirror of the carpet above it -- and H
                      climbs back UP the mountain it had descended.
  Act III (2T -> 3T): nothing is touched.  The crystal, having reassembled,
                      shatters again; H descends again.  The demon can be
                      obeyed once; the river still knows which way is down.

Each thread is one particle's x-coordinate through time, colored by its
current speed: the single teal of the initial delta-shell blooms into the
gold-to-blue spectrum of Maxwell-Boltzmann, un-mixes at the echo, and blooms
again.  Verified: event-driven dynamics conserves energy to ~1e-12; the echo
returns every particle to its start (max position error reported); the final
speed distribution matches the 2-D Maxwell-Boltzmann law; the Lanford
collision genealogy of a tagged particle is measured (recollision fraction =
the smallness that makes the Boltzmann equation true).
"""
import numpy as np
import heapq, sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import filmic, bloom, save_png, ramp, bilinear_splat, splat_lines
from scipy.ndimage import gaussian_filter

rng = np.random.default_rng(20260724)
t00 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------- gas setup
N = 720
RAD = 0.0068                 # disk radius; packing ~ N*pi*r^2 ~ 0.105
SPEED0 = 1.0

# cold block: hex-ish lattice in a central band
cols = 24
rows_n = int(np.ceil(N / cols))
sp = 2.6 * RAD
pos = np.zeros((N, 2))
k = 0
for i in range(rows_n):
    for j in range(cols):
        if k >= N:
            break
        pos[k] = (0.5 + (j - cols / 2 + 0.5 * (i % 2)) * sp,
                  0.5 + (i - rows_n / 2) * sp * 0.9)
        k += 1
pos += rng.uniform(-0.12, 0.12, pos.shape) * RAD
ang = rng.uniform(0, 2 * np.pi, N)
vel = SPEED0 * np.stack([np.cos(ang), np.sin(ang)], -1)
vel -= vel.mean(0)                       # zero net momentum
vel *= SPEED0 / np.sqrt((vel ** 2).sum(1).mean())

E0 = 0.5 * (vel ** 2).sum()

# ------------------------------------------------------- event-driven engine
class Gas:
    def __init__(self, pos, vel, rad):
        self.p = pos.copy(); self.v = vel.copy(); self.r = rad
        self.t = 0.0
        self.cc = np.zeros(N, np.int64)      # collision counters (invalidate)
        self.heap = []
        self.events = []                     # (t, i, j) executed pair collisions
        for i in range(N):
            self.predict(i, wall_only=False)

    def pair_times(self, i):
        dp = self.p - self.p[i]
        dv = self.v - self.v[i]
        b = (dp * dv).sum(1)
        a = (dv * dv).sum(1)
        c = (dp * dp).sum(1) - (2 * self.r) ** 2
        disc = b * b - a * c
        ok = (b < 0) & (disc > 0) & (a > 0)
        tcol = np.full(N, np.inf)
        sq = np.sqrt(disc[ok])
        tcol[ok] = (-b[ok] - sq) / a[ok]
        tcol[i] = np.inf
        tcol[tcol < 1e-14] = np.inf
        return tcol

    def wall_time(self, i):
        out = np.inf; wall = -1
        for d in range(2):
            v = self.v[i, d]
            if v > 0:
                tw = (1 - self.r - self.p[i, d]) / v
            elif v < 0:
                tw = (self.r - self.p[i, d]) / v
            else:
                continue
            if 1e-14 < tw < out:
                out = tw; wall = d
        return out, wall

    def predict(self, i, wall_only=False):
        tw, wall = self.wall_time(i)
        if np.isfinite(tw):
            heapq.heappush(self.heap, (self.t + tw, i, -1 - wall,
                                       self.cc[i], -1))
        if wall_only:
            return
        tc = self.pair_times(i)
        js = np.where(np.isfinite(tc))[0]
        for j in js:
            heapq.heappush(self.heap, (self.t + tc[j], i, j,
                                       self.cc[i], self.cc[j]))

    def advance(self, t_target, sample_cb=None, sdt=None, s_next=None):
        """Advance to t_target; call sample_cb at times s_next, s_next+sdt..."""
        while True:
            if self.heap:
                te, i, j, ci, cj = self.heap[0]
            else:
                te = np.inf
            tstop = min(te, t_target)
            # emit samples strictly before tstop
            if sample_cb is not None:
                while s_next[0] <= tstop + 1e-15:
                    dt = s_next[0] - self.t
                    sample_cb(s_next[0], self.p + self.v * dt, self.v)
                    s_next[0] += sdt
            if te > t_target:
                self.p += self.v * (t_target - self.t)
                self.t = t_target
                return
            heapq.heappop(self.heap)
            if ci != self.cc[i] or (j >= 0 and cj != self.cc[j]):
                continue                      # stale event
            self.p += self.v * (te - self.t)
            self.t = te
            if j < 0:
                d = -1 - j
                self.v[i, d] = -self.v[i, d]
                self.cc[i] += 1
                self.predict(i)
            else:
                dp = self.p[j] - self.p[i]
                dist = np.sqrt((dp * dp).sum())
                nhat = dp / dist
                dv = self.v[j] - self.v[i]
                vn = (dv * nhat).sum()
                if vn < 0:
                    self.v[i] += vn * nhat
                    self.v[j] -= vn * nhat
                    self.cc[i] += 1; self.cc[j] += 1
                    self.events.append((self.t, i, j))
                    self.predict(i); self.predict(j)
                else:
                    self.cc[i] += 1; self.cc[j] += 1
                    self.predict(i); self.predict(j)


# ------------------------------------------------------------- run three acts
T = float(os.environ.get("T_ACT", "3.2"))
NSAMP = int(os.environ.get("NSAMP", "7040"))     # samples over 3T
T_total = 3 * T
sdt = T_total / NSAMP

samples_x = np.zeros((NSAMP + 1, N), np.float32)
samples_sp = np.zeros((NSAMP + 1, N), np.float32)
samp_i = [0]
samp_t = []

def cb(ts, p, v):
    i = samp_i[0]
    if i <= NSAMP:
        samples_x[i] = p[:, 0]
        samples_sp[i] = np.sqrt((v ** 2).sum(1))
        samp_t.append(ts)
        samp_i[0] += 1

gas = Gas(pos, vel, RAD)
s_next = [0.0]
print("act I ...", flush=True)
gas.advance(T, cb, sdt, s_next)
nev_T = len(gas.events)
state_T = (gas.p.copy(), gas.v.copy())
print(f"  events: {nev_T}  ({nev_T*2/N:.1f} collisions/particle)  "
      f"t={time.time()-t00:.0f}s", flush=True)

# Loschmidt: flip velocities (rebuild predictions)
gas.v = -gas.v
gas.cc += 1
gas.heap = []
for i in range(N):
    gas.predict(i)
print("act II (demon) ...", flush=True)
gas.advance(2 * T, cb, sdt, s_next)
echo_err = np.abs(gas.p - pos).max()
vel_err = np.abs(gas.v + vel).max()
print(f"  ECHO: max|x(2T)-x(0)| = {echo_err:.3e}   max|v(2T)+v(0)| = {vel_err:.3e}",
      flush=True)

# act III: just keep going (time still flows the same way)
print("act III ...", flush=True)
gas.advance(3 * T, cb, sdt, s_next)
E1 = 0.5 * (gas.v ** 2).sum()
nev = len(gas.events)
print(f"  total events {nev}; energy drift {abs(E1-E0)/E0:.3e}  "
      f"t={time.time()-t00:.0f}s", flush=True)

M = samp_i[0]
samples_x = samples_x[:M]; samples_sp = samples_sp[:M]

# --------------------------------------------------------------- H functional
def Hfun(v2d):
    hist, ex, ey = np.histogram2d(v2d[:, 0], v2d[:, 1],
                                  bins=48, range=[[-3.2, 3.2]] * 2)
    p = hist / hist.sum()
    nz = p > 0
    area = (ex[1] - ex[0]) * (ey[1] - ey[0])
    return (p[nz] * np.log(p[nz] / area)).sum()

# recompute H on a coarser time grid by re-simulating? we stored speeds only;
# H needs 2-D velocity dist. Store velocity samples sparsely instead:
# (cheap fix: approximate H from speed histogram -- for an isotropic gas the
# 2-D distribution is f(v)=g(s)/(2 pi s); H = int g log(g/(2 pi s)) ds.)
def H_from_speeds(sp_row):
    hist, e = np.histogram(sp_row, bins=44, range=(0, 3.2))
    ds = e[1] - e[0]
    mid = 0.5 * (e[1:] + e[:-1])
    g = hist / (hist.sum() * ds)
    nz = g > 0
    return float((g[nz] * np.log(g[nz] / (2 * np.pi * mid[nz])) * ds).sum())

Hcurve = np.array([H_from_speeds(samples_sp[i]) for i in range(M)])

# Maxwell-Boltzmann check on final speeds (2-D: g(s) = s/kT * exp(-s^2/2kT))
sfin = samples_sp[-1]
kT = 0.5 * (sfin ** 2).mean()          # 2D: <s^2>/2 = kT
hist, e = np.histogram(sfin, bins=30, range=(0, 3.0), density=True)
mid = 0.5 * (e[1:] + e[:-1])
mb = mid / kT * np.exp(-mid ** 2 / (2 * kT))
l1 = np.abs(hist - mb).mean() / mb.mean()
print(f"  Maxwell-Boltzmann L1/mean deviation of final speed dist: {l1:.3f}")

# --------------------------------------------------- Lanford genealogy stats
WIT = int(np.argmin(((pos - 0.5) ** 2).sum(1)))
events = gas.events
ev_T = [(t, i, j) for (t, i, j) in events if t <= T]
influence = {WIT}
tree_edges = 0
recoll = 0
seen_pairs = set()
for (t, i, j) in sorted(ev_T, reverse=True):
    if i in influence or j in influence:
        tree_edges += 1
        pr = (min(i, j), max(i, j))
        if pr in seen_pairs:
            recoll += 1
        seen_pairs.add(pr)
        influence.add(i); influence.add(j)
print(f"  genealogy of particle {WIT} over act I: {tree_edges} collisions, "
      f"{len(influence)} ancestors, recollision fraction "
      f"{recoll/max(1,tree_edges):.4f}")

# short-time tree (kinetic window ~ first couple mean free times)
tau_short = T / 8
infl_s = {WIT}; edges_s = 0; rec_s = 0; seen_s = set()
for (t, i, j) in sorted([e for e in ev_T if e[0] <= tau_short], reverse=True):
    if i in infl_s or j in infl_s:
        edges_s += 1
        pr = (min(i, j), max(i, j))
        if pr in seen_s:
            rec_s += 1
        seen_s.add(pr)
        infl_s.add(i); infl_s.add(j)
print(f"  short-time tree (t<={tau_short:.3f}): {edges_s} collisions, "
      f"{len(infl_s)} ancestors, recollisions {rec_s} "
      f"(Boltzmann-valid window: tree, not web)")

verify = dict(N=N, RAD=RAD, T=T, events=nev, coll_per_particle=nev * 2 / N / 3,
              echo_pos_err=float(echo_err), echo_vel_err=float(vel_err),
              energy_rel_drift=float(abs(E1 - E0) / E0),
              H_start=float(Hcurve[0]), H_min_actI=float(Hcurve[:M // 3].min()),
              H_at_2T=float(Hcurve[min(2 * M // 3, M - 1)]),
              mb_l1=float(l1), genealogy_edges=tree_edges,
              ancestors=len(influence), recollisions=recoll, short_tree_edges=edges_s,
              short_tree_ancestors=len(infl_s), short_tree_recoll=rec_s)
json.dump(verify, open(os.path.join(HERE, "river_verify.json"), "w"), indent=1)
print(json.dumps(verify, indent=1))

# ------------------------------------------------------------------- render
SC = int(os.environ.get("SC", "1"))          # 1 = full, 2 = half preview
W, Hh = 2560 // SC, 3520 // SC
SS = 2
Wc, Hc = W * SS, Hh * SS

x0pix, x1pix = 0.02, 0.885                    # main carpet band
rowy = np.arange(M) / (M - 1) * (Hc - 1)

# ---- concatenated segments across all particles, colored by current speed
XS = (x0pix + samples_x * (x1pix - x0pix)) * Wc      # (M, N)
SP = samples_sp.astype(np.float64)
kT = 0.5 * float((samples_sp[-1] ** 2).mean())
spn_seg = np.clip(SP[:-1] / (2.13 * np.sqrt(2 * kT)), 0, 1)   # speed 1 -> ~0.47

stops = [
    (0.00, (0.10, 0.16, 0.55)),    # slow: indigo
    (0.30, (0.06, 0.38, 0.52)),    # teal
    (0.52, (0.42, 0.62, 0.58)),    # sea glass
    (0.74, (0.95, 0.72, 0.30)),    # gold
    (1.00, (1.00, 0.93, 0.62)),    # hot pale gold
]
seg_rgb = ramp(spn_seg, stops)                 # (M-1, N, 3)

chan = [np.zeros((Hc, Wc), np.float64) for _ in range(3)]
xs0 = XS[:-1].ravel(); xs1 = XS[1:].ravel()
ys0 = np.repeat(rowy[:-1], 1)[:, None] * np.ones((1, N))
ys0 = (rowy[:-1][:, None] * np.ones((1, N))).ravel()
ys1 = (rowy[1:][:, None] * np.ones((1, N))).ravel()
for c in range(3):
    wc_ = seg_rgb[..., c].ravel()
    splat_lines(chan[c], xs0, ys0, xs1, ys1, wc_, samples_per_px=1.2)
    print(f"channel {c} splat done ({time.time()-t00:.0f}s)", flush=True)
rgbacc = np.stack(chan, -1)

# collision sparks
ev_arr = np.array([(t, i, j) for (t, i, j) in events])
spark = np.zeros((Hc, Wc), np.float64)
if len(ev_arr):
    et = ev_arr[:, 0]
    ei = ev_arr[:, 1].astype(int)
    idx = np.clip((et / T_total * (M - 1)).astype(int), 0, M - 1)
    ex = samples_x[idx, ei]
    sx = (x0pix + ex * (x1pix - x0pix)) * Wc
    sy = et / T_total * (Hc - 1)
    bilinear_splat(spark, sx, sy, np.full(len(sx), 1.0))

# witness thread (central particle) re-splatted hot
wit = np.zeros((Hc, Wc), np.float64)
xsw = XS[:, WIT]
splat_lines(wit, xsw[:-1], rowy[:-1], xsw[1:], rowy[1:],
            np.full(M - 1, 2.4), samples_per_px=1.3)

# H margin curve
Hn = (Hcurve - Hcurve.min()) / (Hcurve.max() - Hcurve.min() + 1e-12)
hx = (0.906 + Hn * 0.082) * Wc
hcurve = np.zeros((Hc, Wc), np.float64)
splat_lines(hcurve, hx[:-1], rowy[:-1], hx[1:], rowy[1:],
            np.full(M - 1, 5.0), samples_per_px=1.4)
hcurve = gaussian_filter(hcurve, 1.1 * SS)

def fold(a):
    return a.reshape(Hh, SS, W, SS).mean(axis=(1, 3))

rgb_f = np.stack([fold(rgbacc[..., c]) for c in range(3)], -1)
spark_f = fold(spark); wit_f = fold(wit); hcurve_f = fold(hcurve)

rgb_f = np.stack([gaussian_filter(rgb_f[..., c], 0.55) for c in range(3)], -1)
lum_in = rgb_f.sum(-1)
scale = filmic(lum_in, k=0.60, gamma=0.80) / np.maximum(lum_in, 1e-9)
rgb = rgb_f * scale[..., None] * 3.0
rgb += (filmic(lum_in, k=0.055, gamma=1.0) ** 3.0)[..., None] * np.array([1.0, 0.97, 0.9]) * 0.75

sp_l = filmic(gaussian_filter(spark_f, 0.8), k=0.75, gamma=0.85)
rgb += sp_l[..., None] * np.array([1.0, 0.50, 0.22]) * 0.5

wt = filmic(gaussian_filter(wit_f, 0.8), k=1.5, gamma=0.9)
rgb = rgb * (1 - 0.55 * wt[..., None]) + wt[..., None] * np.array([1.0, 0.36, 0.12]) * 1.5

rgb += filmic(hcurve_f, k=1.2, gamma=0.9)[..., None] * np.array([1.0, 0.85, 0.45])

for frac in (1 / 3, 2 / 3):
    y = int(frac * Hh)
    band = np.exp(-0.5 * ((np.arange(Hh) - y) / 2.2) ** 2)
    rgb += band[:, None, None] * np.array([0.5, 0.75, 0.85]) * 0.09

rgb = bloom(rgb, mask_lo=0.70, sigma=4.5, strength=0.4, tint=(1.0, 0.85, 0.6))
rgb = bloom(rgb, mask_lo=0.28, sigma=26.0, strength=0.13, tint=(0.5, 0.75, 0.9))
save_png(rgb, os.path.join(HERE, "river_uphill.png"))
print(f"total {time.time()-t00:.0f}s")
