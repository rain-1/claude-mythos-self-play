"""THE TWO WHEELS -- what the overlap decides.  4096^2 hero (supersampled x2).
Two overlapping cycle-wheels sharing m=5 teeth; the product's cycles as luminous threads;
ensemble fog of 300 tau-resamples; c-spectrum band showing k-independence."""
import numpy as np, sys, glob
from fractions import Fraction
from collections import defaultdict
import artlib as A

PREVIEW = len(sys.argv) > 1 and sys.argv[1] == 'preview'
FINAL = 1024 if PREVIEW else 4096
SS = 1 if PREVIEW else 2
S = FINAL*SS
rs = S/8192.0   # scale factor vs full
rng = np.random.default_rng(20260804)

k, m = 41, 5
N = 2*k - m
S1 = list(range(k)); Aset = list(range(k-m, k)); S2 = list(range(k-m, N))
B1 = list(range(0, k-m)); B2 = list(range(k, N))

def rand_cycle(support):
    per = list(support[1:]); rng.shuffle(per)
    cyc = [support[0]] + per
    p = list(range(N))
    for a,b in zip(cyc, cyc[1:]+cyc[:1]): p[a]=b
    return p, cyc

def cycles_of(p):
    seen=[False]*N; out=[]
    for i in range(N):
        if not seen[i]:
            c=[]; j=i
            while not seen[j]: seen[j]=True; c.append(j); j=p[j]
            out.append(c)
    return out

# --- specimen: resample until product has exactly 3 cycles, all length >= 12
while True:
    sig, sigcyc = rand_cycle(S1)
    tau, taucyc = rand_cycle(S2)
    pi = [sig[tau[i]] for i in range(N)]
    cyc = cycles_of(pi)
    if len(cyc)==3 and min(len(c) for c in cyc) >= 14:
        break
print("specimen type:", sorted((len(c) for c in cyc), reverse=True))

# --- layout ---------------------------------------------------------------
cx, cy = S*0.5, S*0.42
D = S*0.205          # ring center offset
R = S*0.29           # ring radius
c1 = np.array([cx-D, cy]); c2 = np.array([cx+D, cy])
# lens: A points on small vertical ellipse at center, in sigma_A cyclic order
sig_order_A = [x for x in sigcyc if x in Aset]
posN = {}
la, lb = S*0.028, S*0.105
for i, a in enumerate(sig_order_A):
    th = -np.pi/2 + 2*np.pi*i/m
    posN[a] = np.array([cx + la*np.sin(th)*2.2, cy - lb*np.cos(th)])
# left ring: B1 in sigma cyclic order, placed around circle 1 avoiding lens sector
# sigma cycle starting from first A elem: arcs between A's
start = sigcyc.index(sig_order_A[0])
seq = sigcyc[start:] + sigcyc[:start]
b1seq = [x for x in seq if x in B1]
ang0, ang1 = np.pi*0.42, 2*np.pi - np.pi*0.42   # avoid right-facing sector (toward lens)
for i, b in enumerate(b1seq):
    th = ang0 + (ang1-ang0)*(i+0.5)/len(b1seq)
    posN[b] = c1 + R*np.array([np.cos(th), np.sin(th)])
start2 = taucyc.index(sig_order_A[0]) if sig_order_A[0] in taucyc else 0
seq2 = taucyc[start2:] + taucyc[:start2]
b2seq = [x for x in seq2 if x in B2]
for i, b in enumerate(b2seq):
    th = np.pi - (np.pi*0.42) - (2*np.pi - 2*np.pi*0.42)*(i+0.5)/len(b2seq)
    posN[b] = c2 + R*np.array([np.cos(th), np.sin(th)])
P = np.array([posN[i] for i in range(N)])

buf = A.canvas(S)

GOLD  = np.array([1.00, 0.78, 0.36])
CYAN  = np.array([0.36, 0.75, 1.00])
VIOLET= np.array([0.62, 0.44, 1.00])
EMBER = np.array([1.00, 0.42, 0.30])
ICE   = np.array([0.45, 1.00, 0.75])
CYCHUE= [GOLD, ICE, EMBER]

# --- faint ring skeletons
th = np.linspace(0, 2*np.pi, 720)
for c, col in ((c1, CYAN), (c2, VIOLET)):
    ring = np.stack([c[0]+R*np.cos(th), c[1]+R*np.sin(th)], 1)
    A.polyline(buf, ring, col, amp=0.16*rs, closed=True)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    d2 = (xx-c[0])**2 + (yy-c[1])**2
    glow = np.exp(-d2/(2*(R*0.75)**2)) * (d2 < (R*1.05)**2)
    for ch in range(3): buf[...,ch] += 0.014*glow*col[ch]
    del yy, xx, d2, glow

# --- ensemble fog: 300 tau-resamples, threads colored by their cycle length (ECDF warm-cool)
NFOG = 70 if PREVIEW else 260
fog = A.canvas(S)
lens_all = []
samples = []
for it in range(NFOG):
    sig2, _ = rand_cycle(S1)
    tau2, _ = rand_cycle(S2)
    pi2 = [sig2[tau2[i]] for i in range(N)]
    cyc2 = cycles_of(pi2)
    samples.append(cyc2)
    lens_all += [len(c) for c in cyc2]
lens_sorted = np.sort(np.array(lens_all))
def ecdf(l): return np.searchsorted(lens_sorted, l, 'right')/len(lens_sorted)
for cyc2 in samples:
    for c in cyc2:
        if len(c) < 3: continue
        pts = A.catmull(P[c], closed=True, subdiv=10)
        e = ecdf(len(c))
        col = (1-e)*np.array([0.25,0.45,0.85]) + e*np.array([0.95,0.55,0.30])
        A.polyline(fog, pts, col, amp=0.030*rs, closed=True)
buf += fog * 0.75

# --- machinery threads: sigma (cyan) and tau (violet), dim
sigpts = A.catmull(P[[x for x in sigcyc]], closed=True, subdiv=12)
taupts = A.catmull(P[[x for x in taucyc]], closed=True, subdiv=12)
A.polyline(buf, sigpts, CYAN, amp=0.20*rs, closed=True)
A.polyline(buf, taupts, VIOLET, amp=0.20*rs, closed=True)

# --- specimen product cycles: blazing threads
for ci, c in enumerate(sorted(cyc, key=len, reverse=True)):
    pts = A.catmull(P[c], closed=True, subdiv=26)
    n = len(pts)
    t = np.arange(n)/n
    amps = 0.75 + 0.25*np.sin(2*np.pi*(3*t + ci/3))
    # draw in slightly varying amp for life
    A.polyline(buf, pts, CYCHUE[ci], amp=1.5*rs, closed=True)
    A.polyline(buf, pts+np.array([0.9*rs*2,0.9*rs*2]), CYCHUE[ci]*0.65+0.35, amp=0.45*rs, closed=True)

# --- points
for b in B1: A.star(buf, *P[b], CYAN, amp=1.0, rad=2.4*rs*2)
for b in B2: A.star(buf, *P[b], VIOLET, amp=1.0, rad=2.4*rs*2)
for a in Aset: A.star(buf, *P[a], GOLD, amp=5.0, rad=6.0*rs*2)

# --- spectrum band: c-distribution per m, k-independence -------------------
# load census probabilities
data = defaultdict(dict)
for f in glob.glob('qdata/q_*.txt'):
    for line in open(f):
        p = line.split()
        if len(p)!=4: continue
        data[(int(p[0]),int(p[1]))][tuple(int(x) for x in p[2].split(','))] = Fraction(p[3])
def cdist(k_, m_):
    d = defaultdict(Fraction)
    for nu,q in data[(k_,m_)].items(): d[len(nu)] += q
    return d
band_y0, band_y1 = S*0.80, S*0.965
ms = [2,3,4,5,6,7,8]
bw = S*0.94/len(ms)
x0 = S*0.03
for j, mm in enumerate(ms):
    bx = x0 + j*bw
    ks = sorted(kk for (kk,m_) in data if m_==mm and kk in (mm, 10, 12))
    base = cdist(ks[0], mm)
    cs = sorted(base)
    for c in cs:
        xx0 = bx + bw*(0.12 + 0.76*(c-0.5)/9.0)
        for ri, kk in enumerate(ks):
            pv = float(cdist(kk, mm)[c])
            xx = xx0 + (ri-1)*3.4*rs*2
            yy0 = band_y1 - (band_y1-band_y0)*pv*0.88
            col = GOLD if ri==0 else (ICE if ri==1 else VIOLET*0.75+0.25)
            A.polyline(buf, np.array([[xx,yy0],[xx,band_y1]]), col, amp=0.85*rs)
            A.star(buf, xx, yy0, col, amp=1.8, rad=2.0*rs*2)
# band baseline
A.polyline(buf, np.array([[x0, band_y1],[x0+len(ms)*bw, band_y1]]), GOLD*0.6, amp=0.25*rs)

img = A.bloom(buf, sigmas=(2.0*rs*2, 8*rs*2, 28*rs*2), weights=(1.0, 0.4, 0.22))
img = A.tonemap(img, k=1.6, gamma=0.85)

# --- text
tx = []
W = S
def T(x,y,s,size,col=(0.88,0.84,0.76),bold=False,anchor='la'): tx.append((x*W, y*W, s, int(size*rs*2), col, bold, anchor))
T(0.030, 0.030, "THE TWO WHEELS", 46, (1.0,0.87,0.55), True)
T(0.030, 0.058, "what the overlap decides  (MO 513838)", 22, (0.75,0.72,0.66))
T(0.030, 0.090, f"one product of two {k}-cycles sharing m={m} points - its {len(cyc)} cycles as threads; 300 re-drawn partners as fog", 15, (0.62,0.60,0.56))
T(0.500, 0.775, "the emission spectrum of the cycle count depends only on the shared teeth:", 17, (0.75,0.72,0.66), anchor='ma')
T(0.500, 0.792, "Pr[c cycles] identical for every k: three instruments (k=m gold, k=10 ice, k=12 violet) strike the same lines exactly", 14, (0.62,0.60,0.56), anchor='ma')
for j, mm in enumerate(ms):
    T((x0 + j*bw + bw*0.5)/W + 0.0, 0.968, f"m={mm}", 15, (0.7,0.67,0.6), anchor='ma')
T(0.970, 0.030, "q(nu) = sum_L  q_mm(L) x gap-dressing(L,nu,k)", 19, (0.85,0.80,0.70), anchor='ra')
T(0.970, 0.054, "m=3:  q = 2|perm|(bc - t(t+1)) / (k-1)^2(k-2)^2,  t=(k-2-a)+", 17, (0.75,0.72,0.66), anchor='ra')
T(0.115, 0.130, "sigma - a 41-cycle on S1", 17, (0.55,0.75,0.95))
T(0.885, 0.130, "tau - a 41-cycle on S2", 17, (0.72,0.60,0.95), anchor='ra')
T(0.500, 0.435, "the five shared teeth", 15, (1.0,0.87,0.55), anchor='ma')
T(0.500, 0.720, "specimen type (29, 27, 21)  -  every cycle passes through the lens", 16, (0.75,0.72,0.66), anchor='ma')
img = A.bake_text(img, tx, S)
A.save(img, 'hero_preview.png' if PREVIEW else 'wheels_4096.png', final=FINAL)
print("saved")
