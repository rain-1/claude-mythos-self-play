"""Indra's Curve — the limit set of a quasi-Fuchsian punctured-torus group
(Grandma's recipe, Mumford–Series–Wright), drawn as one ink thread on paper, with the
images of the two cusp horocycles as pearls: hierarchy-as-palette — side of the curve =
warm/cool, first letter = pigment, word depth = lightness.

usage: python3 kleinian.py SIZE ta_re ta_im tb_re tb_im [out]
"""
import sys, math, time, cmath
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
from pastel import *


def grandma(ta, tb):
    tab = (ta * tb - cmath.sqrt(ta * ta * tb * tb - 4 * (ta * ta + tb * tb))) / 2
    z0 = ((tab - 2) * tb) / (tb * tab - 2 * ta + 2j * tab)
    a = np.array([[ta / 2, (ta * tab - 2 * tb + 4j) / ((2 * tab + 4) * z0)],
                  [(ta * tab - 2 * tb - 4j) * z0 / (2 * tab - 4), ta / 2]], complex)
    b = np.array([[(tb - 2j) / 2, tb / 2], [tb / 2, (tb + 2j) / 2]], complex)
    return a, b, tab


def inv(m):
    return np.array([[m[1, 1], -m[0, 1]], [-m[1, 0], m[0, 0]]], complex)


def mob(m, z):
    return (m[0, 0] * z + m[0, 1]) / (m[1, 0] * z + m[1, 1])


def fix(m):
    a, b, c, d = m[0, 0], m[0, 1], m[1, 0], m[1, 1]
    if abs(c) < 1e-14:
        return b / (d - a)
    disc = cmath.sqrt((a - d) ** 2 + 4 * b * c)
    z1 = ((a - d) + disc) / (2 * c); z2 = ((a - d) - disc) / (2 * c)
    d1 = abs(1 / (c * z1 + d) ** 2); d2 = abs(1 / (c * z2 + d) ** 2)
    return z1 if d1 <= d2 else z2


def explore(gens, P, eps, maxdepth=200, maxnodes=12_000_000):
    """DFS in cyclic order gens=[a,B,A,b]. Returns leaf points (curve order) and ALL nodes
    (matrix entries, first letter, depth)."""
    pts, letters, depths = [], [], []
    nodeM, nodeL, nodeD = [], [], []
    stack = [(np.eye(2, dtype=complex), None, 0, None)]
    order = {None: [0, 1, 2, 3]}
    for i in range(4):
        order[i] = [(i - 1) % 4, i, (i + 1) % 4]
    while stack:
        M, last, d, fl = stack.pop()
        if last is not None:
            imgs = mob(M, P)
            diam = max(abs(imgs[i] - imgs[j]) for i in range(4) for j in range(i + 1, 4))
            nodeM.append((M[0, 0], M[0, 1], M[1, 0], M[1, 1])); nodeL.append(fl); nodeD.append(d)
            if len(nodeM) > maxnodes:
                raise RuntimeError('too many nodes')
            if diam < eps or d >= maxdepth:
                pts.append(imgs[last]); letters.append(fl); depths.append(d)
                continue
        for i in reversed(order[last]):
            stack.append((M @ gens[i], i, d + 1, fl if fl is not None else i))
    return (np.array(pts), np.array(letters), np.array(depths),
            np.array(nodeM, complex), np.array(nodeL), np.array(nodeD))


def circumcircle(z1, z2, z3):
    """vectorised circumcentre of three complex points"""
    ax, ay = z1.real, z1.imag; bx, by = z2.real, z2.imag; cx, cy = z3.real, z3.imag
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    c = ux + 1j * uy
    return c, np.abs(z1 - c)


def horocycle_normal(K, P0):
    q = P0 + 1e-3
    c, r = circumcircle(np.array([P0]), np.array([mob(K, q)]), np.array([mob(inv(K), q)]))
    n = (c[0] - P0) / abs(c[0] - P0)
    return n


def max_embedded_rho(curve, P0, n):
    z = curve - P0
    proj = (z * np.conj(n)).real
    m = proj > 1e-9
    m &= np.abs(z) > 1e-9
    if not m.any():
        return float('inf')
    return float(np.min(np.abs(z[m]) ** 2 / (2 * proj[m])))


def render(SIZE, ta, tb, out, eps_px=0.5, rho_frac=0.92):
    SS = 2
    W = H = SIZE * SS
    a, b, tab = grandma(ta, tb)
    A, B = inv(a), inv(b)
    gens = [a, B, A, b]
    K = a @ b @ A @ B
    cert = dict(tr_a=complex(np.trace(a)), tr_b=complex(np.trace(b)), tr_ab=complex(np.trace(a @ b)),
                tr_comm=complex(np.trace(K)),
                markov=complex(ta * tb * tab - (ta ** 2 + tb ** 2 + tab ** 2)),
                det_a=complex(np.linalg.det(a)), det_b=complex(np.linalg.det(b)))
    for k_, v in cert.items():
        print('%-8s %s' % (k_, v))
    P = []
    for i in range(4):
        m = np.eye(2, dtype=complex)
        for j in range(4):
            m = m @ gens[(i + j) % 4]
        P.append(fix(m))
    P = np.array(P)
    # coarse pass: bbox + embedded-horoball radius
    pts0, _, _, _, _, _ = explore(gens, P, 0.01, maxdepth=60)
    xs, ys = pts0.real, pts0.imag
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    span = max(x1 - x0, y1 - y0) * 1.10
    cxw, cyw = (x0 + x1) / 2, (y0 + y1) / 2
    scale = W / span
    eps = eps_px * SS / scale
    P0 = P[0]
    K0 = gens[0] @ gens[1] @ gens[2] @ gens[3]
    n = horocycle_normal(K0, P0)
    rho_p = min(rho_frac * max_embedded_rho(pts0, P0, n), 0.35 * span)
    rho_m = min(rho_frac * max_embedded_rho(pts0, P0, -n), 0.35 * span)
    # precise invariance: shrink until no image under a short word (not in <K>) overlaps the ball
    words = []
    for i in range(4):
        words.append(gens[i])
        for j in range(4):
            if j != (i + 2) % 4:
                words.append(gens[i] @ gens[j])
                for l in range(4):
                    if l != (j + 2) % 4:
                        words.append(gens[i] @ gens[j] @ gens[l])
    def shrink(cen_dir, rho):
        for _ in range(60):
            cen = P0 + rho * cen_dir
            zs = np.array([cen + rho, cen + rho * 1j, cen - rho])
            bad = False
            for Wm in words:
                c, r = circumcircle(*[np.array([mob(Wm, z)]) for z in zs])
                d = abs(c[0] - cen)
                if abs(d - 0) < 1e-9 * rho and abs(r[0] - rho) < 1e-9 * rho:
                    continue  # same ball (stabiliser)
                if d < 0.999 * (r[0] + rho):
                    bad = True; break
            if not bad:
                return rho
            rho *= 0.88
        return rho
    rho_p = shrink(n, rho_p); rho_m = shrink(-n, rho_m)
    print('horoball radii', rho_p, rho_m, 'span', span)
    t0 = time.time()
    pts, letters, depths, nodeM, nodeL, nodeD = explore(gens, P, eps, maxdepth=200)
    print('leaf points', len(pts), 'nodes', len(nodeM), 'depth max', depths.max(), 'mean %.1f' % depths.mean(), '%.0fs' % (time.time() - t0))
    tx = lambda z: (z.real - cxw) * scale + W / 2
    ty = lambda z: (cyw - z.imag) * scale + H / 2
    px, py = tx(pts), ty(pts)
    gaps = np.hypot(np.diff(px), np.diff(py))
    print('consecutive gaps px: median %.3f  p99 %.3f  max %.3f' % (np.median(gaps), np.percentile(gaps, 99), gaps.max()))
    # inside mask (Jordan curve polygon)
    step = max(1, len(px) // 500000)
    poly = list(zip(px[::step].tolist(), py[::step].tolist()))
    mask_im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask_im).polygon(poly, fill=255)
    inside = np.asarray(mask_im, np.float32) / 255
    # which horoball is inside? test its centre
    cp = P0 + rho_p * n; cm = P0 - rho_m * n
    ip = inside[int(np.clip(ty(cp), 0, H - 1)), int(np.clip(tx(cp), 0, W - 1))] > 0.5
    if ip:
        ball_in, ball_out = (cp, rho_p), (cm, rho_m)
    else:
        ball_in, ball_out = (cm, rho_m), (cp, rho_p)
    print('inside ball', ball_in, 'outside ball', ball_out)
    sheet = Sheet(W, H, seed=5)
    dist_in = distance_transform_edt(inside > 0.5)
    dist_out = distance_transform_edt(inside <= 0.5)
    win = 0.05 * W
    glaze_in = inside * (0.16 + 0.30 * np.exp(-dist_in / win))
    glaze_out = (1 - inside) * (0.10 + 0.22 * np.exp(-dist_out / (win * 1.5)))
    sheet.wash(glaze_in, 'apricot', granulate=0.35, seed=21)
    sheet.wash(glaze_out, 'aqua', granulate=0.35, seed=22)
    # --- pearls: images of the two horoballs under every node word, deduplicated
    M00, M01, M10, M11 = nodeM[:, 0], nodeM[:, 1], nodeM[:, 2], nodeM[:, 3]
    warm = ['coral', 'apricot', 'lemon', 'blush']
    cool = ['aqua', 'cornflower', 'lavender', 'mint']
    stats = {}
    for side, (cen, rho), pigs, base_dens in (('in', ball_in, warm, 0.62), ('out', ball_out, cool, 0.55)):
        zs = [cen + rho, cen + rho * cmath.exp(2j * math.pi / 3), cen + rho * cmath.exp(4j * math.pi / 3)]
        ws = [(M00 * z + M01) / (M10 * z + M11) for z in zs]
        c, r = circumcircle(*ws)
        # a word whose pole lies inside the ball maps it to the EXTERIOR of a circle — not a disc; skip
        pole = -M11 / np.where(np.abs(M10) < 1e-300, 1e-300, M10)
        is_disc = np.abs(pole - cen) > rho
        n_ext = int((~is_disc).sum())
        # include the identity word (the base ball itself)
        c = np.concatenate([[cen], c]); r = np.concatenate([[rho], r])
        L = np.concatenate([[0], nodeL]); D = np.concatenate([[0], nodeD])
        is_disc = np.concatenate([[True], is_disc])
        cxp, cyp, rp = tx(c), ty(c), r * scale
        good = is_disc & np.isfinite(rp) & (rp > 0.45 * SS) & (rp < 0.6 * W) & (cxp > -rp) & (cxp < W + rp) & (cyp > -rp) & (cyp < H + rp)
        print(side, 'exterior images skipped', n_ext)
        cxp, cyp, rp, L, D = cxp[good], cyp[good], rp[good], L[good], D[good]
        key = np.round(np.c_[cxp, cyp, rp] / 0.25).astype(np.int64)
        _, ui = np.unique(key, axis=0, return_index=True)
        cxp, cyp, rp, L, D = cxp[ui], cyp[ui], rp[ui], L[ui], D[ui]
        stats[side] = dict(n=int(len(rp)), rmax=float(rp.max() / SS), rmin=float(rp.min() / SS))
        print(side, 'pearls', len(rp), 'r px %.1f..%.1f' % (rp.min() / SS, rp.max() / SS))
        dens = base_dens * (0.40 + 0.60 * (1 - np.exp(-D / 5.0)))
        order = np.argsort(-rp)
        for li in range(4):
            m = order[L[order] == li]
            if len(m) == 0:
                continue
            im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
            for x, y, rr_, dd in zip(cxp[m], cyp[m], rp[m], dens[m]):
                # pearl: a disc with a lighter core (pooling rim)
                dr.ellipse([x - rr_, y - rr_, x + rr_, y + rr_], fill=float(dd))
                if rr_ > 4 * SS:
                    dr.ellipse([x - 0.72 * rr_, y - 0.72 * rr_, x + 0.72 * rr_, y + 0.72 * rr_], fill=float(dd * 0.55))
            Dm = gaussian_filter(np.asarray(im, np.float32), 0.5 * SS)
            sheet.wash(Dm, pigs[li], granulate=0.30, seed=41 + li)
    # --- the thread: ink, crisp
    im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
    dr.line(list(zip(px.tolist(), py.tolist())), fill=1.0, width=int(round(1.1 * SS)))
    Dl = gaussian_filter(np.asarray(im, np.float32), 0.5 * SS)
    Dl = Dl / (Dl.max() + 1e-9)
    sheet.wash(Dl * 0.75, 'ink')
    items = [("Indra's Curve", 0.05 * W, 0.935 * H, 0.030 * W, 'serif_bold', 'ls'),
             ("one point, two maps, every word: tr a = %s, tr b = %s, tr[a,b] = -2 — the pearls are the cusp seen from every address" % (
                 fmt(ta), fmt(tb)), 0.05 * W, 0.962 * H, 0.0135 * W, 'italic', 'ls')]
    T = text_density(W, H, items)
    sheet.wash(T * 0.85, 'ink')
    img = sheet.develop()
    finish(img, (SIZE, SIZE), out)
    return dict(npts=int(len(pts)), nodes=int(len(nodeM)), gap_med=float(np.median(gaps)), gap_p99=float(np.percentile(gaps, 99)),
                gap_max=float(gaps.max()), depth_max=int(depths.max()), pearls=stats,
                rho_in=float(ball_in[1]), rho_out=float(ball_out[1]), cert={k_: str(v) for k_, v in cert.items()})


def fmt(z):
    if abs(z.imag) < 1e-12:
        return '%g' % z.real
    return '%g%+gi' % (z.real, z.imag)


if __name__ == '__main__':
    SIZE = int(sys.argv[1])
    ta = complex(float(sys.argv[2]), float(sys.argv[3])); tb = complex(float(sys.argv[4]), float(sys.argv[5]))
    out = sys.argv[6] if len(sys.argv) > 6 else 'kleinian_%d.png' % SIZE
    import json
    res = render(SIZE, ta, tb, out)
    print(res)
    json.dump(res, open(out.replace('.png', '_cert.json'), 'w'), indent=1)
