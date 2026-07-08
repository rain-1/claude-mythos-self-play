#!/usr/bin/env python3
"""
Panel B: The Drain of the Primes.

T(p) = largest prime factor of p+1  maps every prime to a smaller prime
(strict descent for p > 2), so the functional graph on all primes < N is a
single tree draining into the 2 <-> 3 cycle.  (MO front page 2026-07-08 asks
whether T is surjective.)  Radial layout: radius = log p, angular wedge
allocated recursively by subtree mass, streams drawn child -> parent with
brightness/width ~ mass, coloured by drain depth.
"""
import numpy as np, sys, time

def sieve_gpf(N):
    """gpf[n] = greatest prime factor of n, for 0..N (gpf[p]=p iff prime)."""
    isp = np.ones(N + 1, bool); isp[:2] = False
    for q in range(2, int(N ** 0.5) + 1):
        if isp[q]:
            isp[q * q::q] = False
    gpf = np.zeros(N + 1, np.int64)
    for q in np.flatnonzero(isp):                     # ascending: last write wins
        gpf[q::q] = q
    return gpf

def build_tree(N):
    t0 = time.time()
    gpf = sieve_gpf(N + 1)
    primes = np.where(gpf[2:N + 1] == np.arange(2, N + 1))[0] + 2
    parent = gpf[primes + 1]              # T(p)
    # verify claims
    assert parent[0] == 3 and primes[0] == 2          # 2 -> 3
    assert parent[1] == 2 and primes[1] == 3          # 3 -> 2
    assert np.all(parent[2:] < primes[2:]), "descent fails"
    assert np.all(gpf[parent] == parent), "parent not prime"
    print(f"N={N}: {len(primes)} primes, sieve+tree {time.time()-t0:.1f}s")

    idx = np.searchsorted(primes, parent)             # parent index per prime
    assert np.all(primes[idx] == parent)
    n = len(primes)
    # subtree mass: descending p order; children have larger p than parent
    mass = np.ones(n, np.float64)
    order = np.arange(n - 1, 1, -1)                   # skip 3(1) and 2(0) cycle
    pidx = idx
    for i in order:                                    # python loop, ~1e6 it
        mass[pidx[i]] += mass[i]
    mass[0] += mass[1]                                 # fold 3 into 2 for wedges
    # depth from the cycle
    depth = np.zeros(n, np.int32)
    # process ascending p (parents first)
    for i in range(2, n):
        depth[i] = depth[pidx[i]] + 1
    print(f"mass/depth done {time.time()-t0:.1f}s; max depth {depth.max()}")
    return primes, pidx, mass, depth

def layout(primes, pidx, mass, depth):
    """Angles: recursive wedge subdivision by mass; radius = log p."""
    t0 = time.time()
    n = len(primes)
    # children lists via argsort of parent
    order = np.argsort(pidx[2:], kind="stable") + 2    # nodes 2.. sorted by parent
    par_sorted = pidx[order]
    starts = np.searchsorted(par_sorted, np.arange(n))
    ends = np.searchsorted(par_sorted, np.arange(n) + 1)
    theta = np.zeros(n)
    wlo = np.zeros(n); whi = np.zeros(n)
    wlo[0], whi[0] = 0.0, 2 * np.pi                    # node 2 owns the circle
    wlo[1], whi[1] = 0.0, 2 * np.pi                    # node 3 shares it
    theta[0], theta[1] = 0.0, np.pi                    # cycle partners opposite
    # BFS by depth so parents are set first
    for d in range(0, depth.max()):
        nodes = np.where(depth == d)[0]
        for u in nodes:
            ch = order[starts[u]:ends[u]]
            ch = ch[ch >= 2]
            if len(ch) == 0:
                continue
            ch = ch[np.argsort(primes[ch])]            # order by size: swirl
            w = mass[ch]
            w = w / w.sum()
            lo = wlo[u]
            span = whi[u] - wlo[u]
            cum = np.concatenate([[0], np.cumsum(w)])
            clo = lo + span * cum[:-1]
            chi = lo + span * cum[1:]
            wlo[ch] = clo; whi[ch] = chi
            theta[ch] = 0.5 * (clo + chi)
    print(f"layout {time.time()-t0:.1f}s")
    r = np.log(primes.astype(np.float64))
    return r, theta

def splat(primes, pidx, mass, depth, r, theta, S=1024, ss=2,
          gamma=0.80, swirl=0.45):
    """Additive splat of all edges child->parent as polar-interp streams."""
    t0 = time.time()
    W = S * ss
    n = len(primes)
    rmax = r.max() * 1.04
    scale = (W / 2 - 8) / rmax
    cx = W / 2.0

    # palette by depth (core -> rim)
    stops = np.array([
        [1.00, 0.86, 0.55],   # molten gold (core)
        [1.00, 0.55, 0.20],   # amber
        [0.85, 0.25, 0.16],   # ember red
        [0.55, 0.12, 0.35],   # magenta-wine
        [0.22, 0.16, 0.60],   # indigo
        [0.10, 0.35, 0.55],   # deep teal (rim)
    ], np.float64)
    # depth -> palette position via mass-weighted CDF (palette by frequency)
    dmax = depth.max()
    wts = np.bincount(depth, weights=mass ** gamma, minlength=dmax + 1)
    cdf = np.cumsum(wts) / wts.sum()
    dpos = np.concatenate([[0.0], cdf])[:dmax + 1]     # position of each depth

    acc = np.zeros((W, W, 3), np.float32)
    nodes = np.arange(2, n)
    # edge endpoints in polar
    r1, th1 = r[nodes], theta[nodes]
    r0, th0 = r[pidx[nodes]], theta[pidx[nodes]]
    dth = (th0 - th1 + np.pi) % (2 * np.pi) - np.pi    # shortest way
    m = mass[nodes] ** gamma
    dpt = depth[nodes]
    rng = np.random.default_rng(7)
    basin_drift = rng.uniform(-1, 1, n)
    drift = basin_drift[pidx[nodes]] * (0.15 + 0.85 * np.abs(r1 - r0) / rmax)

    # pixel length estimate for sample counts
    ell = np.abs(r1 - r0) * scale + np.abs(dth) * r1 * scale
    ns = np.clip((ell * 1.0).astype(np.int64), 2, 2500)
    tot = ns.sum()
    print(f"edges {len(nodes)}, samples {tot/1e6:.1f}M")

    # chunk by EDGES so per-chunk sample arrays stay small
    csum = np.cumsum(ns)
    starts_e = [0]
    TARGET = 6_000_000
    nextgoal = TARGET
    for i_e in range(len(ns)):
        if csum[i_e] >= nextgoal:
            starts_e.append(i_e + 1)
            nextgoal = csum[i_e] + TARGET
    starts_e.append(len(ns))
    for ci in range(len(starts_e) - 1):
        ea, eb = starts_e[ci], starts_e[ci + 1]
        if ea >= eb:
            continue
        nsb = ns[ea:eb]
        e = np.repeat(np.arange(ea, eb), nsb)
        cum = np.arange(nsb.sum()) - np.repeat(np.cumsum(nsb) - nsb, nsb)
        sv = (cum + 0.5) / np.repeat(nsb, nsb)
        b = csum[eb - 1]
        ease = sv * (2 - sv)                            # e'(1)=0: merge at parent
        rr = r1[e] + (r0[e] - r1[e]) * sv
        curl = swirl * np.sin(np.pi * sv) * drift[e]
        tt = th1[e] + dth[e] * ease + curl
        x = cx + scale * rr * np.cos(tt)
        y = cx + scale * rr * np.sin(tt)
        wgt = (m[e] * (ell[e] / ns[e])).astype(np.float32)
        dd = dpos[np.clip(dpt[e], 0, dmax)] * (len(stops) - 1)
        i0 = np.clip(dd.astype(np.int64), 0, len(stops) - 2)
        f = (dd - i0)[:, None]
        col = stops[i0] * (1 - f) + stops[i0 + 1] * f
        xi = np.floor(x).astype(np.int64); yi = np.floor(y).astype(np.int64)
        fx = (x - xi).astype(np.float32); fy = (y - yi).astype(np.float32)
        ok = (xi >= 0) & (xi < W - 1) & (yi >= 0) & (yi < W - 1)
        xi, yi, fx, fy = xi[ok], yi[ok], fx[ok], fy[ok]
        wgt = wgt[ok]; col = col[ok].astype(np.float32)
        for c in range(3):
            v = wgt * col[:, c]
            np.add.at(acc[:, :, c], (yi, xi), v * (1 - fx) * (1 - fy))
            np.add.at(acc[:, :, c], (yi, xi + 1), v * fx * (1 - fy))
            np.add.at(acc[:, :, c], (yi + 1, xi), v * (1 - fx) * fy)
            np.add.at(acc[:, :, c], (yi + 1, xi + 1), v * fx * fy)
        print(f"  chunk {b/1e6:.0f}M ({time.time()-t0:.1f}s)", flush=True)
    # the drain itself: bright core stars at 2 and 3
    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
    core_amp = float(np.percentile(acc.max(2)[acc.max(2) > 0], 99.9)) if (acc.max(2) > 0).any() else 1.0
    for node, hue in ((0, np.array([1.0, 0.88, 0.55])), (1, np.array([1.0, 0.72, 0.38]))):
        px = cx + scale * r[node] * np.cos(theta[node])
        py = cx + scale * r[node] * np.sin(theta[node])
        g = np.exp(-(((xx - px) ** 2 + (yy - py) ** 2) / (2 * (0.008 * W) ** 2)))
        acc += (core_amp * 1.2) * g[..., None] * hue[None, None, :].astype(np.float32)
    return acc

def tone(acc, S, k=1.0, blur=1.6, halo=0.25):
    from scipy.ndimage import gaussian_filter
    from PIL import Image
    W = acc.shape[0]
    img = acc.copy()
    lum = img.mean(2)
    p = np.percentile(lum[lum > 0], 99.2) if (lum > 0).any() else 1.0
    img /= max(p, 1e-9)
    soft = np.stack([gaussian_filter(img[:, :, c], blur * W / 2048) for c in range(3)], -1)
    img = img + halo * soft
    img = 1.0 - np.exp(-k * img)
    img = img ** (1 / 1.18)
    out = (img.clip(0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(out[::-1]).resize((S, S), Image.LANCZOS)
    return im

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    S = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    tag = sys.argv[3] if len(sys.argv) > 3 else "a"
    primes, pidx, mass, depth = build_tree(N)
    r, theta = layout(primes, pidx, mass, depth)
    acc = splat(primes, pidx, mass, depth, r, theta, S=S, ss=2)
    tone(acc, S).save(f"draft_river_{S}_{tag}.png")
    print("saved")
