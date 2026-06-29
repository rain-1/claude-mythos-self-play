"""Midsommar — the celebration in the sun: the leaf-wreathed maypole
(midsommarstang) in a flowering meadow, with rings of people dancing around it,
hand in hand, under a bright Swedish summer sky.
"""
import sys, numpy as np
from PIL import ImageDraw
from scipy.ndimage import gaussian_filter
import vista as V

W = int(sys.argv[1]) if len(sys.argv)>1 else 2560
H = int(sys.argv[2]) if len(sys.argv)>2 else 1440
seed = int(sys.argv[3]) if len(sys.argv)>3 else 6
outp = sys.argv[4] if len(sys.argv)>4 else "midsommar.png"
rng = np.random.default_rng(seed)
yy, xx, ny, nx = V.grid(H, W)
img = np.zeros((H, W, 3))
hor = 0.40                                   # horizon

# ---------------- sky ----------------
sky = V.lerp_color(np.clip(ny/hor,0,1), [
    (0.00, ( 78,148,214)),    # summer blue
    (0.55, (140,184,224)),
    (1.00, (214,228,234)),    # pale at horizon
])
img[ny<hor] = sky[ny<hor]
# sun high-right
sx, sy = 0.80*W, 0.16*H
img += np.exp(-(((xx-sx)/(0.34*W))**2+((yy-sy)/(0.34*H))**2))[...,None]*np.array([1.0,0.92,0.7])*0.55*(ny<hor)[...,None]
img += np.exp(-(((xx-sx)/(0.045*W))**2+((yy-sy)/(0.045*H))**2))[...,None]*np.array([1.0,0.98,0.9])*1.0
# soft clouds
cl = V.fbm((H,W), 70, 4, seed+2)
clm = np.clip((cl-0.55)/0.3,0,1)*np.clip((hor-ny)/hor,0,1)
img += (clm*0.7)[...,None]*np.array([1.0,1.0,1.0])

# ---------------- distant treeline ----------------
base = hor
top = np.full(W, base)
xc = np.arange(W)
for _ in range(420):
    c = rng.integers(-20,W+20); h=(0.012+0.05*rng.random()**1.7); wd=(0.004+0.012*rng.random())*W
    top = np.minimum(top, base - h*np.clip(1-np.abs(xc-c)/wd,0,1))
tmask = (ny>=top[None,:]) & (ny<hor+0.012)
treecol = V.lerp_color(0.5+0.5*V.vnoise((H,W),(5,3),seed+3), [(0,(28,60,40)),(1,(46,92,56))])
img[tmask] = treecol[tmask]

# ---------------- meadow ----------------
fmask = ny>=hor
ft = np.clip((ny-hor)/(1-hor),0,1)
field = V.lerp_color(ft, [
    (0.00, (150,178, 96)),    # sunlit far grass (warm green-gold)
    (0.30, (108,156, 72)),
    (0.70, ( 74,128, 56)),
    (1.00, ( 52,102, 46)),    # deep foreground green
])
grain = 0.88 + 0.24*V.vnoise((H,W),(2,2),seed+4)
field *= grain[...,None]
# sunlight warm wash across the field
field += (np.exp(-((xx-sx)/(0.6*W))**2)*ft)[...,None]*np.array([1.0,0.9,0.5])*0.10
img = np.where(fmask[...,None], field, img)

# wildflowers: white/yellow/blue/red dabs, denser & bigger in foreground
fl = np.zeros((H,W,3))
nfl = 9000
fy = hor + (1-hor)*rng.random(nfl)**0.7
fyr = (fy*H).astype(int)
fxr = rng.integers(0,W,nfl)
depth = np.clip((fy-hor)/(1-hor),0,1)
palette = np.array([(255,255,255),(255,236,120),(120,170,255),(240,90,90),(255,255,255),(255,250,180)])/255
for i in range(nfl):
    if rng.random() > (0.25+0.75*depth[i]):    # fewer far away
        continue
    yiv,xiv = fyr[i],fxr[i]
    if 0<=yiv<H and 0<=xiv<W:
        fl[yiv,xiv] += palette[rng.integers(0,len(palette))]*(0.5+0.7*depth[i])
fl = gaussian_filter(fl,(0.6,0.6,0))
img += fl*fmask[...,None]

# ---------------- tone-map background, then draw figures in PIL ----------------
bg = V.tonemap(img, k=1.16, gamma=0.95)
pim = V.to_pil(bg)
draw = ImageDraw.Draw(pim, "RGBA")
S = H/1440.0

px, pbase = 0.5*W, 0.63*H          # maypole base (planted in the ring centre)
def lerp(a,b,t): return a+(b-a)*t

# ---- people: concentric dancing rings (ellipses) + outer crowd ----
skin = [(238,200,170),(225,180,150),(248,212,185),(205,160,130)]
clothes = [(238,238,242),(214,64,60),(70,110,200),(245,210,80),(236,240,245),
           (210,120,170),(90,160,120),(250,250,252)]
figs = []   # (yfeet, x, h, body, skinc, ang)
def add_ring(r_frac, squash, n, hbase, jitter):
    R = r_frac*W
    for k in range(n):
        ang = 2*np.pi*k/n + rng.random()*jitter
        fx = px + R*np.cos(ang)
        fy = pbase + R*squash*np.sin(ang)
        d = 0.5+0.5*np.sin(ang)                 # nearer (front, sin>0) bigger
        h = hbase*(0.8+0.5*d)*S
        figs.append([fy, fx, h, clothes[rng.integers(0,len(clothes))],
                     skin[rng.integers(0,len(skin))], ang])
add_ring(0.085, 0.42, 22, 34, 0.05)
add_ring(0.140, 0.42, 34, 36, 0.05)
add_ring(0.200, 0.42, 46, 40, 0.04)
# scattered onlookers further out
for _ in range(90):
    ang = rng.random()*2*np.pi
    R = (0.24+0.22*rng.random())*W
    fx = px + R*np.cos(ang); fy = pbase + R*(0.42)*np.sin(ang) + (rng.random()-0.2)*0.05*H
    if fy < pbase-0.05*H: continue
    d = np.clip((fy-(pbase-0.1*H))/(0.3*H),0,1)
    figs.append([fy, fx, (30+18*d)*S, clothes[rng.integers(0,len(clothes))],
                 skin[rng.integers(0,len(skin))], ang])

def draw_person(x, y, h, body, sk):
    hw = h*0.19                                  # head radius
    bw = h*0.42                                  # shoulder width
    lw = max(1,int(h*0.07))
    neck = y-h*0.62                              # shoulder height
    # legs
    draw.line([(x-bw*0.18,y),(x-bw*0.16,neck)], fill=(54,52,64,255), width=lw)
    draw.line([(x+bw*0.18,y),(x+bw*0.16,neck)], fill=(54,52,64,255), width=lw)
    # linked arms: short outstretched stubs to the neighbours' hands
    draw.line([(x-bw*0.5,neck+h*0.10),(x-bw*0.10,neck+h*0.02)], fill=body+(255,), width=lw)
    draw.line([(x+bw*0.5,neck+h*0.10),(x+bw*0.10,neck+h*0.02)], fill=body+(255,), width=lw)
    # body (summer dress / shirt): trapezoid widening to the hem
    draw.polygon([(x-bw*0.26,neck),(x+bw*0.26,neck),
                  (x+bw*0.5,y-h*0.02),(x-bw*0.5,y-h*0.02)], fill=body+(255,))
    draw.ellipse([x-bw*0.26,neck-h*0.05,x+bw*0.26,neck+h*0.05], fill=body+(255,))
    # head
    draw.ellipse([x-hw,y-h, x+hw,y-h+2*hw], fill=sk+(255,))
    # flower crown
    draw.arc([x-hw*1.1,y-h-hw*0.7,x+hw*1.1,y-h+hw*0.7],180,360,
             fill=(255,238,110,255), width=max(1,int(h*0.06)))

# draw order: far (small y) first; insert maypole at its base depth
figs.sort(key=lambda f: f[0])

def draw_maypole():
    Hp = 0.45*H
    ytop = pbase - Hp
    w_pole = max(5,int(13*S))
    green = (58,118,52,255)
    # pole (birch-leaf-wrapped): a column of green dabs
    draw.line([(px,pbase),(px,ytop)], fill=green, width=w_pole)
    for t in np.linspace(0,1,70):
        yy_ = lerp(pbase,ytop,t); r = w_pole*0.62
        c = (48+rng.integers(0,30),104+rng.integers(0,30),46+rng.integers(0,20),255)
        draw.ellipse([px-r,yy_-r,px+r,yy_+r], fill=c)
    # crossbar
    ycb = ytop + Hp*0.15
    Wc = 0.17*W
    draw.line([(px-Wc/2,ycb),(px+Wc/2,ycb)], fill=green, width=max(4,int(11*S)))
    for t in np.linspace(0,1,40):
        xx_=lerp(px-Wc/2,px+Wc/2,t); r=w_pole*0.45
        draw.ellipse([xx_-r,ycb-r,xx_+r,ycb+r],fill=(52,110,48,255))
    # two hanging wreaths (the signature hoops)
    rR = Wc*0.34
    for sgnx in (-1,1):
        cxr = px+sgnx*Wc/2; cyr = ycb+rR+0.015*H
        draw.line([(cxr,ycb),(cxr,cyr-rR)],fill=green,width=max(2,int(4*S)))
        draw.ellipse([cxr-rR,cyr-rR,cxr+rR,cyr+rR], outline=green, width=max(4,int(9*S)))
        for a in np.linspace(0,2*np.pi,12,endpoint=False):
            fxw=cxr+rR*np.cos(a); fyw=cyr+rR*np.sin(a)
            col=[(255,255,255),(255,225,90),(240,90,90),(245,150,190)][rng.integers(0,4)]
            rr=max(1,int(4.2*S)); draw.ellipse([fxw-rr,fyw-rr,fxw+rr,fyw+rr],fill=col+(255,))
    # top wreath + Swedish pennant (blue/yellow)
    tR=rR*0.95
    draw.ellipse([px-tR,ytop-tR*1.9,px+tR,ytop-tR*1.9+2*tR],outline=green,width=max(3,int(7*S)))
    draw.line([(px,ytop),(px,ytop-0.085*H)],fill=(120,90,60,255),width=max(2,int(5*S)))
    draw.polygon([(px,ytop-0.085*H),(px,ytop-0.045*H),(px+0.055*W,ytop-0.065*H)],fill=(70,140,205,255))
    # flowers up the pole
    for t in np.linspace(0.05,0.95,22):
        yy_=lerp(pbase,ytop,t); off=(rng.random()-0.5)*w_pole*1.1
        col=[(255,255,255),(255,225,90),(240,120,160),(120,170,255)][rng.integers(0,4)]
        rr=max(1,int(3.4*S)); draw.ellipse([px+off-rr,yy_-rr,px+off+rr,yy_+rr],fill=col+(255,))

pole_drawn=False
for f in figs:
    if (not pole_drawn) and f[0] >= pbase:
        draw_maypole(); pole_drawn=True
    draw_person(f[1],f[0],f[2],f[3],f[4])
if not pole_drawn: draw_maypole()

# gentle warm glow overlay (sunny day)
arr = np.asarray(pim).astype(np.float64)/255
glow = gaussian_filter(np.clip(arr.max(axis=2)-0.8,0,1), 6)
arr += glow[...,None]*np.array([1.0,0.95,0.8])*0.25
arr = np.clip(arr,0,1)
pim = V.to_pil(arr)
V.caption(pim, H, "MIDSOMMAR", "dancing round the maypole in the sun  ·  Sverige 2026")
pim.save(outp); print("saved", outp, pim.size)
