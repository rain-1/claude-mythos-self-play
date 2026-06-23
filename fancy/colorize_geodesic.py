"""
Colour-map the cached diffractive-geodesic field into the final 4096 image.
Reads out/_geo_inten.npy and out/_geo_phase.npy (written by
diffractive_geodesic.py) so the palette can be tuned without re-solving.
"""
import numpy as np
from PIL import Image

inten = np.load("out/_geo_inten.npy").astype(np.float64)
phase = np.load("out/_geo_phase.npy").astype(np.float64)
S = inten.shape[0]

# --- intensity tone curve ---------------------------------------------------
norm = np.percentile(inten, 99.7)
I = np.clip(inten / norm, 0, 1.0)
I = I ** 0.52                                  # lift fringes, keep the void deep


def lerp(c0, c1, t):
    return c0[None, None, :] * (1 - t)[..., None] + c1[None, None, :] * t[..., None]


# a 5-stop gradient: void indigo -> violet -> magenta -> amber -> white crest
stops = [
    (0.00, np.array([0.010, 0.012, 0.035])),   # near-black indigo void
    (0.42, np.array([0.18, 0.08, 0.36])),      # violet
    (0.64, np.array([0.78, 0.18, 0.52])),      # magenta
    (0.84, np.array([1.00, 0.62, 0.24])),      # amber
    (1.00, np.array([1.00, 0.98, 0.90])),      # white-gold crest
]
rgb = np.zeros((S, S, 3))
for (a0, c0), (a1, c1) in zip(stops[:-1], stops[1:]):
    m = (I >= a0) & (I <= a1) if a1 < 1.0 else (I >= a0)
    t = np.clip((I - a0) / (a1 - a0), 0, 1)
    seg = lerp(c0, c1, t)
    rgb[m] = seg[m]

# subtle phase iridescence: tint the fringes by arg(U), strongest mid-tones
irid_str = (0.18 * np.clip(I * (1 - I) * 4, 0, 1))[..., None]
ph = 2 * np.pi * ((phase + np.pi) / (2 * np.pi))
irid = np.stack([np.cos(ph), np.cos(ph - 2.094), np.cos(ph + 2.094)], -1)
rgb = rgb + irid_str * irid

# bloom on the brightest crests for a touch of glow
crestmask = np.clip(I - 0.78, 0, 1) ** 1.4
rgb += crestmask[..., None] * np.array([0.6, 0.5, 0.35])[None, None, :]

rgb = 1.0 - np.exp(-1.55 * np.clip(rgb, 0, None))
rgb = np.clip(rgb, 0, 1) ** (1 / 1.85)

out = (rgb * 255 + 0.5).astype(np.uint8)
Image.fromarray(out, "RGB").save("out/05_diffractive_geodesic_4096.png", optimize=True)
Image.fromarray(out, "RGB").resize((768, 768), Image.LANCZOS).save(
    "out/05_diffractive_geodesic_preview.png")
print("wrote 4096 image + preview")
