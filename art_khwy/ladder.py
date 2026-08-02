"""PIECE 2 (2560²) — 'The Ladder of Fainter Creases'  (MO 513816)
Chart: x = log_4 |z| in [-2.2, 5.4], y = arg z in [0, 2pi] (center row
= negative real axis). F(z) = sum 3^-n sqrt(1+z/4^n) (principal sheet).
Luminance: log|F'| (creases flare at each branch point -4^m, dimming
12x per rung). Warm overlay: |Im F| = the second sheet bleeding through
across the cut. Cyan: the |z|=1 Taylor aperture and the Hadamard
partner's pole ladder at +4^m (top/bottom edges).  All laws verified in
fseries.py / fexact.py to 30-60 digits."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rendlib import Canvas, save
from scipy.ndimage import gaussian_filter

S = 2560; SS = 2
W = H = S * SS
GX0, GX1 = -2.2, 5.4
gx = np.linspace(GX0, GX1, W, dtype=np.float64)
gy = np.linspace(0, 2*np.pi, H, dtype=np.float64)

absF1 = np.zeros((H, W), np.float32)   # |F'|
imF   = np.zeros((H, W), np.float32)   # |Im F|
argF  = np.zeros((H, W), np.float32)
CH = 256
NT = 60
for s in range(0, H, CH):
    e = min(s + CH, H)
    zz = (4.0 ** gx[None, :]) * np.exp(1j * gy[s:e, None])
    Fv = np.zeros(zz.shape, np.complex128)
    Fp = np.zeros(zz.shape, np.complex128)
    for n in range(NT):
        w = np.sqrt(1 + zz * 4.0**-n)
        Fv += 3.0**-n * w
        Fp += (3.0**-n * 4.0**-n * 0.5) / w
    absF1[s:e] = np.log10(np.abs(Fp) + 1e-12).astype(np.float32)
    imF[s:e] = np.abs(Fv.imag).astype(np.float32)
    argF[s:e] = np.angle(Fv).astype(np.float32)
print("field done", absF1.min(), absF1.max())

# ---- compose ----
cv = Canvas(W, H, (0.008, 0.010, 0.016))

# base luminance: log|F'| normalized with soft knee; keep grain of the ladder
lo, hi = np.percentile(absF1, 2), np.percentile(absF1, 99.8)
base = np.clip((absF1 - lo) / (hi - lo), 0, 1)
base = base ** 1.6
# equipotential web on log|F'| for texture (per-pixel gradient normalized)
gyy, gxx = np.gradient(absF1)
gmag = np.sqrt(gxx**2 + gyy**2) + 1e-9
DU = 0.13
frac = np.abs(((absF1 / DU) % 1.0) - 0.5) * 2  # 0 at contour
ring = np.clip(1 - (frac * DU / gmag) / (1.6 * SS), 0, 1) ** 2
web = (0.35 * ring * base).astype(np.float32)

steel = np.array([0.36, 0.47, 0.70], np.float32)
violet = np.array([0.52, 0.38, 0.72], np.float32)
hue_t = (0.5 + 0.5*np.cos(argF)).astype(np.float32)[..., None]
field_col = hue_t * steel + (1 - hue_t) * violet
cv.buf += (0.55*base + web)[..., None] * field_col

# warm second-sheet bleed: |Im F| (soft-knee); crease band glows
imn = imF / (np.percentile(imF, 99.5) + 1e-9)
imn = 1 - np.exp(-2.6 * imn)
amber = np.array([1.00, 0.62, 0.22], np.float32)
cv.buf += (0.85 * imn ** 1.35)[..., None] * amber

del absF1, imF, argF, base, web, ring, frac, gmag, gxx, gyy, field_col, hue_t, imn

def x2px(v): return (v - GX0) / (GX1 - GX0) * (W - 1)
def y2px(v): return v / (2*np.pi) * (H - 1)

# Taylor aperture |z|=1
cv.segments(np.array([[x2px(0), 0]]), np.array([[x2px(0), H-1]]),
            np.array([0.45, 0.80, 0.95]), width=1.4*SS, amp=0.16, step=0.7)

# branch-point stars at (m, pi) with 1/3-per-rung amplitude ramp (rank-lit)
mstars = np.arange(0, 6)
amps = 1.9 * (0.62 ** mstars)
cv.stars(x2px(mstars.astype(float)), np.full(6, y2px(np.pi)),
         np.array([1.0, 0.78, 0.35]), sigma=5.0*SS, amp=amps)
cv.stars(x2px(mstars.astype(float)), np.full(6, y2px(np.pi)),
         np.array([1.0, 0.92, 0.70]), sigma=1.8*SS, amp=amps)

# Hadamard partner pole needles at (m, 0) and (m, 2pi)
for yy in [1.0, H-2.0]:
    cv.stars(x2px(mstars.astype(float)), np.full(6, yy),
             np.array([0.55, 0.88, 1.0]), sigma=3.0*SS, amp=1.1*(0.72**mstars))
    A = np.stack([x2px(mstars.astype(float)), np.full(6, yy)], 1)
    B = A + np.array([0, 26*SS if yy < 10 else -26*SS])
    cv.segments(A, B, np.array([0.55, 0.88, 1.0]), width=1.0*SS,
                amp=0.5, amp_per=0.5*(0.72**mstars))

cv.bloom(sigmas=(4*SS, 14*SS, 40*SS), gains=(0.35, 0.22, 0.12), thresh=0.42)
img = cv.tonemap(k=1.7, gamma=2.1)

# downsample
pil = Image.fromarray(img).resize((S, S), Image.LANCZOS)
d = ImageDraw.Draw(pil)
FP = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def Fnt(sz): return ImageFont.truetype(FP, sz)
warm = (238, 209, 156); dim = (128, 136, 160); ice = (150, 208, 235)
d.text((S//2, 74), "T H E   L A D D E R   O F   F A I N T E R   C R E A S E S",
       font=Fnt(52), fill=warm, anchor="mm")
d.text((S//2, 128), "F(z) = Σ 3⁻ⁿ √(1 + z/4ⁿ)   on the log₄|z| × arg z cylinder   ·   MO 513816",
       font=Fnt(30), fill=dim, anchor="mm")
# rung labels
for m in range(6):
    px = int(x2px(m) / SS)
    d.text((px, int(y2px(np.pi)/SS) + 58), f"−4^{m}", font=Fnt(26),
           fill=(214, 168, 108), anchor="mm")
d.text((int(x2px(0)/SS) + 8, S - 430), "|z| = 1 — the Taylor aperture:\nthe series sees one crease;\nthe function owns them all",
       font=Fnt(27), fill=ice, anchor="lm", align="left")
d.text((S//2, S-150),
       "branch points at −4ⁿ (weight 3⁻ⁿ, sqrt monodromy) ⇒ F is neither D-finite nor q-holonomic.  Twin shores, one law:",
       font=Fnt(28), fill=dim, anchor="mm")
d.text((S//2, S-104),
       "c_m = C(½,m)/(1−4⁻ᵐ/3) at 0     ·     a_k = C(½,k)/(1−4ᵏ/6) at ∞     ·     between them  x^(−log₄3)·Φ(log₄x),  Φ̂ = Γ-exact",
       font=Fnt(28), fill=warm, anchor="mm")
d.text((S//2, S-58),
       "exact identity  F = Σ aₖ x^(½−k) + x^(−log₄3) Φ  verified to 10⁻⁵⁸ at x = 0.51, 2, 10, 100   ·   poles of the Hadamard partner at +4ⁿ (frame edges)",
       font=Fnt(24), fill=dim, anchor="mm")
pil.save("ladder_2560.png")
print("saved ladder_2560.png")
