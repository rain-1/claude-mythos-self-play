"""completion.py — stochastic completion fields (Mumford 1994; Williams & Jacobs 1997).

A contour that the eye adds between two edge fragments is modelled as the path of a particle that
moves at unit speed, whose heading performs Brownian motion (variance sigma^2 per unit length) and
which dies at rate 1/tau.  The completion field between a source edge element (x_s, theta_s) and a
sink element (x_k, theta_k) is

    C_sk(x) = ∫ P_s(x, theta) · P_k(x, theta + pi) dtheta

where P_s is the time-integrated density of the process started at the source (its Green's function)
and P_k the same for the sink, run *out* of the sink (by reversibility the reversed path leaves the
sink heading outward and carries the opposite heading at every point).

Because the process is invariant under rigid motions, ONE Green's function G(x, y, theta) for a
source at the origin heading +x is enough: every P_s is G rotated by theta_s and translated to x_s.
G is computed spectrally: in (kx, ky) Fourier space the drift is a phase, in theta-Fourier space
the heading diffusion is a Gaussian damping, the decay is a scalar — operator splitting with a
step of dt (exact advection, exact diffusion, first-order splitting).

The ALL-PAIRS completion field is a single product:  sum_{s != k} C_sk = ∫ S(theta) S(theta + pi)
with S = sum_s P_s (minus the negligible self terms).
"""
import numpy as np
from scipy.ndimage import rotate as nd_rotate, shift as nd_shift, map_coordinates
import time


def greens(N, ntheta, sigma, tau, dt=1.0, T=None, src_sigma=1.0, verbose=True, dtype=np.complex64):
    """Time-integrated density G[y, x, theta] (N, N, ntheta), source at the centre heading +x
    (theta index 0 = +x, angles increase counter-clockwise in a y-UP frame; we use array row = y)."""
    if T is None:
        T = 6.0 * tau
    kx = 2 * np.pi * np.fft.fftfreq(N)              # per pixel
    ky = 2 * np.pi * np.fft.fftfreq(N)
    KX, KY = np.meshgrid(kx, ky)                    # [y, x]
    th = 2 * np.pi * np.arange(ntheta) / ntheta
    # initial condition: Gaussian blob in (x,y) (spectral: exp(-k^2 s^2/2)) and in theta (wrapped Gaussian)
    blob = np.exp(-0.5 * (KX ** 2 + KY ** 2) * src_sigma ** 2).astype(np.float32)
    dth = 2 * np.pi / ntheta
    tg = np.exp(-0.5 * (np.angle(np.exp(1j * th)) / (dth * 1.0)) ** 2); tg /= tg.sum()
    p = (blob[:, :, None] * tg[None, None, :]).astype(dtype)          # spectral in (x,y), physical in theta
    # advection phase per theta slice (position += (cos, sin) dt)
    phase = np.exp(-1j * (KX[:, :, None] * np.cos(th)[None, None, :] + KY[:, :, None] * np.sin(th)[None, None, :]) * dt).astype(dtype)
    m = np.fft.fftfreq(ntheta) * ntheta
    damp = np.exp(-0.5 * sigma ** 2 * m ** 2 * dt).astype(np.float32) * np.exp(-dt / tau)
    G = np.zeros_like(p)
    nsteps = int(round(T / dt))
    t0 = time.time()
    for s in range(nsteps):
        G += p * dt
        p *= phase
        ph = np.fft.fft(p, axis=2)
        ph *= damp[None, None, :]
        p = np.fft.ifft(ph, axis=2).astype(dtype)
        if verbose and (s % 50 == 0 or s == nsteps - 1):
            print(f'  greens step {s}/{nsteps} [{time.time() - t0:.0f}s]', flush=True)
    # back to physical (x,y): inverse FFT over the first two axes
    g = np.fft.ifft2(G, axes=(0, 1)).real.astype(np.float32)
    g = np.fft.fftshift(g, axes=(0, 1))           # source at the centre
    g[g < 0] = 0
    return g


def place(G, x, y, theta, W, H, oob=0.0):
    """P(y, x, theta') for a source at (x, y) heading theta (radians, y-up sense is handled by the caller
    who passes theta measured in array coordinates: theta = atan2(dy_row, dx_col))."""
    N, _, nt = G.shape
    # rotate the (x,y) plane by theta about the centre, then roll theta axis
    deg = np.degrees(theta)
    R = nd_rotate(G, -deg, axes=(1, 0), reshape=False, order=1, mode='constant', cval=0.0, prefilter=False)
    # heading index shift: a path that had heading phi in G has heading phi + theta now
    sh = theta / (2 * np.pi) * nt
    i0 = int(np.floor(sh)); f = sh - i0
    R = (1 - f) * np.roll(R, i0, axis=2) + f * np.roll(R, i0 + 1, axis=2)
    # translate into the (H, W) canvas: G centre (N/2, N/2) goes to (y, x)
    out = np.zeros((H, W, nt), np.float32)
    ox = int(round(x - N / 2)); oy = int(round(y - N / 2))
    xs0, xs1 = max(0, ox), min(W, ox + N)
    ys0, ys1 = max(0, oy), min(H, oy + N)
    if xs1 > xs0 and ys1 > ys0:
        out[ys0:ys1, xs0:xs1] = R[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
    return out


def completion_all(S):
    """all-pairs field from the summed source field S[y,x,theta]: ∫ S(th) S(th+pi) dth"""
    nt = S.shape[2]
    Spi = np.roll(S, nt // 2, axis=2)
    return (S * Spi).sum(axis=2) * (2 * np.pi / nt)


def completion_pair(Ps, Pk):
    nt = Ps.shape[2]
    return (Ps * np.roll(Pk, nt // 2, axis=2)).sum(axis=2) * (2 * np.pi / nt)


def ridge(C, p0, p1, n=200, half=None, lens=False):
    """most likely path of a pair field: perpendicular argmax along the chord p0->p1
    (lens=True: the search half-width is a lens, 2 px at the ends and `half` in the middle)"""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = np.hypot(*d); u = d / L; v = np.array([-u[1], u[0]])
    if half is None:
        half = 0.5 * L
    ts = np.linspace(0, 1, n)
    ss = np.linspace(-half, half, int(2 * half) + 1)
    pts = []
    for t in ts:
        c = p0 + t * d
        if lens:
            hw = 2.0 + half * np.sin(np.pi * t)
            ss = np.linspace(-hw, hw, int(2 * hw) + 3)
        xs = c[0] + ss * v[0]; ys = c[1] + ss * v[1]
        vals = map_coordinates(C, [ys, xs], order=1, mode='constant', cval=0.0)
        j = int(np.argmax(vals))
        pts.append((xs[j], ys[j], vals[j]))
    return np.array(pts)
