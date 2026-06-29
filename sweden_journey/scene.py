"""The Long Way Home — a procedural altitude vista for a flight home from Sweden.
Nordic summer dusk (the sun grazes the horizon, never quite setting), the curve
of the Earth with its thin atmosphere band, aurora curtains, a starfield, and a
glowing great-circle flight arc from Sweden (behind) to the warm glow of home
(ahead), with a plane marker for 'right now, today'.
"""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

W = int(sys.argv[1]) if len(sys.argv) > 1 else 2560
H = int(sys.argv[2]) if len(sys.argv) > 2 else 1440
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7
outp = sys.argv[4] if len(sys.argv) > 4 else "the_long_way_home.png"
rng = np.random.default_rng(seed)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
ny = yy / H            # 0 top -> 1 bottom
nx = xx / W
img = np.zeros((H, W, 3), np.float64)

def lerp_color(t, pts):
    xs = np.array([p[0] for p in pts]); cs = np.array([p[1] for p in pts], float)/255
    out = np.empty(t.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(t, xs, cs[:, c])
    return out

def vnoise(shape, sigma, s):
    """smooth value noise in [0,1] = blurred white noise (no upsample blocks)"""
    r = np.random.default_rng(s).random(shape)
    b = gaussian_filter(r, sigma)
    b -= b.min(); b /= (b.max()+1e-9)
    return b

def noise1d(n, sigma, s):
    r = np.random.default_rng(s).random(n)
    b = gaussian_filter(r, sigma); b -= b.min(); b /= (b.max()+1e-9)
    return b

# ---------------------------------------------------------------- sky gradient
sky = lerp_color(ny, [
    (0.00, ( 6,  10, 34)),    # deep space indigo
    (0.30, ( 18, 28, 70)),    # night blue
    (0.58, ( 40, 58,108)),    # dusk blue
    (0.72, ( 96, 92,132)),    # mauve dusk
    (0.84, (208,140,116)),    # warm horizon haze
    (0.90, (250,196,110)),    # the grazing sun band (Swedish gold)
    (0.95, (120, 96, 92)),    # darker just under haze
    (1.00, ( 20, 22, 40)),
])
img[:] = sky

# ---------------------------------------------------------------- Earth limb
cx_e, R_e = W*0.5, W*2.25
cy_e = H*0.86 + R_e            # centre far below frame -> shallow convex limb low in frame
dist = np.sqrt((xx-cx_e)**2 + (yy-cy_e)**2)
above = dist <= R_e            # sky side (closer to viewer than the limb? no: above limb)
# limb is where dist==R_e; sky is dist>R_e (farther up), earth is dist<R_e (lower)
sky_side = dist >= R_e
earth_side = ~sky_side

# atmosphere band: glow just ABOVE the limb (sky side), warm at the line -> cyan -> blue up
d_above = (dist - R_e)
atmo_t = np.clip(d_above / (H*0.16), 0, 1)
atmo_col = lerp_color(atmo_t, [
    (0.00, (255,224,150)),    # gold rim at the limb
    (0.12, (255,150,110)),    # orange
    (0.30, (120,180,210)),    # cyan
    (0.60, ( 50, 90,170)),    # blue
    (1.00, (  8, 14, 44)),
])
atmo_strength = np.exp(-d_above/(H*0.05)) * sky_side
img = img*(1-atmo_strength[...,None]*0.9) + atmo_col*(atmo_strength[...,None]*0.9)

# ---------------------------------------------------------------- aurora curtains
def aurora(base_x_frac, halfwidth_frac, wave_amp, baseline_frac, height_frac,
           hue_bottom, hue_top, strength, s):
    # the curtain meanders horizontally as a smooth function of height
    drift = (noise1d(H, H*0.05, s+1)-0.5)*2*W*wave_amp
    cx = base_x_frac*W + drift[:,None]
    # soft horizontal envelope of the whole curtain
    env = np.exp(-((xx-cx)/(W*halfwidth_frac))**2)
    # fine vertical rays = smooth 1D noise along x, with a gentle vertical shear
    shear = (ny-baseline_frac)*W*0.04
    ray_field = noise1d(W*2, W*0.0016, s+2)        # high-freq but smooth
    idx = np.clip((xx + shear).astype(int), 0, W*2-1)
    rays = ray_field[idx]
    rays = np.clip((rays-0.35)/0.65, 0, 1)**1.3
    # vertical profile: green base, rays RISE upward and fade; quick cutoff below
    base_y = (baseline_frac + (noise1d(W, W*0.02, s+5)[np.clip(xx.astype(int),0,W-1)]-0.5)*0.04)
    vp = (base_y - ny)/height_frac                 # 0 at baseline, 1 at top (upward)
    vprof = np.where(vp>=0, np.exp(-vp*1.3), np.exp(vp*16))  # hard cutoff below baseline
    a = env*rays*vprof*strength
    mid = tuple((hue_bottom[i]+hue_top[i])//2 for i in range(3))
    col = lerp_color(np.clip(vp,0,1), [(0.0,hue_bottom),(0.5,mid),(1.0,hue_top)])
    return a[...,None]*col

au = np.zeros_like(img)
au += aurora(0.33, 0.12, 0.05, 0.47, 0.34, (60,255,140),(70,110,235), 1.30, 11)
au += aurora(0.60, 0.10, 0.045, 0.42, 0.30, (110,255,170),(150,95,225), 0.95, 23)
au = gaussian_filter(au, sigma=(2.0,1.0,0))
img += au

# ---------------------------------------------------------------- stars
nst = 900
sx = rng.integers(0, W, nst); sy = (rng.power(0.7, nst)*H*0.78).astype(int)
mag = rng.power(3.0, nst)
star = np.zeros((H, W))
for i in range(nst):
    b = 0.25 + 1.3*mag[i]
    star[sy[i], sx[i]] += b
# fewer stars in the bright horizon haze
star *= np.clip((0.86-ny)/0.5, 0.05, 1.0)
star_glow = gaussian_filter(star, 0.7) + 0.4*gaussian_filter(star, 2.2)
tint = lerp_color(rng.random(1), [(0,(255,255,255))])  # white base
img += star_glow[...,None]*np.array([1.0,0.98,0.92])*0.9

# ---------------------------------------------------------------- city lights below the limb
ncity = 240
clx = rng.integers(0, W, ncity)
# place them just under the limb following the curve
under = R_e - rng.random(ncity)*H*0.10
ang = np.arctan2(0, 1)  # not used; place by x then find limb y
city = np.zeros((H, W))
for i in range(ncity):
    x = clx[i]
    # y on limb for this x:
    val = R_e**2 - (x-cx_e)**2
    if val <= 0: continue
    ylimb = cy_e - np.sqrt(val)
    yy2 = int(ylimb + rng.random()*H*0.09 + 2)
    if 0 <= yy2 < H:
        city[yy2, x] += 0.4 + rng.random()*0.9
city_glow = gaussian_filter(city, 0.6) + 0.5*gaussian_filter(city,2.5)
img += city_glow[...,None]*np.array([1.0,0.82,0.5])*0.8

# earth body: darken below limb
earth_dark = lerp_color(np.clip((R_e-dist)/(H*0.6),0,1), [(0,(14,16,30)),(1,(3,4,9))])
img = np.where(earth_side[...,None], earth_dark*0.9 + img*0.1, img)
# re-add city glow over the darkened earth
img += city_glow[...,None]*np.array([1.0,0.82,0.5])*0.7*earth_side[...,None]

# ---------------------------------------------------------------- flight arc
# endpoints: Sweden (left, behind) -> home (right, ahead)
P0 = np.array([W*0.16, H*0.52])      # Sweden
P1 = np.array([W*0.86, H*0.44])      # home
ctrl = np.array([W*0.5, H*0.16])     # arc apex (great-circle bow upward)
t = np.linspace(0, 1, 4000)[:,None]
arc = (1-t)**2*P0 + 2*(1-t)*t*ctrl + t**2*P1
arcbuf = np.zeros((H, W))
dashbuf = np.zeros((H, W))
arclen = np.cumsum(np.r_[0, np.hypot(np.diff(arc[:,0]), np.diff(arc[:,1]))])
for i in range(arc.shape[0]):
    x, y = arc[i]; xi, yi = int(round(x)), int(round(y))
    if 0<=xi<W and 0<=yi<H:
        arcbuf[yi, xi] += 1.0
        if (int(arclen[i]/22) % 2) == 0:
            dashbuf[yi, xi] += 1.0
arc_glow = (gaussian_filter(arcbuf, 1.0)*1.0 + gaussian_filter(arcbuf, 4.0)*0.6
            + gaussian_filter(arcbuf, 12.0)*0.35)
dash_core = gaussian_filter(dashbuf, 0.6)
arc_col = np.array([1.0, 0.86, 0.55])
img += arc_glow[...,None]*arc_col*0.5
img += dash_core[...,None]*np.array([1.0,0.96,0.85])*0.9

def glow_point(cx, cy, rad, color, amp):
    g = np.exp(-(( (xx-cx)**2+(yy-cy)**2 )/(2*rad**2)))
    img_local = g[...,None]*np.array(color)*amp
    return img_local

# endpoint glows
img += glow_point(*P0, H*0.05, [0.30,0.55,1.0], 0.8)     # Sweden blue
img += glow_point(*P0, H*0.018, [1.0,0.85,0.4], 1.0)     # Sweden gold core
img += glow_point(*P1, H*0.075, [1.0,0.72,0.42], 1.1)    # home amber (bigger, ahead)
img += glow_point(*P1, H*0.02, [1.0,0.92,0.7], 1.2)

# plane marker: ~68% along the arc (today, mid-flight, almost there)
pi = int(0.68*(arc.shape[0]-1))
px, py = arc[pi]
# little comet trail behind
trail = np.zeros((H,W))
for j in range(pi-160, pi):
    if j<0: continue
    x,y = arc[j]; xi,yi=int(round(x)),int(round(y))
    if 0<=xi<W and 0<=yi<H:
        trail[yi,xi] += (j-(pi-160))/160.0
trailg = gaussian_filter(trail, 2.0)
img += trailg[...,None]*np.array([1.0,0.95,0.8])*0.9
img += glow_point(px, py, H*0.012, [1.0,1.0,1.0], 1.4)
img += glow_point(px, py, H*0.03, [1.0,0.9,0.7], 0.7)

# ---------------------------------------------------------------- tone map
img = img / (1 + 0.0)            # already in scene-linear-ish
img = 1 - np.exp(-1.18*np.clip(img,0,None))   # filmic
img = np.clip(img, 0, 1) ** 0.92
out = (img*255).astype(np.uint8)
pim = Image.fromarray(out)

# ---------------------------------------------------------------- caption + labels
draw = ImageDraw.Draw(pim)
def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(p, sz)
        except: pass
    return ImageFont.load_default()
S = H/1440.0
fbig = font(int(40*S)); fsm = font(int(21*S))
def text_sp(x, y, s, f, fill, sp):
    cx = x
    for ch in s:
        draw.text((cx, y), ch, font=f, fill=fill)
        cx += draw.textlength(ch, font=f) + sp
# endpoint labels
draw.text((P0[0]-int(10*S), P0[1]+int(18*S)), "SVERIGE", font=fsm, fill=(200,215,255))
draw.text((P1[0]-int(20*S), P1[1]+int(20*S)), "hem", font=font(int(30*S)), fill=(255,224,170))
# title bottom-left
text_sp(int(60*S), H-int(110*S), "THE LONG WAY HOME", fbig, (244,236,222), int(6*S))
draw.text((int(62*S), H-int(56*S)),
          "two weeks of midsummer light  ·  Stockholm ↗ home  ·  June 2026",
          font=fsm, fill=(176,184,210))

pim.save(outp)
print("saved", outp, pim.size)
