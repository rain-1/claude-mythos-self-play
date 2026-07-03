"""03 — TWO RAINS, ONE LAW  (2048 x 2048)

The 3-point correlation field R3(u,v) of a unit-spacing point process:
how often, standing on one level, you find neighbours at displacements u
and v. Repulsion digs black canyons along u=0, v=0, u=v — a six-armed
star of absence — and piles faint golden pearls where u and v are both
near whole spacings (the crystal the repulsion wishes it could build).

LEFT half: grown from the first 2,001,052 zeros of the Riemann zeta
function (Odlyzko's tables), unfolded to unit mean spacing.
RIGHT half: grown from the bulk eigenvalues of Gaussian-Unitary-Ensemble
random matrices (Dumitriu-Edelman tridiagonal beta=2).

Two utterly different makers — the primes' spectrum and quantum chaos —
draw the same figure (Montgomery's pair-correlation theorem, made 2-D).
The only seam is the noise. Find it.
"""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image
from r3_field import r3_hist, r3_theory

OUT = 2048
CROP = 30          # display |u|,|v| < 3.6 of the 4.2 field

# ---------------- fields ----------------
Hz = np.load("r3_zeta2M.npy")
import os
g = np.load("gue_levels.npy")
if os.path.exists("gue_levels2.npy"):
    g2 = np.load("gue_levels2.npy")
    g = np.concatenate([g, g2 + 2e9])
print("GUE levels:", len(g))
Hg = r3_hist(g)
np.save("r3_gue.npy", Hg)
T = r3_theory()

# ---- verification block (printed, quoted in README) ----
ez = np.median(np.abs(Hz - T)); eg = np.median(np.abs(Hg - T))
ezg = np.median(np.abs(Hz - Hg)); e1z = np.median(np.abs(Hz - 1))
print(f"VERIFY median|zeta-theory|={ez:.4f}  |gue-theory|={eg:.4f}  "
      f"|zeta-gue|={ezg:.4f}  |zeta-flat1|={e1z:.4f}")

def prep(H):
    H = H[CROP:-CROP, CROP:-CROP]
    Hs = gaussian_filter(H, 0.8)
    return zoom(Hs, OUT / H.shape[0], order=3)

Fz, Fg = prep(Hz), prep(Hg)
# join: u is the COLUMN axis (x). left half u<0 -> zeta, right -> GUE.
# r3_hist axes: H[iu, iv] with u along axis0. transpose so x=u, y=v.
Fz, Fg = Fz.T, Fg.T
xs = np.linspace(-3.6, 3.6, OUT)
w = np.clip((xs - (-0.12)) / 0.24, 0, 1)      # 0 left, 1 right (crossfade)
w = w[None, :] * np.ones((OUT, 1))
F = Fz * (1 - w) + Fg * w
D = F - 1.0

# ---------------- tone (locked from proto_r3c) ----------------
neg = np.clip(np.where(D < 0, -D, 0), 0, 1)
pos = np.clip(np.where(D > 0, D, 0), 0, None)
img = np.zeros(F.shape + (3,))
PLATEAU = np.array([0.13, 0.095, 0.19])
WALLGLOW = np.array([0.10, 0.35, 0.95])
FLOOR = np.array([0.004, 0.004, 0.025])
GOLD = np.array([1.00, 0.78, 0.30])
ROSE = np.array([0.95, 0.42, 0.40])
img += PLATEAU * (1 + 2.2 * np.clip(D, -0.04, 0.04) / 0.04 * 0.35)[..., None]
rim = np.exp(-((neg - 0.45) / 0.16) ** 2) * (neg > 0.08)
floor = np.clip((neg - 0.55) / 0.4, 0, 1) ** 1.3
img += WALLGLOW * (rim * 0.55)[..., None]
img *= (1 - floor[..., None] * 0.985)
img += FLOOR * floor[..., None]
p1 = 1 - np.exp(-pos * 22)
img += ROSE * (p1 ** 1.5)[..., None] * 0.5
img += GOLD * (p1 ** 3.0)[..., None] * 1.1
lum = (img * [0.35, 0.5, 0.15]).sum(2)
mask = np.clip((lum - 0.35) / 0.45, 0, 1) ** 2
img += 0.45 * gaussian_filter(mask, 8 * OUT / 840)[..., None] * np.array([0.9, 0.7, 0.5])
yy, xx = np.mgrid[0:OUT, 0:OUT] / (OUT - 1) * 2 - 1
r2 = xx ** 2 + yy ** 2
img *= (1 - 0.32 * np.clip(r2 - 0.35, 0, 1.2) / 1.2)[..., None]
img = 1 - np.exp(-2.2 * img)
Image.fromarray((np.clip(img, 0, 1) ** 0.95 * 255).astype(np.uint8)
                ).save("03_two_rains_one_law.png")
print("saved 03_two_rains_one_law.png")
