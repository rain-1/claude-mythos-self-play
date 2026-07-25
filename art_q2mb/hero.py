"""
HERO — "The Wound in the Court of Shapes"  (4096², supersampled 2x)

Dominance lattice of all 77 partitions of 12 as a chandelier of Young diagrams.
Glow = exact Schur coefficient of X_G (MO 513515 counterexample, verified here).
Ghost = zero. Ice = the unique negative a_(3,3,3,3) = -64.
Warm dust = stable partitions (colorings) of that type.
"""
import json, math, sys
import numpy as np
from collections import defaultdict
from scipy.ndimage import gaussian_filter
sys.path.insert(0, "art_q2mb")
from kit import tonemap, save, draw_text, ramp
from scipy.ndimage import zoom as ndzoom

def fblur(buf, sig):
    if sig <= 10: return gaussian_filter(buf, (sig,sig,0))
    ds = max(2, int(sig//6))
    small = buf[::ds, ::ds]
    bl = gaussian_filter(small, (sig/ds, sig/ds, 0))
    big = ndzoom(bl, (ds, ds, 1), order=1)[:buf.shape[0], :buf.shape[1]]
    if big.shape[:2] != buf.shape[:2]:
        pad = np.zeros_like(buf); pad[:big.shape[0], :big.shape[1]] = big; big = pad
    return big

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
FINAL = 1024 if PROTO else 4096
SS = 2
S = FINAL * SS
rs = S / 2048.0
rng = np.random.default_rng(12)

R = json.load(open("art_q2mb/results.json"))
E = json.load(open("art_q2mb/extras.json"))
a_s = {tuple(map(int,k.split())): v for k,v in R["a_s"].items()}
census = {tuple(map(int,k.split())): v for k,v in E["census"].items()}

# ---------------- lattice ----------------
def partitions(n, maxp=None):
    if maxp is None: maxp=n
    if n==0: yield (); return
    for p in range(min(n,maxp),0,-1):
        for rest in partitions(n-p,p): yield (p,)+rest
P = sorted(partitions(12), reverse=True)
def nrank(l): return sum(i*p for i,p in enumerate(l))
def dom_leq(mu,lam):
    sm=sl=0
    for i in range(max(len(mu),len(lam))):
        sm += mu[i] if i<len(mu) else 0
        sl += lam[i] if i<len(lam) else 0
        if sm>sl: return False
    return True
rel = {(a,b) for a in P for b in P if a!=b and dom_leq(b,a)}
covers = [(a,b) for (a,b) in rel
          if not any((a,c) in rel and (c,b) in rel for c in P)]

# ---------------- layout: even level spacing ----------------
top, bot = 0.060*S, 0.840*S
levels = defaultdict(list)
for l in P: levels[nrank(l)].append(l)
lev_sorted = sorted(levels)
lev_y = {n: top + (bot-top)*i/(len(lev_sorted)-1) for i,n in enumerate(lev_sorted)}
pos = {}
for n, ls in levels.items():
    xs = {l: l[0]-len(l) for l in ls}
    mean = sum(xs.values())/len(ls)
    for l in ls:
        pos[l] = [0.5*S + (xs[l]-mean)*0.085*S, lev_y[n]]
mind = 0.105*S
for it in range(600):
    moved=False
    for i,a in enumerate(P):
        for b in P[i+1:]:
            dx = pos[b][0]-pos[a][0]; dy = (pos[b][1]-pos[a][1])*1.35
            d = math.hypot(dx, dy)
            if 1e-9 < d < mind:
                push = 0.45*(mind-d)/d * mind*0.12
                sx = dx/ (abs(dx)+1e-9)
                pos[a][0] -= sx*push; pos[b][0] += sx*push
                moved=True
    if not moved: break
xs_all=[p[0] for p in pos.values()]
shift = 0.5*S - 0.5*(min(xs_all)+max(xs_all))
for l in pos: pos[l][0] += shift

# ---------------- palette ----------------
VOID   = np.array([0.012, 0.014, 0.030])
POS_RAMP = [(0.22,0.055,0.020),(0.62,0.22,0.05),(0.95,0.55,0.13),(1.0,0.86,0.42)]
GHOST  = (0.17, 0.16, 0.32)
ICE    = (0.42, 0.88, 1.05)
DUST   = (1.0, 0.80, 0.50)
THREAD_LIT   = (0.85, 0.45, 0.14)
THREAD_GHOST = (0.24, 0.23, 0.46)

maxa = max(a_s.values())
def light(l):
    a = a_s.get(l,0)
    return math.log(a)/math.log(maxa) if a>0 else 0.0

# ---------------- batched splatting ----------------
groups = defaultdict(lambda: [[],[],[]])   # color -> [xs, ys, ws]
def add(buf_key, xs, ys, w, col):
    g = groups[(buf_key, tuple(np.round(col,4)))]
    g[0].append(np.asarray(xs,np.float64)); g[1].append(np.asarray(ys,np.float64))
    g[2].append(np.broadcast_to(np.asarray(w,np.float64), np.shape(xs)).copy())

def flush(buffers):
    for (bk, col), (xs,ys,ws) in groups.items():
        xs=np.concatenate(xs); ys=np.concatenate(ys); ws=np.concatenate(ws)
        buf = buffers[bk]
        x0=np.floor(xs).astype(np.int64); y0=np.floor(ys).astype(np.int64)
        fx=xs-x0; fy=ys-y0
        for dx in (0,1):
            for dy in (0,1):
                wx = fx if dx else 1-fx; wy = fy if dy else 1-fy
                xi=x0+dx; yi=y0+dy
                m=(xi>=0)&(xi<S)&(yi>=0)&(yi<S)
                if not m.any(): continue
                idx=yi[m]*S+xi[m]; ww=(ws*wx*wy)[m]
                acc = np.bincount(idx, weights=ww, minlength=S*S).reshape(S,S)
                for c in range(3):
                    if col[c]: buf[...,c] += (acc*col[c]).astype(np.float32)
    groups.clear()

# ---------------- threads (cover web) ----------------
NTH = 22 if not PROTO else 10
NSAMP = int(150*rs)
for (lam, mu) in covers:
    xa,ya = pos[lam]; xb,yb = pos[mu]
    la, lb = light(lam), light(mu)
    neg = (lam==(3,3,3,3)) or (mu==(3,3,3,3))
    lit = (a_s.get(lam,0)!=0) + (a_s.get(mu,0)!=0)
    if neg:      col = ICE;         amp = 1.7
    elif lit==2: col = THREAD_LIT;  amp = 1.45*(0.35+0.65*0.5*(la+lb))
    elif lit==1: col = tuple(0.5*(a+b) for a,b in zip(THREAD_LIT,THREAD_GHOST)); amp=0.44
    else:        col = THREAD_GHOST; amp = 0.36
    mx, my = 0.5*(xa+xb), 0.5*(ya+yb) + 0.012*S
    t = np.linspace(0,1,NSAMP)
    for t_i in range(NTH):
        j1 = rng.normal(0, 0.0014*S); j2 = rng.normal(0, 0.0014*S)
        px = (1-t)**2*xa + 2*(1-t)*t*(mx+j1) + t**2*xb
        py = (1-t)**2*ya + 2*(1-t)*t*(my+j2) + t**2*yb
        add("threads", px, py, amp*rs/NTH*3.2, col)

# ---------------- dust: stable partitions ----------------
for l, N in census.items():
    if l not in pos: continue
    lx, ly = pos[l]
    n_ = int(min(3200, 120 + N*0.18)) if not PROTO else int(min(800, 50+N*0.06))
    sig = 0.040*S*(1.0 + 0.45*math.log10(1+N))
    ang = rng.uniform(0, 2*np.pi, n_)
    if l == (3,3,3,3):   # the wound: a visible warm ORBIT around the cold heart
        rad = rng.normal(0.048*S, 0.0055*S, n_)
        mass = 3.2 * rs*rs / n_ * 110
    else:
        rad = np.abs(rng.normal(0, sig, n_)) + 0.014*S
        mass = (N**0.62) * 0.045 * rs*rs / n_ * 52
    add("dust", lx+rad*np.cos(ang), ly+rad*np.sin(ang), mass, DUST)

# ---------------- node halo cores ----------------
for l in P:
    a = a_s.get(l,0)
    if a == 0: continue
    lx, ly = pos[l]
    if l==(3,3,3,3): hcol, hamp = ICE, 2.6
    else:
        t = light(l); hcol = ramp(POS_RAMP, 0.3+0.7*t); hamp = (0.35+1.35*t**1.5)
    n_ = 500
    ang = rng.uniform(0,2*np.pi,n_); rad = np.abs(rng.normal(0, 0.030*S, n_))
    add("cores", lx+rad*np.cos(ang), ly+rad*np.sin(ang), hamp*rs*rs*640/n_, hcol)

buffers = {k: np.zeros((S,S,3), np.float32) for k in ("threads","dust","cores")}
flush(buffers)
threads, dust, cores = buffers["threads"], buffers["dust"], buffers["cores"]

# ---------------- Young diagram cells ----------------
cell_layer = np.zeros((S,S,3), np.float32)
def hooklen(l):
    conj = [sum(1 for p in l if p > j) for j in range(l[0])]
    return [[l[i]-j + conj[j]-i - 1 for j in range(l[i])] for i in range(len(l))]
BOX = 0.066*S
for l in P:
    a = a_s.get(l,0)
    lx, ly = pos[l]
    w_, h_ = l[0], len(l)
    cs = BOX / max(w_, h_, 5)
    x0 = lx - 0.5*w_*cs; y0 = ly - 0.5*h_*cs
    hooks = hooklen(l)
    if l == (3,3,3,3): base, amp = ICE, 1.5
    elif a > 0:
        t = light(l); base = ramp(POS_RAMP, 0.25+0.75*t); amp = 0.26 + 0.66*t
    else: base, amp = GHOST, 0.17
    # per-node light normalization: equalize total emitted light across shapes
    area = 12 * cs*cs
    amp *= (BOX*BOX*0.48/area)**0.58
    gap = max(1.0, 0.09*cs)
    for i in range(h_):
        for j in range(l[i]):
            hb = 0.55 + 0.45*(1.0/hooks[i][j])**0.6
            xa_, ya_ = x0+j*cs+gap*0.5, y0+i*cs+gap*0.5
            xb_, yb_ = x0+(j+1)*cs-gap*0.5, y0+(i+1)*cs-gap*0.5
            ia0,ia1 = int(max(0,ya_)), int(min(S,yb_))
            ja0,ja1 = int(max(0,xa_)), int(min(S,xb_))
            if ia1<=ia0 or ja1<=ja0: continue
            for c in range(3):
                cell_layer[ia0:ia1, ja0:ja1, c] += amp*hb*base[c]

# ---------------- compose ----------------
img = np.zeros((S,S,3), np.float32)
yy = np.linspace(0,1,S)[:,None,None]
img += VOID[None,None,:]*(0.75+0.5*yy)
img += gaussian_filter(threads, (0.9*rs,0.9*rs,0))
img += gaussian_filter(dust, (0.9*rs,0.9*rs,0))
img += fblur(dust, 10*rs)*0.6
img += fblur(dust, 40*rs)*0.35
img += gaussian_filter(cell_layer, (0.55*rs,0.55*rs,0))
img += fblur(cell_layer, 5*rs)*0.30
img += fblur(cores, 3*rs)
img += fblur(cores, 16*rs)*0.7
lum = img.sum(2)
m = np.clip((lum-1.1)/2.0, 0, 1)[...,None]*img
img += 0.55*fblur(m, 26*rs)
cyy, cxx = np.mgrid[0:S,0:S]
rr = np.hypot((cxx-0.5*S)/(0.72*S), (cyy-0.55*S)/(0.78*S))
img *= (1.0 - 0.38*np.clip(rr-0.55,0,1)**1.5)[...,None]
del cyy, cxx, rr, lum, m

out = tonemap(img, k=0.88, gamma=0.80)

fs = int(0.0115*S)
ty = 0.882*S
out = draw_text(out, (0.5*S, ty), "THE WOUND IN THE COURT OF SHAPES",
                int(fs*1.7), (0.92,0.80,0.55), anchor="mm")
for i, (ln, colr) in enumerate([
 ("X_G = Σ a_μ s_μ   ·   G = L(H), the 12-vertex claw-free graph of MO 513515   ·   verified from scratch, exactly", (0.62,0.56,0.48)),
 ("all 77 shapes of 12 in dominance order  ·  glow = a_μ (ember→gold, log)  ·  ghost = a_μ = 0  ·  ice = the one negative:  a_(3,3,3,3) = −64", (0.62,0.56,0.48)),
 ("warm dust = the proper colorings of that shape (94 154 stable partitions; 32 live at the wound — the colorings exist, the harmony does not)", (0.62,0.56,0.48)),
 ("remove any single edge of H and every coefficient turns nonnegative", (0.55,0.62,0.68)),
]):
    out = draw_text(out, (0.5*S, ty+(0.028+0.022*i)*S), ln, fs, colr, anchor="mm")

save(out, f"art_q2mb/{'proto_hero' if PROTO else 'hero_wound_court'}.png", final=FINAL)
print("saved", FINAL)
