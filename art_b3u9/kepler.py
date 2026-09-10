"""kepler.py — 'What the Definition Predicts': every Kepler orbit launched from one point at one speed.

Newton's second law alone is a definition of force; add the inverse-square law and it predicts.
From a point P at distance r0 from the sun, with speed v (bound: v^2 < 2 mu / r0), EVERY orbit is an
ellipse with the same semi-major axis a = 1/(2/r0 - v^2/mu), and the union of all of them is bounded by
an ellipse with foci at the sun O and at P and major axis 4a - r0 (the gravitational 'safety ellipse').
Three speeds -> three nested confocal envelopes.  Threads: the orbits, prograde warm, retrograde cool,
lighter as the launch turns radial.  Coral: the envelope, drawn only after the field has been measured.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter
sys.path.insert(0, '.')
from pastel import Sheet, PIG, polyline_density, discs_density, text_density, finish, text_width, absorb

MU, R0 = 1.0, 1.0
WARM = ['coral', 'apricot', 'lemon']       # coral removed below: it is the accent
WARM = ['apricot', 'lemon', 'blush']
COOL = ['cornflower', 'aqua', 'lavender']
BYSPEED = ['lemon', 'apricot', 'orchid']


def orbit_points(v, phi, n=4000):
    """launch at P=(r0,0) with velocity v at angle phi from the +x axis (phi=pi/2: tangential prograde).
    Returns points along the full ellipse (n samples, uniform in eccentric anomaly ~ arc-length-ish)."""
    r = np.array([R0, 0.0]); vel = v * np.array([np.cos(phi), np.sin(phi)])
    L = r[0] * vel[1] - r[1] * vel[0]                       # angular momentum (z)
    E = 0.5 * v * v - MU / R0
    a = -MU / (2 * E)
    # eccentricity vector e = (v x L)/mu - r/|r|  (2-D: v x L = (vy*L, -vx*L))
    evec = np.array([vel[1] * L, -vel[0] * L]) / MU - r / R0
    e = np.hypot(*evec)
    w = np.arctan2(evec[1], evec[0])                        # argument of periapsis
    b = a * np.sqrt(max(0.0, 1 - e * e))
    Ea = np.linspace(0, 2 * np.pi, n, endpoint=False)
    # ellipse in perifocal frame, focus at origin
    xp = a * (np.cos(Ea) - e); yp = b * np.sin(Ea)
    X = xp * np.cos(w) - yp * np.sin(w); Y = xp * np.sin(w) + yp * np.cos(w)
    return np.stack([X, Y], 1), dict(a=a, e=e, L=L, w=w)


def strobe_points(v, phi, n, info):
    a, e, w = info['a'], info['e'], info['w']
    M = 2 * np.pi * (np.arange(n) + 0.5) / n
    E = M.copy()
    for _ in range(12):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    b = a * np.sqrt(max(0.0, 1 - e * e))
    xp = a * (np.cos(E) - e); yp = b * np.sin(E)
    X = xp * np.cos(w) - yp * np.sin(w); Y = xp * np.sin(w) + yp * np.cos(w)
    return np.stack([X, Y], 1)


def envelope(v):
    a = 1.0 / (2.0 / R0 - v * v / MU)
    A = (4 * a - R0) / 2.0                 # semi-major of the envelope (foci O and P)
    cx = R0 / 2.0
    B = np.sqrt(A * A - (R0 / 2.0) ** 2)
    return a, A, B, cx


def render(FINAL=1024, SS=2, tag='proto_kepler', speeds=(0.95, 1.12, 1.26), n_orb=90, thread_w=0.7,
           thread_d=1.0, caption=True, env_w=1.3, env_d=1.4, gran=0.12, fill=0.86, rad_pow=0.5,
           light_min=0.35, blur=0.5, palette='speed', strobe=0, strobe_gain=2.5, dens_by_speed=(0.55, 0.9, 1.3), foci_d=0.9, foci_r=1.1):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    envs = [envelope(v) for v in speeds]
    Amax = max(E[1] for E in envs); cx_env = envs[0][3]
    # frame: centre on the envelope centre, extent = 2*Amax
    S = fill * W / (2 * Amax)
    cx, cy = 0.5 * W, 0.5 * H

    def xf(P):
        return np.stack([cx + S * (P[:, 0] - cx_env), cy - S * P[:, 1]], 1)

    sheet = Sheet(W, H, seed=41)
    cert = dict(speeds=list(speeds), envelopes=[dict(a=a, A=A, B=B) for (a, A, B, _) in envs], n_orbits_per_speed=n_orb)
    acc = {}
    # threads: per speed, n_orb launch angles; prograde (L>0) warm, retrograde cool; lightness by |L|/L_max
    occupancy = np.zeros((H, W), np.float32)     # union of orbits, for the certificate
    for si, v in enumerate(speeds):
        phis = (np.arange(n_orb) + 0.5) / n_orb * 2 * np.pi
        for phi in phis:
            P, info = orbit_points(v, phi, n=int(3000 * rs))
            px = xf(P)
            Lrel = abs(info['L']) / (R0 * v)
            pig = BYSPEED[si] if palette == 'speed' else (WARM if info['L'] > 0 else COOL)[si]
            wgt = thread_d * dens_by_speed[si] * (light_min + (1 - light_min) * Lrel ** rad_pow)
            if strobe:
                # equal TIME steps (Kepler's second law): mean anomaly uniform, E by Newton
                Pt = strobe_points(v, phi, int(strobe * rs), info)
                q = xf(Pt)
                ok = (q[:, 0] >= 0) & (q[:, 0] < W) & (q[:, 1] >= 0) & (q[:, 1] < H)
                ii = q[ok, 1].astype(np.int64) * W + q[ok, 0].astype(np.int64)
                cnt = np.bincount(ii, minlength=H * W).astype(np.float32).reshape(H, W)
                acc[pig] = acc.get(pig, 0) + cnt * wgt * strobe_gain
                dens = polyline_density(W, H, px, thread_w * rs, weight=1.0, closed=True)
            else:
                dens = polyline_density(W, H, px, thread_w * rs, weight=1.0, closed=True)
                acc[pig] = acc.get(pig, 0) + dens * wgt
            occupancy = np.maximum(occupancy, dens)
    for pig, d in acc.items():
        d = gaussian_filter(d, (blur if not strobe else max(blur, 0.75)) * rs)
        sheet.wash(1.4 * np.tanh(d / 1.2), pig, granulate=gran, seed=50 + len(pig))
    print(f'threads {time.time()-t0:.0f}s')
    # ---- certificate: measured extent of the union along rays from the envelope centre vs the ellipse
    occ = gaussian_filter(occupancy, 0.5 * rs) > 0.05
    ang = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    A, B = envs[-1][1], envs[-1][2]
    rr = np.linspace(0, Amax * 1.05, 4000)
    meas = []
    for th in ang:
        xs = cx + S * rr * np.cos(th); ys = cy - S * rr * np.sin(th)
        ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
        hit = occ[ys[ok].astype(int), xs[ok].astype(int)]
        meas.append(rr[ok][hit].max() if hit.any() else 0.0)
    meas = np.array(meas)
    r_ell = A * B / np.sqrt((B * np.cos(ang)) ** 2 + (A * np.sin(ang)) ** 2)
    cert.update(envelope_check=dict(max_rel_overshoot=float(((meas - r_ell) / r_ell).max()),
                                    median_rel_gap=float(np.median((r_ell - meas) / r_ell)),
                                    max_rel_gap=float(((r_ell - meas) / r_ell).max())))
    print('envelope check', cert['envelope_check'])
    # ---- coral: the three envelopes (ellipses with foci O and P)
    ink = np.zeros((H, W), np.float32)
    for (a, A, B, cxe) in envs:
        tt = np.linspace(0, 2 * np.pi, int(4000 * rs), endpoint=False)
        E = np.stack([cxe + A * np.cos(tt), B * np.sin(tt)], 1)
        ink += polyline_density(W, H, xf(E), env_w * rs, closed=True)
    sheet.wash(np.clip(gaussian_filter(ink, 0.35 * rs), 0, 1) * env_d, 'coral')
    # the second foci: for each orbit F = P + (2a - r0) * unit(-e), on a circle round P; beads + a faint ink circle
    fx, fy = [], []
    for si, v in enumerate(speeds):
        a = envs[si][0]
        phis = (np.arange(n_orb) + 0.5) / n_orb * 2 * np.pi
        for phi in phis:
            _, info = orbit_points(v, phi, n=16)
            e, w = info['e'], info['w']
            F = np.array([[R0 - (2 * a - R0) * np.cos(w), -(2 * a - R0) * np.sin(w)]])
            q = xf(F); fx.append(q[0, 0]); fy.append(q[0, 1])
        tt = np.linspace(0, 2 * np.pi, int(3000 * rs), endpoint=False)
        C = np.stack([R0 + (2 * a - R0) * np.cos(tt), (2 * a - R0) * np.sin(tt)], 1)
        sheet.wash(polyline_density(W, H, xf(C), 0.5 * rs, closed=True) * 0.22, 'ink')
    sheet.wash(discs_density(W, H, fx, fy, [foci_r * rs] * len(fx), [1.0] * len(fx), sigma=0.4 * rs) * foci_d, 'ink')
    cert.update(second_foci_check='F = P + (2a - r0) * (-e_hat); |OF| + ... each orbit: |XO| + |XF| = 2a')
    # the two foci: sun (ink dot with a warm halo) and the launch point P (coral bead)
    O = xf(np.array([[0.0, 0.0]])); Pp = xf(np.array([[R0, 0.0]]))
    sheet.wash(discs_density(W, H, O[:, 0], O[:, 1], [7 * rs], [1.0], sigma=3.0 * rs) * 0.9, 'lemon')
    sheet.wash(discs_density(W, H, O[:, 0], O[:, 1], [2.6 * rs], [1.0], sigma=0.6 * rs) * 1.6, 'ink')
    sheet.wash(discs_density(W, H, Pp[:, 0], Pp[:, 1], [3.0 * rs], [1.0], sigma=0.6 * rs) * 1.6, 'coral')
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        title = 'What the Definition Predicts'
        sub = ("F = ma defines force; add 1/r² and it predicts: from one point at one speed every orbit is an ellipse "
               "of one size, and together they fill an ellipse with foci at the sun and the launch. Three speeds, three rims.")
        fs = 0.0135 * H
        fs = min(fs, fs * 0.90 * W / max(1, text_width(sub, fs, 'italic')))
        items = [(title, 0.045 * W, 0.925 * H, 0.030 * H, 'serif_bold', 'ls'),
                 (sub, 0.045 * W, 0.962 * H, fs, 'italic', 'ls')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(f'done {time.time()-t0:.0f}s')


if __name__ == '__main__':
    kw = {}
    for a in sys.argv[1:]:
        k, v = a.split('=', 1)
        try:
            kw[k] = eval(v)
        except Exception:
            kw[k] = v
    render(**kw)
