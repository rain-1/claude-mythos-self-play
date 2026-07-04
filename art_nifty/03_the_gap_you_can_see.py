"""
03 — The Gap You Can See
Inspired by MathOverflow front page: "Discrepancy in the first eigenvalue
upper bound under nonnegative Ricci curvature: Cheng 1975 vs Ledoux's
survey" -- two competing theorems bound the SPECTRAL GAP (lambda_2 - lambda_1)
of the Laplacian on a curved domain from geometric data (curvature, diameter),
and disagree on the sharp constant.

Piece 01 rendered the spectral gap as an abstract, discrete, undecidable
question (Cubitt-Perez-Garcia-Wolf). This piece renders the OTHER spectral
gap: a real, continuous, and fully computable one. We build an irregular
"drum" (a blob domain, no symmetry to exploit -- the honest hard case the
Cheng/Ledoux bounds are trying to control) and solve for its two lowest
Dirichlet Laplacian eigenmodes with a genuine finite-difference sparse
eigensolver. lambda_1 is the fundamental tone; lambda_2 - lambda_1 is the
gap the theorems are arguing about. We then render the complex superposition
Psi = v1 + i*v2 domain-coloured by phase -- so the two competing modes beating
against each other, and the literal nodal line of v2 splitting the drum in two,
becomes the visible anatomy of the gap.
"""
import numpy as np
from PIL import Image
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.ndimage import gaussian_filter, zoom

rng = np.random.default_rng(20260704)

# ---------------------------------------------------------------------------
# 1. Build an irregular blob domain via thresholded sum-of-Gaussians (a
#    genuinely asymmetric drum -- no separable coordinates, no cheap closed
#    form, exactly the situation the Cheng/Ledoux bounds are needed for).
# ---------------------------------------------------------------------------
G = 320  # solver grid resolution (keep modest: eigensolve cost)
y, x = np.mgrid[0:G, 0:G].astype(np.float64)
cx, cy = G/2, G/2

field = np.zeros((G, G))
n_bumps = 9
for i in range(n_bumps):
    ang = 2*np.pi*i/n_bumps + rng.uniform(-0.35, 0.35)
    rad = G*0.30*rng.uniform(0.55, 1.05)
    bx = cx + rad*np.cos(ang)
    by = cy + rad*np.sin(ang)
    sig = G*rng.uniform(0.11, 0.20)
    amp = rng.uniform(0.8, 1.3)
    field += amp*np.exp(-(((x-bx)**2+(y-by)**2)/(2*sig**2)))
# central blob to keep the domain connected
field += 1.4*np.exp(-(((x-cx)**2+(y-cy)**2)/(2*(G*0.16)**2)))

mask = field > 0.62
# keep only the largest connected component
from scipy.ndimage import label
lab, nlab = label(mask)
sizes = np.bincount(lab.ravel())
sizes[0] = 0
mask = lab == sizes.argmax()
print("domain pixels:", mask.sum())

# ---------------------------------------------------------------------------
# 2. Finite-difference Dirichlet Laplacian on the interior nodes of `mask`,
#    5-point stencil, sparse matrix, standard shift-invert eigensolve.
# ---------------------------------------------------------------------------
idx = -np.ones((G, G), dtype=np.int64)
interior_pts = np.argwhere(mask)
idx[mask] = np.arange(len(interior_pts))
n = len(interior_pts)
print("interior dof:", n)

rows, cols, vals = [], [], []
for k, (iy, ix) in enumerate(interior_pts):
    rows.append(k); cols.append(k); vals.append(4.0)
    for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
        ny, nx = iy+dy, ix+dx
        if 0 <= ny < G and 0 <= nx < G and mask[ny, nx]:
            j = idx[ny, nx]
            rows.append(k); cols.append(j); vals.append(-1.0)
        # else: Dirichlet zero boundary -- just omit (no off-diag contribution)

L = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n))

# smallest eigenvalues via shift-invert around 0 (Laplacian is PSD here)
evals, evecs = eigsh(L, k=6, sigma=0, which='LM')
order = np.argsort(evals)
evals = evals[order]; evecs = evecs[:, order]
print("eigenvalues:", evals)
print("spectral gap lambda2-lambda1 =", evals[1]-evals[0])

def to_grid(vec):
    g = np.zeros((G, G))
    g[mask] = vec
    return g

v1 = to_grid(evecs[:, 0])
v2 = to_grid(evecs[:, 1])
# normalize each to unit max-abs
v1 = v1 / np.max(np.abs(v1))
v2 = v2 / np.max(np.abs(v2))

# ---------------------------------------------------------------------------
# 3. Upsample to canvas resolution with smooth interpolation, then domain-
#    colour the complex combination Psi = v1 + i*v2 by phase (hue) and
#    magnitude (saturation/value), exactly like a wavefunction portrait --
#    this literally overlays the fundamental tone and the first excited mode
#    whose energy difference IS the spectral gap in question.
# ---------------------------------------------------------------------------
CANVAS = 2048
scale = CANVAS / G
v1_up = zoom(v1, scale, order=3)
v2_up = zoom(v2, scale, order=3)
mask_up = zoom(mask.astype(np.float64), scale, order=1) > 0.5

phase = np.arctan2(v2_up, v1_up)
amp = np.sqrt(v1_up**2 + v2_up**2)
amp_n = amp / np.percentile(amp[mask_up], 99.5)
amp_n = np.clip(amp_n, 0, 1.4)

hue = (phase / (2*np.pi)) % 1.0
sat = np.clip(0.25 + 0.75*amp_n, 0, 1)
val = np.clip(amp_n ** 0.75, 0, 1)
val = np.where(mask_up, val, 0.0)

# nodal line of v2 (the nodal set that literally splits the drum -- Courant
# nodal domain theorem territory) drawn as a fine dark seam
grad_v2 = np.abs(np.gradient(v2_up)[0]) + np.abs(np.gradient(v2_up)[1])
nodal = (np.abs(v2_up) < 0.02) & (grad_v2 > 0.0005) & mask_up

Hf, Sf, Vf = hue.ravel(), sat.ravel(), val.ravel()
i = np.floor(Hf*6.0); f = Hf*6.0 - i
p = Vf*(1-Sf); q = Vf*(1-f*Sf); t = Vf*(1-(1-f)*Sf)
ii = i.astype(int) % 6
conds = [ii==k for k in range(6)]
r = np.select(conds, [Vf,q,p,p,t,Vf])
gc = np.select(conds, [t,Vf,Vf,q,p,p])
b = np.select(conds, [p,p,t,Vf,Vf,q])
rgb = np.stack([r,gc,b], axis=-1).reshape(CANVAS, CANVAS, 3)

rgb[nodal] *= 0.15  # dark nodal seam

# outside domain: deep space void, very dark blue-black
outside = ~mask_up
rgb[outside] = np.array([0.015, 0.02, 0.035])

# a soft ring marking the drum boundary
from scipy.ndimage import binary_erosion
boundary = mask_up & ~binary_erosion(mask_up, iterations=2)
rgb[boundary] = np.clip(rgb[boundary]*1.4 + 0.08, 0, 1)

# bloom on bright peaks
lum = 0.2126*rgb[...,0]+0.7152*rgb[...,1]+0.0722*rgb[...,2]
bmask = np.clip((lum-0.55)/0.45,0,1)**2
bsrc = rgb*bmask[...,None]
bl1 = gaussian_filter(bsrc, sigma=(3,3,0))
bl2 = gaussian_filter(bsrc, sigma=(10,10,0))
final = rgb + 0.4*bl1 + 0.25*bl2
final = final/(1.0+final)
final = np.clip(final,0,1)**(1/2.2)

out = (final*255).astype(np.uint8)
Image.fromarray(out,'RGB').save('/home/user/claude-mythos-self-play/art_nifty/03_the_gap_you_can_see.png')
print("saved 03")
