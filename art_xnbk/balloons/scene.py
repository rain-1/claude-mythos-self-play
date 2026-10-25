"""Every amicable pair below 100,000 as a pair of hot-air balloons.
Balloon n is sewn from its proper divisors: panel widths are proportional to the
divisors, so the panels of n go round exactly s(n) = its friend.
usage: python3 scene.py cfg.json out.npy W H spp
"""
import sys, json, math
import numpy as np
from tracer import build_sdf, render, camera

PAIRS = [(220, 284), (1184, 1210), (2620, 2924), (5020, 5564), (6232, 6368), (10744, 10856),
         (12285, 14595), (17296, 18416), (63020, 76084), (66928, 66992), (67095, 71145),
         (69615, 87633), (79750, 88730)]

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])

def lin(c):
    c = np.asarray(c, float); return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

SORBET = dict(strawberry='#f48aa6', coral='#fa8f7c', peach='#ffbf94', butter='#ffe58f',
              honey='#ffd06e', lime='#cbe889', mint='#93e2c4', sky='#94cdf6',
              periwinkle='#a3acf5', lilac='#c9a7f2', bubblegum='#f7a1d7', rose='#f9b4c0',
              cream='#fff6e6')
WARM = ['strawberry', 'butter', 'coral', 'cream', 'peach', 'rose', 'honey', 'bubblegum']
COOL = ['sky', 'lime', 'periwinkle', 'cream', 'mint', 'lilac', 'butter', 'sky']

def divisors(n):
    return [d for d in range(1, n) if n % d == 0]

def balloon_panels(n, fam, rot):
    ds = divisors(n)
    s = sum(ds)
    cum = np.cumsum([0] + ds[:-1]) / s
    m = len(ds)
    # largest divisor gets the pair's main hue, then walk the family downward
    cols = [lin(hexc(SORBET[fam[(rot + (m - 1 - i)) % len(fam)]])) for i in range(m)]
    # rotate the whole pattern (yaw does it too, but keep panel 0 off the seam)
    return cum, cols

def build(cfg):
    rng = np.random.default_rng(cfg.get('seed', 3))
    place = cfg['place']  # list of [x, y, z, R, yawA, sep] per pair
    nb = 2 * len(place)
    B = np.zeros((nb, 8)); GB = np.ones((nb, 65)); GN = np.zeros(nb, np.int64); GC = np.zeros((nb, 64, 3))
    for k, (pr, pl) in enumerate(zip(PAIRS, place)):
        x, y, z, R, yaw, sep = pl[:6]
        dy = pl[6] if len(pl) > 6 else 0.15
        for m in range(2):
            n = pr[m]
            fam = WARM if m == 0 else COOL
            cum, cols = balloon_panels(n, fam, k * 3)
            b = 2 * k + m
            sgn = -1 if m == 0 else 1
            bx = x + sgn * sep * R * 0.5; bz = z + sgn * 0.3 * R
            # turn the seam between the small-divisor fan and the largest panel toward the camera
            cam = cfg['cam']
            vx, vz = cam[0] - bx, cam[2] - bz
            ang = math.atan2(vz, vx)  # world azimuth of the camera seen from the balloon
            phi = 2 * math.pi * (cum[-2] * cfg.get('fan_off', 0.7)) + (yaw - 1.0) * cfg.get('yaw_jit', 0.6)
            # local phi = world angle - yaw_rot ; lx = c*px + s*pz rotates by -yaw
            yw = ang - phi
            B[b] = [bx, y + (dy * R if m == 1 else 0), bz,
                    R, yw, 0, cfg.get('burn', {}).get(str(b), 0.0), b]
            GN[b] = len(cum); GB[b, :len(cum)] = cum; GC[b, :len(cum)] = cols
    return B, GB, GN, GC

def params(cfg):
    P = np.zeros(32)
    el = math.radians(cfg['sun_el']); az = math.radians(cfg['sun_az'])
    P[0:3] = [math.cos(el) * math.sin(az), math.sin(el), math.cos(el) * math.cos(az)]
    P[3:6] = lin(hexc(cfg.get('zen', '#9ccbf2')))
    P[6:9] = lin(hexc(cfg.get('mid', '#d9d7f2')))
    P[9:12] = lin(hexc(cfg.get('hor', '#ffe1cf')))
    P[12:15] = lin(hexc(cfg.get('sunc', '#fff1dc')))
    P[15] = cfg.get('cloud_h', 1600); P[16] = cfg.get('cloud_s', 2500); P[17] = cfg.get('cloud_t', 0.56)
    P[18] = cfg.get('cloud_a', 0.8); P[19] = cfg.get('haze', 2600)
    P[20:23] = lin(hexc(cfg.get('water', '#bfe6e0')))
    P[23] = cfg.get('ripple', 0.05); P[24] = cfg.get('ripple_sc', 0.9); P[25] = cfg.get('F0', 0.3)
    P[26] = cfg.get('near_rip', 3.0); P[27] = cfg.get('near_d', 120.0)
    return P

def hills_arr(cfg):
    H = []
    for L in cfg['hills']:  # z, base, amp, freq, seed, colour
        H.append([L[0], L[1], L[2], L[3], L[4], *lin(hexc(L[5]))])
    return np.array(H, float)

if __name__ == '__main__':
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
    W, H, spp = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    sdf, r0, z0, res = build_sdf()
    B, GB, GN, GC = build(cfg)
    cam = camera(cfg['cam'], cfg['look'], cfg['fov'])
    import time; t = time.time()
    img = render(W, H, spp, cam, B, GB, GN, GC, sdf, r0, z0, res, params(cfg), hills_arr(cfg), 1)
    print('render', time.time() - t)
    np.save(out, img)
