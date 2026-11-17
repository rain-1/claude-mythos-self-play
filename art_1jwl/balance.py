"""balance.py — 'Thirty-Five Against Three'
An explicit way to share 1^8, 2^8, ..., 75^8 between two pans of equal weight.  Cream discs are the odd
numbers; modulo 64 each of them weighs 1 or 33 and every even one weighs 0, so the count of odd weights
on one pan is forced modulo 32: it must be 3 (or 35).   usage: balance.py SIZE out.png"""
import sys, json, numpy as np
from papercut import Box, rgb, mix, SERIF, SERIF_I, SERIF_B

def rows_of(nums, wmax, rad, gap):
    """largest at the bottom; returns list of rows (bottom first), each a list of numbers"""
    nums = sorted(nums, reverse=True); rows = []; cur = []; w = 0
    for i in nums:
        d = 2 * rad(i) + gap
        if cur and w + d > wmax: rows.append(cur); cur = []; w = 0
        cur.append(i); w += d
    if cur: rows.append(cur)
    return rows

def main():
    S = int(sys.argv[1]); out = sys.argv[2]; u = S / 4096.0
    sol = json.load(open('math_balance/balance75.json'))
    B = Box(S, seed=33, light=(-0.58, -0.81))
    X0, X1, Y0, Y1 = 300 * u, 3796 * u, 280 * u, 3500 * u
    x, y = B.grid(); rng = np.random.default_rng(8)
    # wall: three papers, a dado and a floor line
    B.lay(B.rect(X0 - 40 * u, Y0 - 40 * u, X1 + 40 * u, Y1 + 40 * u), rgb('#2a3060'), 1, shadow=0, k=0)
    e = 3050 * u + (10 * np.sin(x / (420 * u)) + 4 * np.sin(x / (97 * u) + 1)) * u
    B.lay(np.clip(y - e + 0.5, 0, 1), rgb('#1e2349'), 2, shadow=0.3, reach=6, soft=4, edge=0.6, k=1)
    B.lay(B.rect(X0 - 40 * u, 3330 * u, X1 + 40 * u, Y1 + 40 * u), rgb('#3b3560'), 3, shadow=0.3, reach=6, soft=4, edge=0.6, k=2)
    # a round window with the moon's sky, upper right
    wx, wy, wr = 2938 * u, 1560 * u, 205 * u
    B.lay(B.disc(wx, wy, wr + 26 * u), rgb('#474d86'), 3, shadow=0.35, reach=5, soft=3, k=3)
    B.lay(B.disc(wx, wy, wr), rgb('#12163a'), 2.2, shadow=0, k=4)
    B.lay(B.disc(wx - 34 * u, wy - 26 * u, 78 * u) * B.disc(wx, wy, wr), rgb('#f7edcf'), 2.6, shadow=0.3, reach=5, soft=3, k=2)
    st = np.zeros((S, S), np.float32)
    for _ in range(26):
        a, r = rng.uniform(0, 6.283), wr * np.sqrt(rng.uniform(0, 0.9)); sx, sy = wx + r * np.cos(a), wy + r * np.sin(a)
        if np.hypot(sx - wx + 34 * u, sy - wy + 26 * u) < 110 * u: continue
        st = np.maximum(st, np.clip(rng.choice([3.5, 5.0]) * u - np.hypot(x - sx, y - sy) + 0.5, 0, 1))
    B.lay(st, rgb('#f7edcf'), 2.4, shadow=0, edge=0.3, k=2)
    # the scale
    wood, wood2 = rgb('#b78a5a'), rgb('#8f6740')
    cx = 2048 * u; beam_y = 600 * u; arm = 890 * u
    zc = 6
    B.lay(B.poly([(cx - 46 * u, 3330 * u), (cx - 24 * u, 500 * u), (cx + 24 * u, 500 * u), (cx + 46 * u, 3330 * u)]), wood2, zc, shadow=0.5, reach=7, soft=3.5, k=5)
    B.lay(B.poly([(cx - 330 * u, 3340 * u), (cx - 250 * u, 3250 * u), (cx + 250 * u, 3250 * u), (cx + 330 * u, 3340 * u)]), wood2, zc + 1, shadow=0.5, reach=6, soft=3, k=6)
    rad = lambda i: (34 + 1.22 * i) * u
    pans = {}
    for side, nums, pcx in (('L', sol['left'], cx - arm), ('R', sol['right'], cx + arm)):
        rows = rows_of(nums, 1360 * u, rad, 10 * u)
        pans[side] = (rows, pcx)
    tray_y = 3040 * u
    # strings and trays first (behind the discs)
    strings = np.zeros((S, S), np.float32)
    for side, (rows, pcx) in pans.items():
        hw = 715 * u
        for sgn in (-1, 1):
            strings = np.maximum(strings, B.poly([(pcx - 3 * u, beam_y), (pcx + 3 * u, beam_y), (pcx + sgn * hw + 3 * u, tray_y), (pcx + sgn * hw - 3 * u, tray_y)], ss=2))
    B.lay(strings, rgb('#d9cdb4'), zc + 1, shadow=0.4, reach=6, soft=3, edge=0.5, k=7)
    for side, (rows, pcx) in pans.items():
        hw = 745 * u
        B.lay(B.poly([(pcx - hw, tray_y), (pcx + hw, tray_y), (pcx + hw - 60 * u, tray_y + 54 * u), (pcx - hw + 60 * u, tray_y + 54 * u)]), wood, zc + 2, shadow=0.5, reach=7, soft=3.5, k=8)
    # beam with a pointer
    B.lay(B.poly([(cx - arm - 60 * u, beam_y - 14 * u), (cx, beam_y - 44 * u), (cx + arm + 60 * u, beam_y - 14 * u), (cx + arm + 60 * u, beam_y + 16 * u), (cx, beam_y + 30 * u), (cx - arm - 60 * u, beam_y + 16 * u)]), wood, zc + 2, shadow=0.5, reach=8, soft=4, k=9)
    B.lay(B.poly([(cx - 9 * u, beam_y), (cx + 9 * u, beam_y), (cx + 2 * u, beam_y + 300 * u), (cx - 2 * u, beam_y + 300 * u)]), rgb('#d9cdb4'), zc + 3, shadow=0.45, reach=5, soft=2.5, k=7)
    B.lay(B.disc(cx, beam_y - 6 * u, 30 * u), wood2, zc + 3, shadow=0.45, reach=5, soft=2.5, k=6)
    # the discs, row by row from the tray up
    cream, blue, red = rgb('#f5e6bd'), rgb('#6f7fb8'), rgb('#e2452c')
    minority = set(i for i in sol['right'] if i % 2 == 1)
    labels = []
    for side, (rows, pcx) in pans.items():
        ybase = tray_y
        for ri, row in enumerate(rows):
            rmax = max(rad(i) for i in row)
            # alternate big and small so the row is not a staircase
            order = row[::2] + row[1::2][::-1]
            wtot = sum(2 * rad(i) + 10 * u for i in order) - 10 * u
            xx = pcx - wtot / 2
            groups = {}
            for i in order:
                r = rad(i); cxi = xx + r; cyi = ybase - r; xx += 2 * r + 10 * u
                col = 'red' if i in minority else ('cream' if i % 2 else 'blue')
                groups.setdefault(col, []).append((cxi, cyi, r, i))
            for col, items in groups.items():
                m = np.zeros((S, S), np.float32)
                for cxi, cyi, r, i in items:
                    a, b_, c_, d_ = int(max(cyi - r - 2, 0)), int(cyi + r + 3), int(max(cxi - r - 2, 0)), int(cxi + r + 3)
                    yy, xx2 = np.mgrid[a:b_, c_:d_]
                    m[a:b_, c_:d_] = np.maximum(m[a:b_, c_:d_], np.clip(r - np.hypot(xx2 + 0.5 - cxi, yy + 0.5 - cyi) + 0.5, 0, 1))
                    labels.append((cxi, cyi, str(i), SERIF, max(r * 0.78, 22 * u), 'mm', col))
                B.lay(m, {'red': red, 'cream': cream, 'blue': blue}[col], zc + 4 + 0.3 * ri, shadow=0.5, reach=6, soft=2.6, edge=1.0, k=ri + (3 if col == 'blue' else 0))
            ybase -= 2 * rmax + 8 * u
    B.ink(B.text_mask([l[:6] for l in labels if l[6] == 'cream']), '#5b4a2e', 0.8)
    B.ink(B.text_mask([l[:6] for l in labels if l[6] != 'cream']), '#f4ecd6', 0.85)
    B.mat(X0, Y0, X1, Y1)
    mcx = (X0 + X1) / 2
    cap = [(mcx, 3622 * u, "Thirty-Five Against Three", SERIF, 104 * u, 'ma'),
           (mcx, 3766 * u, "The weights 1⁸, 2⁸, …, 75⁸ in two pans of 4,426,102,656,785,155 each. Disc n weighs n⁸; cream and red discs are the odd n.", SERIF_I, 50 * u, 'ma'),
           (mcx, 3834 * u, "Modulo 64 an odd weight is 1 or 33 and an even one is 0, so the scale can only level with exactly three odd weights set apart.", SERIF_I, 50 * u, 'ma'),
           (mcx, 3926 * u, "with 67 weights it would have to be thirty-three against one, and no such sharing exists: the best is off by 6", SERIF, 40 * u, 'ma')]
    B.ink(B.text_mask(cap), '#4a4640', 0.88)
    B.save(out)
if __name__ == "__main__":
    main()
