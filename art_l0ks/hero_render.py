#!/usr/bin/env python3
"""HERO: The Crowns of Crooked Trees — Steiner minimal trees of regular n-gons.
n=3..40 as concentric crowns. Cyan ghost = the D_n orbit of equally-best trees
(the symmetry the problem promises); gold = one blazing representative (the
choice a solution must make). The inhabited middle dies at n=6."""
import numpy as np, math, json, sys
import artlib as A
from steiner import full_component

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS = 2
S = FINAL*SS
rs = FINAL/1024.0

GOLD = np.array([1.00, 0.76, 0.34])
GOLD_HI = np.array([1.00, 0.90, 0.62])
CYAN = np.array([0.30, 0.68, 0.95])
BEAD = np.array([1.00, 0.95, 0.82])

def smt_geometry(n):
    """Return list of segments [(p,q),...] in unit-circumradius coords + steiner pts."""
    ang = 2*np.pi*np.arange(n)/n + np.pi/2   # vertex 0 at top
    V = np.stack([np.cos(ang), np.sin(ang)], axis=1)
    if n <= 5:
        L, edges, P = full_component(V)
        pts = {i: V[i] for i in range(n)}
        for i in range(len(P)):
            pts[n+i] = P[i]
        segs = [(pts[a], pts[b]) for a, b in edges]
        return segs, [P[i] for i in range(len(P))], L
    else:
        # rim: drop edge between vertex n-1 and 0 (the "crack" at top-left of vertex 0)
        segs = [(V[i], V[i+1]) for i in range(n-1)]
        return segs, [], (n-1)*2*math.sin(math.pi/n)

def rot(segs, th):
    c, s = math.cos(th), math.sin(th)
    R = np.array([[c, -s], [s, c]])
    return [(R@p, R@q) for p, q in segs]

def to_px(p, cx, cy, rad):
    return (cx + p[0]*rad, cy + p[1]*rad)

def draw_segs(buf, segs, cx, cy, rad, color, amp):
    for p, q in segs:
        a = to_px(p, cx, cy, rad); b = to_px(q, cx, cy, rad)
        A.polyline(buf, np.array([a, b]), color, amp=amp)

def main():
    print("hero render S =", S)
    ghost = A.canvas(S)
    gold = A.canvas(S)
    cx = cy = S/2
    NMIN, NMAX = 3, 40
    geo = {}
    for n in range(NMIN, NMAX+1):
        geo[n] = smt_geometry(n)
        print("geom n", n, "len", geo[n][2], flush=True)
    GA = 0.30
    base_amp = 1.15*rs**0.85
    def ring_radius(n):
        if n == 3: return 0.075*S
        if n == 4: return 0.150*S
        if n == 5: return 0.232*S
        return S*(0.292 + (0.468-0.292)*((n-6)/34.0)**0.92)
    for n in range(NMIN, NMAX+1):
        rad = ring_radius(n)
        segs, spts, L = geo[n]
        th0 = ((n-NMIN)*GA) % (2*np.pi)
        depth = (3.0/n)**0.52
        # ghost: orbit under rotation subgroup (n copies), equal total ink per ring
        if n == 3:
            orbit = []          # orbit size 1: the promise is kept, no ghost needed
        else:
            orbit = [rot(segs, th0 + 2*np.pi*k/n) for k in range(n)]
        g_scale = 0.55 if n == 4 else (0.30 if n == 5 else 0.55)
        g_amp = base_amp*depth*g_scale/max(1, len(orbit))
        for osegs in orbit:
            draw_segs(ghost, osegs, cx, cy, rad, CYAN, g_amp)
        # gold representative
        rsegs = rot(segs, th0)
        gboost = 1.9 if n == 3 else (1.18 if n <= 5 else 1.0)
        draw_segs(gold, rsegs, cx, cy, rad, GOLD, base_amp*depth*gboost)
        # the crack: for rim crowns, light the unchosen edge cold
        if n >= 6:
            ang0 = np.pi/2 + th0
            ang1 = 2*np.pi*(n-1)/n + np.pi/2 + th0
            p = np.array([math.cos(ang1), math.sin(ang1)])
            q = np.array([math.cos(ang0), math.sin(ang0)])
            A.polyline(ghost, np.array([to_px(p, cx, cy, rad), to_px(q, cx, cy, rad)]),
                       CYAN, amp=base_amp*(depth**0.3)*0.62)
            mid = 0.5*(p+q)
            A.star(ghost, cx+mid[0]*rad, cy+mid[1]*rad, CYAN,
                   amp=1.5*(depth**0.3)*rs*rs*0.75, rad=2.8*rs)
        # terminal beads
        ang = 2*np.pi*np.arange(n)/n + np.pi/2 + th0
        for aa in ang:
            x, y = cx + math.cos(aa)*rad, cy + math.sin(aa)*rad
            A.star(gold, x, y, BEAD, amp=0.22*depth*rs*rs, rad=1.3*rs)
        # steiner points: blazing stars (exist only n<=5)
        c, sn = math.cos(th0), math.sin(th0)
        R = np.array([[c, -sn], [sn, c]])
        for p in spts:
            q = R@p
            x, y = cx + q[0]*rad, cy + q[1]*rad
            A.star(gold, x, y, GOLD_HI, amp=2.2*rs*rs, rad=3.2*rs)
            A.star(gold, x, y, np.array([1., 1., 1.]), amp=0.9*rs*rs, rad=1.3*rs)
    # centre: the Fermat jewel is ring n=3 itself; add a soft center glow
    A.star(gold, cx, cy, GOLD_HI, amp=1.2*rs*rs, rad=5.0*rs)
    # compose
    ghost_b = A.bloom(ghost, sigmas=(1.6*rs, 7*rs), weights=(0.9, 0.30))
    gold_b = A.bloom(gold, sigmas=(1.6*rs, 8*rs, 26*rs), weights=(1.0, 0.30, 0.13))
    buf = ghost_b*0.9 + gold_b
    # warm fog in the inhabited middle
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    r2 = ((xx-cx)**2 + (yy-cy)**2)/(0.20*S)**2
    fog = np.exp(-r2*1.8)[..., None]*np.array([0.055, 0.038, 0.018], np.float32)
    buf = buf + fog
    img = A.tonemap(buf, k=1.55, gamma=0.94)
    if FINAL > 1400:
        F = FINAL
        img_small = np.asarray(A.save(img, '/tmp/tmp_hero.png', final=F)).astype(np.float32)/255.0
        GOLDt = (1.0, 0.86, 0.55); GREYt = (0.62, 0.66, 0.72); CYANt = (0.55, 0.78, 0.95)
        texts = [
          (0.028*F, 0.958*F, "THE CROWNS OF CROOKED TREES", int(0.0155*F), GOLDt, True, 'ls'),
          (0.028*F, 0.9735*F, "Steiner minimal trees of the regular n-gons, n = 3..40, each drawn with its whole orbit of equally-shortest rivals (cyan) and one chosen answer (gold)", int(0.0082*F), GREYt, False, 'ls'),
          (0.028*F, 0.9865*F, "n=3 keeps every symmetry of its question (orbit 1) - n=4 breaks to orbit 2 - n=5 to orbit 5 - from n=6 the interior is abandoned forever: the best network is the rim minus one edge (orbit n) - SMT/rim = 0.8660, 0.9107, 0.9728, then = 1", int(0.0082*F), GREYt, False, 'ls'),
          (0.972*F, 0.958*F, "THE SHAPE OF THE ANSWER - I", int(0.0092*F), CYANt, True, 'rs'),
          (0.972*F, 0.9725*F, "should symmetric problems have symmetric solutions?", int(0.0075*F), GREYt, False, 'rs'),
        ]
        out = A.bake_text(img_small, texts, F)
        A.save(out, OUT, final=None, dither=False)
    else:
        A.save(img, OUT, final=FINAL)
    print("saved", OUT)

OUT = f"hero_proto.png" if FINAL <= 1400 else "hero_final.png"
if __name__ == '__main__':
    main()
