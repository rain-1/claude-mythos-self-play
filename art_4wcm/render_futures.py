"""render_futures.py — 'One Defector, N Futures' : the complete census of what a single defector
can do, as a specimen sheet.  The dynamics depend on b only through which fractions n/m
(1<=n<=9, 1<=m<=8) lie below b, so the 27 breakpoints cut (1, inf) into 28 open intervals and
one run per interval is exhaustive.  Futures are classified by the hash of the WHOLE trajectory
(every generation), not the final frame, so a 2-cycle and a fixed point count as different.
Each distinct future is drawn once, at generation T_show, in the four transition pigments
(D->D apricot, C->C mint, C->D lemon, D->C aqua), labelled by the union of its b-intervals.
"""
import numpy as np, sys, json, time, hashlib
from fractions import Fraction
from scipy.ndimage import gaussian_filter, zoom
sys.path.insert(0, '.')
import nowak
from census_futures import midpoints
from pastel import Sheet, PIG, text_density, text_width, finish


def trajectory(b, T):
    N = 2 * T + 41
    D = np.zeros((N, N), bool); D[N // 2, N // 2] = True
    hsh = hashlib.sha1(); counts = []
    Dp = D
    for t in range(T):
        nd = nowak.step(D, b)
        hsh.update(nd.tobytes()); counts.append(int(nd.sum()))
        Dp, D = D, nd
    c = N // 2; s = T + 1
    sl = slice(c - s, c + s + 1)
    return hsh.hexdigest()[:12], counts, Dp[sl, sl], D[sl, sl]


def fstr(x):
    return 'inf' if x is None else (str(x.numerator) if x.denominator == 1 else f'{x.numerator}/{x.denominator}')


def render(FINAL=2560, SS=2, T=100, T_show=70, tag='futures', caption=True):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    ivs = midpoints()
    groups = {}   # hash -> dict(intervals=[...], frames)
    order = []
    for lo, hi, mid in ivs:
        h, counts, Dp, D = trajectory(mid, T)
        if h not in groups:
            groups[h] = dict(intervals=[], counts=counts, mid=mid)
            order.append(h)
        groups[h]['intervals'].append((lo, hi))
        print(f'({fstr(lo)},{fstr(hi)}) -> {h}  D={counts[-1]}', flush=True)
    n = len(order)
    print('distinct futures:', n, f'{time.time()-t0:.0f}s')
    # label: union of consecutive intervals
    labels = []
    for h in order:
        iv = groups[h]['intervals']
        lo = iv[0][0]; hi = iv[-1][1]
        labels.append(f'b in ({fstr(lo)}, {fstr(hi)})' if hi is not None else f'b > {fstr(lo)}')
    # frames at T_show
    tiles = []
    for h in order:
        _, counts, Dp, D = trajectory(groups[h]['mid'], T_show)
        tiles.append((Dp, D, counts))
    # ---- layout
    cols = 4
    rows = (n + 1 + cols - 1) // cols
    mx = 0.05 * W; top = 0.105 * H
    gap = 0.03 * W
    tw = (W - 2 * mx - (cols - 1) * gap) / cols
    th = tw + 0.052 * H
    sheet = Sheet(W, H, seed=9)
    layers = {k: np.zeros((H, W), np.float32) for k in ('apricot', 'mint', 'lemon', 'aqua')}
    items = []; seeds = []
    for i, ((Dp, D, counts), lab) in enumerate(zip(tiles, labels)):
        rr, cc = divmod(i, cols)
        x0 = mx + cc * (tw + gap); y0 = top + rr * (th + gap)
        Ncell = D.shape[0]
        if max(counts) < 100:                      # tiny futures: magnify the central 15 x 15 cells
            cc0 = Ncell // 2; k = 7
            Dp = Dp[cc0 - k:cc0 + k + 1, cc0 - k:cc0 + k + 1]; D = D[cc0 - k:cc0 + k + 1, cc0 - k:cc0 + k + 1]
            Ncell = D.shape[0]
        px = tw / Ncell
        seeds.append((x0 + tw / 2, y0 + tw / 2, px))
        z = lambda a: zoom(a.astype(np.float32), px, order=0)
        for name, msk in (('apricot', Dp & D), ('mint', ~Dp & ~D), ('lemon', ~Dp & D), ('aqua', Dp & ~D)):
            zz = z(msk)
            hh, ww = zz.shape
            X0, Y0 = int(x0), int(y0)
            layers[name][Y0:Y0 + hh, X0:X0 + ww] = np.maximum(layers[name][Y0:Y0 + hh, X0:X0 + ww], zz)
        c = counts
        if c[-1] == c[-2] == c[-3]:
            kind = 'frozen' if c[-1] > 1 else 'the seed alone, frozen'
        elif c[-1] == c[-3] and c[-1] != c[-2]:
            kind = f'breathing, period 2 ({min(c[-2:])} and {max(c[-2:])})'
        elif c[-1] == c[-4] and c[-2] == c[-5] and c[-3] == c[-6]:
            kind = f'breathing, period 3 ({", ".join(str(v) for v in sorted(c[-3:]))})'
        else:
            kind = 'growing'
        items.append((lab, x0 + tw / 2, y0 + tw + 0.010 * H, 0.0135 * H, 'serif_bold', 'mt'))
        mag = ' (central 15 x 15 sites)' if max(counts) < 100 else ''
        items.append((f'{c[-1]:,} defector{"s" if c[-1] != 1 else ""} at generation {T_show}{mag}', x0 + tw / 2, y0 + tw + 0.027 * H, 0.0100 * H, 'italic', 'mt'))
        items.append((kind, x0 + tw / 2, y0 + tw + 0.040 * H, 0.0100 * H, 'italic', 'mt'))
    # the last cell holds the theorem
    rr, cc = divmod(n, cols)
    x0 = mx + cc * (tw + gap); y0 = top + rr * (th + gap)
    thm = ['A cooperator with n cooperating', 'neighbours (itself included) scores n;', 'a defector with m of them scores b·m.',
           'Every decision is one comparison', 'n > b·m or n < b·m with n ≤ 9, m ≤ 8,', 'so b matters only through the 27',
           'fractions n/m it lies between.', '', 'Between two fractions the map is the', 'same map: 28 runs are every future.',
           f'{n} of them are different.']
    for k, line in enumerate(thm):
        items.append((line, x0 + 0.03 * tw, y0 + 0.06 * tw + k * 0.082 * tw, 0.0115 * H, 'italic', 'ls'))
    for i, (name, d) in enumerate(layers.items()):
        d = gaussian_filter(d, 0.5 * rs)
        amp = 1.25 if name in ('lemon', 'aqua') else 1.05
        sheet.wash(d * amp, name, granulate=0.2, seed=60 + i)
    # coral: the seed site of every tile
    from pastel import polyline_density, discs_density
    cor = discs_density(W, H, [sx for sx, sy, p in seeds], [sy for sx, sy, p in seeds], [min(max(0.5 * p, 1.6 * rs), 2.2 * rs) for sx, sy, p in seeds], [1.0] * len(seeds), sigma=0.4 * rs)
    sheet.wash(np.clip(cor, 0, 1) * 1.5, 'coral')
    # thin ink frame around each tile
    frame = np.zeros((H, W), np.float32)
    for i in range(n):
        rr, cc = divmod(i, cols)
        x0 = mx + cc * (tw + gap); y0 = top + rr * (th + gap)
        frame += polyline_density(W, H, [(x0, y0), (x0 + tw, y0), (x0 + tw, y0 + tw), (x0, y0 + tw)], 1.0 * rs, closed=True)
    sheet.wash(np.clip(gaussian_filter(frame, 0.4 * rs), 0, 1) * 0.5, 'ink')
    words = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve']
    title = f'One Defector, {words[n - 1]} Futures'
    if caption:
        items.append((title, 0.05 * W, 0.045 * H, 0.030 * H, 'serif_bold', 'ls'))
        sub1 = 'Spatial Prisoner\'s Dilemma (Nowak & May 1992), one defector in a sea of cooperators, temptation b.'
        sub2 = f'The future can change only at 27 fractions; one run per interval is the whole census (trajectories compared to generation {T}).'
        items.append((sub1, 0.05 * W, 0.068 * H, 0.0125 * H, 'italic', 'ls'))
        items.append((sub2, 0.05 * W, 0.086 * H, 0.0125 * H, 'italic', 'ls'))
    sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    cert = dict(T=T, T_show=T_show, n_intervals=len(ivs), distinct=n,
                groups=[dict(hash=h, label=labels[i], intervals=[(fstr(a), fstr(b)) for a, b in groups[h]['intervals']],
                             counts=groups[h]['counts'][::10]) for i, h in enumerate(order)])
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print('done', f'{time.time()-t0:.0f}s')


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--final', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--T', type=int, default=100)
    ap.add_argument('--tshow', type=int, default=70)
    ap.add_argument('--tag', default='proto_futures')
    a = ap.parse_args()
    render(FINAL=a.final, SS=a.ss, T=a.T, T_show=a.tshow, tag=a.tag)
