#!/usr/bin/env python3
"""01 — Order Without Period.
Penrose tiling by de Bruijn's pentagrid (a cut-and-project: an irrational
2D slice through a periodic 5D lattice). The tiling is the dual of five
families of parallel lines at 72 degrees. Rhombi are coloured by type and
by a multiplicative radial warp so the aperiodicity reads as depth.
"""
import numpy as np
from PIL import Image, ImageDraw
import sys

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 768
N    = int(sys.argv[2]) if len(sys.argv) > 2 else 22     # pentagrid half-range
OUT  = sys.argv[3] if len(sys.argv) > 3 else "out/quasicrystal_proto.png"
SS   = 3                                                  # supersample

zeta = np.exp(2j * np.pi * np.arange(5) / 5)             # 5 grid directions
# generic offsets summing to ~0 -> a clean Penrose (no defects)
gamma = np.array([0.3, -0.1, 0.15, -0.25, -0.10])
gamma -= gamma.mean()

def build_rhombi(N):
    rhombi = []
    for r in range(5):
        for s in range(r + 1, 5):
            ur, us = zeta[r], zeta[s]
            A = np.array([[ur.real, ur.imag], [us.real, us.imag]])
            Ainv = np.linalg.inv(A)
            for kr in range(-N, N + 1):
                for ks in range(-N, N + 1):
                    rhs = np.array([kr - gamma[r], ks - gamma[s]])
                    xy = Ainv @ rhs
                    z = xy[0] + 1j * xy[1]
                    K = np.ceil((z * np.conj(zeta)).real + gamma)
                    K[r], K[s] = kr, ks
                    corners = []
                    for dr, ds in [(0, 0), (1, 0), (1, 1), (0, 1)]:
                        Kc = K.copy(); Kc[r] += dr; Kc[s] += ds
                        v = np.sum(Kc * zeta)
                        corners.append((v.real, v.imag))
                    rhombi.append((corners, (s - r) % 5))
    return rhombi

rhombi = build_rhombi(N)
print(f"{len(rhombi)} rhombi", flush=True)

# world extent -> pixel transform
allpts = np.array([c for poly, _ in rhombi for c in poly])
R = N * 0.62                                              # crop radius (tiles span ~N)
S = SIZE * SS
def to_px(p):
    x = (p[0] / R * 0.5 + 0.5) * S
    y = (p[1] / R * 0.5 + 0.5) * S
    return (x, y)

img = Image.new("RGB", (S, S), (6, 6, 10))
dr = ImageDraw.Draw(img)

# two warm/cool palettes for thin vs fat rhombi; gentle radial warp -> depth
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
THIN_IN, THIN_OUT = (255, 208, 110), (196, 86, 96)       # gold -> rose
FAT_IN,  FAT_OUT  = (120, 222, 240), (44, 70, 150)        # cyan -> indigo

for poly, t in rhombi:
    cx = np.mean([p[0] for p in poly]); cy = np.mean([p[1] for p in poly])
    rad = np.hypot(cx, cy) / R
    rad = min(rad / 0.62, 1.0) ** 0.9 * 0.85              # never fully dark
    thin = t in (1, 4)
    col = lerp(THIN_IN, THIN_OUT, rad) if thin else lerp(FAT_IN, FAT_OUT, rad)
    # facet shading: brightness from tile orientation -> the Penrose 3D shimmer
    ex = poly[1][0] - poly[0][0]; ey = poly[1][1] - poly[0][1]
    ang = np.arctan2(ey, ex)
    shade = 0.80 + 0.30 * (0.5 + 0.5 * np.cos(2 * ang))   # 0.80 .. 1.10
    col = tuple(min(255, int(c * shade)) for c in col)
    px = [to_px(p) for p in poly]
    dr.polygon(px, fill=col, outline=(14, 16, 26))

img = img.resize((SIZE, SIZE), Image.LANCZOS)
img.save(OUT)
print("saved", OUT, flush=True)
