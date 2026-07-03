"""Abelian sandpile: stabilize N grains dropped on one site of Z^2.

Engine: parallel multi-toppling (t = h//4) over an incrementally-tracked active
bounding box.  Multigrid acceleration: stabilize N/4, upsample its odometer
u_{4N}(2x) ~= 4 u_N(x), shave it to stay <= the true odometer, apply as forced
topplings (h += L u0), then relax the remainder legally.

Correctness (least-action principle): if u0 <= u* pointwise then forcing u0 and
stabilizing yields exactly the true stabilization.  We VERIFY exact array
equality vs the naive engine on small N, and equality across different shave
margins at larger N.
"""
import numpy as np, time, sys

SCRATCH = "/tmp/claude-0/-home-user-claude-mythos-self-play/14486fce-1a7e-527f-9de4-a144326c3b0e/scratchpad"

def relax(h, u=None, report_every=0):
    """Parallel multi-topple until stable. Returns h, u, sweeps.
    Tracks active bbox incrementally (unstable set only grows by 1 cell/sweep)."""
    if u is None: u = np.zeros_like(h)
    S0, S1 = h.shape
    ys, xs = np.nonzero(h >= 4)
    if len(ys) == 0: return h, u, 0
    y0, y1 = ys.min(), ys.max() + 1
    x0, x1 = xs.min(), xs.max() + 1
    sweeps = 0
    t0 = time.time()
    while True:
        # pad box by 1 (toppling can destabilize one ring out)
        y0 = max(y0 - 1, 0); x0 = max(x0 - 1, 0)
        y1 = min(y1 + 1, S0); x1 = min(x1 + 1, S1)
        hs = h[y0:y1, x0:x1]
        # only sites >= 4 topple; hs may hold negative values during a staged
        # warm start and >> on negatives would anti-topple (illegal)
        t = np.where(hs >= 4, hs >> 2, 0)
        if not t.any():
            break
        hs -= t << 2
        hs[1:, :] += t[:-1, :]; hs[:-1, :] += t[1:, :]
        hs[:, 1:] += t[:, :-1]; hs[:, :-1] += t[:, 1:]
        u[y0:y1, x0:x1] += t
        # shrink box to unstable extent for next round
        un = hs >= 4
        ry = un.any(axis=1); rx = un.any(axis=0)
        if not ry.any():
            break
        iy = np.nonzero(ry)[0]; ix = np.nonzero(rx)[0]
        y1 = y0 + iy[-1] + 1; y0 = y0 + iy[0]
        x1 = x0 + ix[-1] + 1; x0 = x0 + ix[0]
        sweeps += 1
        if report_every and sweeps % report_every == 0:
            print(f"  sweep {sweeps}  box {y1-y0}x{x1-x0}  {time.time()-t0:.1f}s", flush=True)
    return h, u, sweeps

def lap_apply(u):
    out = -4 * u
    out[1:, :] += u[:-1, :]; out[:-1, :] += u[1:, :]
    out[:, 1:] += u[:, :-1]; out[:, :-1] += u[:, 1:]
    return out

def upsample2_centered(u, S_new):
    """Center-aligned 2x bilinear upsample of odometer u (S_old odd) into an
    S_new x S_new grid (odd): fine cell at offset d from the fine center samples
    the coarse field at offset d/2 from the coarse center."""
    from scipy.ndimage import map_coordinates
    S_old = u.shape[0]
    c_old = S_old // 2; c_new = S_new // 2
    idx = (np.arange(S_new) - c_new) / 2.0 + c_old
    yy, xx = np.meshgrid(idx, idx, indexing="ij")
    out = map_coordinates(u.astype(np.float64), [yy, xx], order=1, mode="constant", cval=0.0)
    return out

def radius_for(N):
    return int(np.sqrt(N / (np.pi * 2.1)))

def grid_for(N):
    S = 2 * radius_for(N) + 32
    return S + 1 - (S % 2)  # odd

def pile_naive(N):
    S = grid_for(N)
    h = np.zeros((S, S), np.int64)
    h[S // 2, S // 2] = N
    h, u, sw = relax(h)
    return h, u, sw

def staged(N_target, shave=0.98, margin=800, N0=1 << 12, report=True):
    Ns = [N_target]
    while Ns[-1] > N0: Ns.append(Ns[-1] // 4)
    Ns = Ns[::-1]
    S = grid_for(Ns[0])
    h = np.zeros((S, S), np.int64); h[S // 2, S // 2] = Ns[0]
    t0 = time.time()
    h, u, sw = relax(h)
    if report: print(f"stage N={Ns[0]:>12,}  S={S}  sweeps={sw:>7}  {time.time()-t0:.1f}s", flush=True)
    for N in Ns[1:]:
        Sn = grid_for(N)
        c_new = Sn // 2
        uf = upsample2_centered(u, Sn) * 4.0 * shave
        u0 = np.maximum(np.floor(uf) - margin, 0).astype(np.int64)
        # safety bands where the scaled guess is least reliable:
        # (a) the core, where |grad u| ~ N/|x| dwarfs any shave;
        # (b) the rim, where the support radius has finite-size corrections.
        d2 = (np.arange(Sn) - c_new) ** 2
        core = d2[:, None] + d2[None, :] < 6 ** 2
        u0[core] = 0
        u0[u0 < 50] = 0
        h = np.zeros((Sn, Sn), np.int64); h[c_new, c_new] = N
        h += lap_apply(u0)
        t0 = time.time()
        h, v, sw = relax(h)
        u = u0 + v
        if report: print(f"stage N={N:>12,}  S={Sn}  sweeps={sw:>7}  {time.time()-t0:.1f}s", flush=True)
    assert h.min() >= 0 and h.max() <= 3, (h.min(), h.max())
    assert h.sum() == N_target, (h.sum(), N_target)
    assert h[0, :].max() == 0 and h[-1, :].max() == 0 and h[:, 0].max() == 0 and h[:, -1].max() == 0
    return h, u

def relax_folded(f, u=None, report_every=0):
    """Quadrant-folded parallel multi-topple. f[i,j] = h(i,j), i,j>=0, with the
    pile symmetric under (i,j) -> (+-i,+-j).  Mirror contributions: the virtual
    row -1 is row 1, virtual col -1 is col 1.
    Optimized: preallocated t buffer, in-place ops.
    (t = maximum(f,0)>>2 equals the masked shift: f in [0,3] -> 0, f<0 -> 0.)"""
    if u is None: u = np.zeros_like(f)
    t = np.empty_like(f)
    t4 = np.empty_like(f)
    sweeps = 0
    t0 = time.time()
    while True:
        np.maximum(f, 0, out=t)
        t >>= 2
        if not t.any():
            break
        np.left_shift(t, 2, out=t4)
        f -= t4
        f[1:, :] += t[:-1, :]; f[:-1, :] += t[1:, :]
        f[:, 1:] += t[:, :-1]; f[:, :-1] += t[:, 1:]
        f[0, :] += t[1, :]   # mirror across y=0 axis
        f[:, 0] += t[:, 1]   # mirror across x=0 axis
        u += t
        sweeps += 1
        if report_every and sweeps % report_every == 0:
            print(f"  folded sweep {sweeps}  {time.time()-t0:.1f}s", flush=True)
    return f, u, sweeps

def lap_apply_folded(u):
    out = -4 * u
    out[1:, :] += u[:-1, :]; out[:-1, :] += u[1:, :]
    out[:, 1:] += u[:, :-1]; out[:, :-1] += u[:, 1:]
    out[0, :] += u[1, :]
    out[:, 0] += u[:, 1]
    return out

def unfold(f):
    R = f.shape[0] - 1
    S = 2 * R + 1
    out = np.empty((S, S), f.dtype)
    out[R:, R:] = f
    out[R:, :R] = f[:, :0:-1]
    out[:R, :] = out[R + 1:, :][::-1, :]
    return out

def upsample2_folded(u, R_new):
    """Folded odometer u[(R_old+1)^2] -> (R_new+1)^2, fine (i,j) samples coarse (i/2, j/2)."""
    from scipy.ndimage import map_coordinates
    idx = np.arange(R_new + 1) / 2.0
    yy, xx = np.meshgrid(idx, idx, indexing="ij")
    return map_coordinates(u.astype(np.float64), [yy, xx], order=1, mode="constant", cval=0.0)

def staged_folded(N_target, shave=0.995, N0=1 << 12, report=True, dtype=np.int64):
    Ns = [N_target]
    while Ns[-1] > N0: Ns.append(Ns[-1] // 4)
    Ns = Ns[::-1]
    R = grid_for(Ns[0]) // 2
    f = np.zeros((R + 1, R + 1), dtype); f[0, 0] = Ns[0]
    t0 = time.time()
    f, u, sw = relax_folded(f, u=np.zeros((R + 1, R + 1), dtype))
    if report: print(f"stage N={Ns[0]:>12,}  R={R}  sweeps={sw:>7}  {time.time()-t0:.1f}s", flush=True)
    for N in Ns[1:]:
        Rn = grid_for(N) // 2
        margin = max(150, int(2.5 * np.sqrt(u.max())))
        uf = upsample2_folded(u, Rn) * 4.0 * shave
        u0 = np.maximum(np.floor(uf) - margin, 0).astype(dtype)
        ii = np.arange(Rn + 1)
        core = ii[:, None] ** 2 + ii[None, :] ** 2 < 6 ** 2
        u0[core] = 0
        u0[u0 < 50] = 0
        f = np.zeros((Rn + 1, Rn + 1), dtype); f[0, 0] = N
        f += lap_apply_folded(u0)
        t0 = time.time()
        f, v, sw = relax_folded(f)
        u = u0 + v
        if report: print(f"stage N={N:>12,}  R={Rn}  margin={margin}  sweeps={sw:>7}  {time.time()-t0:.1f}s", flush=True)
    # invariants: stable, non-negative, mass conserved, border empty
    assert f.min() >= 0 and f.max() <= 3, (f.min(), f.max())
    mass = int(f[0, 0]) + 2 * int(f[0, 1:].sum()) + 2 * int(f[1:, 0].sum()) + 4 * int(f[1:, 1:].sum())
    assert mass == N_target, (mass, N_target)
    assert f[-1, :].max() == 0 and f[:, -1].max() == 0
    return f, u

def center_crop_equal(a, b):
    s = min(a.shape[0], b.shape[0])
    ca = a[(a.shape[0]-s)//2:(a.shape[0]+s)//2, (a.shape[0]-s)//2:(a.shape[0]+s)//2]
    cb = b[(b.shape[0]-s)//2:(b.shape[0]+s)//2, (b.shape[0]-s)//2:(b.shape[0]+s)//2]
    return np.array_equal(ca, cb)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "scaling"
    if mode == "scaling":
        for e in (14, 16, 18):
            N = 1 << e
            t0 = time.time(); h, u, sw = pile_naive(N); t1 = time.time()
            print(f"naive N=2^{e}: sweeps={sw}, {t1-t0:.1f}s, grid={h.shape[0]}", flush=True)
    elif mode == "verify":
        for e in (16, 18):
            N = 1 << e
            h1, _, _ = pile_naive(N)
            h2, _ = staged(N, report=False)
            h3, _ = staged(N, shave=0.90, margin=2, report=False)
            print(f"N=2^{e}: staged==naive {center_crop_equal(h1,h2)}, shave90==naive {center_crop_equal(h1,h3)}", flush=True)
    elif mode == "run":
        e = int(sys.argv[2])
        N = 1 << e
        t0 = time.time()
        h, u = staged(N)
        np.save(f"{SCRATCH}/pile_{e}.npy", h.astype(np.uint8))
        print(f"total {time.time()-t0:.1f}s, grid {h.shape[0]}", flush=True)
    elif mode == "runbig":
        N = int(sys.argv[2])
        t0 = time.time()
        f, u = staged_folded(N, dtype=np.int32)
        np.save(f"{SCRATCH}/pile_folded_h.npy", f.astype(np.uint8))
        np.save(f"{SCRATCH}/pile_folded_u.npy", u)
        print(f"total {time.time()-t0:.1f}s, folded grid {f.shape[0]}", flush=True)
