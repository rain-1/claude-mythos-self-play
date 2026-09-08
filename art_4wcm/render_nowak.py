"""render_nowak.py — 'The Seed It Permits' : one defector in a sea of cooperators (Nowak–May
spatial Prisoner's Dilemma, b in (9/5, 2)), painted by PERSISTENCE.

Measure: over the last K generations, the fraction of time each site spent defecting, f.
Pigment: warm (defection) vs cool (cooperation); density = |2f - 1| — a site that keeps
changing its mind fades to paper, a site that has settled holds its pigment.  A second
channel: the age of the site's current strategy (time since the last flip) darkens the
settled ones.  Ink: the boundary of the defector clusters at the final generation.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter, zoom, distance_transform_edt, binary_dilation
sys.path.insert(0, '.')
import nowak
from pastel import Sheet, PIG, ink_from_distance, text_density, finish


def run_history(T, K, b=1.9):
    N = 2 * T + 41
    D = np.zeros((N, N), bool); D[N // 2, N // 2] = True
    cnt = np.zeros((N, N), np.int32)
    last = np.zeros((N, N), np.int32)
    flips = np.zeros((N, N), np.int32)
    cd = np.zeros((N, N), np.int32); dc = np.zeros((N, N), np.int32)
    Dprev = D
    for t in range(T):
        nd = nowak.step(D, b)
        ch = nd != D
        Dprev = D
        last[ch] = t
        if t >= T - K:
            flips += ch
            cnt += nd
            cd += (nd & ~D); dc += (~nd & D)
        D = nd
    c = N // 2
    sl = slice(c - T, c + T + 1)
    return dict(Dprev=Dprev[sl, sl], D=D[sl, sl], cnt=cnt[sl, sl], last=last[sl, sl], flips=flips[sl, sl], cd=cd[sl, sl], dc=dc[sl, sl], T=T, K=K, N=2 * T + 1)


def render(FINAL=1024, SS=2, T=200, K=60, b=1.9, tag='proto_nowak', caption=True, fill=0.86,
           dens=1.3, age_pow=0.5, ink_w=0.55, ink_amp=0.5, mode='transitions', gran=0.2, settled_floor=0.3):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    hist = run_history(T, K, b)
    N = hist['N']
    print(f'history {N}x{N} in {time.time()-t0:.1f}s; D frac {hist["D"].mean():.3f}')
    f = hist['cnt'] / K                        # fraction of last K generations as defector
    age = (T - 1 - hist['last']) / T           # 0 = just flipped, 1 = never flipped
    # cell -> canvas: pattern square of side N cells fills `fill` of the canvas
    px = fill * W / N
    ox = oy = (1 - fill) / 2 * W

    def up(a, order=0):
        z = zoom(a.astype(np.float32), px, order=order)
        out = np.zeros((H, W), np.float32)
        hh, ww = min(H - int(oy), z.shape[0]), min(W - int(ox), z.shape[1])
        out[int(oy):int(oy) + hh, int(ox):int(ox) + ww] = z[:hh, :ww]
        return out

    sheet = Sheet(W, H, seed=5)
    if mode == 'persist':
        decided = np.abs(2 * f - 1)                     # 0 = flips half the time, 1 = settled
        warm = f > 0.5
        # pigment families: defection = apricot(settled) / lemon(churning-warm) ; cooperation = aqua / mint
        agef = age ** age_pow
        layers = [('apricot', warm * decided * (0.35 + 0.65 * agef)), ('lemon', warm * (1 - decided) * 0.9),
                  ('cornflower', ~warm * decided * (0.35 + 0.65 * agef)), ('mint', ~warm * (1 - decided) * 0.9)]
        for i, (name, wgt) in enumerate(layers):
            d = up(wgt, order=0)
            d = gaussian_filter(d, 0.6 * rs)
            sheet.wash(d * dens, name, granulate=gran, seed=50 + i)
    elif mode == 'transitions':
        # the classic Nowak–May four colours, in pastel: D->D apricot, C->C mint, C->D lemon, D->C aqua;
        # density of the settled classes rises with the age of the site's strategy
        Dn, Dp = hist['D'], hist['Dprev']
        agef = age ** age_pow
        layers = [('apricot', (Dp & Dn) * (settled_floor + (1 - settled_floor) * agef)),
                  ('mint', (~Dp & ~Dn) * (settled_floor + (1 - settled_floor) * agef)),
                  ('lemon', (~Dp & Dn) * 1.0), ('aqua', (Dp & ~Dn) * 1.0)]
        for i, (name, wgt) in enumerate(layers):
            d = up(wgt, order=0)
            d = gaussian_filter(d, 0.5 * rs)
            sheet.wash(d * dens, name, granulate=gran, seed=50 + i)
    # ink: boundary of defector clusters in the final generation
    Dbig = up(hist['D'], order=0) > 0.5
    edt_in = distance_transform_edt(Dbig); edt_out = distance_transform_edt(~Dbig)
    dist = np.where(Dbig, edt_in - 0.5, edt_out - 0.5)
    ink = ink_from_distance(np.abs(dist), ink_w * rs)
    # restrict to the reached square
    sheet.wash(ink * ink_amp, 'ink')
    # coral: the seed site
    c = N // 2
    yy, xx = np.mgrid[0:H, 0:W]
    sx, sy = ox + (c + 0.5) * px, oy + (c + 0.5) * px
    rr = np.hypot(xx - sx, yy - sy)
    sheet.wash(np.exp(-(rr / (0.55 * px)) ** 4).astype(np.float32) * 1.6, 'coral')
    del xx, yy, rr
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        title = 'The Seed It Permits'
        sub = (f'One defector among cooperators, generation {T}, 9/5 < b < 2 (Nowak & May 1992). '
               f'Apricot keeps defecting, mint keeps cooperating; lemon just fell, aqua just came back.')
        items = [(title, 0.045 * W, 0.925 * H, 0.030 * H, 'serif_bold', 'ls'),
                 (sub, 0.045 * W, 0.962 * H, 0.0135 * H, 'italic', 'ls')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    cert = dict(T=T, K=K, b=b, N=N, D_frac=float(hist['D'].mean()), settled_frac=float((np.abs(2 * f - 1) > 0.9).mean()),
                never_flipped_frac=float((hist['last'] == 0).mean()))
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(json.dumps(cert), f'done {time.time()-t0:.0f}s')


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--final', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--T', type=int, default=200)
    ap.add_argument('--K', type=int, default=60)
    ap.add_argument('--b', type=float, default=1.9)
    ap.add_argument('--fill', type=float, default=0.86)
    ap.add_argument('--dens', type=float, default=1.3)
    ap.add_argument('--agepow', type=float, default=0.5)
    ap.add_argument('--inkw', type=float, default=0.55)
    ap.add_argument('--inkamp', type=float, default=0.5)
    ap.add_argument('--gran', type=float, default=0.2)
    ap.add_argument('--tag', default='proto_nowak')
    ap.add_argument('--mode', default='transitions')
    ap.add_argument('--floor', type=float, default=0.3)
    ap.add_argument('--nocap', action='store_true')
    a = ap.parse_args()
    render(FINAL=a.final, SS=a.ss, T=a.T, K=a.K, b=a.b, tag=a.tag, caption=not a.nocap, fill=a.fill, dens=a.dens,
           age_pow=a.agepow, ink_w=a.inkw, ink_amp=a.inkamp, gran=a.gran, mode=a.mode, settled_floor=a.floor)
