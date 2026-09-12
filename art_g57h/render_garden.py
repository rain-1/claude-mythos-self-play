"""render_garden.py — WHAT COUNTS AS ALIVE: a garden of Lenia creatures on paper, each species in
its own world (its own rule), all painting their histories on one sheet.

Layers: each species is simulated on its own torus (full sheet or a window), several copies
launched at random headings.  Every `stride` steps the field is strobed onto the sheet in the
species' pigment pair (mixing from the first to the second over the run, fainter when older),
so a creature leaves its whole life behind it: straight ribbons (Orbium, Paraptera), drifting
rings (Synptera sinus pedes), a short wander that ends (Kronium vagus), rosettes (spinners).
Ink outlines the creatures as they are NOW; coral rings mark where one died or two merged.

usage: python3 render_garden.py FINAL steps stride out_prefix [seed]
   FINAL = 1024 (proto: sim 512, native R) or 4096 (hero: sim 2048, R x4)
"""
import sys, json, time
import numpy as np
from fractions import Fraction
from scipy.ndimage import zoom, rotate, label, center_of_mass, distance_transform_edt, gaussian_filter
from lenia import Lenia, rle2arr
import pastel as P

FINAL = int(sys.argv[1]); STEPS = int(sys.argv[2]); STRIDE = int(sys.argv[3]); OUT = sys.argv[4]
SEED = int(sys.argv[5]) if len(sys.argv) > 5 else 1
rng = np.random.default_rng(SEED)
t_start = time.time()
NSIM = FINAL // 2            # full-layer sim size
SCALE = FINAL / 1024.0       # species scale (native R at 1024)
UP = FINAL / NSIM            # upsample sim -> sheet
rs = FINAL / 1024.0

zoo = json.load(open('animals.json'))


def animal(code):
    for a in zoo:
        if a.get('code') == code:
            return a


def seed_at(a, scale):
    """evolved crop of species `a` at R*scale (doubling with settles), plus heading (deg) and mass"""
    p = a['params']; beta = tuple(float(Fraction(b)) for b in str(p['b']).split(','))
    R = p['R']
    crop = rle2arr(a['cells'])
    s_done = 1.0
    stages = []
    while s_done < scale - 1e-9:
        s = min(2.0, scale / s_done); stages.append(s); s_done *= s
    if scale < 1 - 1e-9:
        stages = [scale]
    L = None
    for k, s in enumerate([None] + stages):
        if s is not None:
            crop = np.clip(zoom(crop, s, order=3), 0, 1); R = R * s
        N = int(max(384, 10 * R)); N += N % 2
        L = Lenia(N, R=R, T=p['T'], mu=p['m'], sigma=p['s'], beta=beta)
        L.place(crop, N // 2, N // 2); L.step(250)
        c0 = L.centroid(); L.step(80); c1 = L.centroid()
        if L.mass() < 1e-3:
            raise RuntimeError('species died while rescaling: ' + a['code'])
        # torus-aware: roll the creature to the centre, then crop
        A = np.roll(np.roll(L.A, int(round(N / 2 - c1[0])), axis=0), int(round(N / 2 - c1[1])), axis=1)
        m = int(2.6 * R) + 4
        crop = A[N // 2 - m:N // 2 + m, N // 2 - m:N // 2 + m]
    dy, dx = (c1[0] - c0[0] + N / 2) % N - N / 2, (c1[1] - c0[1] + N / 2) % N - N / 2
    speed = float(np.hypot(dy, dx) / 80.0)
    return crop, np.degrees(np.arctan2(dy, dx)), float(A.sum()), R, beta, p, speed


def label_periodic(mask):
    lab, n = label(mask)
    if n == 0:
        return lab, 0
    parent = list(range(n + 1))
    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]; u = parent[u]
        return u
    def union(u, v):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[max(ru, rv)] = min(ru, rv)
    for a_, b_ in [(lab[0, :], lab[-1, :]), (lab[:, 0], lab[:, -1])]:
        both = (a_ > 0) & (b_ > 0)
        for u, v in set(zip(a_[both].tolist(), b_[both].tolist())):
            union(u, v)
    roots = np.array([find(i) for i in range(n + 1)])
    uniq = {r: i for i, r in enumerate(sorted(set(roots[1:])), start=1)}
    remap = np.array([0] + [uniq[roots[i]] for i in range(1, n + 1)])
    return remap[lab], len(uniq)


# ---- layer specification: (code, copies, size fraction, pigA, pigB, window centre, weight) ----
LAYERS = [
    ('O2u',   4, 1.00, 'cornflower', 'aqua',      None,         1.0),
    ('P4op',  1, 1.00, 'mint',       'pistachio', None,         1.0),
    ('3U4lv', 1, 1.00, 'blush',      'lavender',  None,         0.5),
    ('3P3sp', 1, 1.00, 'lemon',      'apricot',   None,         1.0),
    ('3P3sp', 1, 0.60, 'apricot',    'lemon',     (0.72, 0.30), 1.0),
    ('K4v',   2, 0.50, 'lavender',   'orchid',    (0.30, 0.68), 1.0),
    ('OG2g',  1, 0.35, 'blush',      'orchid',    (0.80, 0.78), 1.0),
    ('2H3t',  1, 0.35, 'lavender',   'cornflower', (0.20, 0.24), 1.0),
    ('H3as',  1, 0.35, 'blush',      'lavender',  (0.55, 0.52), 1.0),
    ('2D6t',  1, 0.35, 'orchid',     'blush',     (0.84, 0.50), 1.0),
]
if len(sys.argv) > 6:
    keep = sys.argv[6].split(',')
    LAYERS = [l for l in LAYERS if l[0] in keep]

W = H = FINAL
sheet = P.Sheet(W, H, seed=SEED + 3)
now_mask = np.zeros((H, W), bool)
birth_mask = np.zeros((H, W), bool)
events_all = []
cert_layers = []
yy, xx = np.mgrid[:H, :W]

for (code, ncopy, frac, pigA, pigB, win, wgt) in LAYERS:
    a = animal(code)
    t_l = time.time()
    try:
        crop, hd0, mass1, R, beta, p, spd = seed_at(a, SCALE)
    except RuntimeError as e:
        print('SKIP', e, flush=True)
        continue
    N = int(round(NSIM * frac)); N += N % 2
    L = Lenia(N, R=R, T=p['T'], mu=p['m'], sigma=p['s'], beta=beta)
    Lb = Lenia(N, R=R, T=p['T'], mu=p['m'], sigma=p['s'], beta=beta)
    launch = []
    g = int(np.ceil(np.sqrt(ncopy)))
    cells = [(i, j) for i in range(g) for j in range(g)]; rng.shuffle(cells)
    for k in range(ncopy):
        i, j = cells[k]
        cy = (i + 0.5 + rng.uniform(-0.3, 0.3)) * N / g; cx = (j + 0.5 + rng.uniform(-0.3, 0.3)) * N / g
        h = rng.uniform(0, 360)
        L.place(crop, cy, cx, angle_deg=(hd0 - h)); Lb.place(crop, cy, cx, angle_deg=(hd0 - h))
        launch.append((cy, cx, h))
    print(f'layer {code} {a["name"]}: R={R:.1f} mass={mass1:.0f} heading={hd0:.0f} N={N} copies={ncopy} seed-time {time.time()-t_l:.0f}s', flush=True)
    absA, absB = P.absorb(P.PIG[pigA]), P.absorb(P.PIG[pigB])
    Aabs = np.zeros((N, N, 3), np.float32)
    nstrobe = STEPS // STRIDE
    # strobe weight: a moving creature overlaps itself 2R/(speed*stride) times along its ribbon;
    # a stationary one overlaps nstrobe times — floor the total so a rosette is a mid-tone, not a hole
    overlap = (2.0 * R) / (max(spd, 1e-3) * STRIDE)
    w_strobe = wgt * 2.8 / max(1.0, overlap)
    w_strobe = max(w_strobe, wgt * 2.4 / nstrobe)
    print(f'  speed {spd:.3f} cells/step, overlap {overlap:.1f}, w_strobe {w_strobe:.4f}', flush=True)
    tracks, events, prev, next_id = {}, [], None, 0
    for s in range(nstrobe):
        L.step(STRIDE)
        f = s / max(1, nstrobe - 1)
        ab = (1 - f) * absA + f * absB
        Aabs += (w_strobe * (0.35 + 0.65 * f) * L.A)[..., None] * ab[None, None, :]
        lab, n = label_periodic(L.A > 0.12)
        cur = []
        if n:
            ms = np.bincount(lab.ravel(), weights=L.A.ravel(), minlength=n + 1)[1:]
            cms = center_of_mass(L.A, lab, range(1, n + 1))
            comps = [(cms[k][0], cms[k][1], ms[k]) for k in range(n) if ms[k] > 0.45 * mass1]
        else:
            comps = []
        def td(a_, b_):
            dy = abs(a_[0] - b_[0]); dx = abs(a_[1] - b_[1]); dy = min(dy, N - dy); dx = min(dx, N - dx)
            return np.hypot(dy, dx)
        if prev is None:
            for (cy, cx, m) in comps:
                cur.append((next_id, cy, cx, m)); tracks[next_id] = [(L.t, cy, cx, m)]; next_id += 1
        else:
            used = set()
            for (cy, cx, m) in comps:
                best, bd = None, 1e9
                for (pid, py, px, pm) in prev:
                    d = td((cy, cx), (py, px))
                    if d < bd:
                        best, bd = pid, d
                if best is not None and bd < 1.5 * R and best not in used:
                    used.add(best); cur.append((best, cy, cx, m)); tracks[best].append((L.t, cy, cx, m))
                else:
                    cur.append((next_id, cy, cx, m)); tracks[next_id] = [(L.t, cy, cx, m)]; next_id += 1
            for (pid, py, px, pm) in prev:
                if pid not in used and len(tracks[pid]) >= 40 and pm > 0.7 * mass1:  # a creature that LIVED (≥320 steps), not collision debris
                    near = [c for c in cur if td((py, px), (c[1], c[2])) < 2.5 * R]
                    events.append((L.t, py, px, 'merge' if near else 'death', len(tracks[pid]) * STRIDE, float(pm / mass1)))
        prev = cur
        if s % max(1, nstrobe // 5) == 0:
            print(f'  {code} strobe {s}/{nstrobe} alive={len(cur)} events={len(events)} mass={L.mass():.0f} [{time.time()-t_start:.0f}s]', flush=True)
    # paste onto the sheet
    Aup = np.stack([zoom(Aabs[..., c], UP, order=1) for c in range(3)], -1) if UP != 1 else Aabs
    Anow = zoom(L.A, UP, order=1) if UP != 1 else L.A
    Ab = zoom(Lb.A, UP, order=1) if UP != 1 else Lb.A
    n_up = Aup.shape[0]
    if win is None:
        y0 = x0 = 0
        fade = 1.0
    else:
        y0 = int(win[1] * H - n_up / 2); x0 = int(win[0] * W - n_up / 2)
        ly, lx = np.mgrid[:n_up, :n_up]
        rr = np.hypot(ly - n_up / 2, lx - n_up / 2) / (n_up / 2)
        fade = np.clip((1.0 - rr) / 0.25, 0, 1)[..., None]
    ys, ye = max(0, y0), min(H, y0 + n_up); xs_, xe = max(0, x0), min(W, x0 + n_up)
    sheet.A[ys:ye, xs_:xe] += (Aup * fade)[ys - y0:ye - y0, xs_ - x0:xe - x0]
    now_mask[ys:ye, xs_:xe] |= (Anow > 0.18)[ys - y0:ye - y0, xs_ - x0:xe - x0]
    birth_mask[ys:ye, xs_:xe] |= (Ab > 0.18)[ys - y0:ye - y0, xs_ - x0:xe - x0]
    for (t, cy, cx, kind, age, mfrac) in events:
        events_all.append((code, int(t), float(cy * UP + y0), float(cx * UP + x0), kind, int(age), round(mfrac, 3)))
    sp = []
    for tid, tr in tracks.items():
        if len(tr) > 6:
            (ta, ya, xa, _), (tb, yb, xb, _) = tr[0], tr[-1]
            sp.append(td((ya, xa), (yb, xb)) / (tb - ta))
    cert_layers.append(dict(code=code, name=a['name'], R=R, copies=ncopy, sim=N, seed_mass=mass1, heading=hd0,
                            alive_end=len(prev), deaths=sum(e[3] == 'death' for e in events),
                            merges=sum(e[3] == 'merge' for e in events), final_mass=L.mass(),
                            net_speed=float(np.mean(sp)) if sp else None, seconds=time.time() - t_l))
    print('  done', cert_layers[-1], flush=True)
    del Aabs, Aup, Anow, Ab, L, Lb

# ---- ink: the creatures now, faint birth outlines ----
d_now = np.where(now_mask, distance_transform_edt(now_mask), distance_transform_edt(~now_mask))
sheet.wash(0.95 * P.ink_from_distance(d_now, 1.1 * rs), 'ink')
d_b = np.where(birth_mask, distance_transform_edt(birth_mask), distance_transform_edt(~birth_mask))
sheet.wash(0.30 * P.ink_from_distance(d_b, 0.8 * rs), 'ink')
# coral rings at deaths and merges
ring = np.zeros((H, W), np.float32)
for (code, t, cy, cx, kind, age, mfrac) in events_all:
    if kind != 'death':
        continue
    R_ = [l for l in cert_layers if l['code'] == code][0]['R'] * UP
    r0 = 1.35 * R_
    dd = np.hypot(yy - cy, xx - cx)
    ring += np.exp(-((dd - r0) / (1.4 * rs)) ** 2)
sheet.wash(np.clip(ring, 0, 1) * 1.2, 'coral')
n_alive = sum(l['alive_end'] for l in cert_layers)
n_death = sum(l['deaths'] for l in cert_layers); n_merge = sum(l['merges'] for l in cert_layers)
title = 'What Counts as Alive'
sub = (f'{len(LAYERS)} Lenia species, each in its own world, {STEPS} steps: pigment is history (fainter when older), '
       f'ink is now, a coral ring where one ended — {n_alive} still going')
sheet.caption_strip(0.925, 0.985, 0.62)
items = [(title, 0.04 * W, 0.955 * H, int(0.030 * H), 'serif_bold', 'ls'),
         (sub, 0.04 * W, 0.978 * H, int(0.0135 * H), 'italic', 'ls')]
print('caption width', P.text_width(sub, int(0.0135 * H), 'italic') / W, flush=True)
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + f'_{FINAL}.png')
json.dump(dict(final=FINAL, steps=STEPS, stride=STRIDE, seed=SEED, layers=cert_layers,
               events=events_all, alive=n_alive, deaths=n_death, merges=n_merge, seconds=time.time() - t_start),
          open(OUT + f'_{FINAL}_cert.json', 'w'), indent=1)
print('ALL DONE', time.time() - t_start)
