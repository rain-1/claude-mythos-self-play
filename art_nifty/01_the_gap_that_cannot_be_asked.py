"""
01 — The Gap That Cannot Be Asked
Inspired by MathOverflow front page: "How undecidable is the spectral gap?"
  (Cubitt-Perez-Garcia-Wolf: whether a translation-invariant quantum Hamiltonian
  has a spectral gap is UNDECIDABLE in general -- the proof works by encoding a
  Turing machine's halting behaviour into an aperiodic tiling of the plane, so
  that the tiling exists (gapless) iff the machine never halts.)

We don't simulate an actual Turing-machine tiling (that's a research project),
but we build the honest visual kernel of the idea: a self-similar, NON-PERIODIC
hierarchical substitution tiling (a "chair"-style rep-tile system) in which
EVERY finite patch looks locally unremarkable, yet the global existence of the
infinite tiling encodes a fact (here: a synthetic "halting oracle" bit sequence)
that cannot be read off from any bounded window. We render the substitution
hierarchy directly (levels 0..L), colouring by level and by the injected "oracle
bit" at each node, so the eye sees an endless nested lattice that looks the same
at every scale -- and the one bit that would tell you "does this branch halt"
is buried one level deeper than you can ever look.

Technique: L-shaped (chair) rep-tile inflation, 4 orientations, recorded as a
parent tree (an actual substitution DAG, not just a fractal texture) so we can:
 - depth-color (level = age of the tile in the inflation process)
 - inject a deterministic pseudo-random "oracle" bit per node from a hash of its
   address (its position in the substitution tree) -- a stand-in for "the digit
   of the halting sequence encoded at this scale" -- and let that oracle bit
   perturb hue/luminance ever so slightly, so the piece visibly says: the
   structure is fully deterministic and self-similar, but a bounded observer
   looking at any single tile cannot distinguish "this branch's oracle bit is 0"
   from "1" without going one level deeper -- forever.
"""
import numpy as np
from PIL import Image, ImageFilter
import hashlib

W = H = 4096
SUPER = 1  # render straight at target res via analytic substitution, no need to supersample geometry
rng_seed = 20260704

# ---------------------------------------------------------------------------
# Chair rep-tile substitution: an L-tromino-like rep-4 tile that inflates by
# factor 2 into 4 self-similar copies (classic "chair" / L-tiling, aperiodic
# under forced non-periodic matching rules -- we use the substitution itself,
# which is enough to produce the genuine non-periodic hierarchical texture).
#
# We represent a placed tile as (x, y, size, orientation, address, depth)
# and recurse until size <= 1 pixel, emitting leaf rectangles (actually
# L-shaped hexominoes at each scale, built from 3 unit squares of the previous
# scale) painted by depth + oracle hash.
# ---------------------------------------------------------------------------

# The 4 orientations of the "chair" hexomino built from 4 sub-squares in a
# 2x2 macro-cell, with one sub-square OMITTED (the notch) -- this is what
# makes the substitution non-trivial (not just a quadtree) and gives the
# classic pinwheel-free but still aperiodic "chair" look under the standard
# forced boundary matching (we render the pure substitution figure).
# For each orientation, list which of the 4 quadrants (TL,TR,BL,BR) are FILLED
# with a next-level tile, and which single quadrant is the "notch" that
# instead gets subdivided one extra level deeper (this recursive notch is what
# breaks periodicity -- the classic chair-tile rule).
ORIENTATIONS = {
    0: ['TL', 'TR', 'BL'],       # notch at BR
    1: ['TR', 'BR', 'TL'],       # notch at BL
    2: ['BR', 'BL', 'TR'],       # notch at TL
    3: ['BL', 'TL', 'BR'],       # notch at TR
}
QUAD_OFFSET = {'TL': (0, 0), 'TR': (1, 0), 'BL': (0, 1), 'BR': (1, 1)}
# each orientation's notch quadrant maps to the orientation used for the
# recursive notch-fill (rotate by one step) -- standard chair-tile recursion
NOTCH_OF = {0: 'BR', 1: 'BL', 2: 'TL', 3: 'TR'}
NEXT_ORIENT = {0: 1, 1: 2, 2: 3, 3: 0}

img = np.zeros((H, W, 3), dtype=np.float64)
depth_buf = np.zeros((H, W), dtype=np.float32)
oracle_buf = np.zeros((H, W), dtype=np.float32)

MIN_PIX = 3.0  # stop subdividing once a cell is this small (leaf tile)

def addr_hash(address_bytes):
    h = hashlib.blake2b(address_bytes, digest_size=8).digest()
    return int.from_bytes(h, 'big') / 2**64

def paint_quad(x, y, s, quad, orient, address, depth, out_list):
    dx, dy = QUAD_OFFSET[quad]
    qs = s / 2.0
    nx, ny = x + dx * qs, y + dy * qs
    new_addr = address + bytes([orient, {'TL':0,'TR':1,'BL':2,'BR':3}[quad]])
    stack.append((nx, ny, qs, orient, new_addr, depth + 1))

# Recursive subdivision with an oracle-driven STOP decision per quadrant:
# every quadrant of the chair substitution independently decides -- via a hash
# of its own tree address (its full history of orientations) -- whether it
# freezes into a leaf tile NOW or keeps subdividing.  The one exception is the
# "notch" quadrant, which is FORCED to always continue (this is the actual
# chair-tile aperiodicity rule: the notch never closes, matching the real
# proof's undecidable branch that never terminates from the outside).  Stop
# probability grows with depth so most mass freezes as mid-size tiles while a
# sparse minority tunnels all the way down -- this is what gives the canvas
# genuinely varied tile SIZES (the visible signature of "you cannot know how
# deep this box goes until you open it").
MAX_DEPTH = 13
MIN_PIX = 2.0

def stop_prob(depth):
    return min(0.93, 0.045 + 0.062 * depth)

# Seed with all 4 orientations tiling the 4 root quadrants -- avoids the
# single-orientation macro bias (one giant stripe) that a single root produces,
# giving a more balanced, mandala-like global partition.
half = W / 2.0
stack = [
    (0.0,  0.0,  half, 0, b'\x00', 0),
    (half, 0.0,  half, 1, b'\x01', 0),
    (0.0,  half, half, 2, b'\x02', 0),
    (half, half, half, 3, b'\x03', 0),
]
leaves = []  # (x,y,s,depth,oracle)

while stack:
    x, y, s, orient, address, depth = stack.pop()
    forced_leaf = (s <= MIN_PIX) or (depth >= MAX_DEPTH)
    fills = ORIENTATIONS[orient]
    notch_quad = NOTCH_OF[orient]
    for quad in fills:
        dx, dy = QUAD_OFFSET[quad]
        qs = s / 2.0
        nx, ny = x + dx * qs, y + dy * qs
        new_addr = address + bytes([orient, {'TL':0,'TR':1,'BL':2,'BR':3}[quad]])
        o = addr_hash(new_addr)
        if forced_leaf or o < stop_prob(depth + 1):
            leaves.append((nx, ny, qs, depth + 1, o))
        else:
            stack.append((nx, ny, qs, orient, new_addr, depth + 1))
    # notch quadrant: forced to keep going (unless truly forced_leaf by size cap)
    dx, dy = QUAD_OFFSET[notch_quad]
    qs = s / 2.0
    nx, ny = x + dx * qs, y + dy * qs
    new_addr = address + bytes([orient, 9])
    if forced_leaf:
        o = addr_hash(new_addr)
        leaves.append((nx, ny, qs, depth + 1, o))
    else:
        stack.append((nx, ny, qs, NEXT_ORIENT[orient], new_addr, depth + 1))

print(f"leaves: {len(leaves)}")

# Rasterize leaves: draw filled squares with depth + oracle recorded.
# Sort by size descending so fine leaves paint over any rounding overlaps.
leaves.sort(key=lambda t: -t[2])
for (x, y, s, depth, oracle) in leaves:
    x0 = int(round(x)); y0 = int(round(y))
    x1 = int(round(x + s)); y1 = int(round(y + s))
    x0 = max(0, x0); y0 = max(0, y0)
    x1 = min(W, x1); y1 = min(H, y1)
    if x1 <= x0 or y1 <= y0:
        continue
    depth_buf[y0:y1, x0:x1] = depth
    oracle_buf[y0:y1, x0:x1] = oracle

max_depth = depth_buf.max()
print(f"max depth: {max_depth}")

# ---------------------------------------------------------------------------
# Palette: depth -> a cool-to-warm ladder (each inflation level = one "layer
# of the question you cannot resolve without descending further"), oracle bit
# -> a subtle hue/luminance jitter (the undecidable residue at the leaf you
# actually stopped at).
# ---------------------------------------------------------------------------
import colorsys

d_norm = depth_buf / max(max_depth, 1)

# base hue sweeps deep indigo (shallow/large tiles, "the visible question")
# through teal, to a hot ember (deepest/smallest tiles, "the buried answer")
hue = 0.68 - 0.75 * d_norm  # 0.68 (deep violet) -> -0.07 -> wraps to warm amber/rose
hue = hue % 1.0
sat = 0.45 + 0.5 * d_norm
val = 0.08 + 0.68 * d_norm

# oracle bit perturbs hue by a tiny amount (+/- 0.02) and val by (+/- 0.08) --
# small enough that no single tile "announces" its bit, but large enough that
# across the whole lattice the eye can sense an irreducible shimmer of noise
# riding on the deterministic geometric order.
hue = (hue + (oracle_buf - 0.5) * 0.05) % 1.0
val = np.clip(val + (oracle_buf - 0.5) * 0.18, 0.02, 1.0)
sat = np.clip(sat + (oracle_buf - 0.5) * 0.10, 0, 1)

Hf = hue.ravel(); Sf = sat.ravel(); Vf = val.ravel()
rgb = np.empty((Hf.size, 3), dtype=np.float64)
# vectorized HSV->RGB
i = np.floor(Hf * 6.0)
f = Hf * 6.0 - i
p = Vf * (1 - Sf)
q = Vf * (1 - f * Sf)
t = Vf * (1 - (1 - f) * Sf)
i = i.astype(int) % 6
conds = [i == k for k in range(6)]
r = np.select(conds, [Vf, q, p, p, t, Vf])
g = np.select(conds, [t, Vf, Vf, q, p, p])
b = np.select(conds, [p, p, t, Vf, Vf, q])
rgb[:, 0] = r; rgb[:, 1] = g; rgb[:, 2] = b
rgb_img = rgb.reshape(H, W, 3)

# Draw thin dark seams at tile boundaries (edges of leaves) to reveal the
# hierarchical grid itself -- the "matching rule" seams.
gy, gx = np.gradient(depth_buf)
edge = (np.abs(gx) + np.abs(gy)) > 0.4
seam = np.zeros((H, W), dtype=np.float64)
seam[edge] = 1.0
from scipy.ndimage import gaussian_filter
seam_soft = gaussian_filter(seam, sigma=0.6)

rgb_img = rgb_img * (1.0 - 0.45 * seam_soft[..., None])

# gentle bloom on the deepest (hottest) tiles -- "the answer trying to surface"
lum = 0.2126 * rgb_img[...,0] + 0.7152 * rgb_img[...,1] + 0.0722 * rgb_img[...,2]
mask = np.clip((lum - 0.55) / 0.45, 0, 1) ** 2
bloom_src = (rgb_img * mask[..., None])
b1 = gaussian_filter(bloom_src, sigma=(4,4,0))
b2 = gaussian_filter(bloom_src, sigma=(14,14,0))
final = rgb_img + 0.35*b1 + 0.25*b2

# filmic tone map + gamma
final = final / (1.0 + final)
final = np.clip(final, 0, 1) ** (1/2.2)

out = (final * 255).astype(np.uint8)
Image.fromarray(out, 'RGB').save('/home/user/claude-mythos-self-play/art_nifty/01_the_gap_that_cannot_be_asked.png')
print("saved 01")
