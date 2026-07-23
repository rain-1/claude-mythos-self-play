"""The Ascent to the Cube — Hasse lattice of the 122 under add-one-edge.
Brightness = number of maximal chains through each node/edge (exact big-int flow).
Apex: the complete cube, present only as a ghost, receiving a single thread.
"""
import json, sys, numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation
from lib import line_splat, splat_pts, wide_bloom, filmic, to_img, nzpct
from enumerate import EDGES, VERTS, ROT_E, apply_ep

FINAL = int(sys.argv[1]) if len(sys.argv)>1 else 1024
SS = 2; S = FINAL*SS; rs = FINAL/2560.0
d = json.load(open('enum.json'))
reps = d['reps']; FULL = 4095
covers = [tuple(c) for c in json.load(open('covers.json'))]
nodes = reps + [FULL]
K = {r: bin(r).count('1') for r in nodes}

# exact chain-count flux
up = {FULL: 1}
for k in range(11, 2, -1):
    for r in [x for x in reps if K[x]==k]:
        up[r] = sum(up[b] for a,b in covers if a==r)
down = {r: 1 for r in reps if K[r]==3}
for k in range(4,13):
    for r in [x for x in nodes if K[x]==k]:
        down[r] = sum(down[a] for a,b in covers if b==r) or down.get(r,1)
flux = {r: down[r]*up.get(r,1) for r in nodes}
total_chains = sum(down[a] for a,b in covers if b==FULL)
print("maximal chains 3->12:", total_chains)

# ---- layout: rank rows (k=3 bottom ... 12 top), barycentric x-ordering
ranks = {k: sorted([r for r in nodes if K[r]==k]) for k in range(3,13)}
pos = {}
for k in range(3,13):
    n = len(ranks[k])
    for i,r in enumerate(ranks[k]):
        pos[r] = (i - (n-1)/2)
for _ in range(60):   # barycentric sweeps both directions
    for k in list(range(4,13)) + list(range(11,2,-1)):
        for r in ranks[k]:
            nbr = [pos[a] for a,b in covers if b==r] + [pos[b] for a,b in covers if a==r]
            if nbr: pos[r] = 0.75*np.mean(nbr) + 0.25*pos[r]
        order = sorted(ranks[k], key=lambda r: pos[r])
        n = len(order)
        for i,r in enumerate(order):
            pos[r] = 0.5*pos[r] + 0.5*(i-(n-1)/2)
# final: evenly spread each rank preserving order
XY = {}
margin = 0.075*S
Hspan = S - 2.3*margin
maxw = max(len(v) for v in ranks.values())
for k in range(3,13):
    order = sorted(ranks[k], key=lambda r: pos[r])
    n = len(order)
    y = S - margin*1.55 - (k-3)/9.0 * Hspan
    w = S*0.86 * (0.25 + 0.75*np.sqrt(n/maxw))
    rowgap = Hspan/9.0
    for i,r in enumerate(order):
        x = S/2 + (0 if n==1 else (i/(n-1)-0.5))*w
        dy = (0.16*rowgap if (i%2) else -0.16*rowgap) if n>18 else 0.0
        XY[r] = (x, y+dy)

# ---- draw
c30 = np.cos(np.pi/6)
def iso(p): x,y,z=p; return ((x-y)*c30,(x+y)*0.5-z)
def grounded(mask):
    best=None;bs=None
    for ep in ROT_E:
        m2=apply_ep(mask,ep)
        es=[(VERTS[a],VERTS[b]) for e,(a,b) in enumerate(EDGES) if m2>>e&1]
        sc=sum(p[2]+q[2] for p,q in es)-0.5*sum(1 for p,q in es if p[2]==0 and q[2]==0)
        if bs is None or sc<bs: bs, best = sc, m2
    return best

thread = np.zeros((S,S), np.float32)
threadk = np.zeros((S,S), np.float32)
glyph_w = np.zeros((S,S), np.float32)
glyph_wk = np.zeros((S,S), np.float32)
glyph_c = np.zeros((S,S), np.float32)
bead = np.zeros((S,S), np.float32)

lf = {r: np.log1p(flux[r]) for r in nodes}
mx = max(lf.values())
# edges as cubic bezier threads, mass ~ chain flux
for a,b in covers:
    xa,ya = XY[a]; xb,yb = XY[b]
    BN = max(48, int(1.6*np.hypot(xb-xa, yb-ya)))
    t = np.linspace(0,1,BN)
    ef = np.log1p(down[a]*up.get(b,1))/mx
    c1 = (xa, ya-0.45*(ya-yb)); c2 = (xb, yb+0.45*(ya-yb))
    xs = (1-t)**3*xa+3*(1-t)**2*t*c1[0]+3*(1-t)*t**2*c2[0]+t**3*xb
    ys = (1-t)**3*ya+3*(1-t)**2*t*c1[1]+3*(1-t)*t**2*c2[1]+t**3*yb
    kn = (K[a]-3+t)/9.0
    seg = np.hypot(np.diff(xs), np.diff(ys))
    m = (0.06+0.94*ef**1.6)
    splat_pts(thread, xs[:-1], ys[:-1], m*seg/seg.mean()*0.5)
    splat_pts(threadk, xs[:-1], ys[:-1], kn[:-1]*m*seg/seg.mean()*0.5)

csize = 0.023*S
for r in nodes:
    x0,y0 = XY[r]
    m = 0 if r==FULL else grounded(r)
    nrank = len(ranks[K[r]])
    sc = csize*(0.85+0.5*lf[r]/mx)/max(1.0, np.sqrt(nrank/14.0))
    if r==FULL: sc = csize*1.9
    for e,(va,vb) in enumerate(EDGES):
        pa,pb = iso(VERTS[va]), iso(VERTS[vb])
        A=(x0+pa[0]*sc, y0-pa[1]*sc+sc*0.6); B=(x0+pb[0]*sc, y0-pb[1]*sc+sc*0.6)
        if r!=FULL and (m>>e&1):
            line_splat(glyph_w,[A[0]],[A[1]],[B[0]],[B[1]], 1.0)
            line_splat(glyph_wk,[A[0]],[A[1]],[B[0]],[B[1]], (K[r]-3)/9.0)
        else:
            line_splat(glyph_c,[A[0]],[A[1]],[B[0]],[B[1]], 1.0 if r==FULL else 0.55)
    splat_pts(bead, np.array([x0]), np.array([y0+sc*1.15]), 0.0)  # placeholder

def stroke(l,w,bl): return gaussian_filter(grey_dilation(l,size=(int(w),int(w))),bl)
tq = gaussian_filter(thread, 1.4*SS*rs); tkq = gaussian_filter(threadk, 1.4*SS*rs)
gq = stroke(glyph_w, max(2,2.2*SS*rs), 1.0*SS*rs)
gkq = stroke(glyph_wk, max(2,2.2*SS*rs), 1.0*SS*rs)
cq = stroke(glyph_c, max(2,1.6*SS*rs), 1.6*SS*rs)
tn = nzpct(tq,97); tq/=tn; tkq/=tn
gn = nzpct(gq,88); gq/=gn; gkq/=gn
cq/=nzpct(cq,90)
kthr = np.where(tq>1e-5, tkq/np.maximum(tq,1e-5), 0)
kgly = np.where(gq>1e-5, gkq/np.maximum(gq,1e-5), 0)
silver = np.array([0.62,0.76,0.98]); gold = np.array([1.10,0.78,0.30])
rgb = np.zeros((S,S,3), np.float32)
colt = silver[None,None,:]*(1-kthr[...,None]) + gold[None,None,:]*kthr[...,None]
rgb += colt * (0.55*np.clip(tq,0,2.2))[...,None]
colg = silver[None,None,:]*(1-kgly[...,None]) + gold[None,None,:]*kgly[...,None]
rgb += colg * (1.15*np.clip(gq,0,1.6))[...,None]
rgb[...,0]+=0.17*0.42*cq; rgb[...,1]+=0.17*0.72*cq; rgb[...,2]+=0.17*1.05*cq
glow = wide_bloom(gq+0.5*tq, 16*SS*rs); glow/=max(glow.max(),1e-9)
rgb[...,0]+=0.30*glow; rgb[...,1]+=0.25*glow; rgb[...,2]+=0.22*glow
# apex halo: cool
ax,ay = XY[FULL]
yy,xx = np.mgrid[0:S,0:S].astype(np.float32)
halo = np.exp(-(((xx-ax)**2+(yy-ay)**2))/(2*(0.05*S)**2))
rgb[...,0]+=0.10*halo; rgb[...,1]+=0.16*halo; rgb[...,2]+=0.26*halo

out = filmic(rgb, k=1.25, gamma=0.85)
from PIL import Image, ImageDraw, ImageFont
img = to_img(out).resize((FINAL,FINAL), Image.LANCZOS)
draw = ImageDraw.Draw(img)
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", max(10,int(15*FINAL/1024)))
except: font = ImageFont.load_default()
draw.text((int(0.018*FINAL), int(0.975*FINAL)),
  f"THE 122 UNDER ONE-EDGE ASCENT · {len(covers)} COVER RELATIONS · {total_chains:,} MAXIMAL CHAINS · EVERY ROAD ENDS AT THE GHOST",
  fill=(120,124,135), font=font)
img.save(f'ascent_{FINAL}.png'); print("saved", f'ascent_{FINAL}.png')
