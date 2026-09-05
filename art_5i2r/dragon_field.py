"""dragon_field.py — 'The Word Not Yet Spoken' (2560²).
Birth time of every Gaussian integer under the binary dragon D_{k+1} = βD_k ∪ (1 − βD_k), β = 1+i:
birth(z) = min{k : z ∈ D_k}. Points already spoken by time k0 are paper; the words spoken between k0
and K are pigment by birth time (hierarchy as palette); the holes at time K are hatched ink.
Coral: the nearest missing point of each order k (the closed form ⌈β^{k−1}/3⌉, rounded outward) and the
exact spiral β^{t−1}/3 through them.
Truncation is exact: a point outside |z| ≤ W maps under both maps to |·| ≥ √2|z| − 1 > W, so it never
re-enters the window.
"""
import numpy as np, json, time, sys
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import pastel as P
from dragon import s_from_c, s_formula

INK = P.PIG['ink']


def birth_field(K, W):
    """array birth[y+W, x+W] = first k with x+iy in D_k (0 = never up to K); window |x|,|y| <= W."""
    size = 2 * W + 1
    birth = np.zeros((size, size), np.int16)
    birth[W, W] = 1                      # 0 ∈ D_0 (born at 0; use 1 as 'born at k=0' marker → shift later)
    cur = np.array([0 + 0j])
    born = {0: 0}
    t0 = time.time()
    for k in range(1, K + 1):
        nxt = np.concatenate([(1 + 1j) * cur, 1 - (1 + 1j) * cur])
        nxt = np.unique(np.round(nxt.real).astype(np.int64) + 1j * np.round(nxt.imag).astype(np.int64))
        keep = (np.abs(nxt.real) <= W + 2) & (np.abs(nxt.imag) <= W + 2)
        cur = nxt[keep]
        xs = cur.real.astype(int); ys = cur.imag.astype(int)
        inwin = (np.abs(xs) <= W) & (np.abs(ys) <= W)
        xi = xs[inwin] + W; yi = ys[inwin] + W
        new = birth[yi, xi] == 0
        birth[yi[new], xi[new]] = k + 1   # store k+1 so that 0 means 'not yet'
        print(f'k={k:2d} |D_k ∩ window|={inwin.sum():8d} newly born={new.sum():8d} {time.time()-t0:.1f}s', flush=True)
    return birth  # value v>0 means born at k=v-1


def render(K=22, W=640, k0=12, S=2560, out='dragon_2560.png', seed=12):
    t0 = time.time()
    birth = birth_field(K, W)
    b = birth.astype(int) - 1            # -1 = unborn (hole at time K)
    size = 2 * W + 1
    # certificate: nearest hole at each k matches the closed form
    cert = {}
    for k in range(6, K + 1):
        yy, xx = np.where((b < 0) | (b > k))          # not in D_k
        d2 = (xx - W) ** 2 + (yy - W) ** 2
        i = np.argmin(d2)
        cert[k] = dict(s_enum=int(d2[i]), s_formula=int(s_formula(k)), z=[int(xx[i] - W), int(yy[i] - W)])
    all_ok = all(v['s_enum'] == v['s_formula'] for v in cert.values())
    print('closed form vs field, k=6..%d:' % K, all_ok, flush=True)
    # ---- image: 2 px per Gaussian integer, nearest upscale
    SS = 2
    Wd = size * SS
    sh = P.Sheet(Wd, Wd, seed=seed)
    # pigment by birth time for k0 < birth <= K ; paper for birth <= k0 ; holes hatched
    late = (b > k0)
    A = np.zeros((size, size, 3), np.float32)
    levels = list(range(k0 + 1, K + 1))
    for j, k in enumerate(levels):
        m = b == k
        pig = P.CYCLE[(j * 3) % len(P.CYCLE)]           # stride 3 through the box: neighbours differ
        dens = 0.40 + 0.45 * (j / max(1, len(levels) - 1))
        A[m] = dens * P.absorb(P.PIG[pig])
    A = np.repeat(np.repeat(A, SS, axis=0), SS, axis=1)
    # soften pixel edges very slightly, granulate
    A = gaussian_filter(A, [0.6, 0.6, 0])
    g = P.noise(Wd, Wd, 1.6, seed + 11)
    A *= (1 + 0.14 * g)[..., None]
    sh.A += A
    del A
    # holes at time K inside the region where D_K is dense: hatch in ink where a hole is surrounded
    hole = (b < 0)
    born_any = ~hole
    from scipy.ndimage import binary_dilation, uniform_filter
    dense = uniform_filter(born_any.astype(np.float32), 9) > 0.55
    hh = hole
    hh2 = np.repeat(np.repeat(hh, SS, axis=0), SS, axis=1).astype(np.float32)
    # hatch: diagonal lines mask
    sh.wash(gaussian_filter(hh2, 1.0) * 0.55, 'blush')
    # ---- coral: nearest missing points for k = 8..K and the spiral β^{t−1}/3
    sp_im = Image.new('F', (Wd, Wd), 0.0); ds = ImageDraw.Draw(sp_im)
    px = lambda x, y: ((x + W + 0.5) * SS, (W - y + 0.5) * SS)
    ts = np.linspace(6, K + 0.6, 3000)
    zz = (1 + 1j) ** (ts - 1) / 3
    pts = [px(zc.real, zc.imag) for zc in zz]
    ds.line(pts, fill=1.0, width=4, joint='curve')
    for k in range(8, K + 1):
        zk, zk2 = s_from_c(k)
        zc = zk2 if zk2 is not None else zk
        x, y = px(zc.real, zc.imag)
        rad = 6 + 1.1 * (k - 8)
        ds.ellipse([x - rad, y - rad, x + rad, y + rad], outline=1.0, width=4)
    sh.wash(gaussian_filter(np.asarray(sp_im, np.float32), 0.7) * 2.0, 'coral')
    # ---- caption
    sh.caption_strip(0.905, 0.99, 0.55)
    items = [("The Word Not Yet Spoken", 0.5 * Wd, 0.925 * Wd, int(0.032 * Wd), 'serif_bold', 'mm'),
             (f"Every Gaussian integer is eventually spelled in the alphabet {{0,1}} of the binary dragon; pigment = the time it is first spoken (k = {k0+1}…{K}), paper = spoken before k = {k0+1}, blush = still unsaid at k = {K}.",
              0.5 * Wd, 0.955 * Wd, int(0.0112 * Wd), 'italic', 'mm'),
             (f"The coral rings are the nearest unsaid word of each order, exactly β^(k−1)/3 rounded away from zero (all {len(cert)} orders checked against the field); they climb the coral spiral β^(t−1)/3.",
              0.5 * Wd, 0.975 * Wd, int(0.0112 * Wd), 'italic', 'mm')]
    sh.wash(P.text_density(Wd, Wd, items) * 1.1, INK)
    img = sh.develop()
    P.finish(img, (S, S), out)
    json.dump(dict(K=K, W=W, k0=k0, closed_form_matches_field=bool(all_ok), nearest=cert,
                   points_in_window_born=int(born_any.sum()), holes_in_window=int(hole.sum())),
              open(out.replace('.png', '_cert.json'), 'w'), indent=1)
    print(f'render {out} {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    out = sys.argv[2] if len(sys.argv) > 2 else f'proto_dragon_{S}.png'
    K = int(sys.argv[3]) if len(sys.argv) > 3 else 22
    W = int(sys.argv[4]) if len(sys.argv) > 4 else 640
    render(K=K, W=W, S=S, out=out)
