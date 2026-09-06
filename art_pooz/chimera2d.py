"""chimera2d.py — 2-D nonlocally coupled Kuramoto phase oscillators on a torus.

    dθ/dt (x) = ω − K ∫ G(x−y) sin(θ(x) − θ(y) + α) dy

Kernel G: normalised, isotropic (exponential-like via a screened-Poisson Green's
function or a Gaussian), convolution by FFT.  With α a little below π/2 the
system supports SPIRAL-WAVE CHIMERAS (Shima–Kuramoto 2004; Martens–Laing–
Strogatz 2010): rotating spiral arms of phase-locked oscillators around a core
of drifting, incoherent ones.  On a torus the total topological charge is 0, so
the cores come in ± pairs.
"""
import numpy as np, time, sys, json

def kernel(N, L, kind, R):
    """returns FFT of a normalised kernel on an N×N periodic grid of side L."""
    x = (np.arange(N) - N // 2) * (L / N)
    X, Y = np.meshgrid(x, x, indexing='ij')
    r = np.hypot(X, Y)
    if kind == 'gauss':
        G = np.exp(-0.5 * (r / R) ** 2)
    elif kind == 'exp':
        G = np.exp(-r / R)
    elif kind == 'k0':               # screened Poisson (Shima–Kuramoto)
        from scipy.special import k0
        rr = np.maximum(r, 0.25 * L / N)
        G = k0(rr / R)
    elif kind == 'top':
        G = (r <= R).astype(float)
    G = np.fft.ifftshift(G)
    G /= G.sum()
    return np.fft.rfft2(G)

OPEN = {'on': False, 'Ghat2': None, 'norm': None}
FREQWIN = {'T': 0.0, 'omega': None, 'Rbar': None}

def order_field(theta, Ghat):
    e = np.exp(1j * theta)
    if OPEN['on']:
        N = theta.shape[0]
        pad = np.zeros((2 * N, 2 * N), complex); pad[:N, :N] = e
        Zr = np.fft.irfft2(np.fft.rfft2(pad.real) * OPEN['Ghat2'], s=pad.shape)[:N, :N]
        Zi = np.fft.irfft2(np.fft.rfft2(pad.imag) * OPEN['Ghat2'], s=pad.shape)[:N, :N]
        return (Zr + 1j * Zi) / OPEN['norm']
    Zr = np.fft.irfft2(np.fft.rfft2(e.real) * Ghat, s=theta.shape)
    Zi = np.fft.irfft2(np.fft.rfft2(e.imag) * Ghat, s=theta.shape)
    return Zr + 1j * Zi

def set_open(N, L, kind, R):
    """no-flux (open) boundaries: kernel on a 2N grid, normalised by the kernel mass inside the domain"""
    Ghat2 = kernel(2 * N, 2 * L, kind, R)
    ind = np.zeros((2 * N, 2 * N)); ind[:N, :N] = 1
    norm = np.fft.irfft2(np.fft.rfft2(ind) * Ghat2, s=ind.shape)[:N, :N]
    OPEN.update(on=True, Ghat2=Ghat2, norm=np.maximum(norm, 1e-9))

def rhs(theta, Ghat, K, alpha):
    Z = order_field(theta, Ghat)
    return -K * np.imag(np.exp(1j * (theta + alpha)) * np.conj(Z)), Z

def run(N=256, L=1.0, kind='exp', R=0.04, alpha=1.45, K=1.0, dt=0.05, T=400.0,
        ic='dipole', seed=1, snap_every=None, verbose=True, schedule=None, theta0=None):
    """schedule: list of (alpha, T) stages run consecutively (α annealing); theta0: warm start"""
    if schedule is not None:
        theta = theta0
        allsnaps = []
        for (al, TT) in schedule:
            if verbose: print(f'--- stage alpha={al} T={TT}', flush=True)
            theta, Z, snaps = run(N=N, L=L, kind=kind, R=R, alpha=al, K=K, dt=dt, T=TT, ic=ic, seed=seed,
                                  snap_every=snap_every, verbose=verbose, theta0=theta)
            allsnaps.append(theta.copy())
        return theta, Z, allsnaps
    rng = np.random.default_rng(seed)
    Ghat = kernel(N, L, kind, R)
    x = (np.arange(N) + 0.5) / N * L
    X, Y = np.meshgrid(x, x, indexing='ij')
    if ic == 'dipole':
        z = (X - 0.25 * L) + 1j * (Y - 0.5 * L)
        w = (X - 0.75 * L) + 1j * (Y - 0.5 * L)
        theta = np.angle(z) - np.angle(w)
    elif ic == 'quad':
        theta = np.zeros_like(X)
        for (cx, cy, s) in [(0.25, 0.25, 1), (0.75, 0.25, -1), (0.25, 0.75, -1), (0.75, 0.75, 1)]:
            theta += s * np.angle((X - cx * L) + 1j * (Y - cy * L))
    elif ic == 'random':
        theta = rng.uniform(-np.pi, np.pi, (N, N))
    elif ic == 'single':
        theta = np.angle((X - 0.5 * L) + 1j * (Y - 0.5 * L))
        core = np.hypot(X - 0.5 * L, Y - 0.5 * L) < 1.5 * R
        theta = np.where(core, rng.uniform(-np.pi, np.pi, (N, N)), theta)
    theta = theta + 0.3 * rng.standard_normal((N, N))
    if theta0 is not None:
        theta = theta0.copy()
    theta = np.mod(theta + np.pi, 2 * np.pi) - np.pi
    nsteps = int(round(T / dt))
    snaps = []
    t0 = time.time()
    nwin = int(round(FREQWIN['T'] / dt)) if FREQWIN['T'] > 0 else 0
    acc_w = np.zeros_like(theta); acc_R = np.zeros_like(theta); nacc = 0
    for it in range(nsteps):
        # RK2 (midpoint)
        k1, Z = rhs(theta, Ghat, K, alpha)
        k2, _ = rhs(theta + 0.5 * dt * k1, Ghat, K, alpha)
        if nwin and it >= nsteps - nwin:
            acc_w += k2; acc_R += np.abs(Z); nacc += 1
        theta = theta + dt * k2
        theta = np.mod(theta + np.pi, 2 * np.pi) - np.pi
        if snap_every and (it + 1) % snap_every == 0:
            snaps.append(theta.copy())
        if verbose and (it + 1) % max(1, nsteps // 10) == 0:
            Rloc = np.abs(Z)
            print(f"  t={(it+1)*dt:7.1f}  mean|Z|={Rloc.mean():.3f}  min|Z|={Rloc.min():.3f}  "
                  f"frac|Z|<0.5={np.mean(Rloc<0.5):.3f}  {time.time()-t0:.0f}s", flush=True)
    _, Z = rhs(theta, Ghat, K, alpha)
    if nacc:
        FREQWIN['omega'] = acc_w / nacc; FREQWIN['Rbar'] = acc_R / nacc
    return theta, Z, snaps

def local_coherence(theta, Ghat_small):
    """time-free coherence proxy: |mean of e^{iθ} over a small neighbourhood|"""
    return np.abs(order_field(theta, Ghat_small))

if __name__ == '__main__':
    import argparse
    from PIL import Image
    ap = argparse.ArgumentParser()
    ap.add_argument('--N', type=int, default=256)
    ap.add_argument('--kind', default='exp')
    ap.add_argument('--R', type=float, default=0.04)
    ap.add_argument('--alpha', type=float, default=1.45)
    ap.add_argument('--T', type=float, default=400)
    ap.add_argument('--dt', type=float, default=0.05)
    ap.add_argument('--ic', default='dipole')
    ap.add_argument('--tag', default='p')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--schedule', default='', help='e.g. 1.0:200,1.3:200,1.45:400')
    ap.add_argument('--open', type=int, default=0)
    ap.add_argument('--load', default='', help='warm start: npz with theta')
    ap.add_argument('--freqwin', type=float, default=0.0, help='average dθ/dt and |Z| over the last T units')
    a = ap.parse_args()
    if a.open:
        set_open(a.N, 1.0, a.kind, a.R)
    FREQWIN['T'] = a.freqwin
    theta0 = None
    if a.load:
        theta0 = np.load(a.load)['theta']
        if theta0.shape[0] != a.N:
            from scipy.ndimage import zoom as _zoom
            c = np.cos(theta0); s_ = np.sin(theta0); f = a.N / theta0.shape[0]
            theta0 = np.arctan2(_zoom(s_, f, order=1), _zoom(c, f, order=1))
    sched = None
    if a.schedule:
        sched = [(float(p.split(':')[0]), float(p.split(':')[1])) for p in a.schedule.split(',')]
    theta, Z, snaps = run(N=a.N, kind=a.kind, R=a.R, alpha=a.alpha, T=a.T, dt=a.dt, ic=a.ic, seed=a.seed, schedule=sched, theta0=theta0)
    if sched:
        import matplotlib.colors as mc
        for si, th in enumerate(snaps):
            h = (th + np.pi) / (2 * np.pi)
            rgb = mc.hsv_to_rgb(np.stack([h, np.ones_like(h) * 0.7, np.ones_like(h) * 0.9], -1))
            Image.fromarray((rgb * 255).astype(np.uint8)).resize((384, 384), Image.NEAREST).save(f'chim_{a.tag}_s{si}.png')
    extra = {}
    if FREQWIN['omega'] is not None: extra = dict(omega=FREQWIN['omega'], Rbar=FREQWIN['Rbar'])
    np.savez_compressed(f'chim_{a.tag}.npz', theta=theta, Z=Z, args=json.dumps(vars(a)), **extra)
    # quick look: hue = phase, value = |Z|
    import colorsys
    h = (theta + np.pi) / (2 * np.pi)
    v = 0.35 + 0.65 * np.clip(np.abs(Z), 0, 1)
    rgb = np.zeros(theta.shape + (3,))
    hsv = np.stack([h, np.ones_like(h) * 0.7, v], -1)
    import matplotlib.colors as mc
    rgb = mc.hsv_to_rgb(hsv)
    Image.fromarray((rgb * 255).astype(np.uint8)).resize((512, 512), Image.NEAREST).save(f'chim_{a.tag}.png')
    print('saved', f'chim_{a.tag}.png')
