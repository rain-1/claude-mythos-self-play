"""WHERE THE TIME IS SPENT -- the deliberation web of a TSP solve.
Held-Karp 1-tree subgradient ascent over 8000 iterations: every edge that ever
entered a 1-tree relaxation, drawn as a rope whose thickness and heat is the
number of iterations the solver held it (dwell = literal time spent).  Violet
ghosts = edges abandoned early; teal = edges held late; gold = the best tour
found (within the printed gap of optimal, certified by the HK bound).
Live MO 501687: 'Where does Concorde spend its time'."""
import sys, pickle, numpy as np
from kit import splat, draw_polyline, wide_bloom, tonemap, save, ramp, typ

PROTO  = "final" not in sys.argv
S      = 1600 if PROTO else 5120
FINAL  = 800 if PROTO else 2560
rs     = S / 1600.0

d = pickle.load(open("dwell_data.pkl","rb"))
P, dwell, last, tour, pi = d['P'], d['dwell'], d['last'], d['tour'], d['pi']
tog = d['tog']
lb, L = d['lb'], d['L']
print(f"edges {len(dwell)}, tour {L:.5f}, HK {lb:.5f}, gap {(L-lb)/lb*100:.3f}%")
T = max(last.values()) + 1

cx = cy = S/2
SC = S * 0.405
def w2s(p): return cx + p[...,0]*SC, cy - p[...,1]*SC

web  = np.zeros((S, S, 3), np.float32)
gold = np.zeros((S, S), np.float32)
node = np.zeros((S, S), np.float32)

# hue by volatility (calm teal -> churning ember); transient ghosts violet
HUE = [(0.00,(0.10,0.42,0.55)),(0.40,(0.22,0.58,0.66)),
       (0.70,(0.80,0.34,0.38)),(1.00,(1.00,0.52,0.46))]
VIOLET = np.array([0.36,0.22,0.58])
maxtog = max(tog.values())
print("max toggles", maxtog, " contested(>4):", sum(1 for v in tog.values() if v>4))

rng = np.random.default_rng(5)
tour_edges = set()
for a in range(len(tour)):
    i, j = tour[a], tour[(a+1) % len(tour)]
    tour_edges.add((min(i,j), max(i,j)))

# vectorized ropes: gather every stroke sample into flat arrays, 3 splats total
NPTS = 90 if not PROTO else 60
Xs_all, Ys_all, Wr, Wg, Wb = [], [], [], [], []
for (i, j), c in dwell.items():
    p, q = P[i], P[j]
    v = tog.get((i,j), 1)
    ghost = (c < 60 and v <= 2)
    col = VIOLET if ghost else ramp(HUE, (v / maxtog) ** 0.5)
    nstroke = max(1, int(np.ceil(c / 18)))
    dvec = q - p
    perp = np.array([-dvec[1], dvec[0]]) / (np.hypot(*dvec) + 1e-12)
    width = 0.0016 * (1 + 0.9*np.log1p(c/40))
    mass = 34.0 * rs * rs * c**0.35 / (nstroke * NPTS) * (3.0 if ghost else 1.0)
    off = perp[None,:] * rng.normal(0, width, (nstroke,1))
    bow = perp[None,:] * rng.normal(0, width*0.6, (nstroke,1))
    ts = np.linspace(0, 1, NPTS)[None,:,None]
    pts = ((p+off)[:,None,:]*(1-ts) + (q+off)[:,None,:]*ts
           + bow[:,None,:]*np.sin(np.pi*ts))
    X, Y = w2s(pts)
    Xs_all.append(X.ravel()); Ys_all.append(Y.ravel())
    n = X.size
    Wr.append(np.full(n, mass*col[0])); Wg.append(np.full(n, mass*col[1]))
    Wb.append(np.full(n, mass*col[2]))
Xa = np.concatenate(Xs_all); Ya = np.concatenate(Ys_all)
for ch, W in enumerate((Wr, Wg, Wb)):
    tmp = np.zeros((S, S), np.float32)
    splat(tmp, Xa, Ya, np.concatenate(W))
    web[..., ch] += tmp

# gold tour: continuous closed thread, slight width
tp = P[np.append(tour, tour[0])]
for off in (-0.0018, -0.0009, 0.0, 0.0009, 0.0018):
    X, Y = w2s(tp + off)
    draw_polyline(gold, X, Y, 1300*rs*rs*len(tour))

# cities: beads, brightness lifted by |pi| (the node potentials the ascent paid)
api = np.abs(pi); api /= api.max()
Xn, Yn = w2s(P)
splat(node, Xn, Yn, 0.55 + 2.8*api**1.5)
node = wide_bloom(node, 2.2*rs) * 2400 * rs * rs

img = np.zeros((S, S, 3), np.float32)
w_t = typ(web.sum(-1)); web /= w_t
img += web * 0.62
halo = np.stack([wide_bloom(web[...,ch], 7*rs) for ch in range(3)], -1)
img += halo * (0.75/max(typ(halo.sum(-1)),1e-9))
gold_n = gold/typ(gold)
gold_h = gold_n*1.35 + wide_bloom(gold_n, 5*rs)*1.6
img += gold_h[...,None]*np.array([1.0,0.72,0.24])*1.55
img += node[...,None]*np.array([0.92,0.97,1.0])*1.05
out = tonemap(img, k=1.05, gamma=0.85)
save(out, "proto_dwell.png" if PROTO else "dwell_web.png", FINAL)
