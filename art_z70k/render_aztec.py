"""Render an Aztec-diamond domino tiling: color by domino type (n/s/e/w) so the
four frozen corners read as solid plates and the temperate interior shimmers.
The arctic circle (radius N/sqrt2) emerges as the order/disorder boundary.
"""
import numpy as np, sys, time
from PIL import Image
from aztec import shuffle

N = int(sys.argv[1]) if len(sys.argv) > 1 else 512
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
rot = (len(sys.argv) > 3 and sys.argv[3] == "rot")
outp = sys.argv[4] if len(sys.argv) > 4 else f"aztec_N{N}_s{seed}.png"

t0 = time.time()
T, off = shuffle(N, seed=seed)
print(f"shuffled N={N} in {time.time()-t0:.1f}s")

# crop the diamond region: x,y in [-N, N-1] -> array idx [off-N, off+N-1]
lo = off - N; hi = off + N
C = T[lo:hi, lo:hi]              # (2N, 2N), row=y, col=x
# flip vertically so +y is up in the image
C = C[::-1, :]

# palette  (RGB)  background void = near black
col = {
    0: ( 6,  7, 14),   # empty/void
    1: (240,190, 86),  # n  warm gold
    2: ( 34,151,152),  # s  teal
    3: (214, 92,120),  # e  rose
    4: ( 70, 92,176),  # w  indigo
}
rgb = np.zeros(C.shape + (3,), np.uint8)
for k, c in col.items():
    rgb[C == k] = c

img = Image.fromarray(rgb)
if rot:
    img = img.rotate(45, resample=Image.BICUBIC, expand=True, fillcolor=(6,7,14))
img.save(outp)
print("saved", outp, "size", img.size)
