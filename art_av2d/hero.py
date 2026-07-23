"""The Hundred Twenty-Two — specimen sheet of Sol LeWitt's incomplete open cubes."""
import json, sys, numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation
from lib import line_splat, splat_pts, wide_bloom, filmic, to_img, nzpct
from enumerate import EDGES, VERTS, ROT_E, apply_ep

FINAL = int(sys.argv[1]) if len(sys.argv)>1 else 1024
SS = 2
S = FINAL*SS
rs = FINAL/4096.0

d = json.load(open('enum.json'))
reps = d['reps']
amphi = set(d['amphichiral'])
pairs = [tuple(p) for p in d['chiral_pairs']]
mirror_of = {}
for a,b in pairs: mirror_of[a]=b; mirror_of[b]=a
by_k = {}
for r in reps: by_k.setdefault(bin(r).count('1'), []).append(r)

def form_edges(mask):
    return [(np.array(VERTS[a],float), np.array(VERTS[b],float))
            for e,(a,b) in enumerate(EDGES) if mask>>e&1]
def grounded_score(mask):
    es = form_edges(mask)
    hz = sum((p[2]+q[2]) for p,q in es)
    bottom = sum(1 for p,q in es if p[2]==0 and q[2]==0)
    return (hz - 0.5*bottom)
def best_orient(mask):
    return min({apply_ep(mask, ep) for ep in ROT_E}, key=grounded_score)

c30 = np.cos(np.pi/6)
def iso(p):
    x,y,z = p
    return ((x-y)*c30, (x+y)*0.5 - z)

# ---- layout: groups start fresh rows; within group amphichiral first, mirror twins adjacent
ROWCAP = 14
def group_order(g):
    am = sorted([r for r in g if r in amphi])
    ch = []
    seen=set()
    for r in sorted(g):
        if r in amphi or r in seen: continue
        m = mirror_of[r]
        if m in g:
            ch += [r, m]; seen.add(r); seen.add(m)
    return am + ch
rows = []
for k in range(3,12):
    g = group_order(by_k[k])
    for i in range(0, len(g), ROWCAP):
        rows.append((k, g[i:i+ROWCAP]))
rows.append((12, [4095]))   # the complete cube: all ghost, never shown
NR = len(rows)
cellw = S/(ROWCAP+0.8)
cellh = S/(NR+1.6)
cube_sc = min(cellw,cellh)*0.40

warm  = np.zeros((S,S), np.float32)   # present-edge mass
warmk = np.zeros((S,S), np.float32)   # mass * knorm  (for hue ramp)
cold  = np.zeros((S,S), np.float32)
bead  = np.zeros((S,S), np.float32)
row_meta = []

for ri,(k,row) in enumerate(rows):
    y0 = (ri+1.05)*cellh
    xoff = (S - len(row)*cellw)/2
    row_meta.append((k, y0, xoff))
    knorm = (k-3)/8.0
    handled = {}
    for ci,mask in enumerate(row):
        ghost_only = (k==12)
        if ghost_only:
            m, mirror_draw = 0, False
        elif mask in handled:
            m, mirror_draw = handled[mask], True     # draw as horizontal mirror of twin
        else:
            m = best_orient(mask)
            mirror_draw = False
            if mask in mirror_of and ci+1 < len(row) and row[ci+1] == mirror_of[mask]:
                handled[mirror_of[mask]] = m
        cx = xoff + (ci+0.5)*cellw
        deg = {}
        P = {}
        for e,(a,b) in enumerate(EDGES):
            va = VERTS[a] if not mirror_draw else (VERTS[a][1],VERTS[a][0],VERTS[a][2])
            vb = VERTS[b] if not mirror_draw else (VERTS[b][1],VERTS[b][0],VERTS[b][2])
            pa, pb = iso(va), iso(vb)
            xa,ya = cx+pa[0]*cube_sc, y0-pa[1]*cube_sc+cube_sc*0.72
            xb,yb = cx+pb[0]*cube_sc, y0-pb[1]*cube_sc+cube_sc*0.72
            if m>>e&1:
                line_splat(warm, [xa],[ya],[xb],[yb], 1.0)
                line_splat(warmk,[xa],[ya],[xb],[yb], knorm)
                deg[a]=deg.get(a,0)+1; deg[b]=deg.get(b,0)+1
                P[a]=(xa,ya); P[b]=(xb,yb)
            else:
                line_splat(cold, [xa],[ya],[xb],[yb], 1.0)
        for v,dv in deg.items():
            if dv>=2:
                splat_pts(bead, np.array([P[v][0]]), np.array([P[v][1]]), 2.2)

def stroke(layer, wpx, blur):
    return gaussian_filter(grey_dilation(layer, size=(int(wpx),int(wpx))), blur)

wq  = stroke(warm,  max(2,2.4*SS*rs), 1.1*SS*rs)
wkq = stroke(warmk, max(2,2.4*SS*rs), 1.1*SS*rs)
cq  = stroke(cold,  max(2,1.6*SS*rs), 2.0*SS*rs)
bq  = gaussian_filter(bead, 2.4*SS*rs)
norm = nzpct(wq, 88)
wq/=norm; wkq/=norm
cq /= nzpct(cq, 90); bq /= nzpct(bq, 95)
kpix = np.where(wq>1e-4, wkq/np.maximum(wq,1e-4), 0.0)  # completeness 0..1 per pixel
glow = wide_bloom(wq, 15*SS*rs); glow /= max(glow.max(),1e-9)

# palette ramp: silver (k=3) -> gold (k=11)
silver = np.array([0.62,0.76,0.98]); gold = np.array([1.10,0.78,0.30])
col = silver[None,None,:]*(1-kpix[...,None]) + gold[None,None,:]*kpix[...,None]
bright = 0.62 + 0.66*kpix     # completeness also brightens

rgb = np.zeros((S,S,3), np.float32)
rgb += col * (wq*bright)[...,None]
# soft floor-pool shadow-glow under each piece (warm, displaced down)
pool = wide_bloom(np.roll(warm, int(26*SS*rs), axis=0), 24*SS*rs)
pool /= max(pool.max(),1e-9)
rgb[...,0] += 0.10*pool; rgb[...,1] += 0.065*pool; rgb[...,2] += 0.035*pool
rgb[...,0] += 0.40*glow; rgb[...,1] += 0.34*glow; rgb[...,2] += 0.26*glow
gg = 0.17
rgb[...,0] += gg*0.42*cq; rgb[...,1] += gg*0.72*cq; rgb[...,2] += gg*1.05*cq
rgb[...,0] += 0.85*bq; rgb[...,1] += 0.82*bq; rgb[...,2] += 0.72*bq

out = filmic(rgb, k=1.3, gamma=0.84)
from PIL import Image, ImageDraw, ImageFont
img = to_img(out).resize((FINAL,FINAL), Image.LANCZOS)

# ---- labels after bloom
draw = ImageDraw.Draw(img)
try:
    fs = max(10,int(15*FINAL/1024))
    font  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fs)
    fontB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(fs*1.25))
except: font = fontB = ImageFont.load_default()
lab_done = set()
for (k,y0,xoff) in row_meta:
    if k in lab_done: continue
    lab_done.add(k)
    t = f"{k}" if k<12 else "12"
    colr = (150,160,175) if k<12 else (90,110,140)
    draw.text((int(0.018*FINAL), int(y0/SS - 6*FINAL/1024)), t, fill=colr, font=fontB)
draw.text((int(0.018*FINAL), int(0.972*FINAL)),
          "ALL 122 INCOMPLETE OPEN CUBES · VERIFIED · MIRROR TWINS ADJACENT · THE COMPLETE CUBE APPEARS ONLY AS ITS GHOST",
          fill=(120,124,135), font=font)
img.save(f'hero_{FINAL}.png')
print("saved", f'hero_{FINAL}.png')
