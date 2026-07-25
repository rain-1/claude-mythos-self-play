"""
COMPANION B — "Three Ledgers"  (2560²)

One chromatic symmetric function, three bases, three feathers:
  p — signs fixed by law (Whitney: sign = (-1)^(n-l(lambda)) for EVERY graph)
  s — one barb points the wrong way: a_(3,3,3,3) = -64
  e — two barbs point the wrong way: e_(5,4,3) = -192, e_(4,4,4) = -256
Rows = the 77 partitions of 12 in the same (dominance-rank, lex) order everywhere.
Barb length = log|coefficient|; right = positive, left = negative; ghost tick = zero.
"""
import json, math, sys
import numpy as np
from collections import defaultdict
from scipy.ndimage import gaussian_filter, zoom as ndzoom
sys.path.insert(0, "art_q2mb")
from kit import tonemap, save, draw_text, ramp

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
FINAL = 1024 if PROTO else 2560
SS = 2
S = FINAL*SS
rs = S/2048.0
rng = np.random.default_rng(21)

def fblur(buf, sig):
    if sig <= 10: return gaussian_filter(buf, (sig,sig,0))
    ds = max(2,int(sig//6))
    small = buf[::ds,::ds]
    bl = gaussian_filter(small,(sig/ds,sig/ds,0))
    big = ndzoom(bl,(ds,ds,1),order=1)[:buf.shape[0],:buf.shape[1]]
    if big.shape[:2]!=buf.shape[:2]:
        pad=np.zeros_like(buf); pad[:big.shape[0],:big.shape[1]]=big; big=pad
    return big

R = json.load(open("art_q2mb/results.json"))
c_p = {tuple(map(int,k.split())): v for k,v in R["c_p"].items()}
a_s = {tuple(map(int,k.split())): v for k,v in R["a_s"].items()}
a_e = {tuple(map(int,k.split())): v for k,v in R["a_e"].items()}

def partitions(n, maxp=None):
    if maxp is None: maxp=n
    if n==0: yield (); return
    for p in range(min(n,maxp),0,-1):
        for rest in partitions(n-p,p): yield (p,)+rest
def nrank(l): return sum(i*p for i,p in enumerate(l))
P = sorted(partitions(12), key=lambda l:(nrank(l), l))

VOID = np.array([0.011,0.013,0.029])
POS_RAMP = [(0.30,0.09,0.03),(0.72,0.30,0.07),(1.0,0.72,0.28)]
ICE  = (0.42,0.88,1.05)
LAWNEG = (0.44,0.38,0.85)
GHOST= (0.20,0.19,0.36)
SPINE= (0.55,0.42,0.25)

cols = {"p": (0.185*S, c_p), "s": (0.50*S, a_s), "e": (0.815*S, a_e)}
top, bot = 0.075*S, 0.775*S
rows_y = {l: top + (bot-top)*i/(len(P)-1) for i,l in enumerate(P)}
BARB = 0.115*S

groups = defaultdict(lambda: [[],[],[]])
def add(xs, ys, w, col):
    g = groups[tuple(np.round(col,4))]
    g[0].append(np.asarray(xs,np.float64)); g[1].append(np.asarray(ys,np.float64))
    g[2].append(np.broadcast_to(np.asarray(w,np.float64), np.shape(xs)).copy())
def flush(buf):
    for col,(xs,ys,ws) in groups.items():
        xs=np.concatenate(xs); ys=np.concatenate(ys); ws=np.concatenate(ws)
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

buf = np.zeros((S,S,3), np.float32)

for name,(cx, table) in cols.items():
    maxv = max(abs(v) for v in table.values() if v) if table else 1
    # rachis (spine)
    t=np.linspace(0,1,int(0.8*S))
    for k in range(10):
        j=rng.normal(0,0.0012*S)
        add(np.full_like(t,cx+j), top-0.012*S+(bot-top+0.030*S)*t, 0.08*rs, SPINE)
    for i,l in enumerate(P):
        v = table.get(l,0)
        y = rows_y[l]
        droop = 0.010*S + 0.020*S*(i/len(P))
        if v == 0:
            # ghost tick
            n=60
            tt=np.linspace(-1,1,n)
            add(cx+tt*0.008*S, np.full(n,y), 0.75*rs, GHOST)
            continue
        Lb = BARB*(0.16 + 0.84*math.log(abs(v))/math.log(maxv))
        sgn = 1 if v>0 else -1
        tcol = math.log(abs(v))/math.log(maxv)
        if v<0: col = LAWNEG if name=="p" else ICE
        else:   col = ramp(POS_RAMP, 0.25+0.75*tcol)
        nb = 7
        n=int(300*rs)
        tt=np.linspace(0,1,n)
        amp = (0.52 + 0.85*tcol) * ((1.7 if name!="p" else 1.1) if v<0 else 1.0)
        for b in range(nb):
            j1=rng.normal(0,0.0016*S); j2=rng.normal(0,0.0013*S)
            xx = cx + sgn*tt*Lb + j1*tt
            yyv = y + droop*tt**2 + j2*tt
            wprof = (1.0-0.55*tt)
            add(xx, yyv, amp*rs/nb*1.35*wprof, col)
        # tip bead
        nb2=160
        ang=rng.uniform(0,2*np.pi,nb2); rad=np.abs(rng.normal(0,0.0022*S,nb2))
        add(cx+sgn*Lb+rad*np.cos(ang), y+droop+rad*np.sin(ang),
            amp*rs*rs*22/nb2*(2.2 if v<0 else 1.0), col)
        if v<0 and name!="p":
            # ice flare on the broken barb
            nb3=400
            ang=rng.uniform(0,2*np.pi,nb3); rad=np.abs(rng.normal(0,0.010*S,nb3))
            add(cx+sgn*Lb+rad*np.cos(ang), y+droop+rad*np.sin(ang),
                1.3*rs*rs*30/nb3, ICE)

# mini Young-diagram glyphs at the broken barbs (s,e negatives)
glyph = np.zeros((S,S,3), np.float32)
for name,(cx, table) in cols.items():
    if name=="p": continue
    maxv = max(abs(v) for v in table.values() if v)
    for l,v in table.items():
        if v>=0: continue
        y = rows_y[l]; i = P.index(l)
        droop = 0.010*S + 0.020*S*(i/len(P))
        Lb = BARB*(0.16 + 0.84*math.log(abs(v))/math.log(maxv))
        gx = cx - Lb - 0.030*S; gy = y + droop
        csz = 0.0060*S
        w_, h_ = l[0], len(l)
        x0=gx-0.5*w_*csz; y0=gy-0.5*h_*csz
        for ri in range(h_):
            for rj in range(l[ri]):
                ia0,ia1=int(y0+ri*csz+0.1*csz),int(y0+(ri+1)*csz-0.1*csz)
                ja0,ja1=int(x0+rj*csz+0.1*csz),int(x0+(rj+1)*csz-0.1*csz)
                if ia1<=ia0 or ja1<=ja0: continue
                for c in range(3):
                    glyph[ia0:ia1,ja0:ja1,c] += 0.85*ICE[c]

flush(buf)
buf += gaussian_filter(glyph,(0.5*rs,0.5*rs,0))

img=np.zeros((S,S,3),np.float32)
yy=np.linspace(0,1,S)[:,None,None]
img += VOID[None,None,:]*(0.85+0.3*yy)
img += gaussian_filter(buf,(0.9*rs,0.9*rs,0))
img += fblur(buf,7*rs)*0.35
img += fblur(buf,30*rs)*0.22
lum=img.sum(2)
m=np.clip((lum-1.1)/2.0,0,1)[...,None]*img
img += 0.5*fblur(m,26*rs)
cyy,cxx=np.mgrid[0:S,0:S]
rr=np.hypot((cxx-0.5*S)/(0.78*S),(cyy-0.44*S)/(0.72*S))
img *= (1.0-0.36*np.clip(rr-0.55,0,1)**1.5)[...,None]
del cyy,cxx,rr,lum,m

out=tonemap(img,k=1.0,gamma=0.80)

fs=int(0.0125*S)
heads = {"p":("THE LEDGER OF LAW","signs forced for every graph: (−1)^(12−ℓ)"),
         "s":("THE LEDGER OF HARMONY","one entry points away: −64"),
         "e":("THE LEDGER OF PARTS","two entries point away: −192, −256")}
for name,(cx,_) in cols.items():
    h1,h2 = heads[name]
    out=draw_text(out,(cx,0.812*S),h1,int(fs*1.15),(0.85,0.74,0.52),anchor="mm")
    out=draw_text(out,(cx,0.812*S+0.020*S),h2,int(fs*0.82),(0.58,0.53,0.46),anchor="mm")
out=draw_text(out,(0.5*S,0.872*S),"THREE LEDGERS",int(fs*1.7),(0.92,0.80,0.55),anchor="mm")
for i,(ln,colr) in enumerate([
 ("one chromatic symmetric function — X_G of the claw-free counterexample (MO 513515) — read in three bases",(0.62,0.56,0.48)),
 ("rows = the 77 partitions of 12, dominance-ranked  ·  barb = log|coefficient|  ·  right = positive, left = negative, tick = zero",(0.62,0.56,0.48)),
 ("violet = negatives the p-law forces on every graph  ·  ice = the betrayals, with their shapes: (3,3,3,3) · (5,4,3) · (4,4,4)",(0.62,0.56,0.48)),
 ("positivity is not a property of the object; it is a property of the lens",(0.55,0.62,0.68)),
]):
    out=draw_text(out,(0.5*S,0.872*S+(0.026+0.021*i)*S),ln,fs,colr,anchor="mm")

save(out,f"art_q2mb/{'proto_B' if PROTO else 'companion_ledgers'}.png",final=FINAL)
print("saved",FINAL)
