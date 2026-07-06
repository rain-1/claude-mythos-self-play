"""Hero: golden pair + regular island threads at 8192 (SSAA x2 -> 4096).
Also: per-x-bin barrier verification (seas vs golden curves)."""
import numpy as np
import stdmap_core as sm

S8 = 8192
K = 0.969
GOLD = (np.sqrt(5) - 1) / 2
P_GOLD = 0.664601475   # from bisection at x0=0
P_MIRR = 0.335398525
NBIN = 4096
rng = np.random.default_rng(23)

def splat_bilinear(x, p, K, nsteps, S, weight, per_seed_w=None, record=None):
    acc = np.zeros(S * S, np.float32)
    x = np.asarray(x, np.float64).copy(); p = np.asarray(p, np.float64).copy()
    N = x.size
    wbase = np.full(N, weight, np.float32) if per_seed_w is None else per_seed_w.astype(np.float32)
    BATCH = max(1, 2 ** 20 // max(N, 1))
    bx = np.empty((BATCH, N)); bp = np.empty((BATCH, N))
    bmin = np.full(NBIN, 2.0); bmax = np.full(NBIN, -1.0)
    filled = 0
    for s in range(nsteps):
        x, p = sm.step(x, p, K)
        bx[filled] = x; bp[filled] = p % 1.0
        filled += 1
        if filled == BATCH or s == nsteps - 1:
            fx = bx[:filled].ravel(); fyv = bp[:filled].ravel()
            gx = fx * S; gy = fyv * S
            ix = gx.astype(np.int64); iy = gy.astype(np.int64)
            ax = (gx - ix).astype(np.float32); ay = (gy - iy).astype(np.float32)
            ix1 = (ix + 1) % S; iy1 = (iy + 1) % S
            ww = np.tile(wbase, filled)
            np.add.at(acc, iy * S + ix, ww * (1 - ax) * (1 - ay))
            np.add.at(acc, iy * S + ix1, ww * ax * (1 - ay))
            np.add.at(acc, iy1 * S + ix, ww * (1 - ax) * ay)
            np.add.at(acc, iy1 * S + ix1, ww * ax * ay)
            if record is not None:
                xb = (fx * NBIN).astype(np.int64)
                np.minimum.at(bmin, xb, fyv)
                np.maximum.at(bmax, xb, fyv)
            filled = 0
    return acc.reshape(S, S), (bmin, bmax)

# --- golden pair: build 128-phase ensembles ON each circle, then iterate ---
def circle_ensemble(p0, nphase=128):
    x = np.array([0.0]); p = np.array([p0])
    xs = np.empty(nphase); ps = np.empty(nphase)
    for i in range(nphase):
        x, p = sm.step(x, p, K)
        xs[i] = x[0]; ps[i] = p[0]
    return xs, ps

xg, pg = circle_ensemble(P_GOLD)
xm, pm = circle_ensemble(P_MIRR)
T_GOLD = 60000
acc_g, (gmin, gmax) = splat_bilinear(xg, pg, K, T_GOLD, S8, 1.0, record=True)
acc_m, (mmin, mmax) = splat_bilinear(xm, pm, K, T_GOLD, S8, 1.0, record=True)
np.save("hero_gold8.npy", acc_g + acc_m)
np.save("hero_gold_band.npy", np.stack([gmin, gmax, mmin, mmax]))
print("gold pair splatted; golden band p=[%.4f,%.4f] mirror band p=[%.4f,%.4f]"
      % (gmin.min(), gmax.max(), mmin.min(), mmax.max()), flush=True)

# --- regular threads ---
n_side = 140
gxx, gpp = np.meshgrid(np.linspace(0, 1, n_side, endpoint=False) + 0.5 / n_side,
                       np.linspace(0, 1, n_side, endpoint=False) + 0.5 / n_side)
x0 = gxx.ravel() + rng.normal(0, 0.0015, n_side ** 2)
p0 = gpp.ravel() + rng.normal(0, 0.0015, n_side ** 2)
lam = sm.lyapunov_classify(x0, p0, K, nsteps=1200)
reg = np.where(lam <= 0.02)[0]
keep = rng.choice(reg, size=min(1500, reg.size), replace=False)
T = 6000
wseed = (0.55 + 0.45 * rng.random(keep.size)) / T
acc_reg, _ = splat_bilinear(x0[keep], p0[keep], K, T, S8, 1.0, per_seed_w=wseed)
np.save("hero_reg8.npy", acc_reg)
print("threads done: %d seeds" % keep.size, flush=True)

# --- BARRIER VERIFICATION: per-x-bin sea extremes vs golden band ---
gold_lo = gmin  # per-bin min of golden curve
mirr_hi = mmax
inner_hi = np.full(NBIN, -1.0); inner_lo = np.full(NBIN, 2.0)
outer = []
for wid, which in [(0, "inner"), (1, "inner"), (2, "outer"), (3, "outer")]:
    ext = np.load("hero_ext_%s_%d.npy" % (which, wid))
    if which == "inner":
        inner_lo = np.minimum(inner_lo, ext[0]); inner_hi = np.maximum(inner_hi, ext[1])
    else:
        outer.append(ext)
ok_top = np.all(inner_hi < gold_lo)
ok_bot = np.all(inner_lo > mirr_hi)
margin_top = np.min(gold_lo - inner_hi)
margin_bot = np.min(inner_lo - mirr_hi)
print("BARRIER: inner sea below golden curve in every x-bin: %s (min margin %.2e)" % (ok_top, margin_top))
print("BARRIER: inner sea above mirror curve in every x-bin: %s (min margin %.2e)" % (ok_bot, margin_bot))
# outer sea must never enter the strip between the two curves per-x
viol = 0
for ext in outer:
    lo, hi = ext[0], ext[1]
    # outer occupies [0, mirror) and (golden, 1] per bin; check it never lies strictly inside
    inside = (lo > mmin) & (hi < gmax)   # crude whole-orbit test per bin
    viol += int(np.sum((hi < gold_lo) & (lo > mirr_hi)))
print("outer-sea bins fully inside the forbidden strip:", viol, "(expect 0)")
total_pts = 4 * 8192 * 125000
print("total sea points recorded: %.1e per sea" % (total_pts / 2))
