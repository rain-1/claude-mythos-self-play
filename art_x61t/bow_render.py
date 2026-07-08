"""Composite the double rainbow from the computed spectral profile. v2: arc composition.

Usage: python3 bow_render.py <size> <out.png> [profile_tag] [seed] [k_expo] [bowgain]
"""
import numpy as np, sys, os, time
from scipy.ndimage import gaussian_filter
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spectra import spectra_to_rgb, tonemap

t0 = time.time()
S    = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
OUT  = sys.argv[2] if len(sys.argv) > 2 else "art_x61t/variants/bow_proto.png"
TAG  = sys.argv[3] if len(sys.argv) > 3 else ""
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 7
KEXP = float(sys.argv[5]) if len(sys.argv) > 5 else 1.7
BGAIN= float(sys.argv[6]) if len(sys.argv) > 6 else 0.62
TSUN = float(sys.argv[7]) if len(sys.argv) > 7 else 5778.0

d = np.load(f"art_x61t/data/bow_profile{TAG}.npz")
gamma, lams, I1, I2 = d["gamma"], d["lams"]*1e9, d["I1"], d["I2"]

lut1 = spectra_to_rgb(I1.T, lams, T=TSUN)  # [ngamma, 3] linear sRGB
lut2 = spectra_to_rgb(I2.T, lams, T=TSUN)
lum = lut1 @ np.array([0.2126, 0.7152, 0.0722])
norm = lum.max()
lut1 = (lut1/norm).astype(np.float32); lut2 = (lut2/norm).astype(np.float32)
LW = np.array([0.2126, 0.7152, 0.0722])
# chroma-preserving soft-knee on the radial profile: crest keeps its spectrum
for lut in (lut1, lut2):
    L = lut @ LW
    fkn = (1.0 - np.exp(-2.3*L))/(2.3*L + 1e-12)
    lut *= fkn[:, None].astype(np.float32)
# quiet the pool inside the primary bow (gamma < 40deg): dim + cool slightly
gdeg = np.rad2deg(gamma)
qs = 0.16 + 0.84*np.clip((gdeg-38.5)/2.6, 0, 1)
lut1 *= qs[:, None].astype(np.float32)
lut1 *= (1.0 + (1-qs)[:, None]*np.array([-0.16, -0.04, 0.22])).astype(np.float32)

# --- sky geometry: antisolar point below the bottom edge -> upper arc sweeps frame ---
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
cx, cy = 0.405*S, 1.28*S
# put primary crest (42 deg) at ~0.42 S from top at the centre-line:
r_crest = cy - 0.40*S
scale = np.deg2rad(41.6)/r_crest           # rad per px
g = np.hypot(xx-cx, yy-cy)*scale
gi = np.clip(g/(gamma[-1]-gamma[0])*(len(gamma)-1), 0, len(gamma)-1)
i0 = gi.astype(np.int32); f = (gi-i0)[..., None].astype(np.float32)
i1 = np.minimum(i0+1, len(gamma)-1)
lutb = lut1+lut2
bow = (1-f)*lutb[i0] + f*lutb[i1]           # [S,S,3] linear
del gi, i0, i1, f, g
print(f"bow field {time.time()-t0:.1f}s", flush=True)

# --- rain curtain: vertical streaks + rain-column patchiness ---
def streaks(S, sy, sx, so=0):
    n = np.random.default_rng(SEED+so).standard_normal((S, S)).astype(np.float32)
    m = gaussian_filter(n, (sy, sx)); return m/m.std()

w = (1.5*streaks(S, S*0.034, S*0.0030, 0)
     + 1.0*streaks(S, S*0.012, S*0.0014, 1)
     + 0.5*streaks(S, S*0.005, S*0.0009, 2))
w /= np.std(w)
# domain-warp: gentle varying shear so shafts fan instead of running parallel
from scipy.ndimage import map_coordinates
sh = gaussian_filter(np.random.default_rng(SEED+9).standard_normal(S).astype(np.float32),
                     S*0.08)
sh = sh/np.abs(sh).max()
xw = xx + 0.045*S*sh[None, :]*(yy/S)
w = map_coordinates(w, [yy, np.clip(xw, 0, S-1)], order=1)
rain = np.exp(0.50*w - 0.125)
# columns: broad vertical presence bands
col = streaks(S, S*0.45, S*0.055, 3)
rain *= np.clip(1.0 + 0.62*col, 0.05, 2.0)
# rain curtain thins toward the ground (bottom of frame)
fade = 1.0 - 0.85*np.clip((yy/S - 0.55)/0.45, 0, 1)**1.5
rain = (np.clip(rain, 0.03, 2.2)*fade)[..., None]
print(f"rain {time.time()-t0:.1f}s", flush=True)

# --- ambient storm sky (additive, cold) ---
cloud = streaks(S, S*0.10, S*0.045, 4) + 0.5*streaks(S, S*0.035, S*0.018, 5)
skyv = yy/S
amb = ((0.009 + 0.008*(1-skyv) + 0.0045*np.clip(cloud, -2.2, 2.2))[..., None]
       * np.array([0.34, 0.46, 0.62], dtype=np.float32))

img = bow*rain*BGAIN + amb
del bow, rain

# --- bloom only on the true crests ---
lumI = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
thr = np.percentile(lumI, 99.2)
mask = np.clip((lumI-thr)/(thr+1e-9), 0, None)[..., None]*img
for sg, gn in ((S*0.004, 0.55), (S*0.016, 0.30)):
    img += gn*gaussian_filter(mask, (sg, sg, 0))
print(f"bloom {time.time()-t0:.1f}s", flush=True)

out = tonemap(img, k=KEXP, gamma=2.15, sat=1.04)
Image.fromarray(out).save(OUT)
print(f"saved {OUT} {time.time()-t0:.1f}s")
