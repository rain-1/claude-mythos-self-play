"""PANEL 3 -- The Braid of Forgetting.
Three verified monodromy loops of the governing cubic, drawn as an armillary:
  ring A (inner):  loop around the wall c=0            -> identity  (three rings of memory; the cyan strand is the sheet from infinity)
  ring B (middle): loop around one branch point        -> (1 2)     (two pasts fuse into one double thread)
  ring C (outer):  loop around both real branch points -> (0 1 2)   (three pasts, one thread)
Roots continued numerically; permutations printed and verified to 1e-15."""
import numpy as np, kit, mono
from scipy.ndimage import gaussian_filter
import sys

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS = 2
S = FINAL * SS
rs = FINAL / 1024.0
H = W = S

N = 9000
rings = []
pA, sA, eA = mono.continue_loop(0.0, 0.2548, N)
pB, sB, eB = mono.continue_loop(0.509515, 0.1783, N)
pC, sC, eC = mono.continue_loop(-0.0657635, 0.719098, N)
print("perms:", sA, sB, sC, "errs", f"{eA:.1e} {eB:.1e} {eC:.1e}")
assert sA == (0, 1, 2) and sB == (0, 2, 1) and sC == (2, 0, 1)

def cycles(sigma):
    seen, out = set(), []
    for i in range(3):
        if i in seen: continue
        cyc, j = [], i
        while j not in seen:
            seen.add(j); cyc.append(j); j = sigma[j]
        out.append(cyc)
    return out

# ring geometry: (paths, sigma, R, tilt matrix, cross amplitude)
def rotx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def rotz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])

RINGS = [
    (pA, sA, 0.30, rotx(np.deg2rad(90)) @ rotz(np.deg2rad(0)), 0.16),
    (pB, sB, 0.65, rotx(np.deg2rad(58)) @ rotz(np.deg2rad(18)), 0.22),
    (pC, sC, 1.00, rotx(np.deg2rad(22)) @ rotz(np.deg2rad(-12)), 0.26),
]

CAM = np.array([0.0, 1.55, 3.7]); F = 2.6
TGT = np.array([0.0, 0.0, 0.0])
fw = TGT - CAM; fw = fw / np.linalg.norm(fw)
up0 = np.array([0.0, 1.0, 0.0])
rt = np.cross(fw, up0); rt = rt / np.linalg.norm(rt)
upv = np.cross(rt, fw)
def project(P):
    Q = P - CAM
    zz = Q @ fw
    xx = (Q @ rt) / zz * F
    yy = (Q @ upv) / zz * F
    px = (xx * 0.5 + 0.5) * W
    py = (0.5 - yy * 0.5) * H
    return np.stack([px, py], -1), zz

buf = np.zeros((H, W, 3), np.float32)
ink = np.zeros((H, W, 3), np.float32)

CYCCOL = {
    'spec': np.array([1.0, 0.82, 0.42]),     # untouched sheet: gold
    'inf':  kit.CYAN,                         # the sheet from infinity
}

th = np.linspace(0, 2 * np.pi, N + 1)
for ri, (paths, sigma, R, M, amp) in enumerate(RINGS):
    mu = paths.mean()
    sc = np.median(np.abs(paths - mu)) * 2.2
    that = (paths - mu) / sc
    # asinh compression keeps the infinity strand visible but bounded
    r_c = np.arcsinh(np.abs(that) * 1.0) / 1.0
    that = np.where(np.abs(that) > 1e-12, that / np.abs(that), 0) * r_c
    # pinch glow: brightness rises where two sheets draw near
    d01 = np.abs(paths[:, 0] - paths[:, 1])
    d02 = np.abs(paths[:, 0] - paths[:, 2])
    d12 = np.abs(paths[:, 1] - paths[:, 2])
    dmin = np.minimum(np.minimum(d01, d02), d12)
    pinch = 1.0 + 3.4 * np.exp(-(dmin / (0.30 * np.median(dmin))) ** 2)
    # faint dial (the loop itself)
    dial = np.stack([R * np.cos(th), np.zeros_like(th), R * np.sin(th)], -1) @ M.T
    dpx, dz = project(dial)
    kit.line_splat(ink, dpx, np.array([0.5, 0.35, 0.18]), amp_per_px=0.028)
    for cyc in cycles(sigma):
        L = len(cyc)
        # stitched path: follow strand cyc[0] through L loops
        seq = []
        j = cyc[0]
        for rep in range(L):
            seq.append(that[:-1, j] if rep < L - 1 else that[:, j])
            pin = pinch[:-1] if rep < L - 1 else pinch
            j = int(np.argmin(np.abs(that[0] - that[-1, j]))) if L > 1 else j
        strand = np.concatenate(seq)
        pinL = np.concatenate([pinch[:-1]] * (L - 1) + [pinch]) if L > 1 else pinch
        thL = np.concatenate([th[:-1] + 2 * np.pi * k for k in range(L - 1)] + [th + 2 * np.pi * (L - 1)]) if L > 1 else th
        # 3-D embed
        rad = R + amp * R * strand.real / 0.85
        pos = np.stack([rad * np.cos(thL / L * (2 * np.pi) / (2 * np.pi)), np.zeros_like(rad), np.zeros_like(rad)], -1)
        ang = thL / L  # wrap L loops onto one circuit? NO -- keep physical loops
        ang = thL % (2 * np.pi)
        pos = np.stack([rad * np.cos(ang), amp * R * strand.imag / 0.85, rad * np.sin(ang)], -1) @ M.T
        ppx, pz = project(pos)
        # color
        if L == 3:
            TRIPLE = [(0.00, (1.00, 0.80, 0.35)), (0.25, (0.35, 0.80, 0.70)),
                      (0.50, (0.45, 0.50, 0.95)), (0.75, (0.95, 0.42, 0.28)),
                      (1.00, (1.00, 0.80, 0.35))]
            cols = kit.ramp(np.linspace(0, 1, len(strand)), TRIPLE) * 1.05
        elif L == 2:
            cols = kit.ramp(0.5 + 0.5 * np.sin(np.linspace(0, np.pi, len(strand))),
                            [(0.0, (0.85, 0.30, 0.10)), (1.0, (1.0, 0.85, 0.45))])
        else:
            big = np.median(np.abs(paths[:, cyc[0]] - mu)) > 2.5 * sc
            cols = np.tile(CYCCOL['inf'] if big else CYCCOL['spec'], (len(strand), 1))
        depth = np.clip(2.4 / (pz + 1e-6), 0.25, 1.6) ** 1.2
        w_amp = 0.55 * pinL * depth
        # draw in chunks of constant color/amp
        CH = 60
        for s0 in range(0, len(strand) - 1, CH):
            s1 = min(len(strand), s0 + CH + 1)
            kit.line_splat(ink, ppx[s0:s1], cols[(s0 + s1) // 2],
                           amp_per_px=float(w_amp[(s0 + s1) // 2]))

# fatten strokes so they survive the downscale, then amplitude-restored halo
ink = kit.fatten(ink, 1.1 * SS * rs)
ink = gaussian_filter(ink, (0.6 * SS, 0.6 * SS, 0))
def typ(v):
    m = v[v > 0.02 * v.max()]
    return np.percentile(m, 70) if m.size else 1.0
halo = gaussian_filter(ink, (3.5 * SS * rs, 3.5 * SS * rs, 0))
halo = halo * (0.55 * typ(ink) / (typ(halo) + 1e-9))
ink = ink + halo
# the one present: q* sits at w=0, the exact center of every loop
kit.splat_star(ink, (W / 2, H / 2), kit.GOLD, 2.6, 3.0 * SS * rs, 14 * SS * rs, 0.5)
lum = ink.max(-1, keepdims=True)
knee = (1 - np.exp(-1.05 * lum)) / (1.05 * lum + 1e-9)
buf += ink * knee * 1.7
buf = kit.bloom(buf, 6 * SS * rs, 0.65, thresh=0.55)
out = kit.filmic(buf, 1.5, 0.94)
kit.save(out, f"braid_{FINAL}.png", down=SS)
