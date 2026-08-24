"""THE SIXTH RUNG — Atlas piece 44, 2560^2.
The ℤ[√2] run-length ladder over [4.0e11, 1.205e12]: rung l=3 a fog, rung
l=4 a stipple, rung l=5 candles, and rung l=6 — one star, found already
burning in last run's unread ledger. Six-pillar certificate inset, ch-25
beacon strip with the 94 mod 144 arches, pre-committed-model annotations.
python3 atlas_render.py [FINAL]
"""
import numpy as np, sys, math, glob, re, json
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

FINAL = int(sys.argv[1]) if len(sys.argv)>1 else 900
SS=2; S=FINAL*SS; rs=FINAL/2560.0
rng = np.random.default_rng(44)

X0, X1 = 4.0e11, 1.205e12
FRONT1, FRONT2 = 8.8e11, 1.2e12   # old relay end, new relay end

# ---- data ----
# old relay window counts (from 08-23 rungap ledgers), per 1.6e11 window;
# window 3 capped at 8.3e11 (counts scaled 11/16) — the re-scan owns [8.3e11,+)
oldw = [(4.0e11,5.6e11),(5.6e11,7.2e11),(7.2e11,8.3e11)]
sc = 11/16
g24 = {3:[847480,879019,int(903152*sc)], 4:[5835,6080,int(6314*sc)],
       5:[19,27,int(27*sc)], 6:[1,0,0]}
fences25_old = [458171603806, 615709112638, 830595732286]
L6 = 536462850079
# new scans: parse rungap + occ files if present
new_counts = []   # (lo,hi,{l:count for g24}), occ lists
occ = []          # (l, g, start)
for f in glob.glob('hunt_rungap_*txt'):
    m = re.match(r'.*hunt_rungap_(\d+)_(\d+)\.txt', f)
    if not m: continue
    lo, hi = int(m.group(1)), int(m.group(2))
    if hi <= 8.3e11: continue
    cnt = {3:0,4:0,5:0,6:0}
    for line in open(f):
        mm = re.match(r'l=(\d+) g=24 maximal_runs=(\d+)', line)
        if mm and int(mm.group(1)) in cnt: cnt[int(mm.group(1))] += int(mm.group(2))
    new_counts.append((lo,hi,cnt))
for f in glob.glob('hunt_alarms_*txt'):
    for line in open(f):
        mm = re.match(r'(?:OCC|FIRST) l=(\d+) g=(\d+) start=(\d+)', line)
        if mm: occ.append((int(mm.group(1)), int(mm.group(2)), int(mm.group(3))))
        mm = re.match(r'L6\+! l=(\d+) gap=(\d+) start=(\d+)', line)
        if mm: occ.append((int(mm.group(1)), int(mm.group(2)), int(mm.group(3))))
occ = sorted(set(occ))
fences25 = sorted(set([s for l,g,s in occ if g==25 and l>=5] + fences25_old))
sextets  = sorted(set([s for l,g,s in occ if l>=6] + [L6]))
print('fences25:', fences25); print('sextets:', sextets)

BAND=int(0.17*S)
mx0, mx1 = 0.045*S, 0.975*S
def xpx(n): return mx0 + (n-X0)/(X1-X0)*(mx1-mx0)

img = np.zeros((S,S,3), np.float32)
def star(px,py,rad,col,amp):
    r=int(max(2,rad*3.2)); yy,xx=np.ogrid[-r:r+1,-r:r+1]
    g=np.exp(-(xx*xx+yy*yy)/(2*rad*rad)).astype(np.float32)
    xa,ya=max(0,int(px)-r),max(0,int(py)-r); xb,yb=min(S,int(px)+r+1),min(S,int(py)+r+1)
    if xb<=xa or yb<=ya: return
    sub=g[ya-(int(py)-r):yb-(int(py)-r), xa-(int(px)-r):xb-(int(px)-r)]
    img[ya:yb,xa:xb,:] += amp*sub[...,None]*np.asarray(col,np.float32)[None,None,:]

# ---- rung geometry: l=3 bottom .. l=6 top ----
rungy = {3: 0.595*S, 4: 0.487*S, 5: 0.378*S, 6: 0.232*S}
railcol = (0.20,0.30,0.44)
for l,ry in rungy.items():
    yy = int(ry)
    img[yy-max(1,int(1.0*SS*rs)):yy+max(1,int(1.0*SS*rs)), int(mx0):int(mx1), :] += np.asarray(railcol)*0.5

# windows for density strata: old three + new
allw = [(lo,hi,{ll:g24[ll][i] for ll in (3,4,5,6)}) for i,(lo,hi) in enumerate(oldw)] + new_counts

# l=3 fog stratum: grain density prop to count
for lo,hi,cnt in allw:
    n3 = int(cnt[3] * (5500/900000))   # dots ∝ count ⇒ equal true density everywhere
    xs = rng.uniform(xpx(lo), xpx(min(hi,X1)), n3)
    ys = rungy[3] + rng.normal(0, 0.012*S, n3) - 0.012*S*rng.random(n3)
    for x,y in zip(xs,ys):
        star(x, y, 0.75*SS*rs, (0.30,0.42,0.62), 0.38)
# l=4 stipple
for lo,hi,cnt in allw:
    n4 = int(cnt[4]*(450/6000))
    xs = rng.uniform(xpx(lo), xpx(min(hi,X1)), n4)
    ys = rungy[4] + rng.normal(0, 0.010*S, n4)
    for x,y in zip(xs,ys):
        star(x,y,1.2*SS*rs,(0.45,0.62,0.85),0.5)
# l=5 candles: density register for old windows (positions unknown), exact for new occ
for i,(lo,hi) in enumerate(oldw):
    n5 = g24[5][i]
    xs = rng.uniform(xpx(lo), xpx(hi), n5)
    for x in xs: star(x, rungy[5]-0.006*S, 2.2*SS*rs, (0.95,0.80,0.45), 0.95)
for l,g,s in occ:
    if l==5 and g==24 and s>=8.3e11:
        star(xpx(s), rungy[5]-0.006*S, 2.4*SS*rs, (1.0,0.85,0.5), 1.1)
# l=6: the star(s)
for s in sextets:
    px,py = xpx(s), rungy[6]
    star(px,py,5.5*SS*rs,(1.0,0.95,0.85),1.4)
    star(px,py,2.0*SS*rs,(1.0,1.0,1.0),2.0)
    # gate arches: concentric faint rings (the ±1 mod 8, ≢0 mod 3 gate)
    for rr_,aa in [(0.030,0.5),(0.043,0.35),(0.056,0.22)]:
        th=np.linspace(0,2*np.pi,900)
        gx,gy = px+S*rr_*np.cos(th), py+S*rr_*np.sin(th)
        m=(gx>=0)&(gx<S)&(gy>=0)&(gy<S)
        img[gy[m].astype(int),gx[m].astype(int),:] += np.array([1.0,0.8,0.4])*aa*0.35

# frontier lines
for fx, coldash in [(FRONT1,(0.5,0.55,0.7)), (min(FRONT2,X1),(0.9,0.75,0.4))]:
    px=int(xpx(fx))
    for yy in range(int(0.20*S), int(0.70*S), int(0.012*S)):
        img[yy:yy+int(0.006*S), px:px+max(1,int(1.0*SS*rs)), :] += np.asarray(coldash)*0.8

# ---- six-pillar certificate inset (bottom half, left) ----
posts = [
    (536462850079, [(13,2,True),(3174336391,1,False)]),
    (536462850103, [(281,2,False),(6794023,1,False)]),
    (536462850127, [(3943,1,False),(136054489,1,False)]),
    (536462850151, [(536462850151,1,False)]),
    (536462850175, [(5,2,True),(7,1,False),(521,1,False),(5883881,1,False)]),
    (536462850199, [(17,1,False),(13001,1,False),(2427247,1,False)]),
]
flankL = (536462850055, [(5,1,True),(11,1,True),(19,1,True),(103,1,False),(601,1,False),(8293,1,True)])
iy1 = 0.822*S
ix0 = 0.135*S; colw = 0.040*S; gap = 0.020*S
def pillar(cx, facs, dead):
    y = iy1
    for (p,e,bad) in facs:
        hh = 0.0090*S*math.log10(p)
        for rep in range(e):
            if dead: col = (1.0,0.38,0.28) if bad else (0.30,0.38,0.52)
            else:    col = (1.0,0.74,0.22) if bad else (0.38,0.62,0.88)
            x0i,x1i = int(cx-colw/2), int(cx+colw/2)
            y0i,y1i = int(y-hh), int(y)
            img[y0i:y1i, x0i:x1i, :] += np.asarray(col)*(0.75 if not dead else 0.5)
            img[y0i:y0i+max(1,int(1.2*SS*rs)), x0i:x1i, :] *= 0.25   # block seam
            y -= hh + 0.005*S
pillar(ix0 - (colw+gap)*1.35, flankL[1], True)
for i,(n,facs) in enumerate(posts):
    pillar(ix0 + i*(colw+gap), facs, False)
print('pillars drawn')

# ---- ch-25 beacon strip ----
sy = 0.655*S
for s in fences25:
    px = xpx(s)
    star(px, sy, 4.5*SS*rs, (0.55,0.9,1.0), 2.2)
    th=np.linspace(np.pi,2*np.pi,300)
    gx,gy=px+0.014*S*np.cos(th), sy+0.014*S*np.sin(th)*0.7
    m=(gx>=0)&(gx<S)&(gy>=0)&(gy<S)
    img[gy[m].astype(int),gx[m].astype(int),:] += np.array([0.5,0.85,1.0])*0.7

# bloom
small = img[::4,::4]
bl = gaussian_filter(small, (10*rs*SS/4,10*rs*SS/4,0))
img += 0.5*np.kron(bl, np.ones((4,4,1),np.float32))[:S,:S]

img = 1.0-np.exp(-img*1.05)
img = np.clip(img,0,1)**(1/1.32)
img8=(img*255+np.random.uniform(-0.5,0.5,img.shape)).clip(0,255).astype(np.uint8)
out=Image.fromarray(img8).resize((FINAL,FINAL),Image.LANCZOS)

d2=ImageDraw.Draw(out)
def font(sz,bold=False):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if bold else ''),sz)
    except Exception: return ImageFont.load_default()
fs=max(9,int(30*rs))
bandy=FINAL-BAND//SS
d2.rectangle([0,bandy,FINAL,FINAL],fill=(6,7,10))
d2.text((int(0.045*FINAL),bandy+int(0.010*FINAL)),'THE SIXTH RUNG',font=font(int(62*rs),True),fill=(255,214,120))
NC = sum(c[3] for _,_,c in new_counts) if new_counts else 0
caps=[
 'Atlas of AP obstructions, piece 44 — ℤ[√2] country, the run-length ladder over [4.0e11, 1.2e12]. Numbers whose primes ≡ 3,5 (mod 8)',
 'all appear evenly, scanned as consecutive members in equal-gap runs: rung 3 a fog (4.5M runs of gap 24), rung 4 a stipple (33k),',
 'rung 5 candles (123), and RUNG 6 — two stars. The first, n₀ = 536,462,850,079, was already burning in the previous run’s own alarm',
 'ledger (L6+!, 2026-08-23) — logged by the machine, unread by the mind, found today. The second, n₁ = 982,614,621,929, answered this',
 'run’s pre-committed hunt (E≈0.38). Both certified by full factorization: maximal, 24|gap, and the new gate ≡ ±1 (mod 8), ≢ 0 (mod 3).',
 'Pillars: the six factorizations of the first sextet (gold = bad primes, squared; cyan = split primes; the red ruin at left holds',
 '5¹·11¹·19¹ odd — the wall that ends the run). Blue beacons: the FIVE channel-25 fences, every one ≡ 94 (mod 144) as the gate demands;',
 'this window the channel went quiet (1 heard, E≈3.3–4.2 — the drift law bent back). Dashed frontiers: 8.8e11 (grey) → 1.2e12 (gold).']
ytxt=bandy+int(0.036*FINAL)
for c in caps: d2.text((int(0.045*FINAL),ytxt),c,font=font(fs),fill=(158,168,190)); ytxt+=int(fs*1.40)
# rung labels
for l,ry in rungy.items():
    d2.text((int(0.012*FINAL), ry/SS-int(0.012*FINAL)), 'l=%d'%l, font=font(fs,True), fill=(140,170,210))
d2.text((int(0.005*FINAL), sy/SS-int(0.010*FINAL)), 'ch-25', font=font(fs,True), fill=(120,180,220))
d2.text((int(xpx(L6)/SS)+int(0.035*FINAL), rungy[6]/SS-int(0.045*FINAL)), 'n₀ = 536,462,850,079  (logged 08-23, read 08-24)', font=font(fs,True), fill=(255,235,190))
d2.text((int(xpx(982614621929)/SS)-int(0.30*FINAL), rungy[6]/SS+int(0.022*FINAL)), 'n₁ = 982,614,621,929  (hunted and heard 08-24)', font=font(fs,True), fill=(255,235,190))
d2.text((int(0.50*FINAL), int(0.762*FINAL)), 'the six pillars, certified by full factorization', font=font(fs), fill=(210,185,140))
d2.text((int(0.50*FINAL), int(0.762*FINAL)+int(fs*1.5)), 'gold blocks = bad primes (13², 5², even) · cyan = split primes', font=font(fs), fill=(150,160,185))
d2.text((int(0.50*FINAL), int(0.762*FINAL)+int(fs*3.0)), 'red ruin at left: n₀−24, its 5¹·11¹·19¹ stand odd — the wall', font=font(fs), fill=(150,160,185))
# x ticks
for n,lab in [(4.5e11,'4.5e11'),(6e11,'6e11'),(8e11,'8e11'),(1.0e12,'1.0e12'),(1.2e12,'1.2e12')]:
    d2.text((xpx(n)/SS-int(0.02*FINAL),int(0.612*FINAL)),lab,font=font(fs),fill=(110,135,175))
out.save('atlas44_%d.png'%FINAL)
print('saved atlas44_%d.png'%FINAL)
