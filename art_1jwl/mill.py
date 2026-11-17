"""mill.py — 'The Mill with Nine Floors'
Floor k (k = 1 under the roof), window n: the lamp is lit when the weights 1^k, 2^k, ..., n^k can NOT be
shared between two pans to within the forced parity (difference 0, or 1 when the total is odd).
Yellow = lit; red = lit because of the 2-adic lock (k = 4 and k = 8).  usage: mill.py SIZE out.png"""
import sys, json, numpy as np
from scipy import ndimage as ndi
from papercut import Box, rgb, mix, SERIF, SERIF_I

LOCK = {4: {18, 21, 26, 29}, 8: {43, 44, 51, 52, 59, 60, 67, 68}}
def main():
    S = int(sys.argv[1]); out = sys.argv[2]; u = S / 4096.0
    tab = json.load(open('math_balance/table.json'))
    K, NC = 9, 72
    B = Box(S, seed=21, light=(-0.55, -0.83))
    X0, X1, Y0, Y1 = 300 * u, 3796 * u, 280 * u, 3500 * u
    x, y = B.grid(); rng = np.random.default_rng(4)
    # sky
    sky = ['#1c2148', '#2b3162', '#3f4680', '#57558f', '#6f6299']
    B.lay(B.rect(X0 - 40 * u, Y0 - 40 * u, X1 + 40 * u, Y1 + 40 * u), rgb(sky[0]), 1, shadow=0, k=0)
    for i, by in enumerate([640, 900, 1110, 1290]):
        ph = rng.uniform(0, 6.28, 3)
        e = by * u + (30 * np.sin(x / (540 * u) + ph[0]) + 15 * np.sin(x / (190 * u) + ph[1]) + 6 * np.sin(x / (60 * u) + ph[2])) * u
        B.lay(np.clip(y - e + 0.5, 0, 1), rgb(sky[i + 1]), 2 + i, shadow=0.30, reach=7, soft=5, edge=0.6, k=i + 1)
    z = 7
    mx, my, mr = 980 * u, 640 * u, 150 * u
    moon = B.disc(mx, my, mr) * (1 - B.disc(mx + 62 * u, my - 34 * u, mr * 0.93))       # a crescent
    B.lay(moon, rgb('#f7edcf'), z, shadow=0.42, reach=8, soft=4, k=2)
    stars = np.zeros((S, S), np.float32)
    for _ in range(90):
        sx, sy = rng.uniform(X0 + 30 * u, X1 - 30 * u), rng.uniform(Y0 + 30 * u, 1000 * u); r = rng.choice([3.2, 4.2, 5.5, 7.5], p=[.45, .3, .18, .07]) * u
        if np.hypot(sx - mx, sy - my) < mr + 70 * u: continue
        stars = np.maximum(stars, np.clip(r - np.hypot(x - sx, y - sy) + 0.5, 0, 1))
    B.lay(stars, rgb('#f7edcf'), z, shadow=0.3, reach=3, soft=1.5, edge=0.5, k=2)
    # geometry of the mill
    bx0, bx1 = 372 * u, 3724 * u; pitch = (bx1 - bx0) / NC
    ytop, fh = 1170 * u, 150 * u; ybot = ytop + K * fh + 70 * u          # plinth 70
    ww, wh = 25 * u, 100 * u
    def lit(k, n):
        t = tab.get(str(k))
        if t is None: return 0
        if n not in t['known']: return -1          # undecided: no window is cut there
        f = {a for a, b in t['fails']}
        if n in f: return 2 if n in LOCK.get(k, ()) else 1
        return 0
    state = np.zeros((K, NC), int)
    for k in range(1, K + 1):
        for n in range(1, NC + 1): state[k - 1, n - 1] = lit(k, n)
    yel = [rgb('#f7cf62'), rgb('#f3bb4c'), rgb('#f9dc85')]; red = rgb('#e2452c'); drk = rgb('#141834')
    # backing sheet seen through the windows (and through the slits in the canal)
    back = np.empty((S, S, 3), np.float32); back[:] = drk
    wmask = np.zeros((S, S), np.float32)
    def wrect(k, n):
        xc = bx0 + (n - 0.5) * pitch; y0 = ytop + (k - 1) * fh + 26 * u
        return xc - ww / 2, y0, xc + ww / 2, y0 + wh
    cols = {}
    for k in range(1, K + 1):
        for n in range(1, NC + 1):
            xa, ya, xb, yb = wrect(k, n)
            wmask[int(ya):int(np.ceil(yb)), :] = np.maximum(wmask[int(ya):int(np.ceil(yb)), :], 0)  # no-op, keeps shape
            st = state[k - 1, n - 1]
            c = drk if st <= 0 else (red if st == 2 else yel[rng.integers(0, 3)])
            cols[(k, n)] = c
            back[int(ya) - 2:int(np.ceil(yb)) + 2, int(xa) - 2:int(np.ceil(xb)) + 2] = c
    wmask = np.zeros((S, S), np.float32)
    for k in range(1, K + 1):
        for n in range(1, NC + 1):
            xa, ya, xb, yb = wrect(k, n)
            if state[k - 1, n - 1] < 0: continue
            r = B.rect(xa, ya, xb, yb)
            sl = (slice(max(int(ya) - 2, 0), int(np.ceil(yb)) + 2), slice(max(int(xa) - 2, 0), int(np.ceil(xb)) + 2))
            wmask[sl] = np.maximum(wmask[sl], r[sl])
    # canal reflection: mirrored about the quay line, squeezed, broken into dashes
    yq = ybot + 46 * u                                   # water line
    refl_back = np.empty((S, S, 3), np.float32); refl_back[:] = rgb('#101430')
    slit = np.zeros((S, S), np.float32)
    sq = 0.52
    for k in range(1, K + 1):
        for n in range(1, NC + 1):
            st = state[k - 1, n - 1]
            if st <= 0: continue
            xa, ya, xb, yb = wrect(k, n)
            ra, rb = yq + (ybot - yb) * sq + 30 * u, yq + (ybot - ya) * sq + 30 * u
            refl_back[int(ra) - 3:int(np.ceil(rb)) + 3, int(xa) - 14:int(np.ceil(xb)) + 14] = mix(cols[(k, n)], rgb('#e9a04a') if st == 1 else rgb('#c93a2a'), 0.35)
            # two or three wobbling dashes per window
            nd = 3
            for j in range(nd):
                yy0 = ra + (rb - ra) * (j + 0.12) / nd; yy1 = yy0 + (rb - ra) * 0.50 / nd
                dx = 5.0 * u * np.sin(0.9 * j + 0.7 * n + 1.9 * k)
                r = B.rect(xa + dx - 2 * u, yy0, xb + dx + 2 * u, yy1)
                sl = (slice(max(int(yy0) - 2, 0), int(np.ceil(yy1)) + 2), slice(max(int(xa + dx) - 6, 0), int(np.ceil(xb + dx)) + 6))
                slit[sl] = np.maximum(slit[sl], r[sl])
    # lay: backing (windows), far bank silhouette, facade with holes, roof, chimneys, string courses, quay, water
    zb = z + 2
    B.lay(B.rect(bx0 - 30 * u, ytop - 10 * u, bx1 + 30 * u, ybot), back, zb, shadow=0, edge=0, tex=0.5, k=3)
    B.lay(B.rect(X0 - 40 * u, yq, X1 + 40 * u, Y1 + 40 * u), refl_back, zb, shadow=0, edge=0, tex=0.5, k=3)
    # distant rooftops left and right of the mill (one sheet, behind)
    hill = np.clip(y - (ytop + 170 * u + 60 * u * np.sin(x / (260 * u)) + 40 * u * np.sin(x / (97 * u) + 1)) + 0.5, 0, 1) * (y < yq)
    B.lay(hill * ((x < bx0 - 30 * u) | (x > bx1 + 30 * u)), rgb('#232955'), zb, shadow=0.3, k=4)
    fac = B.rect(bx0 - 34 * u, ytop, bx1 + 34 * u, ybot) * (1 - wmask)
    B.lay(fac, rgb('#3a416f'), zb + 3, shadow=0.72, reach=4.2, soft=2.2, edge=1.0, k=5, contact=0.35)
    # string courses and plinth (raised strips)
    crs = np.zeros((S, S), np.float32)
    for k in range(0, K + 1):
        crs = np.maximum(crs, B.rect(bx0 - 40 * u, ytop + k * fh - 5 * u, bx1 + 40 * u, ytop + k * fh + 7 * u))
    B.lay(crs, rgb('#4b5383'), zb + 4, shadow=0.4, reach=4, soft=2, k=6)
    B.lay(B.rect(bx0 - 46 * u, ybot - 58 * u, bx1 + 46 * u, ybot), rgb('#2b315c'), zb + 4, shadow=0.4, reach=4, soft=2, k=7)
    # roof: a long low sheet with saw-teeth (north lights), and chimneys
    roof = np.zeros((S, S), np.float32)
    tooth = 4 * pitch
    for i in range(18):
        xa = bx0 - 34 * u + i * tooth
        roof = np.maximum(roof, B.poly([(xa, ytop), (xa, ytop - 84 * u), (xa + tooth, ytop)], ss=1))
    B.lay(roof * (x < bx1 + 34 * u), rgb('#2b315c'), zb + 2.5, shadow=0.4, reach=5, soft=2.5, k=8)
    for cx, ch in ((0.13, 520), (0.87, 400)):
        xc = bx0 + cx * (bx1 - bx0)
        B.lay(B.poly([(xc - 30 * u, ytop), (xc - 20 * u, ytop - ch * u), (xc + 20 * u, ytop - ch * u), (xc + 30 * u, ytop)], ss=2), rgb('#30375f'), zb + 2, shadow=0.4, reach=6, soft=3, k=9)
    # quay and water
    B.lay(B.rect(X0 - 40 * u, ybot, X1 + 40 * u, yq), rgb('#1d2247'), zb + 5, shadow=0.45, reach=4, soft=2, k=10)
    wcol = np.empty((S, S, 3), np.float32); t = np.clip((y - yq) / (Y1 - yq), 0, 1)[..., None]
    wcol[:] = mix(rgb('#2a3566'), rgb('#161b3c'), 0) ; wcol = rgb('#2c376a') * (1 - t) + rgb('#141a3a') * t
    rip = (np.sin((y - yq) / (15 * u) * 6.283 + 1.6 * np.sin(x / (170 * u))) > 0.95)
    wcol = wcol + (1 - wcol) * (0.07 * rip)[..., None]
    B.lay(B.rect(X0 - 40 * u, yq, X1 + 40 * u, Y1 + 40 * u) * (1 - slit), wcol, zb + 3, shadow=0.6, reach=3.0, soft=1.6, edge=0.8, k=11)
    # numerals on the plinth: every tenth window
    items = [(bx0 + (n - 0.5) * pitch, ybot - 29 * u, str(n), SERIF, 34 * u, 'mm') for n in range(10, NC + 1, 10)] + [(bx0 + 0.5 * pitch, ybot - 29 * u, "1", SERIF, 34 * u, 'mm')]
    B.ink(B.text_mask(items), '#c9c4d8', 0.9)
    B.mat(X0, Y0, X1, Y1)
    fl = [(X0 - 26 * u, ytop + (k - 0.5) * fh + 6 * u, "k = %d" % k, SERIF_I, 40 * u, 'rm') for k in range(1, K + 1)]
    B.ink(B.text_mask(fl), '#6a655c', 0.85)
    cx = (X0 + X1) / 2
    cap = [(cx, 3622 * u, "The Mill with Nine Floors", SERIF, 104 * u, 'ma'),
           (cx, 3766 * u, "Floor k, window n: the lamp burns when the weights 1ᵏ, 2ᵏ, …, nᵏ cannot be shared out evenly between two pans.", SERIF_I, 50 * u, 'ma'),
           (cx, 3834 * u, "Yellow lamps go out when there are enough weights. The red ones burn on for a reason of arithmetic: floors 4 and 8 are locked modulo 32 and 64.", SERIF_I, 50 * u, 'ma'),
           (cx, 3926 * u, "last lamp on floors 2 … 8:  5, 11, 29, 27, 35, 38, 68   ·   every window decided exactly; floor 9 is undecided past window 63, so the wall is blank there", SERIF, 40 * u, 'ma')]
    B.ink(B.text_mask(cap), '#4a4640', 0.88)
    B.save(out)
if __name__ == "__main__":
    main()
