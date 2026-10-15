# orrery.py — a glass orrery set to the sky of 2026-10-15 (heliocentric mean longitudes, J2000 elements)
import numpy as np, sys
from scene import *
JD = 2461328.5; T = (JD - 2451545.0) / 36525
EL = {  # L0, rate (deg/century), e, perihelion lon (deg)
 'Mercury': (252.25032350, 149472.67411175, 0.2056, 77.457),
 'Venus':   (181.97909950, 58517.81538729, 0.0068, 131.602),
 'Earth':   (100.46457166, 35999.37244981, 0.0167, 102.937),
 'Mars':    (-4.55343205, 19140.30268499, 0.0934, -23.944),
 'Jupiter': (34.39644051, 3034.74612775, 0.0484, 14.728),
 'Saturn':  (49.95424423, 1222.49362201, 0.0539, 92.599)}
def true_lon(p):
    L0, rate, e, w = EL[p]; L = np.radians(L0 + rate * T); M = L - np.radians(w)
    E = M
    for _ in range(30): E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
    return (nu + np.radians(w)) % (2 * np.pi)
FOOT = 9.0; CAGE_R = 4.2; LR = 1.3; LC = (95, 80, 58)
def build(rot=0.0, fn='orrery.bin', zl=26.0, zp=19.0, ab=1.0, arm_rings=True, belt=0, P=None, zh0=7.0, dzh=1.25, zsp=6.2, ztri=5.0, ring=True, cage=True, ringz=4.0):
    S = Scene()
    S.sphere((0, 0, zl), LR, EMIT, tuple(c * (2.3 / LR) ** 2 for c in LC))            # the lamp
    S.cap((0, 0, 0.0), (0, 0, zl - LR - 1.0), 0.45, METAL, BRASS, 0.06)   # column
    S.sphere((0, 0, zl - LR - 1.2), 0.75, METAL, BRASS, 0.04)
    for k in range(3):                                        # tripod
        a = 2 * np.pi * k / 3 + 0.5
        f = (FOOT * np.cos(a), FOOT * np.sin(a), 0.8)
        S.cap((0, 0, ztri), f, 0.42, METAL, BRASS, 0.06); S.sphere(f, 0.95, METAL, BRASS, 0.04)
    P = P or [('Mercury', 6.5, 1.0, 'lilac'), ('Venus', 10.0, 1.5, 'butter'), ('Earth', 14.0, 1.6, 'sky'),
         ('Mars', 18.0, 1.2, 'strawberry'), ('Jupiter', 23.5, 2.9, 'peach'), ('Saturn', 30.0, 2.5, 'mint')]
    out = {}
    for i, (name, r, R, col) in enumerate(P):
        th = true_lon(name) + rot
        zh = zh0 + dzh * i
        c = np.array([r * np.cos(th), r * np.sin(th), zp])
        S.cap((0, 0, zh), (c[0], c[1], zh), 0.2, METAL, BRASS, 0.08)
        S.sphere((0, 0, zh), 0.75, METAL, BRASS, 0.05)
        S.cap((c[0], c[1], zh), (c[0], c[1], zp - R * 0.9), 0.16, METAL, BRASS, 0.08)
        S.sphere((c[0], c[1], zh), 0.38, METAL, BRASS, 0.05)
        S.sphere(tuple(c), R, GLASS, glass_abs(col, ab))
        out[name] = (c, R, col)
        if name == 'Earth':   # the Moon on a little arm
            mth = th + 1.9
            m = c + np.array([3.2 * np.cos(mth), 3.2 * np.sin(mth), 0.6])
            S.cap(tuple(c + np.array([0, 0, -R * 0.6])), (m[0], m[1], m[2] - 0.5), 0.08, METAL, BRASS, 0.08)
            S.sphere(tuple(m), 0.5, GLASS, glass_abs('white', ab))
        if name == 'Jupiter':  # Galilean moons as seed pearls on a fine wire circle
            for j, (rr, ph) in enumerate([(4.2, 0.4), (5.0, 2.6), (5.9, 4.1), (7.0, 5.6)]):
                m = c + np.array([rr * np.cos(ph), rr * np.sin(ph), 0])
                S.sphere(tuple(m), 0.33, CANDY, SORBET[['butter', 'peach', 'rose', 'lilac'][j]])
            S.circle(c, 5.6, (1, 0, 0), (0, 1, 0), 0.05, METAL, BRASS, n=80, rough=0.1)
        if name == 'Saturn':   # ring of tiny glass beads, tilted 27 degrees
            tilt = np.radians(27); u = np.array([1, 0, 0]); v = np.array([0, np.cos(tilt), np.sin(tilt)])
            for rr, nb, cc in [(3.6, 44, 'honey'), (4.2, 52, 'peach'), (4.8, 60, 'butter')]:
                for t in np.linspace(0, 2 * np.pi, nb, endpoint=False):
                    S.sphere(tuple(c + rr * (np.cos(t) * u + np.sin(t) * v)), 0.24, GLASS, glass_abs(cc, 1.6))
    if belt:   # the asteroid belt: a necklace of tiny glass beads on a fine wire hoop held by four spokes
        rng = np.random.default_rng(7); rb = 21.0
        S.circle((0, 0, zp - 0.2), rb, (1, 0, 0), (0, 1, 0), 0.05, METAL, BRASS, n=360, rough=0.1)
        for k in range(4):
            a = np.pi / 4 + k * np.pi / 2; S.cap((0, 0, zsp), (rb * np.cos(a), rb * np.sin(a), zsp), 0.12, METAL, BRASS, 0.08)
            S.cap((rb * np.cos(a), rb * np.sin(a), zsp), (rb * np.cos(a), rb * np.sin(a), zp - 0.2), 0.1, METAL, BRASS, 0.08)
        names = ['strawberry', 'peach', 'butter', 'lime', 'mint', 'sky', 'periwinkle', 'lilac', 'bubblegum']
        t = 0.0
        while t < 2 * np.pi - 0.02:
            r = 0.2 + 0.12 * rng.random(); col = names[int(len(names) * ((t / (2 * np.pi) + 0.03 * rng.standard_normal()) % 1))]
            S.sphere((rb * np.cos(t), rb * np.sin(t), zp - 0.2), r, GLASS, glass_abs(col, 1.8)); t += (2 * r + 0.03) / rb
    if ring: S.circle((0, 0, ringz), 33.5, (1, 0, 0), (0, 1, 0), 0.22, METAL, BRASS, n=240, rough=0.06)
    if cage:   # armillary: ecliptic band + two tilted meridian rings round the lamp
        for a in (0.42, -0.42 + np.pi / 2):   # a small armillary cage round the lamp, as in Wright's painting
            u = np.array([np.cos(a), np.sin(a), 0]); S.circle((0, 0, zl), CAGE_R, u, (0, 0, 1), 0.09, METAL, BRASS, n=120, rough=0.05)
        S.circle((0, 0, zl), CAGE_R, (1, 0, 0), (0, 1, 0), 0.09, METAL, BRASS, n=120, rough=0.05)
    S.save(fn); return out
if __name__ == '__main__':
    o = build(float(sys.argv[1]) if len(sys.argv) > 1 else 0.0)
    for k, v in o.items(): print(k, np.degrees(np.arctan2(v[0][1], v[0][0])).round(1))
