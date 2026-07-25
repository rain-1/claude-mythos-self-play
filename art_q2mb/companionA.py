"""
COMPANION A — "The Graph That Passed Every Test"  (2560²)

H (slate skeleton) -> G = L(H) (12 stars at edge midpoints).
Glass plates = Krausz partition (each H-vertex of degree d spawns K_d):
in a line graph every neighborhood splits into <= 2 cliques — no claw can perch.
Loop-fog = all 224 proper 4-colorings (stable partitions with 4 blocks);
ice loops = the 32 equal-quarters (3,3,3,3) colorings, the shape of the wound.
"""
import json, math, sys, itertools
import numpy as np
from collections import defaultdict
from scipy.ndimage import gaussian_filter, zoom as ndzoom
sys.path.insert(0, "art_q2mb")
from kit import tonemap, save, draw_text

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
FINAL = 1024 if PROTO else 2560
SS = 2
S = FINAL*SS
rs = S/2048.0
rng = np.random.default_rng(7)

def fblur(buf, sig):
    if sig <= 10: return gaussian_filter(buf, (sig,sig,0))
    ds = max(2,int(sig//6))
    small = buf[::ds,::ds]
    bl = gaussian_filter(small,(sig/ds,sig/ds,0))
    big = ndzoom(bl,(ds,ds,1),order=1)[:buf.shape[0],:buf.shape[1]]
    if big.shape[:2]!=buf.shape[:2]:
        pad=np.zeros_like(buf); pad[:big.shape[0],:big.shape[1]]=big; big=pad
    return big

# ---------------- geometry ----------------
Hpos = {'a':(-1.0,0.0),'b':(0.0,-0.85),'c':(1.0,0.0),'d':(0.0,0.85),
        'u':(-1.93,0.47),'v':(-1.93,-0.47),'x':(1.93,-0.47),'y':(1.93,0.47),
        'l':(0.0,-1.72),'m':(0.0,1.72)}
H_edges = [('a','b'),('b','c'),('c','d'),('d','a'),
           ('a','u'),('a','v'),('u','v'),
           ('c','x'),('c','y'),('x','y'),
           ('b','l'),('d','m')]
def world(p):
    x,y = p
    return 0.5*S + x*0.208*S, 0.435*S - y*0.208*S
mid = {}
for i,(p,q) in enumerate(H_edges):
    mid[i] = tuple(0.5*(np.array(Hpos[p])+np.array(Hpos[q])))
Gpos = {i: world(mid[i]) for i in mid}
# adjacency of G
Gadj = [[False]*12 for _ in range(12)]
for i in range(12):
    for j in range(i+1,12):
        if set(H_edges[i])&set(H_edges[j]): Gadj[i][j]=Gadj[j][i]=True
# Krausz cliques: H-vertex -> incident edges
inc = defaultdict(list)
for i,(p,q) in enumerate(H_edges):
    inc[p].append(i); inc[q].append(i)
cliques = {v: js for v,js in inc.items() if len(js) >= 2}

# 224 stable partitions with 4 blocks (from census enumeration, recompute here)
blocks_all = []
def stab(i, blocks):
    if i==12:
        if len(blocks)<=4:
            blocks_all.append(tuple(tuple(sorted(b)) for b in blocks))
        return
    for b in blocks:
        if all(not Gadj[i][w] for w in b):
            b.append(i); stab(i+1,blocks); b.pop()
    if len(blocks)<4:
        blocks.append([i]); stab(i+1,blocks); blocks.pop()
stab(0,[])
blocks_all = [B for B in blocks_all if len(B)==4]
print("stable 4-partitions:", len(blocks_all))
assert len(blocks_all)==224

# ---------------- palette ----------------
VOID = np.array([0.010,0.013,0.028])
SLATE = (0.30,0.34,0.58)
STAR  = (1.0,0.88,0.55)
ICE   = (0.42,0.88,1.05)
WARM  = (0.95,0.55,0.16)
CLIQUE_COLS = {'a':(0.95,0.38,0.10),'c':(1.0,0.72,0.22),
               'b':(0.88,0.22,0.12),'d':(0.98,0.55,0.30),
               'u':(0.45,0.60,0.85),'v':(0.45,0.60,0.85),
               'x':(0.45,0.60,0.85),'y':(0.45,0.60,0.85)}

# ---------------- buffers + batched splat ----------------
groups = defaultdict(lambda: [[],[],[]])
def add(bk, xs, ys, w, col):
    g = groups[(bk, tuple(np.round(col,4)))]
    g[0].append(np.asarray(xs,np.float64)); g[1].append(np.asarray(ys,np.float64))
    g[2].append(np.broadcast_to(np.asarray(w,np.float64), np.shape(xs)).copy())
def flush(buffers):
    for (bk,col),(xs,ys,ws) in groups.items():
        xs=np.concatenate(xs); ys=np.concatenate(ys); ws=np.concatenate(ws)
        buf=buffers[bk]
        x0=np.floor(xs).astype(np.int64); y0=np.floor(ys).astype(np.int64)
        fx=xs-x0; fy=ys-y0
        for dx in (0,1):
            for dy in (0,1):
                wx=fx if dx else 1-fx; wy=fy if dy else 1-fy
                xi=x0+dx; yi=y0+dy
                m=(xi>=0)&(xi<S)&(yi>=0)&(yi<S)
                if not m.any(): continue
                idx=yi[m]*S+xi[m]; ww=(ws*wx*wy)[m]
                acc=np.bincount(idx,weights=ww,minlength=S*S).reshape(S,S)
                for c in range(3):
                    if col[c]: buf[...,c]+=(acc*col[c]).astype(np.float32)
    groups.clear()

def line(bk,p,q,w,col,n=None,jit=0.0):
    n = n or int(math.hypot(q[0]-p[0],q[1]-p[1])/1.2)+2
    t=np.linspace(0,1,n)
    px=p[0]+(q[0]-p[0])*t + (rng.normal(0,jit,n) if jit else 0)
    py=p[1]+(q[1]-p[1])*t + (rng.normal(0,jit,n) if jit else 0)
    add(bk,px,py,w,col)

# ---------------- co-color ropes ----------------
# for each of the 224 colorings, each color class contributes its consecutive
# pairs (angular order); identical pairs bundle into ropes.
# rope brightness = co-color frequency across the whole 4-coloring ecology.
pair_warm = defaultdict(int)
pair_ice  = defaultdict(int)
for B in blocks_all:
    sizes = tuple(sorted(map(len,B),reverse=True))
    is_wound = sizes==(3,3,3,3)
    for blk in B:
        if len(blk)<2: continue
        pts=np.array([Gpos[i] for i in blk])
        c=pts.mean(0)
        order=sorted(range(len(blk)), key=lambda t: math.atan2(pts[t][1]-c[1],pts[t][0]-c[0]))
        for t in range(len(order)):
            a_,b_ = blk[order[t]], blk[order[(t+1)%len(order)]]
            if len(order)==2 and t==1: break
            key=(min(a_,b_),max(a_,b_))
            (pair_ice if is_wound else pair_warm)[key]+=1
maxw = max(pair_warm.values())
maxi = max(pair_ice.values()) if pair_ice else 1
print("distinct warm pairs:",len(pair_warm),"max count:",maxw," ice pairs:",len(pair_ice),"max:",maxi)
def rope(pairs, maxc, col, gain, bowsign):
    for (i,j),cnt in pairs.items():
        p,q = np.array(Gpos[i]), np.array(Gpos[j])
        d = q-p; L=np.hypot(*d)
        nrm = np.array([-d[1],d[0]])/ (L+1e-9)
        h = hash((i,j,bowsign))
        bow = nrm * L*0.16*(1 if (h%2) else -1) * bowsign
        mx,my = 0.5*(p+q) + bow
        t=np.linspace(0,1,420)
        B_ = max(6, int(4+cnt*0.25))
        w_s = gain*(cnt**0.85)/B_ * rs
        for b_ in range(B_):
            j1=rng.normal(0,0.0028*S); j2=rng.normal(0,0.0028*S)
            px=(1-t)**2*p[0]+2*(1-t)*t*(mx+j1)+t**2*q[0]
            py=(1-t)**2*p[1]+2*(1-t)*t*(my+j2)+t**2*q[1]
            add("fog",px,py,w_s,col)
rope(pair_warm, maxw, WARM, 0.040, 1)
rope(pair_ice,  maxi, ICE,  0.185, -1)

# ---------------- H skeleton ----------------
for (p,q) in H_edges:
    line("hsk", world(Hpos[p]), world(Hpos[q]), 0.62*rs, SLATE, n=int(0.4*S), jit=0.0)
for v,p in Hpos.items():
    x,y=world(p)
    ang=rng.uniform(0,2*np.pi,300); rad=np.abs(rng.normal(0,0.004*S,300))
    add("hsk", x+rad*np.cos(ang), y+rad*np.sin(ang), 0.030*rs*rs*40/300*28, SLATE)

# ---------------- Krausz glass plates ----------------
from PIL import Image, ImageDraw
plates = np.zeros((S,S,3), np.float32)
pil = Image.new("F",(S,S),0.0)
for v,js in cliques.items():
    pts=[Gpos[j] for j in js]
    col=np.array(CLIQUE_COLS[v])
    if len(pts)>=3:
        c=np.mean(pts,axis=0)
        pts_sorted=sorted(pts,key=lambda p:math.atan2(p[1]-c[1],p[0]-c[0]))
        im = Image.new("F",(S,S),0.0)
        d=ImageDraw.Draw(im)
        d.polygon([tuple(map(float,p)) for p in pts_sorted], fill=0.11)
        mask=np.asarray(im)
        plates += mask[...,None]*col[None,None,:]*0.55
    # clique edges (glass rims)
    for aa,bb in itertools.combinations(range(len(pts)),2):
        line("rims", pts[aa], pts[bb], 0.85*rs, tuple(col*1.0), n=int(0.30*S))

# ---------------- G stars ----------------
for i,(x,y) in Gpos.items():
    n_=1400
    ang=rng.uniform(0,2*np.pi,n_); rad=np.abs(rng.normal(0,0.0048*S,n_))
    add("stars", x+rad*np.cos(ang), y+rad*np.sin(ang), 2.7*rs*rs*160/n_, STAR)

buffers={k:np.zeros((S,S,3),np.float32) for k in ("fog","hsk","rims","stars")}
flush(buffers)

# ---------------- compose ----------------
img=np.zeros((S,S,3),np.float32)
yy=np.linspace(0,1,S)[:,None,None]
img += VOID[None,None,:]*(0.8+0.4*yy)
fog = buffers["fog"]
img += gaussian_filter(fog,(1.6*rs,1.6*rs,0))*0.9
img += fblur(fog,12*rs)*0.55
img += fblur(fog,48*rs)*0.15
img += gaussian_filter(buffers["hsk"],(1.0*rs,1.0*rs,0))
img += fblur(plates, 2.0*rs)
img += gaussian_filter(buffers["rims"],(1.0*rs,1.0*rs,0))*0.55
img += fblur(buffers["rims"], 6*rs)*0.30
st = buffers["stars"]
img += gaussian_filter(st,(1.5*rs,1.5*rs,0))
img += fblur(st,14*rs)*0.6
lum=img.sum(2)
m=np.clip((lum-1.2)/2.0,0,1)[...,None]*img
img += 0.5*fblur(m,30*rs)
cyy,cxx=np.mgrid[0:S,0:S]
rr=np.hypot((cxx-0.5*S)/(0.75*S),(cyy-0.47*S)/(0.72*S))
img *= (1.0-0.40*np.clip(rr-0.5,0,1)**1.5)[...,None]
del cyy,cxx,rr,lum,m

out=tonemap(img,k=1.0,gamma=0.80)

fs=int(0.0125*S)
ty=0.870*S
out=draw_text(out,(0.5*S,ty),"THE GRAPH THAT PASSED EVERY TEST",int(fs*1.65),(0.92,0.80,0.55),anchor="mm")
for i,(ln,colr) in enumerate([
 ("H (slate skeleton) → G = L(H): twelve stars, one for each edge of H — the counterexample graph of MO 513515",(0.62,0.56,0.48)),
 ("glass plates = the Krausz partition: in a line graph every neighborhood splits into two cliques, so no claw can perch",(0.62,0.56,0.48)),
 ("all 495 quadruples checked: zero induced K_{1,3}  ·  ropes = the 224 proper 4-colorings: tied stars share a color",(0.62,0.56,0.48)),
 ("rope brightness = how often  ·  ice ropes = the 32 equal-quarters colorings, the shape (3,3,3,3) whose Schur weight is −64",(0.55,0.62,0.68)),
]):
    out=draw_text(out,(0.5*S,ty+(0.030+0.024*i)*S),ln,fs,colr,anchor="mm")

save(out,f"art_q2mb/{'proto_A' if PROTO else 'companion_graph'}.png",final=FINAL)
print("saved",FINAL)
