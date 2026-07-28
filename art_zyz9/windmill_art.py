"""ONE SENTENCE - Zagier's windmill proof as a spiral walk. 2560 final."""
import numpy as np, sys, time
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from artkit import filmic, to_img, wide_bloom
from windmills import solutions, zeta, swap, verify, orbits

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
SS = 2 if FINAL >= 2048 else 1
S = FINAL * SS
rs = S / 2560.0
rng = np.random.default_rng(8009)

P = 8009
Ssol, zfix, sfix, reps = verify(P)
path = orbits(Ssol, P)
N = len(path)
assert N == len(Ssol) == 501 and path[0] == (1,1,2002) and path[-1][1] == path[-1][2]
a_, b_ = reps[0]
print(f"p={P}, N={N}, start={path[0]}, end={path[-1]}, {P}={a_}^2+{b_}^2")

# ---------- spiral layout (walk order, rim -> center) ----------
R0, Rc = 0.455*S, 0.105*S
c_sp = np.sqrt(np.pi*(R0**2 - Rc**2)/(N-1))   # equal spacing along arc AND between rings
cell = c_sp/1.12
pos = []
r = R0
theta = -np.pi/2                # start at top
for i in range(N-1):
    pos.append((r, theta))
    dth = c_sp / r
    theta += dth
    r -= (c_sp/(2*np.pi)) * dth
pos = np.array([(rr*np.cos(tt), rr*np.sin(tt)) for rr, tt in pos])
pos = np.vstack([pos, [0.0, 0.0]])   # the answer at the pupil
pos += S/2

# ---------- glyph rasterization ----------
buf = np.zeros((S, S, 3), np.float32)
ink = np.zeros((S, S), np.float32)     # outlines, dilated later

def rects_for(x, y, z):
    """axis-aligned rects (sqrt-compressed dims) of the windmill, centered at 0."""
    sx, sy, sz = np.sqrt(x), np.sqrt(y), np.sqrt(z)
    R = [(-sx/2, -sx/2, sx, sx)]                        # (x0,y0,w,h) core
    arm = (sx/2, -sx/2, sz, sy)                         # right arm
    # rotate 90deg CCW three times: (u,v) -> (-v-h?, ...) do numerically on corners
    def rot(rc):
        x0,y0,w,h = rc
        # corners
        cs = [(x0,y0),(x0+w,y0),(x0,y0+h),(x0+w,y0+h)]
        rc2 = [(-v,u) for u,v in cs]
        xs = [c[0] for c in rc2]; ys=[c[1] for c in rc2]
        return (min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys))
    a = arm
    for _ in range(4):
        R.append(a); a = rot(a)
    return R[:1] + R[1:5]

def fill_rect(img3, x0, y0, w, h, col, alpha):
    """additive fill with AA on edges via subpixel coverage (draw at SS, simple round)."""
    xi0, yi0 = int(np.floor(x0)), int(np.floor(y0))
    xi1, yi1 = int(np.ceil(x0+w)), int(np.ceil(y0+h))
    xi0c, yi0c = max(xi0,0), max(yi0,0)
    xi1c, yi1c = min(xi1,S), min(yi1,S)
    if xi1c <= xi0c or yi1c <= yi0c: return
    img3[yi0c:yi1c, xi0c:xi1c] += alpha*col[None,None,:]

def rect_outline(ink, x0, y0, w, h, alpha):
    xi0, yi0, xi1, yi1 = int(x0), int(y0), int(x0+w), int(y0+h)
    xi0, yi0 = max(xi0,0), max(yi0,0); xi1, yi1 = min(xi1,S-1), min(yi1,S-1)
    if xi1 <= xi0 or yi1 <= yi0: return
    ink[yi0:yi1+1, xi0] += alpha; ink[yi0:yi1+1, xi1] += alpha
    ink[yi0, xi0:xi1+1] += alpha; ink[yi1, xi0:xi1+1] += alpha

# palette: hue by core share x/sqrt(p)
def glyph_color(x):
    t = x/np.sqrt(P)          # 0..~1
    # slate-violet -> parchment -> ember
    c0 = np.array([0.50,0.58,0.86]); c1 = np.array([0.88,0.78,0.55]); c2 = np.array([1.00,0.55,0.22])
    if t < 0.5: c = c0 + (c1-c0)*(t/0.5)
    else:       c = c1 + (c2-c1)*((t-0.5)/0.5)
    return c

t0 = time.time()
scales = []; inkcol = []; halos = []
for i, (x, y, z) in enumerate(path):
    R = rects_for(x, y, z)
    ext = max(max(abs(r[0]), abs(r[0]+r[2]), abs(r[1]), abs(r[1]+r[3])) for r in R)*2
    sc = min(cell*1.35/ext, cell/9.0)
    scales.append(sc)
    cx, cy = pos[i]
    col = glyph_color(x)
    rad_i = np.hypot(cx-S/2, cy-S/2)
    special = 0.78 + 0.55*(1.0 - rad_i/(0.46*S))     # gathers light toward the pupil
    if i == 0: col = np.array([1.0,0.82,0.38]); special = 1.7         # gold start
    if i == N-1:
        col = np.array([0.42,0.95,1.0]); special = 2.4               # cyan answer
        sc *= 2.1
    for k, (x0,y0,w,h) in enumerate(R):
        alpha = (0.30 if k == 0 else 0.20)*special
        fill_rect(buf, cx+x0*sc, cy+y0*sc, max(w*sc,1.0), max(h*sc,1.0), col*0.85, alpha)
        # outline in the glyph's own colour: splat into per-colour ink via 3 channels
        for ch in range(3):
            pass
        rect_outline(ink, cx+x0*sc, cy+y0*sc, max(w*sc,1.0), max(h*sc,1.0), 0.7*special)
    inkcol.append(col)
    if x >= 87 and i != N-1:                          # near-answer windmills: x^2 close to p
        halos.append((cx, cy))
print("glyphs %.1fs" % (time.time()-t0))

# outlines: dilate + blur the scalar ink, tint softly warm-silver
from scipy.ndimage import grey_dilation
ink_d = grey_dilation(ink, size=(max(1,int(round(1.0*rs))),)*2)
ink_b = gaussian_filter(ink_d, 0.7*rs)
buf += ink_b[...,None]*np.array([0.80,0.80,0.88])[None,None,:]*0.42

# ---------- the walk thread (on top: the proof's alternation) ----------
thr_z = np.zeros((S,S), np.float32)   # zeta steps
thr_s = np.zeros((S,S), np.float32)   # swap steps
from artkit import splat_points
for i in range(N-1):
    p0, p1 = pos[i], pos[i+1]
    n = max(10, int(np.hypot(*(p1-p0))/0.9))
    t = np.linspace(0,1,n)
    mid = (p0+p1)/2; c = mid - S/2; nc = np.linalg.norm(c)
    c = c/(nc+1e-9)
    bow = np.sin(np.pi*t)[:,None]*c[None,:]*cell*0.12
    pts = p0[None,:]*(1-t)[:,None] + p1[None,:]*t[:,None] + bow
    target = thr_s if i % 2 == 0 else thr_z
    splat_points(target, pts[:,0], pts[:,1], 0.55*np.ones(n)*rs, S)
tz = gaussian_filter(thr_z, 0.8*rs); ts = gaussian_filter(thr_s, 0.8*rs)
buf += tz[...,None]*np.array([1.00,0.42,0.30])[None,None,:]*3.4
buf += ts[...,None]*np.array([0.25,0.78,0.85])[None,None,:]*3.4


# center + start glow
yy, xx = np.mgrid[0:S,0:S].astype(np.float32)
d2c = (xx-S/2)**2 + (yy-S/2)**2
rr = np.sqrt(d2c)
buf += np.exp(-d2c/(2*(0.30*S)**2))[...,None]*np.array([0.10,0.13,0.26])[None,None,:]*0.16   # deep fog
buf += np.exp(-d2c/(2*(0.062*S)**2))[...,None]*np.array([0.30,0.75,0.85])[None,None,:]*0.22
buf += np.exp(-((rr-0.088*S)/(1.6*rs))**2)[...,None]*np.array([1.0,0.85,0.5])[None,None,:]*0.30  # gold ring round the answer
d2s = (xx-pos[0][0])**2 + (yy-pos[0][1])**2
buf += np.exp(-d2s/(2*(0.03*S)**2))[...,None]*np.array([1.0,0.8,0.4])[None,None,:]*0.35

# near-answer ember halos
for hx, hy in halos:
    d2h = (xx-hx)**2 + (yy-hy)**2
    buf += np.exp(-d2h/(2*(0.015*S)**2))[...,None]*np.array([1.0,0.55,0.22])[None,None,:]*0.24

# bloom
lum = buf.max(-1)
bl = wide_bloom(np.maximum(lum-0.55,0).astype(np.float32), 16*rs)
buf += bl[...,None]*np.array([0.9,0.8,0.6])[None,None,:]*0.35

out = filmic(np.nan_to_num(buf), 1.5)**0.94
img = to_img(out)

# footer
W = img.size[0]; FH = int(0.075*W)
dr = ImageDraw.Draw(img, 'RGBA')
dr.rectangle([0, W-FH, W, W], fill=(4,6,10,214))
try:
    fs = max(9, int(0.0115*W))
    fm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", fs)
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", fs)
except OSError: fm = fb = ImageFont.load_default()
pad = int(0.016*W); ly = W-FH+pad//1
for txt, fnt, col in [
  ("ONE SENTENCE", fb, (238,205,140)),
  (f"x^2+4yz = {P} has 501 windmills, all of area {P}.  The involution zeta fixes exactly one (gold: x=y=1) -- so 501 is odd --", fm, (176,188,210)),
  (f"so the swap y<->z must also fix one (cyan pupil: arms square, 8009 = 85^2 + 28^2).  The alternating walk visits all 501.", fm, (176,188,210)),
]:
    dr.text((pad, ly), txt, font=fnt, fill=col); ly += int(fs*1.6)

if SS > 1: img = img.resize((FINAL,FINAL), Image.LANCZOS)
img.save("windmills_proto.png" if FINAL < 2048 else "windmills.png")
print("saved %.1fs" % (time.time()-t0))
