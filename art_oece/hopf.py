"""Hopf fibration: S^3 -> S^2, fibers stereographically projected to R^3,
rendered as luminous additive threads with depth dimming.

Fiber over base (sin th cos ph, sin th sin ph, cos th):
    z1 = e^{i(t+ph)} cos(th/2),  z2 = e^{i t} sin(th/2),  t in [0,2pi)
Stereographic projection from (0,0,0,1) (w = Im z2 here):
    (x1,y1,x2,y2) -> (x1, y1, x2)/(1 - y2)
Verified: Hopf map h(z1,z2) = (2 Re z1 conj(z2), 2 Im z1 conj(z2), |z1|^2-|z2|^2).
"""
import numpy as np
import time, sys, os

SCRATCH = "/tmp/claude-0/-home-user-claude-mythos-self-play/14486fce-1a7e-527f-9de4-a144326c3b0e/scratchpad"

def fiber_points(theta, phi, nt):
    """Points along one fiber in R^3 (stereographic). Returns (nt,3)."""
    t = np.linspace(0, 2 * np.pi, nt, endpoint=False)
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    z1 = np.exp(1j * (t + phi)) * c
    z2 = np.exp(1j * t) * s
    x1, y1 = z1.real, z1.imag
    x2, y2 = z2.real, z2.imag
    d = 1.0 - y2
    d = np.where(np.abs(d) < 1e-9, 1e-9, d)
    return np.stack([x1 / d, y1 / d, x2 / d], axis=1)

def verify():
    th, ph = 1.1, 2.3
    t = np.linspace(0, 2 * np.pi, 7)
    z1 = np.exp(1j * (t + ph)) * np.cos(th / 2)
    z2 = np.exp(1j * t) * np.sin(th / 2)
    hx = 2 * (z1 * np.conj(z2)).real
    hy = 2 * (z1 * np.conj(z2)).imag
    hz = np.abs(z1) ** 2 - np.abs(z2) ** 2
    base = np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])
    err = max(np.abs(hx - base[0]).max(), np.abs(hy - base[1]).max(), np.abs(hz - base[2]).max())
    print("hopf map constancy along fiber, err =", err)
    assert err < 1e-12

def rotmat(ax, ay):
    ca, sa = np.cos(ax), np.sin(ax)
    cb, sb = np.cos(ay), np.sin(ay)
    Rx = np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]])
    Ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])
    return Ry @ Rx

def bilin_add(buf, x, y, w):
    """Additive bilinear splat into 2-D buf. x,y float arrays, w weights."""
    H, W = buf.shape
    x0 = np.floor(x).astype(np.int64); y0 = np.floor(y).astype(np.int64)
    fx = x - x0; fy = y - y0
    for dx, dy, ww in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                       (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xi = x0 + dx; yi = y0 + dy
        m = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
        np.add.at(buf, (yi[m], xi[m]), (w * ww)[m])

def okhue(h):
    """Curated bright cyclic-ish palette: h in [0,1) -> rgb (0..1). Thin-film feel."""
    a = 2 * np.pi * h
    r = 0.62 + 0.38 * np.cos(a)
    g = 0.55 + 0.42 * np.cos(a - 2.3)
    b = 0.62 + 0.38 * np.cos(a - 4.2)
    return np.stack([r, g, b], axis=-1)

def ramp_warmcool(t):
    """Non-cyclic curated ramp t in [0,1]: molten gold -> rose -> violet -> deep teal."""
    stops = np.array([
        [1.00, 0.86, 0.45],
        [1.00, 0.62, 0.32],
        [0.94, 0.38, 0.44],
        [0.66, 0.32, 0.72],
        [0.26, 0.42, 0.82],
        [0.10, 0.62, 0.66],
    ])
    x = np.clip(t, 0, 1) * (len(stops) - 1)
    i = np.minimum(x.astype(int), len(stops) - 2)
    f = (x - i)[..., None]
    return stops[i] * (1 - f) + stops[i + 1] * f

def bloom(img, sig1=2.0, sig2=9.0, a1=0.35, a2=0.18, thresh=0.55):
    from scipy.ndimage import gaussian_filter
    lum = img.mean(axis=-1)
    m = np.clip((lum - thresh) / (1 - thresh), 0, 1)[..., None] * img
    out = img.copy()
    for s, a in ((sig1, a1), (sig2, a2)):
        for c in range(3):
            out[..., c] += a * gaussian_filter(m[..., c], s)
    return out

def render(S=900, mode="spiral", nf=700, seed=0, fname="hopf_proto.png",
           cam=(0.42, 0.31), persp=3.6, scale=0.34, samp_per_px=2.4,
           theta_rng=(0.12, 3.02), gamma=0.85, expo=2.2, per_fiber_norm=True,
           huemode="phi", use_bloom=False, energy=900.0, nrings=9,
           ramp_reverse=False, exceptional=False, raw=False):
    """mode: 'spiral' Fibonacci sphere spiral; 'rings' latitude rings."""
    t0 = time.time()
    rng = np.random.default_rng(seed)
    if mode == "spiral":
        i = np.arange(nf) + 0.5
        c0, c1 = np.cos(theta_rng[0]), np.cos(theta_rng[1])
        cth = c0 + (c1 - c0) * i / nf
        thetas = np.arccos(cth)
        phis = (i * (np.pi * (3 - np.sqrt(5)))) % (2 * np.pi)
    else:
        nring = nrings
        thetas_r = np.linspace(theta_rng[0], theta_rng[1], nring)
        per = nf // nring
        thetas = np.repeat(thetas_r, per)
        phis = np.concatenate([np.linspace(0, 2 * np.pi, per, endpoint=False) + 0.13 * k
                               for k in range(nring)])
    R = rotmat(*cam)
    accs = [np.zeros((S, S), np.float64) for _ in range(3)]
    specials = []   # (theta, phi, energy_mult, rgb_override)
    if exceptional:
        specials = [(1e-4, 0.0, 2.5, np.array([1.0, 0.93, 0.72])),      # core circle
                    (np.pi - 1e-4, 0.0, 5.0, np.array([1.0, 0.97, 0.88]))]  # the axis line
    fibers = [(thetas[k], phis[k], 1.0, None) for k in range(len(thetas))] + specials
    for th, ph, emult, rgb_over in fibers:
        # sample count adaptive to projected size: fibers near projection pole are huge
        p = fiber_points(th, ph, 400)
        p = p @ R.T
        z = p @ np.array([0, 0, 1.0])
        # perspective
        depth = persp + p[:, 2]
        if depth.min() < 0.4:  # fiber passes too close/behind camera: clip samples
            pass
        # estimate screen-space arclength to choose sample count
        xs = p[:, 0] / depth * persp * scale * S + S * 0.53
        ys = p[:, 1] / depth * persp * scale * S + S * 0.52
        seg = np.hypot(np.diff(xs, append=xs[:1]), np.diff(ys, append=ys[:1]))
        L = seg.sum()
        nt = int(min(max(L * samp_per_px, 500), 500000))
        p = fiber_points(th, ph, nt) @ R.T
        depth = persp + p[:, 2]
        good = depth > 0.4
        xs = p[:, 0] / depth * persp * scale * S + S * 0.53
        ys = p[:, 1] / depth * persp * scale * S + S * 0.52
        # brightness: depth-dimmed, per-sample spacing-compensated (uniform t samples
        # concentrate near the projection pole -> compensate by segment length)
        seg = np.hypot(np.diff(xs, append=xs[:1]), np.diff(ys, append=ys[:1]))
        # energy ~ screen arclength; kill splats whose spacing exceeds line
        # continuity (they'd render as a trail of dots, not a thread)
        w = np.where(seg > 6.0, 0.0, seg)
        dn = (depth - depth.min()) / max(depth.max() - depth.min(), 1e-9)
        w = w * (0.35 + 0.65 * (1 - dn) ** 1.6)
        w = np.where(good, w, 0)
        if per_fiber_norm:
            w = w / max(w.sum(), 1e-9) * energy * emult  # each fiber same total energy
        litfrac = th / np.pi
        # map the used theta range onto the full ramp
        tfrac = np.clip((th - theta_rng[0]) / (theta_rng[1] - theta_rng[0]), 0, 1)
        if ramp_reverse:
            tfrac = 1 - tfrac
        if rgb_over is not None:
            rgb = rgb_over
        elif huemode == "phi":
            rgb = okhue((ph / (2 * np.pi)) % 1.0) * (0.55 + 0.45 * np.sin(np.pi * litfrac))
        elif huemode == "theta":
            rgb = ramp_warmcool(1 - tfrac)
        else:  # theta hue, phi brightness shimmer
            rgb = ramp_warmcool(1 - tfrac) * (0.75 + 0.25 * np.cos(3 * ph))
        for c in range(3):
            bilin_add(accs[c], xs, ys, w * rgb[c])
    img = np.stack(accs, axis=-1)
    if raw:
        return img
    img = img / np.percentile(img, 99.7)
    img = 1 - np.exp(-expo * img)
    if use_bloom:
        img = bloom(img)
    img = np.clip(img, 0, 1) ** gamma
    from PIL import Image
    Image.fromarray((img * 255).astype(np.uint8)).save(os.path.join(SCRATCH, fname))
    print(fname, f"{time.time()-t0:.1f}s", flush=True)

def render_final(S_out=2048, SS=2, fname="02_only_the_links_are_real.png", outdir=None,
                 expo=2.2, gamma=0.85, use_bloom=True, **kw):
    """Supersampled final: render at S_out*SS, fatten hairlines (~0.6*SS) and scale
    line energy by SS so the downscale doesn't kill thread brightness."""
    from scipy.ndimage import gaussian_filter
    from PIL import Image
    S = S_out * SS
    t0 = time.time()
    img = render(S=S, raw=True, energy=kw.pop("energy", 900.0) * SS, **kw)
    for c in range(3):
        img[..., c] = gaussian_filter(img[..., c], 0.6 * SS)
    img = img / np.percentile(img, 99.7)
    img = 1 - np.exp(-expo * img)
    if use_bloom:
        img = bloom(img)
    img = np.clip(img, 0, 1) ** gamma
    im = Image.fromarray((img * 255).astype(np.uint8)).resize((S_out, S_out), Image.LANCZOS)
    path = os.path.join(outdir or SCRATCH, fname)
    im.save(path)
    print(path, f"{time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    verify()
    if len(sys.argv) > 1 and sys.argv[1] == "proto":
        render(mode="spiral", nf=500, fname="hopf_spiral.png")
        render(mode="rings", nf=540, fname="hopf_rings.png")
    if len(sys.argv) > 1 and sys.argv[1] == "proto2":
        render(mode="rings", nf=660, nrings=11, huemode="theta", fname="hopf_r_theta.png")
        render(mode="spiral", nf=650, huemode="theta", fname="hopf_s_theta.png")
        render(mode="spiral", nf=650, huemode="phi", scale=0.30, cam=(0.35, 0.22),
               use_bloom=True, fname="hopf_s_phi2.png")
    if len(sys.argv) > 1 and sys.argv[1] == "proto3":
        render(mode="rings", nf=780, nrings=13, huemode="theta", theta_rng=(0.18, 2.55),
               exceptional=True, fname="hopf_A.png")
        render(mode="rings", nf=780, nrings=13, huemode="theta", theta_rng=(0.18, 2.55),
               ramp_reverse=True, exceptional=True, fname="hopf_B.png")
        render(mode="spiral", nf=900, huemode="theta", theta_rng=(0.15, 2.75),
               ramp_reverse=True, exceptional=True, fname="hopf_C.png")
