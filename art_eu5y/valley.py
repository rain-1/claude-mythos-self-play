"""valley.py — 'A Lopsided Valley Under an Even Sky'   (cut paper; Fable 5.2, day 9)
Two terraced slopes face each other.  Each is a lattice stair of 23 steps (1 = up, 0 = across):
   left  w  = 11011100110110111010101      right w' = 11001101110110101011101
They are not mirror images, yet the multiset of (across, up) between pairs of corners -- the
'tossprint' of MO 516996 -- is the same for both: 276 pairs each.  The stars are those pairs, the
left wing from the left slope, the right wing from the right slope, disc area = multiplicity.
Red lanterns hang at the six flight starts (the points of the factor that is flipped).
usage: valley.py SIZE out.png"""
import sys, numpy as np
from collections import Counter
from papercut import Box, rgb, mix, SERIF, SERIF_I

WL = "11011100110110111010101"
WR = "11001101110110101011101"

def points(w):
    p = [(0, 0)]
    for c in w: p.append((p[-1][0] + (c == '0'), p[-1][1] + (c == '1')))
    return p
def bag(w):
    p = points(w)
    return Counter((p[j][0] - p[i][0], p[j][1] - p[i][1]) for i in range(len(p)) for j in range(i + 1, len(p)))
BL, BR = bag(WL), bag(WR)
assert BL == BR and WL != WR and WL != WR[::-1] and sum(BL.values()) == 276

def main():
    S = int(sys.argv[1]); out = sys.argv[2]; u = S / 4096.0
    B = Box(S, seed=9, light=(-0.55, -0.83))
    X0, X1, Y0, Y1 = 300 * u, 3796 * u, 280 * u, 3500 * u
    x, y = B.grid(); rng = np.random.default_rng(4)
    xs = np.arange(S, dtype=np.float32)
    # ---------------- sky ---------------------------------------------------------------
    sky = ['#0f1433', '#161d48', '#1f2f62', '#2f4f80', '#5d8a9c', '#b9c9b0', '#efe2bb']
    B.lay(B.rect(X0 - 40 * u, Y0 - 40 * u, X1 + 40 * u, Y1 + 40 * u), rgb(sky[0]), 1, shadow=0, k=0)
    for i, by in enumerate([1330, 1900, 2260, 2520, 2700, 2830]):
        ph = rng.uniform(0, 6.28, 4)
        edge = by * u + (34 * np.sin(x / (700 * u) + ph[0]) + 16 * np.sin(x / (260 * u) + ph[1]) + 7 * np.sin(x / (83 * u) + ph[2]) + 3 * np.sin(x / (21 * u) + ph[3])) * u * (1 - 0.12 * i)
        B.lay(np.clip(y - edge + 0.5, 0, 1), rgb(sky[i + 1]), 2 + i, shadow=0.30, reach=7, soft=5, edge=0.7, k=i + 1)
    zs = 9
    # moon
    mx, my, mr = 800 * u, 760 * u, 158 * u
    B.lay(B.disc(mx, my, mr), rgb('#f7edcf'), zs + 1, shadow=0.45, reach=8, soft=4, edge=0.9, k=2)
    # two torn clouds, one drifting across the lower limb of the moon
    for (cx0, cy0, L, Hh, col, sd) in [(1010, 905, 520, 34, '#27356b', 1), (3050, 640, 430, 26, '#1d2757', 2), (3300, 1130, 360, 22, '#2b3d74', 3)]:
        r4 = np.random.default_rng(40 + sd); ph = r4.uniform(0, 6.28, 6)
        tx = (x - cx0 * u) / (L * u)
        thick = Hh * u * np.clip(1 - tx ** 2, 0, 1) ** 0.6 * (1 + 0.35 * np.sin(x / (95 * u) + ph[0]) + 0.2 * np.sin(x / (37 * u) + ph[1]))
        mid = cy0 * u + 9 * u * np.sin(x / (210 * u) + ph[2])
        cl = np.clip(thick - np.abs(y - mid) * np.where(y > mid, 2.2, 1.0) + 0.5, 0, 1) * (np.abs(tx) < 1)
        B.lay(cl, rgb(col), zs + 2, shadow=0.38, reach=6, soft=3, edge=0.8, k=sd)
    # ---------------- the stars: one disc per (across, up), area = how many pairs --------
    ox, oy, sx, sy = 2048 * u, 1500 * u, 88 * u, 59 * u
    stars = np.zeros((S, S), np.float32)
    def star(cx, cy, r):
        nonlocal stars
        a, b = int(max(cy - r - 2, 0)), int(min(cy + r + 3, S)); c, d = int(max(cx - r - 2, 0)), int(min(cx + r + 3, S))
        stars[a:b, c:d] = np.maximum(stars[a:b, c:d], np.clip(r - np.hypot(x[a:b, c:d] - cx, y[a:b, c:d] - cy) + 0.5, 0, 1))
    for (dz, do), m in BL.items():
        star(ox - dz * sx, oy - do * sy, 6.4 * u * np.sqrt(m))
    for (dz, do), m in BR.items():
        star(ox + dz * sx, oy - do * sy, 6.4 * u * np.sqrt(m))
    B.lay(stars, rgb('#f7edcf'), zs + 1, shadow=0.34, reach=3.2, soft=1.6, edge=0.5, k=2)
    # ---------------- far ridges seen through the valley ----------------------------------
    for i, (by, col) in enumerate([(2560, '#5a6f96'), (2760, '#3c4a7c'), (2930, '#28305f')]):
        ph = np.random.default_rng(60 + i).uniform(0, 6.28, 4)
        cy = by * u - (70 * np.sin(xs / (560 * u) + ph[0]) + 34 * np.sin(xs / (230 * u) + ph[1]) + 12 * np.sin(xs / (90 * u) + ph[2])) * u
        B.lay(np.clip(y - cy[None, :] + 0.5, 0, 1), rgb(col), zs + 3 + i, shadow=0.42, reach=7, soft=3.4, edge=0.9, k=i, ao=0.2)
    # ---------------- the two slopes, one sheet per terrace level, top level first ---------
    ux, uy, yb, half = 140 * u, 100 * u, 3150 * u, 132 * u
    xc = 2048 * u
    def edges(w):      # e[j] = zeros before the (j+1)-th one  -> where level j's riser stands
        e = []; z = 0
        for c in w:
            if c == '1': e.append(z)
            else: z += 1
        return e
    eL, eR = edges(WL), edges(WR); nlev = len(eL); assert nlev == len(eR) == 15
    topL, botL = rgb('#75659b'), rgb('#141839')
    topR, botR = rgb('#c79aa6'), rgb('#2b2d62')
    lipc = rgb('#dfe6e6')
    z = zs + 8
    for j in range(nlev - 1, -1, -1):
        t = (j / (nlev - 1)) ** 0.85
        ytop = yb - (j + 1) * uy
        xl = xc - half - eL[j] * ux; xr = xc + half + eR[j] * ux
        mL = B.rect(0, ytop, xl, yb + 4 * u); mR = B.rect(xr, ytop, S, yb + 4 * u)
        col = np.empty((S, S, 3), np.float32)
        cL, cR = mix(botL, topL, t), mix(botR, topR, t)
        col[:] = cL; col[:, int(xc):] = cR
        # the paddy lip: a pale strip where the terrace top is open to the sky
        nl = xc - half - (eL[j + 1] if j + 1 < nlev else 99) * ux; nr = xc + half + (eR[j + 1] if j + 1 < nlev else 99) * ux
        lip = B.rect(nl - 2 * u, ytop, xl, ytop + 11 * u) * 0.50 + B.rect(xr, ytop, nr + 2 * u, ytop + 11 * u) * 0.72
        col = col + (lipc - col) * lip[..., None]
        B.lay(np.maximum(mL, mR), col, z, shadow=0.5, reach=6, soft=3.0, edge=1.0, k=j, ao=0.26, ao_soft=16.0)
        z += 1
    # pines on the two plateaus and one lit house
    top = yb - nlev * uy
    pines = np.zeros((S, S), np.float32); r5 = np.random.default_rng(77)
    for (px0, hh) in [(380, 150), (455, 200), (545, 130), (3420, 170), (3690, 215), (3745, 150)]:
        px = px0 * u
        for t0, t1, wd in [(1.0, 0.52, 0.30), (0.72, 0.26, 0.24), (0.46, 0.0, 0.17)]:
            pines = np.maximum(pines, B.poly([(px - wd * hh * u, top - (1 - t0) * hh * u + 2 * u), (px + wd * hh * u, top - (1 - t0) * hh * u + 2 * u), (px, top - (1 - t1) * hh * u - 0.2 * hh * u)]))
        pines = np.maximum(pines, B.rect(px - 5 * u, top - 14 * u, px + 5 * u, top + 1 * u))
    B.lay(pines, rgb('#141938'), z + 1, shadow=0.4, reach=4, soft=2, edge=0.7, k=2)
    hx, hw, hh = 3530 * u, 74 * u, 58 * u
    house = np.maximum(B.rect(hx - hw, top - hh, hx + hw, top + 1 * u), B.poly([(hx - hw - 16 * u, top - hh + 1 * u), (hx + hw + 16 * u, top - hh + 1 * u), (hx, top - hh - 50 * u)]))
    B.lay(house, rgb('#1b1f47'), z + 1.5, shadow=0.4, reach=4, soft=2, edge=0.8, k=4)
    B.lay(B.rect(hx - 44 * u, top - 40 * u, hx - 16 * u, top - 12 * u), rgb('#f2c765'), z + 1.6, shadow=0.0, edge=0.3, k=1)
    # ---------------- lanterns at the flight starts (points 0, 4, 8, ..., 20) -------------
    posts = np.zeros((S, S), np.float32); lamps = np.zeros((S, S), np.float32)
    for w, sgn in ((WL, -1), (WR, 1)):
        P = points(w)
        for k in range(0, 24, 4):
            pz, po = P[k]
            px = xc + sgn * (half + pz * ux) + sgn * 20 * u; py = yb - po * uy
            if k == 0: px = xc + sgn * (half - 34 * u)
            posts = np.maximum(posts, B.rect(px - 2.6 * u, py - 64 * u, px + 2.6 * u, py + 1 * u))
            lamps = np.maximum(lamps, B.disc(px, py - 74 * u, 21 * u))
    B.lay(posts, rgb('#0d1026'), z + 1, shadow=0.3, reach=3, soft=1.5, edge=0.4, k=1)
    B.lay(lamps, rgb('#e2452b'), z + 2, shadow=0.45, reach=4.5, soft=2.2, edge=0.9, k=3)
    # ---------------- the river in front -------------------------------------------------
    fy = (yb + 6 * u) + 0 * xs
    water = np.broadcast_to(rgb('#0e1335'), B.img.shape).copy()
    B.lay(np.clip(y - fy[None, :] + 0.5, 0, 1), water, z + 4, shadow=0.5, reach=7, soft=3.2, edge=0.9, k=3, ao=0.2)
    gl = np.zeros((S, S), np.float32); r3 = np.random.default_rng(12)
    for i in range(9):                     # the moon on the water: torn cream slivers under the moon
        gy = yb + (52 + 31 * i) * u; wd = (150 - 9 * i + r3.uniform(-22, 22)) * u; gx = mx + r3.uniform(-18, 18) * u
        th = (9.5 - 0.45 * i) * u
        gl = np.maximum(gl, np.clip(1 - ((x - gx) / wd) ** 2, 0, 1) ** 0.5 * np.clip(th - np.abs(y - gy) * (1 + 1.6 * ((x - gx) / wd) ** 2) + 0.5, 0, 1))
    B.lay(np.clip(gl, 0, 1), rgb('#efe6c8'), z + 5, shadow=0.25, reach=2.5, soft=1.2, edge=0.5, k=2)
    # the lanterns on the water: short red slivers
    rl = np.zeros((S, S), np.float32)
    for sgn in (-1, 1):
        gx = xc + sgn * (half - 34 * u)
        for i in range(3):
            gy = yb + (44 + 30 * i) * u; wd = (30 - 6 * i) * u
            rl = np.maximum(rl, np.clip(1 - ((x - gx) / wd) ** 2, 0, 1) ** 0.5 * np.clip(5.5 * u - np.abs(y - gy) + 0.5, 0, 1))
    B.lay(np.clip(rl, 0, 1), rgb('#c9412f'), z + 5, shadow=0.2, reach=2.5, soft=1.2, edge=0.4, k=2)
    # ---------------- mat and captions ---------------------------------------------------
    B.mat(X0, Y0, X1, Y1)
    cx = (X0 + X1) / 2
    cap = [(cx, 3618 * u, "A Lopsided Valley Under an Even Sky", SERIF, 104 * u, 'ma'),
           (cx, 3762 * u, "On one slope, sight from a terrace corner to a higher one; write down how far across and how far up, and drop the slip in a bag.", SERIF_I, 50 * u, 'ma'),
           (cx, 3830 * u, "Each slope fills its bag with 276 slips. The slopes are cut differently, and the two bags are the same: the left wing of stars is one bag, the right wing the other.", SERIF_I, 50 * u, 'ma'),
           (cx, 3922 * u, "up = 1, across = 0:   left 11011100110110111010101  ·  right 11001101110110101011101   ·   a star's area counts its slips   ·   lanterns start the six flights   ·   cut paper", SERIF, 40 * u, 'ma')]
    B.ink(B.text_mask(cap), '#4a4640', 0.88)
    B.save(out)

if __name__ == "__main__":
    main()
