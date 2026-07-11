"""The Braid of Rings v2 — multiple-exposure leapfrog.

One-and-a-half leapfrog cycles of a Dyson vortex-ring pair, photographed as
N ghosted exposures: each exposure is the true pair of circles in 3-D
perspective, brightness ramping with time. Impulse pi*(R1^2+R2^2) is exactly
conserved: every time one ring fattens, the other must thin.
"""
import sys, os
import numpy as np
from glow import splat_segments, filmic, bloom
from PIL import Image
from dyson import simulate

WPX   = int(sys.argv[1]) if len(sys.argv) > 1 else 1600
HPX   = int(sys.argv[2]) if len(sys.argv) > 2 else 760
GAIN  = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
NEXPO = int(sys.argv[4]) if len(sys.argv) > 4 else 26
DRIFTK= float(sys.argv[5]) if len(sys.argv) > 5 else 0.55  # fraction of drift kept
OUT   = sys.argv[6] if len(sys.argv) > 6 else "proto/expo_a.png"
SS    = 2
W, H = WPX * SS, HPX * SS

# ---- simulate ~1.6 cycles ------------------------------------------------------
dt = 2e-3
G = np.array([1.0, 1.0]); sig0 = [1.0, 1.0]; Z0 = [0.0, 0.9]; a0 = 0.08
# cycle period measured earlier: ~11.4 time units (7 cycles in t=80)
TCYC = 80.0 / 7.0
TTOT = 1.55 * TCYC
steps = int(TTOT / dt)
ts, ss, zs, _ = simulate(sig0, Z0, G, a0, dt, steps, keep_every=5)
R = np.sqrt(ss); F = len(ts)
P = np.pi * (G * ss).sum(axis=1)
print("impulse rel drift:", np.ptp(P) / P[0])

drift = np.polyfit(ts, zs.mean(axis=1), 1)[0]
zt = zs - ((1 - DRIFTK) * drift * ts)[:, None]
zt -= zt.mean()

# ---- camera ---------------------------------------------------------------------
s0 = 0.335 * H
PITCH = np.deg2rad(14)         # slight look-down
YAW = np.deg2rad(float(os.environ.get('YAW','70')))           # axis mostly across frame, receding a bit
FOC = 2.1 * H

def project(ax, ay, az):
    """world: x = axial (along ring axis), y,z = ring plane (y depth-ish, z up)."""
    # yaw about z: axis into view
    x1 = ax * np.sin(YAW) + ay * np.cos(YAW)
    y1 = -ax * np.cos(YAW) + ay * np.sin(YAW)
    z1 = az
    # pitch about x (screen-horizontal)
    y2 = y1 * np.cos(PITCH) - z1 * np.sin(PITCH)
    z2 = y1 * np.sin(PITCH) + z1 * np.cos(PITCH)
    f = FOC / (FOC + y2 + 3.0 * s0)
    return x1 * f, z2 * f, f

HUES = [np.array([1.10, 0.58, 0.14]),   # amber
        np.array([0.16, 0.80, 1.00])]   # cyan

# exposure times: equal spacing
eidx = np.round(np.linspace(0, F - 1, NEXPO)).astype(int)
age = np.linspace(0, 1, NEXPO)
bright = 0.10 + 0.90 * age ** 2.2

# ---- pass 1: bbox --------------------------------------------------------------
thb = np.linspace(0, 2 * np.pi, 64)
allx = []; ally = []
for k, fi in enumerate(eidx):
    for i in range(2):
        px, py, _ = project(zt[fi, i] * s0, R[fi, i] * s0 * np.cos(thb), R[fi, i] * s0 * np.sin(thb))
        allx.append(px); ally.append(py)
allx = np.concatenate(allx); ally = np.concatenate(ally)
sc = min(0.92 * W / np.ptp(allx), 0.86 * H / np.ptp(ally))
ox = W / 2 - (allx.min() + np.ptp(allx) / 2) * sc
oy = H / 2 + (ally.min() + np.ptp(ally) / 2) * sc

acc = np.zeros((H, W, 3), np.float32)
BASE = GAIN * 3.1 * (3200 / W) ** 0.6
NTH = 700

th = np.linspace(0, 2 * np.pi, NTH)
# ghost worldline threads (very dim), 10 per ring
for i in range(2):
    for thg in np.linspace(0, 2 * np.pi, 10, endpoint=False):
        px, py, f = project(zt[:, i] * s0, R[:, i] * s0 * np.cos(thg), R[:, i] * s0 * np.sin(thg))
        sx = px * sc + ox; sy = oy - py
        fn = (f - f.min()) / max(np.ptp(f), 1e-9)
        tfade = 0.10 + 0.90 * (np.arange(F) / F) ** 2.2
        wseg = BASE * 0.085 * (0.4 + 0.6 * fn[:-1]) * tfade[:-1]
        splat_segments(acc, sx[:-1], sy[:-1], sx[1:], sy[1:], wseg,
                       np.broadcast_to(HUES[i] * 0.9, (F - 1, 3)))

# exposures
for k, fi in enumerate(eidx):
    for i in range(2):
        cx3 = zt[fi, i] * s0
        Y = R[fi, i] * s0 * np.cos(th)
        Zc = R[fi, i] * s0 * np.sin(th)
        px, py, f = project(np.full(NTH, cx3), Y, Zc)
        sx = px * sc + ox; sy = oy - py
        fn = (f - f.min()) / max(np.ptp(f), 1e-9)
        shade = (0.30 + 0.70 * fn) ** 2.0
        wseg = BASE * bright[k] * (shade[:-1] + shade[1:]) * 0.5
        hue = HUES[i] * (1.0 + 0.8 * (k >= NEXPO - 2))
        # soft multi-stroke for body
        for off, ow in ((-2.4, 0.10), (-1.2, 0.22), (0.0, 0.40), (1.2, 0.22), (2.4, 0.10)):
            rr = (R[fi, i] * s0 + off * SS)
            Y2 = rr * np.cos(th); Z2 = rr * np.sin(th)
            px2, py2, f2 = project(np.full(NTH, cx3), Y2, Z2)
            sx2 = px2 * sc + ox; sy2 = oy - py2
            splat_segments(acc, sx2[:-1], sy2[:-1], sx2[1:], sy2[1:], wseg * ow,
                           np.broadcast_to(hue, (NTH - 1, 3)))

img = filmic(acc, k=1.0, gamma=0.88)
img = bloom(img, mask_lo=0.45, sigma=6 * SS, gain=0.7)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((WPX, HPX), Image.LANCZOS).save(OUT)
print("saved", OUT, "| cycles:", TTOT / TCYC)
