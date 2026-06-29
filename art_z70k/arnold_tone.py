"""Color the Arnold-tongue winding-number field W(Omega,K).
hue/colour = W (which rational), brightness = lockedness (small |grad W|).
Glowing rational wedges (frozen) over a quasiperiodic sea (free)."""
import numpy as np, sys
from PIL import Image
from scipy.ndimage import gaussian_filter

inp = sys.argv[1]
outp = sys.argv[2] if len(sys.argv) > 2 else inp.replace(".npy", "_tone.png")
Kmax = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
W = np.load(inp).astype(np.float64)
S = W.shape[0]

# lockedness: small gradient magnitude => locked plateau.  Sharp gate so EVERY
# tongue (even thin high-q ones) reads, against a dark 'free' quasiperiodic sea.
gy, gx = np.gradient(W)
gm = np.hypot(gx, gy) * S          # per-pixel gradient scaled to ~1/width units
locked = np.exp(-(gm / 0.30) ** 1.3)

# also treat the K~0 quasiperiodic ramp (W=Omega, slope~1/S*S=1) as unlocked:
# gm there ~ 1 -> locked ~ exp(-0.83) ~ 0.43; tongues gm~0 -> 1. ok.

# colour ramp by W (sequential rainbow-ish, curated jewel tones, cyclic-safe ends)
def ramp(x, pts):
    xs = np.array([p[0] for p in pts]); cs = np.array([p[1] for p in pts], float)
    out = np.empty(x.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(x, xs, cs[:, c])
    return out
pal = [
    (0.00, ( 18, 24, 64)),    # W=0/1  deep navy (recedes into the void)
    (0.17, ( 40,150,185)),    # teal
    (0.30, ( 60,205,150)),    # green  (~1/3)
    (0.42, (130,215,120)),
    (0.50, (255,212, 92)),    # gold   (1/2) -- bright heart
    (0.58, (250,170, 80)),
    (0.70, (240,120, 80)),    # orange (~2/3)
    (0.83, (220, 95,120)),    # rose
    (1.00, ( 18, 24, 64)),    # W=1/1  deep navy (cyclic, recedes)
]
base = ramp(W, pal)

# brightness: dim quasiperiodic sea (smooth W-gradient, still faintly visible =
# the 'free' flow), bright locked tongues (the 'frozen' wedges).
val = 0.16 + 1.0 * locked
rgb = base * val[..., None]
# push the free sea toward a cool void so tongues are clearly the subject
sea = (1 - locked)[..., None]
rgb = rgb * (1 - 0.5*sea) + np.array([7, 10, 26]) * 0.5 * sea

# bloom the locked tongues so they glow
glow = gaussian_filter(np.clip(locked-0.5,0,1), sigma=S/650.0)
glow /= (glow.max()+1e-9)
rgb[...,0] += glow * 40; rgb[...,1] += glow*38; rgb[...,2] += glow*26

rgb = np.clip(rgb, 0, 255).astype(np.uint8)
# row 0 is K=0 at TOP; flip so K increases upward
rgb = rgb[::-1, :]
Image.fromarray(rgb).save(outp)
print("saved", outp)
