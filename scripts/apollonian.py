#!/usr/bin/env python3
"""02 — The Unreasonable Packing.
An Apollonian gasket grown from Descartes' Circle Theorem. Start with four
mutually tangent circles of integer curvature (-1,2,2,3); each tangent triple
spawns another circle whose bend and centre fall straight out of
  b4 = b1+b2+b3 +/- 2 sqrt(b1 b2 + b2 b3 + b3 b1)   (complex form for centres).
Every curvature in this packing is an integer -- arithmetic precipitating out
of pure geometry. Circles are coloured by curvature, so the integers show.
"""
import numpy as np
from PIL import Image, ImageDraw
import sys, math

SIZE     = int(sys.argv[1]) if len(sys.argv) > 1 else 768
MAXBEND  = float(sys.argv[2]) if len(sys.argv) > 2 else 4000.0
OUT      = sys.argv[3] if len(sys.argv) > 3 else "out/apollonian_proto.png"
SS       = 2

# seed quadruple: bends and complex curvature-coords Z = bend * center
seed_b = [-1.0, 2.0, 2.0, 3.0]
seed_Z = [0+0j, 1+0j, -1+0j, 0+2j]   # = b*center for each

circles = {}   # key -> (bend, center_complex)
def add(b, Z):
    if b <= 0:           # keep the outer circle separate (drawn as background)
        return
    c = Z / b
    key = (round(c.real, 5), round(c.imag, 5), round(b, 4))
    if key in circles:
        return
    circles[key] = (b, c)

for b, Z in zip(seed_b, seed_Z):
    if b > 0:
        add(b, Z)
OUTER_R = 1.0   # outer enclosing circle radius (bend -1, centered at 0)

# recursive descent over quadruples
import sys as _s
_s.setrecursionlimit(100000)
seen_quad = set()
def recurse(B, Z):   # B: list of 4 bends, Z: list of 4 coords
    for i in range(4):
        j, k, l = [m for m in range(4) if m != i]
        b_new = 2*(B[j]+B[k]+B[l]) - B[i]
        Z_new = 2*(Z[j]+Z[k]+Z[l]) - Z[i]
        if b_new > MAXBEND or b_new <= 0:
            continue
        c = Z_new / b_new
        key = (round(c.real, 4), round(c.imag, 4), round(b_new, 2))
        if key in seen_quad:
            continue
        seen_quad.add(key)
        add(b_new, Z_new)
        nB = list(B); nZ = list(Z)
        nB[i] = b_new; nZ[i] = Z_new
        recurse(nB, nZ)

recurse(seed_b, seed_Z)
print(f"{len(circles)} circles", flush=True)

# ---- render ----
S = SIZE * SS
img = Image.new("RGB", (S, S), (5, 6, 9))
dr = ImageDraw.Draw(img)
margin = 1.04
def to_px(cx, cy, r):
    x = (cx / (OUTER_R*margin) * 0.5 + 0.5) * S
    y = (cy / (OUTER_R*margin) * 0.5 + 0.5) * S
    rr = r / (OUTER_R*margin) * 0.5 * S
    return x, y, rr

# outer disk = deep base
ox, oy, orr = to_px(0, 0, OUTER_R)
dr.ellipse([ox-orr, oy-orr, ox+orr, oy+orr], fill=(12, 14, 22))

# curated cyclic palette indexed by integer curvature
PAL = [(255,224,120),(255,150,86),(243,92,120),(196,72,168),
       (120,96,222),(70,150,236),(72,210,206),(150,232,140)]
def color_for(bend):
    ib = int(round(bend))
    base = PAL[ib % len(PAL)]
    # smaller circles (bigger bend) -> slightly dimmer so big ones lead
    f = max(0.35, 1.0 - math.log10(max(bend,1.0))/4.2)
    return tuple(int(ch*f) for ch in base), ib

items = sorted(circles.values(), key=lambda t: t[0])                 # ascending bend = big->small

def shade(x, y, rr, col):
    """Flat jewel fill + a crisp dark rim for separation between tangents."""
    dr.ellipse([x-rr, y-rr, x+rr, y+rr], fill=col)
    if rr > 5:
        w = max(1, int(rr*0.02))
        rim = tuple(int(ch*0.45) for ch in col)
        dr.ellipse([x-rr, y-rr, x+rr, y+rr], outline=rim, width=w)

for b, c in items:
    x, y, rr = to_px(c.real, c.imag, 1.0/b)
    if rr < 0.35:
        continue
    col, ib = color_for(b)
    shade(x, y, rr, col)

img = img.resize((SIZE, SIZE), Image.LANCZOS)

# faint global core glow for depth (radial, bounded -- never clips to white)
yy, xx = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
rad = np.hypot(xx - SIZE/2, yy - SIZE/2) / (SIZE/2)
glow = np.clip(1.0 - rad/0.55, 0, 1)[..., None] ** 2 * np.array([46, 28, 60], np.float32)
arr = np.asarray(img).astype(np.float32)
mask = (arr.sum(2) > 40)[..., None]          # only lift inside the packing
arr = np.clip(arr + glow*mask, 0, 255).astype(np.uint8)
img = Image.fromarray(arr)
img.save(OUT)
print("saved", OUT, flush=True)
