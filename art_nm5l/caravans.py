"""caravans.py — 'Seven Caravans and the Camel They Borrowed'
All seven wills (n; 1/a, 1/b, 1/c) with a<b<c dividing n+1 and 1/a+1/b+1/c = n/(n+1), one caravan
per dune, nearest = smallest herd.  Each caravan walks in three groups (the three shares) followed
by one red camel, the lent one.  One paper camel per camel.
usage: caravans.py SIZE out.png"""
import sys, numpy as np
from scipy import ndimage as ndi
from papercut import Box, rgb, mix, SERIF, SERIF_I
from camel import camel

WILLS = [(7, (4, 2, 1)), (11, (6, 4, 1)), (11, (6, 3, 2)), (17, (9, 6, 2)), (19, (10, 5, 4)), (23, (12, 8, 3)), (41, (21, 14, 6))]
for n, sh in WILLS: assert sum(sh) == n and all((n + 1) % s == 0 for s in sh)

def main():
    S = int(sys.argv[1]); out = sys.argv[2]; u = S / 4096.0
    B = Box(S, seed=7, light=(-0.55, -0.83))
    X0, X1, Y0, Y1 = 300 * u, 3796 * u, 280 * u, 3500 * u
    x, y = B.grid(); rng = np.random.default_rng(21)
    # ---------------- sky: night over the desert, a cold glow low down ----------------------
    sky = ['#12173a', '#1a2452', '#243a6c', '#3a5f88', '#7fa3a6', '#e6dcb6']
    B.lay(B.rect(X0 - 40 * u, Y0 - 40 * u, X1 + 40 * u, Y1 + 40 * u), rgb(sky[0]), 1, shadow=0, k=0)
    for i, by in enumerate([640, 950, 1170, 1320, 1420]):
        ph = rng.uniform(0, 6.28, 4)
        edge = by * u + (30 * np.sin(x / (700 * u) + ph[0]) + 16 * np.sin(x / (260 * u) + ph[1]) + 7 * np.sin(x / (83 * u) + ph[2]) + 3 * np.sin(x / (21 * u) + ph[3])) * u * (1 - 0.13 * i)
        B.lay(np.clip(y - edge + 0.5, 0, 1), rgb(sky[i + 1]), 2 + i, shadow=0.30, reach=7, soft=5, edge=0.7, k=i + 1)
    zs = 8
    # crescent moon: a cream disc with a bite cut out
    mx, my, mr = 1010 * u, 760 * u, 150 * u
    moon = B.disc(mx, my, mr) * (1 - B.disc(mx + 78 * u, my - 46 * u, mr * 0.93))
    B.lay(moon, rgb('#f7edcf'), zs + 1, shadow=0.45, reach=8, soft=4, edge=0.9, k=2)
    srng = np.random.default_rng(5); stars = np.zeros((S, S), np.float32)
    for _ in range(120):
        sx, sy = srng.uniform(X0 + 30 * u, X1 - 30 * u), srng.uniform(Y0 + 30 * u, 1120 * u)
        r = srng.choice([3.0, 4.0, 5.4, 7.6], p=[.45, .3, .18, .07]) * u
        if np.hypot(sx - mx, sy - my) < mr + 70 * u: continue
        if srng.uniform() < (sy - Y0) / (1300 * u): continue
        stars = np.maximum(stars, np.clip(r - np.hypot(x - sx, y - sy) + 0.5, 0, 1))
    B.lay(stars, rgb('#f7edcf'), zs + 1, shadow=0.3, reach=3, soft=1.5, edge=0.5, k=2)
    # ---------------- dunes, far to near ----------------------------------------------------
    base = [3110, 2740, 2420, 2140, 1900, 1695, 1545]            # crest level of dune i (0 = nearest)
    dune = ['#232652', '#3d3a72', '#62508a', '#8c6990', '#b78a92', '#d9b199', '#ecd2ae']
    camc = ['#0d1026', '#171a3c', '#2a2a5c', '#433b74', '#5f4a80', '#7c5a84', '#96697f']
    red = ['#e0452c', '#de472f', '#dc4a33', '#d94e38', '#d6533e', '#d25944', '#cd604c']
    xs = np.arange(S, dtype=np.float32)
    def crest(i):
        r = np.random.default_rng(300 + i); ph = r.uniform(0, 6.28, 5)
        k = 1.0 / (1 + 0.42 * i)                                   # farther dunes are lower and tighter
        L = (1500 * k ** 0.5) * u
        t = xs / L + 2.1 + 0.55 * i + 0.3 * ph[0]
        # dune profile: long windward slope, short slip face (a skewed sine), plus slow swell
        prof = np.sin(t + 0.45 * np.sin(t + 0.6)) * 0.5 + 0.5
        yv = base[i] * u - (265 * k * prof + 60 * k * np.sin(xs / (2900 * u) + ph[1]) + 10 * k * np.sin(xs / (310 * u) + ph[2])) * u
        return yv
    z = zs + 3
    for i in range(6, -1, -1):
        n, shares = WILLS[i]; cy = crest(i)
        # --- the caravan: groups separated by a gap of 0.8 camel, the lent camel last
        gap = 0.85; slots = n + 1 + 3 * gap; margin = (150 + 40 * i) * u
        cw = (X1 - X0 - 2 * margin) / slots                         # room per camel
        w = cw * (1.06 if n > 20 else 1.0)                          # camels overlap a little in long files
        direction = 1 if i % 2 == 0 else -1
        m_c = np.zeros((S, S), np.float32); m_r = np.zeros((S, S), np.float32)
        pos = 0.0; r2 = np.random.default_rng(900 + i); idx = 0
        order = list(shares) + [1]
        for g, cnt in enumerate(order):
            for j in range(cnt):
                xc = X0 + margin + (pos + 0.5) * cw
                if direction < 0: xc = X0 + X1 - xc
                cm = camel(w, phase=(0.23 * idx + r2.uniform(0, 0.08)) % 1.0)
                if direction > 0: cm = cm[:, ::-1] if False else cm
                # caravan walks towards the head of the file: head of file is group 0
                if direction > 0: cm = cm[:, ::-1]                 # file starts at the left, so walk left
                h, ww = cm.shape
                ix = int(round(xc - ww / 2)); foot = float(cy[int(np.clip(xc, 0, S - 1))]) + 0.07 * w
                iy = int(round(foot - h))
                tgt = m_r if g == 3 else m_c
                ya, yb, xa, xb = max(iy, 0), min(iy + h, S), max(ix, 0), min(ix + ww, S)
                if yb > ya and xb > xa:
                    tgt[ya:yb, xa:xb] = np.maximum(tgt[ya:yb, xa:xb], cm[ya - iy:yb - iy, xa - ix:xb - ix])
                pos += 1; idx += 1
            pos += gap
        B.lay(m_c, rgb(camc[i]), z, shadow=0.42, reach=5 + 0.5 * (6 - i), soft=2.5, edge=0.8, k=i, ao=0.10)
        B.lay(m_r, rgb(red[i]), z + 0.2, shadow=0.42, reach=5 + 0.5 * (6 - i), soft=2.5, edge=0.8, k=i + 1, ao=0.10)
        # --- the dune itself, a nearer sheet
        dm = np.clip(y - cy[None, :] + 0.5, 0, 1)
        col = np.broadcast_to(rgb(dune[i]), B.img.shape).copy()
        # wind ripples: thin paler slivers that follow the crest
        dep = (y - cy[None, :]) / u
        rip = (np.sin(dep / (26.0 / (1 + 0.25 * i)) + 2.2 * np.sin(x / (420 * u) + i)) > 0.965) & (dep > 30)
        col = col + (1 - col) * (0.07 * rip)[..., None]
        B.lay(dm, col, z + 1, shadow=0.50, reach=8, soft=3.4, edge=1.0, k=i + 2, ao=0.24, ao_soft=18.0)
        z += 2
    # foreground: one dark dune sweeping up to the right, nobody on it
    fy = (3480 - 250 * np.clip((xs / u - 1500) / 2300, 0, 1) ** 1.6 + 26 * np.sin(xs / (520 * u) + 1.0)) * u
    B.lay(np.clip(y - fy[None, :] + 0.5, 0, 1), rgb('#14183a'), z + 1, shadow=0.5, reach=8, soft=3.4, edge=1.0, k=3, ao=0.24, ao_soft=18.0)
    # ---------------- mat and captions ------------------------------------------------------
    B.mat(X0, Y0, X1, Y1)
    cx = (X0 + X1) / 2
    cap = [(cx, 3618 * u, "Seven Caravans and the Camel They Borrowed", SERIF, 104 * u, 'ma'),
           (cx, 3762 * u, "A father leaves n camels to three sons in unequal shares 1/a, 1/b, 1/c that will not divide n. Lend them one camel: every share", SERIF_I, 50 * u, 'ma'),
           (cx, 3830 * u, "comes out whole and one camel is left to give back. Only seven wills allow it. Each walks here in its three shares, the red camel last.", SERIF_I, 50 * u, 'ma'),
           (cx, 3922 * u, "near to far:  7 = 4+2+1  ·  11 = 6+4+1  ·  11 = 6+3+2  ·  17 = 9+6+2  ·  19 = 10+5+4  ·  23 = 12+8+3  ·  41 = 21+14+6   ·   cut paper, one camel per camel", SERIF, 40 * u, 'ma')]
    B.ink(B.text_mask(cap), '#4a4640', 0.88)
    B.save(out)

if __name__ == "__main__":
    main()
