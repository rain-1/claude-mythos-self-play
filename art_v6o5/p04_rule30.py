"""04 - The Only Way to Know.

Rule 30 is a one-dimensional cellular automaton: each cell's next state is
s_i' = s_{i-1} XOR (s_i OR s_{i+1}). From the simplest seed it manufactures
genuine pseudo-randomness; Wolfram's claim of *computational irreducibility* is
that there is no shortcut -- to know row N you must compute rows 1..N-1. The
only way to know is to run it.

We make that visible. Take two universes whose starting rows differ in a SINGLE
bit. Evolve both. XOR the two space-times. Outside the perturbation's reach the
histories are bit-for-bit identical, so the XOR is dead black. Inside, they have
diverged into mutual chaos. The damage can spread no faster than one cell per
step, so its envelope is a perfect triangle -- the discrete *light cone* -- with
ruler-straight edges enclosing an interior nothing short of running it could
have foretold.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def evolve(row0, T):
    """Return the (T, W) uint8 space-time of Rule 30 from initial row row0."""
    W = row0.shape[0]
    st = np.empty((T, W), np.uint8)
    row = row0.copy()
    st[0] = row
    for t in range(1, T):
        left = np.roll(row, 1)
        right = np.roll(row, -1)
        row = left ^ (row | right)
        st[t] = row
    return st


def render(S, supersample=1, n_flips=1, seed=12345, substrate=True,
           fname="04_the_only_way_to_know.png"):
    W = S * supersample
    T = W
    # simulate WIDER than the visible crop so the light cone never reaches the
    # (periodic) boundary within T steps -> the triangle stays clean.
    Wsim = 2 * W + 64
    off = (Wsim - W) // 2                  # crop window [off, off+W)
    rng = np.random.default_rng(seed)
    base = (rng.random(Wsim) < 0.5).astype(np.uint8)

    A = evolve(base, T)
    b2 = base.copy()
    # flip one (or a few) bit(s) near the top centre of the visible window
    centres = [Wsim // 2] if n_flips == 1 else list(
        (off + np.linspace(0.22, 0.78, n_flips) * W).astype(int))
    for c in centres:
        b2[c] ^= 1
    B = evolve(b2, T)

    D = (A ^ B).astype(np.float32)[:, off:off + W]   # divergence cone(s), cropped
    A = A[:, off:off + W]
    print(f"  evolved {T}x{Wsim}; cropped {T}x{W}; cone fill = {D.mean():.3f}")

    # ---- colour ----
    img = np.zeros((T, W, 3), np.float32)
    if substrate:
        # dim cool Rule-30 substrate (the irreducible ground), gamma-dimmed
        sub = A.astype(np.float32)
        img += sub[..., None] * np.array([0.10, 0.19, 0.27])

    # hot divergence cone
    cone = np.array([1.0, 0.72, 0.28])
    img += D[..., None] * cone

    # ---- bloom only on the cone so its interior glows and edges stay crisp ----
    g = gaussian_filter(D, 1.1 * supersample)
    img += g[..., None] * np.array([1.0, 0.55, 0.18]) * 0.5
    g2 = gaussian_filter(D, 4.0 * supersample)
    img += g2[..., None] * np.array([1.0, 0.5, 0.2]) * 0.25

    # filmic tone + gamma
    img = 1.0 - np.exp(-1.5 * np.clip(img, 0, None))
    img = np.clip(img, 0, 1) ** (1 / 1.9)

    out = (img * 255).astype(np.uint8)
    im = Image.fromarray(out, "RGB")
    if supersample != 1:
        im = im.resize((S, S), Image.LANCZOS)
    im.save(fname)
    print("  saved", fname, im.size)
    return im


if __name__ == "__main__":
    import sys
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    ss = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    nf = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sub = (sys.argv[4] != "0") if len(sys.argv) > 4 else True
    render(S, ss, nf, substrate=sub)
