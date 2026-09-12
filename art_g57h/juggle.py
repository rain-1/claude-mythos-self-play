"""juggle.py — HOW TO BE A GOOD CLOWN: a specimen sheet of siteswaps drawn as strobe density.

A siteswap a_0 a_1 ... a_{n-1} is valid iff i + a_i (mod n) is a permutation of 0..n-1;
the number of balls is the mean of the throws (the theorem every juggler knows).
Each cell: two hands (ink cups) at x = ±1, every ball drawn at equal TIME steps over one
full cycle, so beads crowd at the apex (hang time) and thin near the hands; pigment = throw
height; one coral bead = the clown's nose, at the apex height of a 3-throw (eye level).

usage: python3 juggle.py FINAL out_prefix
"""
import sys, json, itertools
import numpy as np
from scipy.ndimage import gaussian_filter
import pastel as P

FINAL = int(sys.argv[1]); OUT = sys.argv[2]
SS = 2
W = H = FINAL * SS
rs = FINAL / 1024.0 * SS


def valid(seq):
    n = len(seq)
    return sorted(((i + a) % n) for i, a in enumerate(seq)) == list(range(n))


def canonical(seq):
    rots = [tuple(seq[i:] + seq[:i]) for i in range(len(seq))]
    return max(rots)


def is_prime(seq):
    """prime siteswap: the state walk never repeats a state inside one period"""
    n = len(seq); h = max(seq)
    state = 0
    # build the ground state by running the pattern once from an empty state? Use standard: find
    # the state by simulating: occupied future slots as a bitmask
    # start: simulate many periods to reach the periodic orbit
    occ = set()
    # derive the state at time 0 of the periodic orbit: slots i + a_i for i<0 that land >= 0
    for i in range(-n * (h + 1), 0):
        a = seq[i % n]
        if i + a >= 0:
            occ.add(i + a)
    states = []
    for t in range(n):
        st = frozenset(x - t for x in occ if x >= t)
        if st in states:
            return False
        states.append(st)
        a = seq[t]
        if a > 0:
            occ.add(t + a)
    return True


def enumerate_siteswaps(balls, max_period, max_throw):
    out = set()
    for n in range(1, max_period + 1):
        for seq in itertools.product(range(max_throw + 1), repeat=n):
            if sum(seq) != balls * n:
                continue
            if not valid(list(seq)):
                continue
            c = canonical(list(seq))
            # reject sequences that are repetitions of a shorter period
            rep = False
            for k in range(1, n):
                if n % k == 0 and c == c[:k] * (n // k):
                    rep = True
            if rep:
                continue
            out.add(c)
    return sorted(out, key=lambda s: (len(s), max(s), s))


# ---- kinematics ----
DWELL = 0.55          # fraction of a beat the ball rests in the hand
XCATCH, XTHROW = 1.05, 0.62   # hand positions: catch outside, throw inside (right hand mirrored)
G = 1.0               # vertical scale: apex height = G/8 * flight^2


def ball_positions(seq, times):
    """positions of every ball at each time; returns list of arrays (x, y, throw) per ball"""
    n = len(seq)
    # ball identities by following throws: at beat t the hand throws one ball with throw seq[t]
    # assign ball ids by simulation over a long horizon
    horizon = 4 * n * (max(seq) + 1)
    inflight = {}   # landing beat -> ball id
    ball_at_beat = {}
    nxt = 0
    for t in range(-horizon, horizon):
        a = seq[t % n]
        if a == 0:
            continue
        if t in inflight:
            b = inflight.pop(t)
        else:
            b = nxt; nxt += 1
        ball_at_beat[t] = (b, a)
        inflight[t + a] = b
    # relabel balls seen in [0, horizon) compactly
    ids = {}
    flights = []  # (ball, t_throw, throw)
    for t in range(-n * (max(seq) + 2), 2 * n * (max(seq) + 2)):
        if t in ball_at_beat:
            b, a = ball_at_beat[t]
            if b not in ids:
                ids[b] = len(ids)
            flights.append((ids[b], t, a))
    nb = len(ids)
    res = []
    for b in range(nb):
        fl = sorted([(t, a) for (bb, t, a) in flights if bb == b])
        xs = np.full(len(times), np.nan); ys = np.full(len(times), np.nan); th = np.zeros(len(times), int)
        for (t, a) in fl:
            hand = 1 if t % 2 else -1          # -1 = left hand throws at even beats
            hand_c = hand if a % 2 == 0 else -hand
            t_throw = t + DWELL                # ball leaves the hand
            t_catch = t + a                    # lands at the beat it is next thrown (then dwells)
            fl_time = max(t_catch - t_throw, 0.05)
            # flight
            m = (times >= t_throw) & (times < t_catch)
            if m.any():
                s = (times[m] - t_throw) / fl_time
                x0, x1 = hand * XTHROW, hand_c * XCATCH
                xs[m] = x0 + (x1 - x0) * s
                ys[m] = G / 8 * fl_time ** 2 * 4 * s * (1 - s)
                th[m] = a
            # dwell in the catching hand: slide from catch point to throw point
            m2 = (times >= t_catch) & (times < t_catch + DWELL)
            if m2.any():
                s = (times[m2] - t_catch) / DWELL
                xs[m2] = hand_c * (XCATCH + (XTHROW - XCATCH) * s)
                ys[m2] = -0.03 * np.sin(np.pi * s)
                th[m2] = 0
        res.append((xs, ys, th))
    return res


# ---- sheet ----
seqs = enumerate_siteswaps(3, 5, 7)
prime = [s for s in seqs if is_prime(list(s))]
print('3-ball siteswaps period<=5 throws<=7:', len(seqs), 'prime:', len(prime))
counts = {n: sum(1 for s in seqs if len(s) == n) for n in range(1, 6)}
print('by period', counts)
# choose 36: all with period <= 3, then period 4 and 5 by max throw
chosen = [s for s in seqs if len(s) <= 3]
rest = [s for s in seqs if len(s) > 3]
rest.sort(key=lambda s: (max(s), len(s), s))
chosen += rest[:36 - len(chosen)]
chosen.sort(key=lambda s: (max(s), len(s), s))
print('chosen', len(chosen), [''.join(map(str, s)) for s in chosen])

sheet = P.Sheet(W, H, seed=11)
COLS = ROWS = 6
mx, my = 0.06 * W, 0.06 * H
cw = (W - 2 * mx) / COLS; ch = (H - 2 * my - 0.06 * H) / ROWS
maxthrow = max(max(s) for s in chosen)
apex_max = G / 8 * (maxthrow - DWELL) ** 2
ux = cw * 0.36 / XCATCH            # px per unit x
uy = (ch * 0.78) / apex_max        # px per unit y (common across the sheet)
TH_PIG = {1: 'cornflower', 2: 'aqua', 3: 'mint', 4: 'pistachio', 5: 'lemon', 6: 'apricot', 7: 'blush', 8: 'orchid', 9: 'lavender'}
bead_lists = {k: [] for k in TH_PIG}
ink = np.zeros((H, W), np.float32)
nose = np.zeros((H, W), np.float32)
from PIL import Image, ImageDraw
imI = Image.new('F', (W, H), 0.0); drI = ImageDraw.Draw(imI)
labels = []
apex3 = G / 8 * (3 - DWELL) ** 2
for idx, s in enumerate(chosen):
    r, c = divmod(idx, COLS)
    ox = mx + (c + 0.5) * cw
    oy = my + (r + 1) * ch - 0.14 * ch
    n = len(s)
    times = np.arange(0, 2 * n, 0.06)   # two periods so every ball completes its cycle
    balls = ball_positions(list(s), times)
    for (xs, ys, th) in balls:
        m = ~np.isnan(xs) & (th > 0)
        px = ox + xs[m] * ux; py = oy - ys[m] * uy
        for k in np.unique(th[m]):
            mk = th[m] == k
            bead_lists[int(k)].append(np.stack([px[mk], py[mk]], 1))
    # hands: two ink cups
    for hand in (-1, 1):
        hx = ox + hand * (XCATCH + XTHROW) / 2 * ux; hy = oy + 0.02 * uy
        wdt = 0.26 * ux
        drI.arc([hx - wdt, hy - wdt * 0.9, hx + wdt, hy + wdt * 0.9], 15, 165, fill=1.0, width=int(max(1, 1.4 * rs)))
    # nose
    nx, ny = ox, oy - apex3 * uy
    rr = 4.2 * rs
    drN = ImageDraw.Draw(imI)
    nose_im = Image.new('F', (W, H), 0.0)  # placeholder (drawn below in bulk)
    labels.append((''.join(map(str, s)), ox, oy + 0.075 * ch, nx, ny, rr))
ink = np.asarray(imI, np.float32)
# nose beads
nI = Image.new('F', (W, H), 0.0); dN = ImageDraw.Draw(nI)
for (_, _, _, nx, ny, rr) in labels:
    dN.ellipse([nx - rr, ny - rr, nx + rr, ny + rr], fill=1.0)
nose = gaussian_filter(np.asarray(nI, np.float32), 0.6 * rs)

# washes
for k, pig in TH_PIG.items():
    if not bead_lists[k]:
        continue
    pts = np.concatenate(bead_lists[k], 0)
    rb = 1.9 * rs
    d = P.discs_density(W, H, pts[:, 0], pts[:, 1], np.full(len(pts), rb), np.full(len(pts), 1.0), sigma=0.5 * rs)
    d = 1.0 - np.exp(-d)          # overlapping beads pool toward a knee
    sheet.wash(2.1 * d, pig, granulate=0.12, seed=20 + k)
sheet.wash(1.1 * gaussian_filter(ink, 0.5 * rs), 'ink')
sheet.wash(1.8 * nose, 'coral')
# labels
items = []
for (txt, lx, ly, *_ ) in labels:
    items.append((txt, lx, ly, int(0.017 * H / SS * SS), 'serif_bold', 'mm'))
title = 'How to Be a Good Clown'
sub = (f'36 of the {len(seqs)} three-ball siteswaps with period ≤ 5 and throws ≤ 7, the balls drawn at equal time steps: '
       'beads crowd where a ball hangs; the nose sits where a 3 peaks')
sheet.caption_strip(0.925, 0.985, 0.62)
items += [(title, 0.04 * W, 0.955 * H, int(0.030 * H), 'serif_bold', 'ls'),
          (sub, 0.04 * W, 0.978 * H, int(0.0135 * H), 'italic', 'ls')]
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + f'_{FINAL}.png')
json.dump(dict(total=len(seqs), prime=len(prime), by_period=counts,
               chosen=[''.join(map(str, s)) for s in chosen],
               all=[''.join(map(str, s)) for s in seqs], dwell=DWELL),
          open(OUT + f'_{FINAL}_cert.json', 'w'), indent=1)
