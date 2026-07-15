"""COMPANION B — 'Five Right Angles' — Gauss's pentagramma mirificum.

On the unit sphere, iterate the self-polar star rule
    P_{k+3} = normalize(P_k x P_{k+1})
starting from P0, P1 and a seed P2 perp to P0.  The construction closes after
exactly FIVE steps into a spherical pentagram whose vertices are mutually
self-polar (P_i . P_{i+2} = 0), and the tan^2 of its five arcs satisfy the
Lyness recurrence y_{k+1} = (1+y_k)/y_{k-1} (verified in verify.py).
A one-parameter FAMILY of pentagrammas (varying the seed angle t) breathes as
ghosts around one blazing hero star, drawn on a softly lit sphere.
"""
import sys, math, time
import numpy as np
sys.path.insert(0, '.')
from kit import *

t0 = time.time()
S   = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
TAG = sys.argv[2] if len(sys.argv) > 2 else 'proto'
SS  = 2
R   = S * SS
RSCALE = R / 2048

GOLD  = hex_rgb('ffd27a'); GOLD2 = hex_rgb('ffc457')
VIOLET = hex_rgb('9a7bff'); CYAN = hex_rgb('7fd8e8')
ROSE  = hex_rgb('ff8fb0')
WHITE = np.array([1.0, 0.96, 0.86], np.float32)

def normalize(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)

# ---------------------------------------------------------------- geometry
def pentagramma(P0, P1, t):
    P0 = P0 / np.linalg.norm(P0)
    P1 = P1 / np.linalg.norm(P1)
    u = np.cross(P0, P1); u = u / np.linalg.norm(u)
    v = np.cross(P0, u)
    P2 = math.cos(t) * v + math.sin(t) * u
    P2 = P2 / np.linalg.norm(P2)
    P = [P0, P1, P2]
    for k in range(2):
        w = np.cross(P[-3], P[-2]); P.append(w / np.linalg.norm(w))
    return np.array(P[:5])

# ---------------------------------------------------------------- camera
# view direction; sphere radius in px
CAMR = R * 0.40
# rotate world so the hero star faces us; light from upper-left-front
def rot_matrix(ax, ay, az):
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return Rz @ Ry @ Rx

def look_at_centroid(P5, spin):
    c = P5.mean(0); c = c / np.linalg.norm(c)
    z = np.array([0, 0, 1.0])
    axis = np.cross(c, z); s = np.linalg.norm(axis)
    if s < 1e-9:
        W = np.eye(3)
    else:
        axis /= s; ang = math.acos(np.clip(np.dot(c, z), -1, 1))
        K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
        W = np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K
    cz, sz = math.cos(spin), math.sin(spin)
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ W

LIGHT = normalize(np.array([-0.5, 0.7, 0.8]))
CX, CY = R * 0.5, R * 0.5

def project(P3):
    """world 3d -> screen; returns (x, y, z_toward_viewer, front_mask)"""
    Q = P3 @ WORLD.T
    x = CX + Q[..., 0] * CAMR
    y = CY - Q[..., 1] * CAMR
    z = Q[..., 2]         # +z toward viewer
    return x, y, z

def great_arc(A, B, n):
    """n points along the shorter great-circle arc A->B on the unit sphere"""
    A = A / np.linalg.norm(A); B = B / np.linalg.norm(B)
    dot = np.clip(np.dot(A, B), -1, 1)
    om = math.acos(dot)
    if om < 1e-9:
        return np.tile(A, (n, 1))
    t = np.linspace(0, 1, n)
    s0 = np.sin((1 - t) * om) / math.sin(om)
    s1 = np.sin(t * om) / math.sin(om)
    return s0[:, None] * A[None, :] + s1[:, None] * B[None, :]

# ---- seeds + centroid-facing camera (defined before drawing) ----
P0 = np.array([1.0, 0.0, 0.0])
P1 = np.array([0.15, 1.0, 0.25])
HERO_T = 0.70
WORLD = look_at_centroid(pentagramma(P0, P1, HERO_T), spin=0.62)
ghost_ts = [tt for tt in np.linspace(0.06, math.pi - 0.06, 46) if abs(tt - HERO_T) > 0.015]

# ---------------------------------------------------------------- layers
L_sphere = canvas(R)
L_ghost  = canvas(R)
L_hero   = canvas(R)
L_star   = canvas(R)

# ---- lit sphere body (backlit rim + soft front shading, dark so stars pop)
yy, xx = np.mgrid[0:R, 0:R].astype(np.float32)
dx = (xx - CX) / CAMR; dy = -(yy - CY) / CAMR
rr2 = dx * dx + dy * dy
inside = rr2 <= 1.0
dz = np.sqrt(np.clip(1 - rr2, 0, 1))
# surface normal in world coords = (dx, dy, dz)
nrm = np.stack([dx, dy, dz], -1)
lam = np.clip(nrm @ LIGHT, 0, 1)
rim = np.clip(1 - dz, 0, 1) ** 3   # limb brightening
body = (0.018 + 0.055 * lam ** 1.6 + 0.10 * rim) * inside
base_col = np.array([0.14, 0.09, 0.20], np.float32)   # cold violet sphere
rim_col  = np.array([0.30, 0.20, 0.12], np.float32)
L_sphere += body[..., None] * base_col[None, None, :]
L_sphere += (0.11 * rim * inside)[..., None] * rim_col[None, None, :]
# faint lat/long graticule
for latd in range(-60, 61, 30):
    lat = math.radians(latd)
    lon = np.linspace(0, 2 * math.pi, 400)
    P = np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon),
                  np.full_like(lon, math.sin(lat))], -1)
    x, y, z = project(P)
    m = z > -0.02
    splat_points(L_sphere, x[m], y[m], 0.012, np.array([0.20, 0.18, 0.26], np.float32))
for lond in range(0, 360, 30):
    lon = math.radians(lond)
    lat = np.linspace(-math.pi / 2, math.pi / 2, 300)
    P = np.stack([np.cos(lat) * math.cos(lon), np.cos(lat) * math.sin(lon),
                  np.sin(lat)], -1)
    x, y, z = project(P)
    m = z > -0.02
    splat_points(L_sphere, x[m], y[m], 0.012, np.array([0.20, 0.18, 0.26], np.float32))
print(f'sphere done t={time.time()-t0:.0f}s', flush=True)

def draw_star(P5, L, mass_scale, palette_cycle, arc_n, bead=True, back_dim=0.18):
    x, y, z = project(P5)
    ps = SS * RSCALE
    # star edges: connect i -> i+2 (the pentagram); i -> i+1 dim pentagon
    for k in range(5):
        for (jj, base_w, pal_shift) in ((2, 1.0, 0), (1, 0.34, 1)):
            A, B = P5[k], P5[(k + jj) % 5]
            arc = great_arc(A, B, arc_n)
            ax, ay, az = project(arc)
            # depth: front bright, back dimmed (arc passes behind sphere)
            depth = np.where(az > 0, 0.5 + 0.5 * az, back_dim * (1 + az))
            col = palette_cycle[(k + pal_shift) % len(palette_cycle)]
            seg = np.hypot(np.diff(ax), np.diff(ay))
            w = np.concatenate([[0], seg]) * 0.5 + np.concatenate([seg, [0]]) * 0.5
            m_arc = np.minimum(w * depth * mass_scale * base_w * 0.05, 0.10 * mass_scale)
            splat_points(L, ax, ay, m_arc, col)
    if bead:
        for k in range(5):
            th = np.linspace(0, 2 * math.pi, 48, endpoint=False)
            d = 1.0 if z[k] > 0 else back_dim
            for rad, ww in ((0.0, 5.0), (1.5 * ps, 2.4), (3.0 * ps, 1.0)):
                splat_points(L, x[k] + rad * np.cos(th), y[k] + rad * np.sin(th),
                             ww * d * mass_scale * ps / 48, WHITE)

# ghosts
GH_PAL = [VIOLET, CYAN, ROSE, VIOLET, CYAN]
for gi, tt in enumerate(ghost_ts):
    P5 = pentagramma(P0, P1, tt)
    s = gi / (len(ghost_ts) - 1)
    gcol = lerp_palette([(0.0, VIOLET), (0.5, CYAN), (1.0, ROSE)], np.array([s]))[0]
    draw_star(P5, L_ghost, 0.60, [gcol] * 5, arc_n=360, bead=False, back_dim=0.11)
print(f'ghosts done t={time.time()-t0:.0f}s', flush=True)

# hero
P5 = pentagramma(P0, P1, HERO_T)
draw_star(P5, L_hero, 1.3, [GOLD, GOLD2, GOLD, GOLD2, GOLD], arc_n=1600, bead=True, back_dim=0.16)
# hero vertices blazing extra
xh, yh, zh = project(P5)
ps = SS * RSCALE
for k in range(5):
    th = np.linspace(0, 2 * math.pi, 96, endpoint=False)
    dfac = 1.0 if zh[k] > 0 else 0.25
    for rad, ww in ((0.0, 8), (1.4 * ps, 4), (2.8 * ps, 1.6), (4.6 * ps, 0.6)):
        splat_points(L_star, xh[k] + rad * np.cos(th), yh[k] + rad * np.sin(th),
                     ww * dfac * ps / 96, np.array([1.0, 0.90, 0.68], np.float32))
print(f'hero done t={time.time()-t0:.0f}s', flush=True)

# ---------------------------------------------------------------- compose
from scipy.ndimage import gaussian_filter as _gf
def fatten(L, amt=0.75):
    sig = 1.15 * SS * max(1.0, RSCALE)
    return L + amt * _gf(L, (sig, sig, 0))
L_ghost = fatten(L_ghost, 0.85)
L_hero  = fatten(L_hero, 0.65)
L_star  = fatten(L_star, 0.55)
def norm99(L, q=99.3):
    v = L.mean(2)
    p = np.percentile(v[v > 0], q) if (v > 0).any() else 1.0
    return L / max(p, 1e-9)
def normq(L, q):
    v = L.mean(2)
    p = np.percentile(v[v > 0], q) if (v > 0).any() else 1.0
    return L / max(p, 1e-9)

sph = L_sphere / max(np.percentile(L_sphere[L_sphere > 0], 99.5), 1e-9)
# hero: hue-locked gold — luminance saturates, colour stays GOLD (never clips to white)
hv = L_hero.mean(2)
hp = np.percentile(hv[hv > 0], 97.0)
hero_gold = (1 - np.exp(-2.2 * hv / max(hp, 1e-9)))[..., None] * GOLD[None, None, :]
img = (0.44 * sph
       + 1.5 * normq(L_ghost, 98.5)
       + 1.15 * hero_gold
       + 1.15 * norm99(L_star))

img = bloom_add(img, tight=max(2, 0.0015 * R), wide=0.032 * R, t_amt=0.5, w_amt=0.26, thresh=0.6)
u8 = tonemap(img, k=1.05, gamma=0.87, sat=1.16)
from PIL import Image
Image.fromarray(u8).resize((S, S), Image.LANCZOS).save(f'penta_{TAG}.png')
print(f'saved penta_{TAG}.png t={time.time()-t0:.0f}s')
