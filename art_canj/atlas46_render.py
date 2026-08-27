"""Atlas piece 46 (2560²) — THE RUNG UNDER THE MICROSCOPE
Three channel lanes over the relay [1.6e12, 2.0e12): every 4-run a star,
every 5-run a beacon.  Below: the 5-adic anatomy of channel 25's 4-run
population (the WHY of the throttled 4->5 rung), and the quarter-by-quarter
hazard meters vs the pre-committed bands.
Run AFTER atlas46_analyze.py (reads atlas46_occ.json).
"""
import numpy as np, json
from PIL import Image, ImageDraw, ImageFont

SS = 2
W = H = 2560
Ws, Hs = W*SS, H*SS
buf = np.zeros((Hs, Ws, 3), np.float32)
X0, X1 = 1.6e12, 2.0e12

def splat(x, y, sigma, color, amp):
    r = int(3*sigma)+1
    xa, ya = max(int(x)-r,0), max(int(y)-r,0)
    xb, yb = min(int(x)+r+1,Ws), min(int(y)+r+1,Hs)
    if xb<=xa or yb<=ya: return
    gy = np.arange(ya,yb)-y; gx = np.arange(xa,xb)-x
    g = np.exp(-(gy[:,None]**2+gx[None,:]**2)/(2*sigma**2))
    for k in range(3):
        buf[ya:yb, xa:xb, k] += amp*color[k]*g

def vline(x, y0, y1, color, amp, wd):
    n = max(int(abs(y1-y0)/(wd*0.6)), 2)
    for t in np.linspace(0,1,n):
        splat(x, y0+t*(y1-y0), wd, color, amp/n*abs(y1-y0)/wd*0.7)

def hline(y, x0, x1, color, amp, wd):
    n = max(int(abs(x1-x0)/(wd*0.6)), 2)
    for t in np.linspace(0,1,n):
        splat(x0+t*(x1-x0), y, wd, color, amp/n*abs(x1-x0)/wd*0.7)

GOLD  = np.array([1.00,0.80,0.40]); EMBER = np.array([1.00,0.60,0.22])
CYAN  = np.array([0.45,0.88,0.95]); STEEL = np.array([0.36,0.52,0.70])
WHITE = np.array([1.00,0.95,0.85]); BG    = np.array([0.008,0.012,0.026])
VIOLET= np.array([0.72,0.48,0.95]); GREEN = np.array([0.45,0.85,0.55])
RED   = np.array([0.98,0.40,0.35])

occ = {tuple(map(int, k.strip('()').split(','))): v
       for k, v in json.load(open('atlas46_occ.json')).items()}

def hx(s): return (120 + (s-X0)/(X1-X0)*(2440-120))*SS

lanes = {23: (560, STEEL), 24: (960, EMBER), 25: (1360, CYAN)}
LH = 130   # half-height of scatter band
for g,(yc,col) in lanes.items():
    hline(yc*SS, 120*SS, 2440*SS, col*0.5, 1.2, 1.5*SS)
    s4 = occ.get((4,g), [])
    s5 = set(occ.get((5,g), []))
    rng = np.random.default_rng(g)
    a4 = 0.85 * min(1.0, 420.0/max(len(s4),1))
    for s in s4:
        yj = yc + rng.uniform(-LH*0.62, LH*0.62)
        splat(hx(s), yj*SS, 2.2*SS, col, a4)
    a5 = 1.0 if len(s5) > 20 else 2.2
    for s in s5:
        vline(hx(s), (yc-LH)*SS, (yc+LH)*SS, GOLD, a5, 1.8*SS)
        if len(s5) <= 20:
            splat(hx(s), yc*SS, 6.5*SS, WHITE, 3.0)
            splat(hx(s), yc*SS, 18*SS, GOLD, 0.8)
        else:
            splat(hx(s), yc*SS, 4.5*SS, WHITE, 1.2)
for (l,g), ss in occ.items():
    if l >= 6:
        for s in ss:
            yc = lanes.get(g, (960,))[0]
            splat(hx(s), yc*SS, 10*SS, WHITE, 6.0)
            splat(hx(s), yc*SS, 30*SS, VIOLET, 1.6)

# 5-adic strip: ch-25 4-runs by residue class row
rows_y0 = 1700
occ25 = np.array(sorted(occ.get((4,25), [])), dtype=np.int64)
cls_cols = [GOLD, STEEL, GREEN, VIOLET, RED]
for r in range(5):
    y = (rows_y0 + r*72)
    hline(y*SS, 120*SS, 2360*SS, np.array([0.2,0.26,0.38]), 0.5, 1.2*SS)
    sel = occ25[occ25 % 5 == r]
    for s in sel:
        splat(hx(s), y*SS, 2.4*SS, cls_cols[r], min(1.0, 300.0/max(len(sel),1)) + 0.35)

# quarter hazard meters: r45 per quarter, ch25 vs ch24, hist band 3-5e-3
MY0, MX0 = 2205, 330
qs = np.linspace(X0, X1, 5)
s4_25 = occ25; s5_25 = np.array(sorted(occ.get((5,25), [])), dtype=np.int64)
s4_24 = np.array(sorted(occ.get((4,24), [])), dtype=np.int64)
s5_24 = np.array(sorted(occ.get((5,24), [])), dtype=np.int64)
RMAX = 8e-3
for i in range(4):
    xq0 = MX0 + i*530
    for (s4a, s5a, col, dy) in [(s4_25, s5_25, CYAN, 0), (s4_24, s5_24, EMBER, 36)]:
        m4 = ((s4a>=qs[i]) & (s4a<qs[i+1])).sum()
        m5 = ((s5a>=qs[i]) & (s5a<qs[i+1])).sum()
        r = m5/max(m4,1)
        ln = min(r/RMAX,1.0)*420
        hline((MY0+dy)*SS, xq0*SS, (xq0+ln)*SS, col, 2.2, 3.2*SS)
        splat((xq0+ln)*SS, (MY0+dy)*SS, 4.5*SS, col, 1.8)
    # historical band 3-5e-3 ticks
    for rv in (3e-3, 5e-3):
        vline((xq0+rv/RMAX*420)*SS, (MY0-16)*SS, (MY0+52)*SS,
              np.array([0.3,0.4,0.55]), 0.8, 1.3*SS)

buf += BG[None,None,:]
from scipy.ndimage import gaussian_filter, zoom as ndzoom
lum = buf.mean(2)
thr = np.percentile(lum, 99.3)
mask = np.clip((lum-thr)/(lum.max()-thr+1e-9),0,1)
small = (buf*mask[:,:,None])[::4,::4]
bl = np.stack([gaussian_filter(small[:,:,k],12) for k in range(3)],2)
buf += 1.1*ndzoom(bl,(4,4,1),order=1)[:Hs,:Ws]
img = 1-np.exp(-1.5*buf)
img = np.clip(img,0,1)**(1/1.9)
img += (np.random.rand(Hs,Ws,1)-0.5)/255.0
im = Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).resize((W,H), Image.LANCZOS)

def lf(p,s):
    try: return ImageFont.truetype(p,s)
    except Exception: return ImageFont.load_default()
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_t=lf(FB,72); f_s=lf(FR,33); f_c=lf(FR,26); f_l=lf(FB,30)
d = ImageDraw.Draw(im)
gold=(255,212,138); dim=(148,164,190); cyn=(150,214,228)
def ctext(x,y,s,f,fill):
    bb=d.textbbox((0,0),s,font=f); d.text((x-(bb[2]-bb[0])/2,y),s,font=f,fill=fill)

VERDICT = json.load(open('atlas46_verdict.json'))
ctext(W/2, 52, "THE RUNG UNDER THE MICROSCOPE", f_t, gold)
ctext(W/2, 146, "AP-obstruction atlas, piece 46  ·  the set S of ℤ[√2]-norms, relay 1.6 → 2.0 ×10¹²  ·  |S ∩ window| = %s" % VERDICT['Scount'], f_s, dim)

d.text((130, 380), "channel 23", font=f_l, fill=(140,160,190))
d.text((130, 780), "channel 24", font=f_l, fill=(230,160,90))
d.text((130,1180), "channel 25", font=f_l, fill=(150,214,228))
for g, yy in ((23,380),(24,780),(25,1180)):
    d.text((330, yy+6), VERDICT['lane_label'][str(g)], font=f_c, fill=dim)
ctext(W/2, 1545, "every faint star = a run of four members in arithmetic progression (gap = channel); every gold beacon = a fifth member heard — a fence", f_c, dim)

d.text((130, 1655), "channel 25's four-runs, sorted by start mod 5:", font=f_c, fill=cyn)
for r in range(5):
    d.text((2395, 1690 + r*72 - 14), VERDICT['mod5'][r], font=f_c,
           fill=tuple(int(255*c) for c in cls_cols[r]))
ctext(W/2, 2075, VERDICT['fiveadic_line'], f_c, cyn)

d.text((130, 2185), "4→5 hazard", font=f_l, fill=dim)
d.text((130, 2228), "by quarter", font=f_c, fill=dim)
for i in range(4):
    d.text((330+i*530, 2130), f"Q{i+1}", font=f_c, fill=dim)
ctext(W/2, 2300, "cyan = channel 25, amber = channel 24;  grey posts mark the historical band r₄₅ = 3–5 ×10⁻³", f_c, dim)

ctext(W/2, 2372, VERDICT['verdict1'], f_l, gold)
ctext(W/2, 2420, VERDICT['verdict2'], f_c, dim)
ctext(W/2, 2462, VERDICT['verdict3'], f_c, dim)

im.save('atlas46_2560.png')
print("saved atlas46_2560.png")
