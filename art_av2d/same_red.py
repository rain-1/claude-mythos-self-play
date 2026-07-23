"""The Same Red — 122 metameric spectra, one perceived color.
Each iris pane renders one spectrum honestly: at radius r the wavelength is
lambda(r), the pane's brightness is S_i(lambda), the hue is the spectral color.
All 122 integrate to the SAME CIE XYZ (verified ~1e-14): the pupil.
"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d
from lib import wide_bloom, filmic, to_img, nzpct

FINAL = int(sys.argv[1]) if len(sys.argv)>1 else 1024
SS = 2; S = FINAL*SS; rs = FINAL/2560.0
rng = np.random.default_rng(7)

# ---- CIE 1931 CMFs
dat = np.loadtxt('ciexyz31.csv', delimiter=',')
lam_all, cmf = dat[:,0], dat[:,1:4]
sel = (lam_all>=400)&(lam_all<=700)
lam = lam_all[sel]; CMF = cmf[sel]            # (301,3)
NL = len(lam)

# ---- target red: smooth spectrum peaked long-wave
S0 = 0.15*np.exp(-((lam-480)/70.)**2) + 1.0*np.exp(-((lam-625)/45.)**2)
XYZ_T = CMF.T @ S0
xy = XYZ_T[:2]/XYZ_T.sum()
print("target xy chromaticity:", np.round(xy,4))

# ---- metamer sampling: smooth basis + null space
NB = 24
centers = np.linspace(402, 698, NB)
B = np.exp(-((lam[:,None]-centers[None,:])/30.0)**2)   # (301,NB)
A = CMF.T @ B                                          # (3,NB)
# null space of A
_,_,Vt = np.linalg.svd(A)
NS = Vt[3:]                                            # (NB-3, NB)
N_MET = 122
specs = [S0]
tries = 0
while len(specs) < N_MET:
    tries += 1
    nmix = rng.integers(1,4)
    z = rng.normal(size=(NB-3,)) * (rng.random(NB-3) < 0.5*nmix)
    if not z.any(): continue
    z = z/np.linalg.norm(z)
    pert = B @ (NS.T @ z)                              # spectrum-space perturbation, zero XYZ
    # max step keeping S0 + t*pert >= 0
    neg = pert < -1e-12
    tmax = np.min(-S0[neg]/pert[neg]) if neg.any() else 3.0
    t = tmax * rng.uniform(0.88, 0.995)
    Snew = S0 + t*pert
    if Snew.min() < -1e-9: continue
    specs.append(np.clip(Snew,0,None))
specs = np.array(specs[:N_MET])                        # (122, 301)
XYZs = specs @ CMF                                     # (122,3)
err = np.abs(XYZs - XYZ_T).max()/XYZ_T.max()
D = np.linalg.norm(specs[:,None,:]-specs[None,:,:],axis=2)
np.fill_diagonal(D, np.inf)
print(f"metamers: {len(specs)}  max rel XYZ err: {err:.2e}  min pairwise L2: {D.min():.3f}  mean: {D[np.isfinite(D)].mean():.3f}")

# order panes by spectral centroid
cent = (specs*lam).sum(1)/specs.sum(1)
order = np.argsort(cent)
specs = specs[order]

# ---- spectral colors and shared red
M = np.array([[ 3.2406,-1.5372,-0.4986],[-0.9689, 1.8758, 0.0415],[ 0.0557,-0.2040, 1.0570]])
def xyz_to_rgb(xyz):
    rgb = M @ xyz
    w = max(0.0, -rgb.min())          # desaturate into gamut
    rgb = rgb + w
    if rgb.max()>0: rgb = rgb/rgb.max()
    return np.clip(rgb,0,1)
spec_rgb = np.array([xyz_to_rgb(CMF[i]) for i in range(NL)])   # (301,3)
shared = M @ (XYZ_T/XYZ_T[1])         # luminance-normalized
shared = np.clip(shared,0,None); shared = shared/max(shared.max(),1e-9)
print("shared sRGB red:", np.round(shared,3))

# ---- polar field render
yy,xx = np.mgrid[0:S,0:S].astype(np.float32)
cx = cy = S/2
dx, dyv = xx-cx, yy-cy
r = np.hypot(dx,dyv)/ (S/2)           # 0..~1.41
th = np.arctan2(dyv,dx)               # -pi..pi
R_PUP, R_IN, R_OUT = 0.190, 0.265, 0.88
# wavelength map: rim->400, pupil->700
u = np.clip((R_OUT - r)/(R_OUT-R_IN), 0, 1)  # 0 rim .. 1 inner
lam_lo, lam_hi = 415.0, 685.0
li = np.clip(((lam_lo-400) + u*(lam_hi-lam_lo)).astype(int), 0, NL-1)
# pane index with per-pane radial wobble
NP = N_MET
base = (th+np.pi)/(2*np.pi)*NP
wob_tab = gaussian_filter1d(rng.normal(size=(NP, 64)), 6, axis=1, mode='wrap')*3.2
rr_idx = np.clip((np.clip((r-R_IN)/(R_OUT-R_IN),0,1)*63).astype(int),0,63)
pane_f = base + 0.0
pane = np.floor(pane_f).astype(int) % NP
wob = wob_tab[pane, rr_idx]
pane_f2 = base + wob*0.26
pane2 = np.floor(pane_f2).astype(int) % NP
frac = pane_f2 - np.floor(pane_f2)
# lead line between panes: darken near boundaries
edge_w = 0.10
lead = 1.0 - np.exp(-((np.minimum(frac,1-frac))/edge_w)**2*0.5)  # ~0 at boundary
Stab = specs / specs.max(axis=1, keepdims=True)
Stab = Stab**1.5
bright = Stab[pane2, li]              # per-pixel spectral power of its pane
col = spec_rgb[li]                    # (S,S,3)
col = np.clip(col + 0.4*(col - col.mean(axis=-1, keepdims=True)), 0, 1)
ann = (r>=R_IN)&(r<=R_OUT)
fade_out = np.clip((R_OUT-r)/0.035,0,1)*np.clip((r-R_IN)/0.012,0,1)
field = np.where(ann, bright*lead*fade_out, 0).astype(np.float32)

rgb = col*field[...,None]
rgb = gaussian_filter(rgb, (1.2*SS*rs,1.2*SS*rs,0))
# glow
lum = rgb.mean(2)
gl = wide_bloom(lum, 12*SS*rs); gl/=max(gl.max(),1e-9)
rgb += 0.22*gl[...,None]*np.array([1.0,0.85,0.75])[None,None,:]

# pupil: the shared red
pup = np.clip((R_PUP-r)/0.012,0,1)
core = np.exp(-(r/(0.55*R_PUP))**2)
rgb += (pup*(0.55+0.75*core))[...,None]*shared[None,None,:]
pglow = wide_bloom(pup.astype(np.float32), 30*SS*rs); pglow/=max(pglow.max(),1e-9)
rgb += 0.5*pglow[...,None]*shared[None,None,:]
# limbal collapse ring: hot rim right at the pupil edge (where integration happens)
ring = np.exp(-((r-R_PUP*1.035)/0.007)**2)
rgb += 0.85*ring[...,None]*np.array([1.15,0.72,0.50])[None,None,:]
# thin outer limbal ring
oring = np.exp(-((r-R_OUT)/0.008)**2)
rgb += 0.16*oring[...,None]*np.array([0.6,0.72,0.95])[None,None,:]

out = filmic(rgb, k=1.55, gamma=0.86)
from PIL import Image, ImageDraw, ImageFont
img = to_img(out).resize((FINAL,FINAL), Image.LANCZOS)
draw = ImageDraw.Draw(img)
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", max(10,int(15*FINAL/1024)))
except: font = ImageFont.load_default()
draw.text((int(0.018*FINAL), int(0.975*FINAL)),
 f"122 DIFFERENT SPECTRA · ONE CIE XYZ (REL ERR {err:.0e}) · MIN PAIRWISE L2 {D.min():.2f} · THE PUPIL IS ALL THE EYE KEEPS",
 fill=(120,124,135), font=font)
img.save(f'same_red_{FINAL}.png'); print("saved", f'same_red_{FINAL}.png')
