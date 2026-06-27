"""
01 · THE ONLY COINCIDENCE   (4096^2 centrepiece)
================================================
Dyson Brownian motion. An N x N Hermitian (GUE) matrix is started at H = 0 --
so ALL N eigenvalues coincide at a single point -- and then driven by an
Ornstein-Uhlenbeck matrix flow whose stationary law is the unit GUE. Its
eigenvalues lambda_i(t) obey Dyson's equation

    d lambda_i = sqrt(2/beta) dB_i  +  sum_{j != i} dt / (lambda_i - lambda_j),

a logarithmic repulsion that forbids any two from ever meeting again. They
fan out of their single shared origin into the Wigner semicircle and braid
forever without crossing. The one place they touch is the beginning.

Front-page seed: MathOverflow, "Spectrum of the sum over a conjugacy class in
S_n tends to Gaussian/Wigner."  Technique new to this thread: random-matrix
level-repulsion as non-crossing eigenvalue threads.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d

def gue(rng, n):
    A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    return (A + A.conj().T) / 2.0

def simulate(N, T, theta, dt, seed):
    rng = np.random.default_rng(seed)
    H = np.zeros((N, N), complex)           # the one allowed coincidence
    a = theta * dt; sig = np.sqrt(2 * theta * dt)
    paths = np.empty((T, N))
    for t in range(T):
        paths[t] = np.linalg.eigvalsh(H) / np.sqrt(N)
        H = H - a * H + sig * gue(rng, N)
    return paths

PAL = np.array([
    [0.13, 0.20, 0.52], [0.10, 0.58, 0.74], [0.62, 0.90, 0.83],
    [0.97, 0.80, 0.46], [0.88, 0.32, 0.34],
])
def palette(u):
    x = u * (len(PAL) - 1)
    i = np.clip(x.astype(int), 0, len(PAL) - 2); f = (x - i)[..., None]
    return PAL[i] * (1 - f) + PAL[i + 1] * f

def render(paths, S, supers=2, ylim=2.3, smooth=6.0):
    T, N = paths.shape
    W = Hh = S * supers
    sc = W / 1800.0                         # scale widths from the prototype res
    paths = gaussian_filter1d(paths, smooth, axis=0, mode='nearest')
    acc = np.zeros((Hh, W, 3), np.float32)
    xs = np.arange(T) / (T - 1) * (W - 1)
    order = np.argsort(paths.mean(0)); rank = np.empty(N)
    rank[order] = np.linspace(0, 1, N); cols = palette(rank)
    nsamp = int(W * 1.6)
    samp = np.linspace(0, T - 1, nsamp)
    xv = np.interp(samp, np.arange(T), xs)
    ix = np.clip(xv.astype(int), 0, W - 1)
    for j in range(N):
        yv = np.interp(samp, np.arange(T), paths[:, j])
        py = (yv + ylim) / (2 * ylim) * (Hh - 1)
        iy = np.clip(py.astype(int), 0, Hh - 1)
        np.add.at(acc, (iy, ix), cols[j])
    base = gaussian_filter(acc, (1.0 * sc, 1.0 * sc, 0))
    glow = gaussian_filter(acc, (7.0 * sc, 7.0 * sc, 0)) * 0.42
    img = base + glow
    img = img / (img.max() + 1e-9)
    img = 1.0 - np.exp(-1.5 * img * 4.0)
    img = np.power(np.clip(img, 0, 1), 0.82)
    out = (img * 255).astype(np.uint8)
    return Image.fromarray(out, "RGB").resize((S, S), Image.LANCZOS)

if __name__ == "__main__":
    import sys
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
    print(f"simulating Dyson BM, render {S}^2 ...")
    p = simulate(N=36, T=1100, theta=1.0, dt=6.0 / 1100, seed=7)
    print("eigenvalue range", round(p.min(), 3), round(p.max(), 3),
          "| min gap >0 ->", np.diff(p, axis=1).min() > 0)
    im = render(p, S=S, smooth=6.0)
    im.save("01_the_only_coincidence.png")
    print("saved 01_the_only_coincidence.png", im.size)
