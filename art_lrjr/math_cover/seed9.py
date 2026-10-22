"""Exact cover time for the coordinator's artwork disc sequence (rng seed 9)."""
import sys, json, math, numpy as np
sys.path.insert(0, '/home/user/claude-mythos-self-play/art_lrjr/math_cover')
from sim import Sim
from validate import first_cover
rng = np.random.default_rng(9); u = rng.random(10**6); th = rng.random(10**6) * 2 * np.pi
cx = np.sqrt(u) * np.cos(th); cy = np.sqrt(u) * np.sin(th)
sim = Sim(cap=2000000)
r1 = sim.run(0, R=1.0, Nmax_log2=21, stream=(cx, cy), count=False)
T = r1['T']; print('T', T, 'Trim', r1['Trim'], 'last', r1['last'], 'amb', r1['ambiguous'])
r2 = sim.run(0, R=1.0, Nmax_log2=21, stream=(cx, cy), count=False, track_from=1024)
assert r2['T'] == T
tr = sim.track
closings = []; prev = None
for (n, nc, x, y) in tr:
    if prev is not None and nc < prev:
        closings.append([n, x, y, prev, nc])
    prev = nc
# exact certificate for last point + zoomed brute force
lx, ly = r1['last']; k = np.arange(1, T + 1)
d2 = (cx[:T] - lx) ** 2 + (cy[:T] - ly) ** 2; cov = d2 < 1.0 / k
cert = bool((not cov[:-1].any()) and cov[-1])
disks = np.stack([k.astype(float), cx[:T], cy[:T]], 1)
G = 1201; w = 3 / math.sqrt(T)
fz = first_cover(disks, G, 1.0, lx - w, ly - w, 2 * w / (G - 1))
Gb = 2501; fb = first_cover(disks, Gb, 1.0, -1, -1, 2 / (Gb - 1))
out = dict(T=T, last_point=[lx, ly], last_point_radius=math.hypot(lx, ly), T_rim=r1['Trim'],
           closings=[[c[0], c[1], c[2]] for c in closings[-12:]],
           closings_detail="each entry [N, x, y]: disc N reduced the number of uncovered components (8-connected cells "
                           "of side <= r_N/16 holding a certified-uncovered point); (x,y) = a certified-uncovered point "
                           "of the hole just before disc N closed it (last 12 such events, chronological).",
           hole_counts_before_after=[[c[0], c[3], c[4]] for c in closings[-12:]],
           certificate_last_point_uncovered_by_discs_lt_T_and_covered_by_T=cert,
           zoom_bruteforce_T=float(fz[fz != -2].max()), global_2501grid_T=float(fb[fb != -2].max()),
           ambiguous_leaves=r1['ambiguous'])
json.dump(out, open('/home/user/claude-mythos-self-play/art_lrjr/math_cover/seed9.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
