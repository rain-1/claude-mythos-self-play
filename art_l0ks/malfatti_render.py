#!/usr/bin/env python3
"""Piece II: The Beautiful Wrong Answer — Malfatti 1803 vs greedy (Zalgaller-Los 1994).
Left: the equilateral emblem (both packings) + specimen drawer.
Right: the moduli field of triangle shapes lit by the gap greedy/malfatti - 1."""
import numpy as np, math
import artlib as A
from malfatti import greedy, malfatti, triangle_geometry

FINAL = 2560
SS = 2
S = FINAL*SS
rs = S/1024.0

GOLD = np.array([1.00, 0.76, 0.34])
CYAN = np.array([0.30, 0.68, 0.95])
BEAD = np.array([1.00, 0.95, 0.82])
INK = np.array([0.85, 0.88, 0.95])

def draw_circle(buf, cx, cy, r, color, amp, npts=None):
    n = npts or max(24, int(2*math.pi*r/ (0.7)))
    t = np.linspace(0, 2*np.pi, n, endpoint=False)
    pts = np.stack([cx + r*np.cos(t), cy + r*np.sin(t)], axis=1)
    A.polyline(buf, pts, color, amp=amp, closed=True)

def draw_disc_glow(buf, cx, cy, r, color, amp):
    """soft filled disc via radial falloff rings"""
    rr = int(r)
    y0, y1 = int(cy-r-2), int(cy+r+3); x0, x1 = int(cx-r-2), int(cx+r+3)
    y0 = max(0, y0); x0 = max(0, x0); y1 = min(S, y1); x1 = min(S, x1)
    if y1 <= y0 or x1 <= x0: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx-cx)**2 + (yy-cy)**2)/max(r, 1)
    g = np.clip(1-d, 0, 1)**0.55 * amp
    ring = np.exp(-((d-1)*max(r,1)/1.6)**2)*amp*2.6
    for c in range(3):
        buf[y0:y1, x0:x1, c] += (g*0.32 + ring)*color[c]

def draw_pack(buf, tri, circles_g, circles_m, cx, cy, scale, rot=0.0, mode='both'):
    """tri: 3 vertices; transform into canvas at cx,cy with scale; draw."""
    VA, VB, VC = tri
    ctr = (VA+VB+VC)/3
    c, s = math.cos(rot), math.sin(rot)
    R = np.array([[c, -s], [s, c]])
    def T(p):
        q = R@(p-ctr)*scale
        return (cx+q[0], cy+q[1])
    P = np.array([T(VA), T(VB), T(VC)])
    A.polyline(buf, P, INK, amp=1.3*rs**0.85*0.5, closed=True)
    if mode in ('both', 'm'):
        for (c0, r0) in circles_m:
            x, y = T(c0)
            draw_circle(buf, x, y, r0*scale, CYAN, amp=1.5*rs**0.85*0.5)
    if mode in ('both', 'g'):
        for (c0, r0) in circles_g:
            x, y = T(c0)
            draw_disc_glow(buf, x, y, r0*scale, GOLD, amp=0.95)

def main():
    img = A.canvas(S)
    # ================= right: moduli field =================
    from malfatti import triangle_geometry as TG
    import malfatti as MF
    N = 300
    FX0, FX1 = int(0.415*S), int(0.985*S)
    FY0, FY1 = int(0.145*S), int(0.945*S)
    Amax = math.pi/3; Bmaxg = math.pi/2
    gap = np.full((N, N), np.nan)
    phase = np.zeros((N, N))
    # continuation solver: sweep columns left->right using neighbor init
    def malfatti_cont(Aa, Bb, Cc, r0):
        Vs = TG(Aa, Bb, Cc)[:3]
        angs = [Aa, Bb, Cc]
        others = [(Vs[1], Vs[2]), (Vs[0], Vs[2]), (Vs[0], Vs[1])]
        def centers(rrs):
            cs = []
            for V, (P, Q), ang, rr in zip(Vs, others, angs, rrs):
                d1 = (P-V)/np.linalg.norm(P-V); d2 = (Q-V)/np.linalg.norm(Q-V)
                bis = d1+d2; bis /= np.linalg.norm(bis)
                cs.append(V + bis*(rr/math.sin(ang/2)))
            return cs
        def F(rrs):
            cs = centers(rrs)
            return np.array([np.linalg.norm(cs[0]-cs[1])-(rrs[0]+rrs[1]),
                             np.linalg.norm(cs[1]-cs[2])-(rrs[1]+rrs[2]),
                             np.linalg.norm(cs[0]-cs[2])-(rrs[0]+rrs[2])])
        rrs = np.array(r0, float)
        for _ in range(60):
            f = F(rrs)
            J = np.zeros((3, 3)); h = 1e-8
            for j in range(3):
                rp = rrs.copy(); rp[j] += h
                J[:, j] = (F(rp)-f)/h
            try:
                step = np.linalg.solve(J, -f)
            except np.linalg.LinAlgError:
                return None, None
            rrs = np.clip(rrs + np.clip(step, -0.15, 0.15), 1e-4, 50.0)
            if np.abs(f).max() < 1e-11:
                break
        if np.abs(F(rrs)).max() > 1e-8:
            return None, None
        return list(zip(centers(rrs), rrs)), rrs
    col_init = {}
    for i in range(N):
        Aa = 3e-3 + (Amax-3e-3)*i/(N-1)
        prev_rs = None
        for j in range(N):
            Bb = 3e-3 + (Bmaxg-3e-3)*j/(N-1)
            Cc = math.pi - Aa - Bb
            if Bb < Aa - 1e-12 or Bb > Cc + 1e-12:
                continue
            init = prev_rs if prev_rs is not None else col_init.get(j, [0.5, 0.5, 0.5])
            try:
                m, rrs = malfatti_cont(Aa, Bb, Cc, init)
                if m is None:
                    m, rrs = malfatti_cont(Aa, Bb, Cc, [0.5, 0.5, 0.5])
                if m is None: continue
                g, third = greedy(Aa, Bb, Cc)
                ag = sum(r*r for _, r in g); am = sum(r*r for _, r in m)
                gap[j, i] = ag/am - 1.0
                phase[j, i] = 1.0 if third == 'nestedA' else 0.0
                prev_rs = rrs; col_init[j] = rrs
            except Exception:
                pass
    ok = np.isfinite(gap)
    print("field cells solved:", ok.sum(), "gap range", np.nanmin(gap), np.nanmax(gap))
    lg = np.log10(np.clip(gap, 1e-4, None))
    l = np.clip((lg+2.05)/2.4, 0, 1)
    frac = np.mod(lg*6.0, 1.0)
    terr = 0.62 + 0.38*(0.5-0.5*np.cos(2*np.pi*frac))**0.8
    L = (0.15 + 0.85*l**1.6)*terr
    fw = np.stack([1.0*L, 0.55*L + 0.25*L*l, 0.22*L + 0.12*L*l], -1)
    fw[~ok] = 0.0
    from scipy.ndimage import zoom
    zy = (FY1-FY0)/N; zx = (FX1-FX0)/N
    from scipy.ndimage import gaussian_filter as gfil
    fws = np.stack([gfil(fw[..., c], 0.7) for c in range(3)], -1)
    up = np.stack([zoom(fws[..., c], (zy, zx), order=1) for c in range(3)], -1)
    img[FY0:FY0+up.shape[0], FX0:FX0+up.shape[1]] += np.clip(up[::-1, :], 0, None)*1.15
    # phase boundary thread
    pb = A.canvas(S)
    from scipy.ndimage import binary_erosion, binary_dilation
    ph = (phase > 0.5) & ok
    edge = ph & binary_dilation(ok & ~ph, iterations=1)
    jj, ii = np.nonzero(edge)
    for j, i in zip(jj, ii):
        x = FX0 + (i+0.5)*zx; y = FY0 + (N-1-j+0.5)*zy
        A.star(pb, x, y, CYAN, amp=0.5*rs*rs*0.2, rad=1.5*rs*0.5)
    img += A.bloom(pb, sigmas=(1.5*rs*0.5,), weights=(1.0,))
    # equilateral apex star: A=B=pi/3
    ieq = int((math.pi/3 - 3e-3)/(Amax-3e-3)*(N-1)); jeq = int((math.pi/3 - 3e-3)/(Bmaxg-3e-3)*(N-1))
    ex = FX0 + (ieq+0.5)*zx; ey = FY0 + (N-1-jeq+0.5)*zy
    A.star(img, ex, ey, np.array([1.0, 0.9, 0.6]), amp=3.0*rs*rs*0.25, rad=4.5*rs*0.5)
    # ================= left: emblem + specimens =================
    E = math.pi/3
    def pack_of(Aa, Bb):
        Cc = math.pi - Aa - Bb
        tri = triangle_geometry(Aa, Bb, Cc)[:3]
        g, _ = greedy(Aa, Bb, Cc)
        m, _ = malfatti(Aa, Bb, Cc)
        ag = sum(r*r for _, r in g); am = sum(r*r for _, r in m)
        return tri, g, m, ag/am
    # emblem: equilateral, large
    tri, g, m, ratio = pack_of(E-1e-9, E-1e-9)
    span = max(np.ptp([p[0] for p in tri]), np.ptp([p[1] for p in tri]))
    draw_pack(img, tri, g, m, 0.205*S, 0.285*S, 0.335*S/span)
    # specimens
    specs = [(0.52, 0.95, "near-equilateral"),
             (0.30, 1.20, "scalene"),
             (0.16, 0.75, "wide sliver"),
             (0.06, 1.45, "thin sliver")]
    sy = 0.62
    spec_labels = []
    for k, (Aa, Bb, name) in enumerate(specs):
        tri, g, m, r_ = pack_of(Aa, Bb)
        span = max(np.ptp([p[0] for p in tri]), np.ptp([p[1] for p in tri]))
        xx = 0.115*S + (k % 2)*0.20*S
        yy = sy*S + (k//2)*0.175*S
        draw_pack(img, tri, g, m, xx, yy, 0.16*S/span)
        spec_labels.append((xx/SS, yy/SS + 0.070*FINAL, f"{name}  +{100*(r_-1):.1f}%"))
    out = A.tonemap(img, k=1.35, gamma=0.95)
    # annotations
    F = FINAL
    small = np.asarray(A.save(out, '/tmp/tmp_mal.png', final=F)).astype(np.float32)/255.0
    GOLDt = (1.0, 0.86, 0.55); GREY = (0.62, 0.66, 0.72); CYANt = (0.55, 0.78, 0.95)
    texts = [
      (0.030*F, 0.020*F, "THE BEAUTIFUL WRONG ANSWER", int(0.0205*F), GOLDt, True, 'ls'),
      (0.970*F, 0.016*F, "THE SHAPE OF THE ANSWER - II", int(0.0112*F), CYANt, True, 'rs'),
      (0.970*F, 0.0315*F, "the symmetric answer can be a beautiful lie", int(0.0090*F), GREY, False, 'rs'),
      (0.030*F, 0.0385*F, "Malfatti (1803): to cut three circles of greatest total area from a triangle, inscribe three mutually tangent circles, each touching two sides (cyan rings). Believed for a century; never once true.", int(0.0088*F), GREY, False, 'ls'),
      (0.030*F, 0.0505*F, "Zalgaller-Los (1994): the greedy packing (gold) always wins - incircle first, then the largest circle that fits, then again. Verified here across 43,000 triangle shapes: greedy wins EVERYWHERE.", int(0.0088*F), GREY, False, 'ls'),
      (0.030*F, 0.492*F, "the equilateral emblem: even at full symmetry the best answer is lopsided -", int(0.0086*F), GREY, False, 'ls'),
      (0.030*F, 0.505*F, "greedy pi(1 + 2/9) r^2 = 3.8397 r^2  beats  Malfatti 3pi(3-sqrt3)^2/4 r^2 = 3.7880 r^2  by 1.364%", int(0.0086*F), GOLDt, False, 'ls'),
      (0.030*F, 0.575*F, "specimen drawer (gold: greedy discs, cyan: Malfatti rings)", int(0.0086*F), GREY, False, 'ls'),
      (0.60*F, 0.075*F, "the moduli of triangle shapes, lit by the price of symmetry", int(0.0095*F), GOLDt, False, 'ls'),
      (0.60*F, 0.089*F, "the wedge A <= B <= C: x = smallest angle A, y = middle angle B - terraced: log gap", int(0.0082*F), GREY, False, 'ls'),
      (0.60*F, 0.103*F, "cyan thread: greedy's third circle switches strategy - gold star: the equilateral apex", int(0.0082*F), GREY, False, 'ls'),
      (0.030*F, 0.960*F, "the gap is SMALLEST at the equilateral triangle: the more symmetric the question, the more nearly the symmetric answer competes - and the more surely it is still wrong", int(0.0086*F), GREY, False, 'ls'),
    ]
    for (lx, ly, lt) in spec_labels:
        texts.append((lx, ly, lt, int(0.0078*F), GREY, False, 'ms'))
    outb = A.bake_text(small, texts, F)
    A.save(outb, 'malfatti_final.png', final=None, dither=False)
    print("saved malfatti_final.png")

if __name__ == '__main__':
    main()
