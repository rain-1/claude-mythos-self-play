"""
Deterministic Freedom
======================
Seed: philosophy.SE "If there is no randomness, in a completely deterministic
world, what is freedom?"

The Gray-Scott reaction-diffusion system

    du/dt = Du*lap(u) - u*v^2 + F*(1-u)
    dv/dt = Dv*lap(v) + u*v^2 - (F+k)*v

is utterly deterministic and seeded with NO randomness -- the initial state
is the interference of a few incommensurate gratings, an exactly specified
crystal of a starting condition. Yet under a fixed law that frozen lattice
melts into an organic, branching, never-quite-repeating labyrinth: membranes,
corridors, a living thing unfolding. Freedom, here, is not the absence of law
but the depth of what a law can become.
"""
import numpy as np
from scipy.ndimage import convolve
from PIL import Image

# 9-point Laplacian stencil (centre -1, edge .2, corner .05) as one C-level conv.
_LAP = np.array([[0.05, 0.20, 0.05],
                 [0.20, -1.0, 0.20],
                 [0.05, 0.20, 0.05]], dtype=np.float32)

def laplacian(a):
    return convolve(a, _LAP, mode="wrap")

def _seed(u, v, n, seed_r, mode):
    def block(cy, cx):
        v[cy - seed_r:cy + seed_r, cx - seed_r:cx + seed_r] = 0.5
        u[cy - seed_r:cy + seed_r, cx - seed_r:cx + seed_r] = 0.25
    if mode == "center":
        block(n // 2, n // 2)
    elif mode == "lattice":
        step = n // 7
        for gy in range(step, n, step):                 # deterministic seed lattice
            for gx in range(step, n, step):
                block(gy, gx)
    elif mode == "interference":
        # A fully deterministic, RNG-free initial condition: the interference
        # of several incommensurate gratings. Irregular enough to break
        # symmetry everywhere, yet not one bit of randomness.
        yy, xx = np.mgrid[0:n, 0:n] / float(n)
        comps = [(11, 3, 0.0), (7, 9, 1.3), (13, 5, 2.1),
                 (5, 14, 0.6), (17, 8, 3.0), (9, 16, 1.9)]
        field = np.zeros((n, n))
        for fx, fy, ph in comps:
            field += np.sin(2 * np.pi * (fx * xx + fy * yy) + ph)
        mask = field > 0.6                               # scattered deterministic patches
        v[mask] = 0.5
        u[mask] = 0.25

def simulate(n, steps, F, k, Du=0.16, Dv=0.08, dt=1.0, seed_r=3,
             seed_mode="center", log_every=4000):
    u = np.ones((n, n), dtype=np.float32)
    v = np.zeros((n, n), dtype=np.float32)
    _seed(u, v, n, seed_r, seed_mode)
    for s in range(steps):
        uvv = u * v * v
        u += dt * (Du * laplacian(u) - uvv + F * (1.0 - u))
        v += dt * (Dv * laplacian(v) + uvv - (F + k) * v)
        if s % log_every == 0:
            print(f"  step {s}/{steps}", end="\r")
    print()
    return u, v

# --- colouring -------------------------------------------------------------
_GRAD = np.array([
    [0.02, 0.03, 0.08],   # near-black blue (substrate)
    [0.05, 0.12, 0.28],   # deep indigo
    [0.10, 0.42, 0.55],   # teal
    [0.35, 0.72, 0.62],   # green-aqua (membranes)
    [0.93, 0.86, 0.55],   # warm bone (cell walls)
    [0.99, 0.97, 0.90],   # luminous crest
])

def colorize(v):
    t = np.clip((v - v.min()) / (v.max() - v.min() + 1e-9), 0, 1)
    t = t ** 0.85
    n = len(_GRAD) - 1
    x = t * n
    i = np.clip(np.floor(x).astype(int), 0, n - 1)
    f = (x - i)[..., None]
    rgb = _GRAD[i] * (1 - f) + _GRAD[i + 1] * f
    # rim light: emphasise the membranes where v changes fastest
    gy, gx = np.gradient(v)
    edge = np.hypot(gx, gy)
    edge = np.clip(edge / (edge.max() + 1e-9), 0, 1) ** 0.6
    rgb = rgb + edge[..., None] * np.array([0.18, 0.16, 0.10])
    return np.clip(rgb, 0, 1)

def render(grid, steps, F, k, out_size=None, **kw):
    u, v = simulate(grid, steps, F, k, **kw)
    rgb = colorize(v)
    img = (rgb * 255 + 0.5).astype(np.uint8)
    pil = Image.fromarray(img, "RGB")
    if out_size and out_size != grid:
        pil = pil.resize((out_size, out_size), Image.LANCZOS)
    return pil

if __name__ == "__main__":
    import sys
    grid = int(sys.argv[1]) if len(sys.argv) > 1 else 256
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    F = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0367
    k = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0649
    out = sys.argv[5] if len(sys.argv) > 5 else "gallery/preview5.png"
    render(grid, steps, F, k).save(out)
    print("saved", out, grid, steps, F, k)
