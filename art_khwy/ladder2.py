"""PIECE 2 v2 — 'The Ladder of Fainter Creases'
Luminance = log10 |F(z) - A(z)|, A = 3-term far-shore ladder law.
The deviation IS the story: O(1) inside the aperture (the law fails),
lobes of size 3^-m at every crease -4^m, and the x^(-log4 3) Phi tail
far out. ECDF-blend normalization keeps all rungs legible."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rendlib import Canvas
from scipy.ndimage import gaussian_filter

S = 2560; SS = 2
W = H = S * SS
GX0, GX1 = -2.2, 5.4
gx = np.linspace(GX0, GX1, W, dtype=np.float64)
gy = np.linspace(0, 2*np.pi, H, dtype=np.float64)

logD = np.zeros((H, W), np.float32)
argD = np.zeros((H, W), np.float32)
a = [6/5, 3/2, 3/40]
CH = 192; NT = 60
for s in range(0, H, CH):
    e = min(s + CH, H)
    zz = (4.0 ** gx[None, :]) * np.exp(1j * gy[s:e, None])
    Fv = np.zeros(zz.shape, np.complex128)
    for n in range(NT):
        Fv += 3.0**-n * np.sqrt(1 + zz * 4.0**-n)
    sq = np.sqrt(zz)
    Av = a[0]*sq + a[1]/sq + a[2]/sq**3
    Dv = Fv - Av
    logD[s:e] = np.log10(np.abs(Dv) + 1e-14).astype(np.float32)
    argD[s:e] = np.angle(Dv).astype(np.float32)
print("field done", logD.min(), logD.max())

# ---- luminance: ECDF blend with soft linear knee ----
flat = logD.ravel()
qs = np.quantile(flat, np.linspace(0, 1, 512))
ecdf = np.interp(logD, qs, np.linspace(0, 1, 512)).astype(np.float32)
lin = np.clip((logD - (-7.5)) / (0.8 - (-7.5)), 0, 1)
lum = (0.55 * ecdf + 0.45 * lin) ** 1.9
del flat, qs, ecdf, lin

# equipotential web on logD (the crease lobes get growth-ring texture)
gyy, gxx = np.gradient(logD)
gmag = np.sqrt(gxx**2 + gyy**2) + 1e-9
DU = 0.35
frac = np.abs(((logD / DU) % 1.0) - 0.5) * 2
ring = np.clip(1 - (frac * DU / gmag) / (1.5 * SS), 0, 1) ** 2
del gxx, gyy, frac

cv = Canvas(W, H, (0.008, 0.010, 0.016))
steel = np.array([0.30, 0.42, 0.68], np.float32)
violet = np.array([0.50, 0.34, 0.70], np.float32)
amberF = np.array([0.95, 0.58, 0.22], np.float32)
# hue: phase of deviation -> 3-anchor cyclic warm/cool
t1 = (0.5 + 0.5*np.cos(argD)).astype(np.float32)
t2 = (0.5 + 0.5*np.cos(argD - 2.1)).astype(np.float32)
t3 = np.clip(1 - t1 - t2 * 0.5, 0, 1)
colf = (t1[..., None]*steel + t2[..., None]*violet + t3[..., None]*amberF)
colf /= np.maximum(colf.max(axis=2, keepdims=True), 1) * 1.0
cv.buf += (0.80 * lum + 0.55 * ring * lum)[..., None] * colf
del argD, t1, t2, t3, colf, ring, lum, gmag, logD

def x2px(v): return (v - GX0) / (GX1 - GX0) * (W - 1)
def y2px(v): return v / (2*np.pi) * (H - 1)

# Taylor aperture
cv.segments(np.array([[x2px(0), 0]]), np.array([[x2px(0), H-1]]),
            np.array([0.45, 0.82, 0.95]), width=1.5*SS, amp=0.14, step=0.7)
# rung stars
m6 = np.arange(0, 6)
amps = 2.2 * (0.62 ** m6)
cv.stars(x2px(m6.astype(float)), np.full(6, y2px(np.pi)),
         np.array([1.0, 0.80, 0.38]), sigma=6.0*SS, amp=amps)
cv.stars(x2px(m6.astype(float)), np.full(6, y2px(np.pi)),
         np.array([1.0, 0.94, 0.74]), sigma=2.0*SS, amp=amps*0.8)
# Hadamard pole needles at arg 0 / 2pi edges
for yy, sgn in [(2.0, 1), (H-3.0, -1)]:
    cv.stars(x2px(m6.astype(float)), np.full(6, yy),
             np.array([0.55, 0.88, 1.0]), sigma=2.6*SS, amp=1.5*(0.72**m6))
    A_ = np.stack([x2px(m6.astype(float)), np.full(6, yy)], 1)
    B_ = A_ + np.array([0, sgn*38.0*SS])
    cv.segments(A_, B_, np.array([0.55, 0.88, 1.0]), width=1.1*SS,
                amp=1.0, amp_per=1.0*(0.72**m6))

cv.bloom(sigmas=(4*SS, 14*SS, 44*SS), gains=(0.40, 0.24, 0.13), thresh=0.40)
img = cv.tonemap(k=1.9, gamma=2.1)
pil = Image.fromarray(img).resize((S, S), Image.LANCZOS)
d = ImageDraw.Draw(pil)
FP = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def Fnt(sz): return ImageFont.truetype(FP, sz)
warm = (240, 212, 158); dim = (135, 142, 168); ice = (155, 210, 238)
d.text((S//2, 74), "T H E   L A D D E R   O F   F A I N T E R   C R E A S E S",
       font=Fnt(52), fill=warm, anchor="mm")
d.text((S//2, 128),
       "F(z) = Σ 3⁻ⁿ√(1+z/4ⁿ)  ·  brightness = deviation from the far-shore law  ·  MO 513816",
       font=Fnt(30), fill=dim, anchor="mm")
for m in range(6):
    px = int(x2px(m) / SS)
    d.text((px, int(y2px(np.pi)/SS) + 60), f"−4^{m}", font=Fnt(27),
           fill=(220, 175, 112), anchor="mm")
d.text((int(x2px(0)/SS) + 10, 320), "|z| = 1 — the Taylor aperture", font=Fnt(27), fill=ice, anchor="lm")
d.text((S//2, S-150),
       "square-root creases at −4ⁿ, each a third as loud, four times as far  ⇒  infinitely many branch points:  F is neither D-finite nor q-holonomic",
       font=Fnt(27), fill=dim, anchor="mm")
d.text((S//2, S-104),
       "twin shores, one law:   c_m = C(½,m)/(1−4⁻ᵐ/3)  at 0      ·      a_k = C(½,k)/(1−4ᵏ/6)  at ∞      ·      between them  x^(−log₄3)·Φ(log₄x)",
       font=Fnt(28), fill=warm, anchor="mm")
d.text((S//2, S-58),
       "exact:  F = Σ aₖx^(½⁻ᵏ) + x^(−log₄3)Φ  (verified to 10⁻⁵⁸ at x=0.51, 2, 10, 100);  Φ̂ⱼ = −Γ(sⱼ)Γ(−½−sⱼ)/(Γ(−½)ln4)  ·  Hadamard-partner poles at +4ⁿ on the frame edges",
       font=Fnt(24), fill=dim, anchor="mm")
pil.save("ladder_2560.png")
print("saved")
