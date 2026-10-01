"""render_fan.py — Pascal's fan: the signs of the Hessenberg minors of [C(i,j)^r] (MO 515594).

Row k of the fan (radius) is the minor f_k(r) = det[C(i,j)^r]_{i=1..k, j=0..k-1}, angle is the
exponent r from 0 (left edge) through r = 1 (the coral hinge) to 1.25 (right edge).
Each constant-sign run is a pillow of glaze: warm where f_k > 0, cool where f_k < 0, swelling in the
middle of the run and pinching to paper at the zeros.  f_k has (certified) k − 2 sign changes in
(0, 1) and none beyond 1, so the cool runs crowd against the hinge and never cross it.
usage: render_fan.py data.npz S out.png [key=val]
"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from sorbet import Sheet, PIG, absorb, text_mask, finish, text_w, lines

ARG = dict(a.split('=', 1) for a in sys.argv[4:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))


def zeros_of(sign, rs):
    s = sign.astype(float)
    idx = np.nonzero(s[1:] * s[:-1] < 0)[0]
    return 0.5 * (rs[idx] + rs[idx + 1])


def ramp(names, u):
    R = np.stack([absorb(n) for n in names])
    x = np.clip(u, 0, 1) * (len(names) - 1)
    i = np.clip(x.astype(int), 0, len(names) - 2); t = (x - i)[..., None]
    return R[i] ** (1 - t) * R[i + 1] ** t if False else (1 - t) * R[i] + t * R[i + 1]


def main():
    D = np.load(sys.argv[1]); S = int(sys.argv[2]); out = sys.argv[3]
    sign, rs = D['sign'], D['rs']
    K = min(sign.shape[0] - 1, P('kmax', 999))
    k0 = P('k0', 2)
    RMAX = P('rmax', 1.25)
    # geometry: apex at (cx, cy), fan opens downward, angle phi in [-A/2, A/2] maps r in [0, RMAX] (left->right)
    cx, cy = S * 0.5, S * P('apex', 0.80)
    A = np.deg2rad(P('open', 128.0))
    rho0, rho1 = S * P('rin', 0.10), S * P('rout', 0.80)
    ss = P('ss', 2)
    H = S * ss
    yy, xx = np.mgrid[0:H, 0:H].astype(np.float32) / ss
    dx, dy = xx - cx, yy - cy
    rho = np.hypot(dx, dy)
    phi = np.arctan2(dx, -dy)             # 0 straight up from the apex; positive toward +x
    rr = (0.5 + phi / A) * RMAX           # r = 0 on the left edge, RMAX on the right edge
    kf = k0 + (rho - rho0) / (rho1 - rho0) * (K - k0)
    kk = np.rint(kf).astype(int)
    inband = (np.abs(kf - kk) < P('band', 0.40)) & (kk >= k0) & (kk <= K) & (rr >= 0) & (rr <= RMAX)
    # per-row run geometry
    pos = np.zeros_like(rr); sg = np.zeros_like(rr); runlen = np.zeros_like(rr)
    for k in range(k0, K + 1):
        m = inband & (kk == k)
        if not m.any():
            continue
        z = np.concatenate([[0.0], zeros_of(sign[k], rs), [RMAX]])
        r = rr[m]
        j = np.clip(np.searchsorted(z, r) - 1, 0, len(z) - 2)
        a, b = z[j], z[j + 1]
        pos[m] = (r - a) / np.maximum(b - a, 1e-12)
        runlen[m] = b - a
        mid = 0.5 * (a + b)
        sg[m] = np.where(np.interp(mid, rs, sign[k].astype(float)) >= 0, 1, -1)
    # pillow profile: across the run (pinch at zeros) and across the strip (round edges)
    across = np.clip(1 - (np.abs(kf - kk) / P('band', 0.40)) ** 2, 0, 1) ** 0.5
    pinch_px = np.clip(runlen * (A / RMAX) * rho / P('pinchpx', 3.0), 0, None)   # run width in px / pinch scale
    along = np.sin(np.pi * np.clip(pos, 0, 1)) ** P('alpow', 0.35)
    along = np.where(pinch_px < 1, along * pinch_px, along)     # tiny runs fade instead of aliasing
    body = inband * across * along
    u = np.clip((kf - k0) / (K - k0), 0, 1)
    warm = ramp(P('warm', 'butter,peach,coral,strawberry').split(','), u)
    cool = ramp(P('cool', 'mint,sky,periwinkle,lilac').split(','), u)
    ab = np.where((sg > 0)[..., None], warm, cool)
    dens = body * P('dens', 0.85)
    # beyond the hinge: calmer (lighter) warm
    dens = np.where(rr > 1, dens * P('calm', 0.55), dens)
    Aimg = ab * dens[..., None]
    if ss > 1:
        Aimg = Aimg.reshape(S, ss, S, ss, 3).mean((1, 3))
        rr_s = rr.reshape(S, ss, S, ss).mean((1, 3)); rho_s = rho.reshape(S, ss, S, ss).mean((1, 3))
    else:
        rr_s, rho_s = rr, rho
    sh = Sheet(S, S, seed=11)
    sh.wash_rgb(Aimg)
    # coral hinge at r = 1 : a fine radial line from rin to rout
    ang = (1.0 / RMAX - 0.5) * A
    p0 = (cx + rho0 * 0.7 * np.sin(ang), cy - rho0 * 0.7 * np.cos(ang))
    p1 = (cx + rho1 * 1.03 * np.sin(ang), cy - rho1 * 1.03 * np.cos(ang))
    hl = lines(S, S, [[p0, p1]], max(1, S * P('hw', 0.0016)), sigma=S / 3000)
    sh.lighten(np.clip(gaussian_filter(hl, S / 600) * 4, 0, 1), 0.5)
    sh.wash(hl * 1.5, 'coral')
    # coral beads: the LAST sign change of every ring (the zero nearest the hinge)
    from sorbet import discs
    bx, by = [], []
    for k in range(k0, K + 1):
        z = zeros_of(sign[k], rs); z = z[z < 1]
        if len(z) == 0:
            continue
        rz = z[-1]
        rad = rho0 + (k - k0) / (K - k0) * (rho1 - rho0)
        an = (rz / RMAX - 0.5) * A
        bx.append(cx + rad * np.sin(an)); by.append(cy - rad * np.cos(an))
    bd = discs(S, S, bx, by, np.full(len(bx), S * P('bead', 0.0032)), sigma=S / 3000)
    sh.lighten(np.clip(gaussian_filter(bd, S / 900) * 3, 0, 1), 0.85)
    sh.wash(bd * 1.8, 'coral')
    np.save(out.replace('.png', '_geom.npy'), np.array([cx, cy, rho0, rho1, A, RMAX, K, k0]))
    img = sh.develop(dmax=P('dmax', 1.8))
    finish(img, S, out)


if __name__ == '__main__':
    main()
