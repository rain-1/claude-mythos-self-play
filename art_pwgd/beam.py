"""beam.py — the coral ray through all three marbles (plane z = 1 of the centres).
Returns world polylines for each segment: straight runs outside, exact arcs inside."""
import numpy as np
from grin import lens_map, nrm

def inside_arc(kind, P, d, n=80):
    """unit-ball arc from P (entry, unit) with inward dir d -> points (n,3)"""
    if kind == 'lune':
        s = np.linspace(0, np.pi / 2, n)
        return np.cos(s)[:, None] * P + np.sin(s)[:, None] * d
    if kind == 'fish':
        # circle through P and -P with tangent d at P (in plane of P, d)
        pd = P @ d
        e = nrm(d - pd * P)             # in-plane unit ⟂ P
        th = np.arccos(np.clip(-pd, -1, 1))   # angle between d and chord (-P)
        if th < 1e-6: s = np.linspace(0, 1, n); return (1 - 2 * s)[:, None] * P
        # centre c = k*e, with |P - c| = rho and tangent at P ⟂ (P-c)
        # tangent d ⟂ (P - c): d·P - k d·e = 0 -> k = pd/(d·e)
        k = pd / (d @ e); c = k * e; rho = np.sqrt(1 + k * k)
        a0 = np.arctan2((P - c) @ e, (P - c) @ P); a1 = np.arctan2((-P - c) @ e, (-P - c) @ P)
        # choose the arc that stays inside (passes near the origin)
        cand = []
        for a_end in (a1, a1 + 2 * np.pi, a1 - 2 * np.pi):
            a = np.linspace(a0, a_end, n)
            pts = c + rho * (np.cos(a)[:, None] * P + np.sin(a)[:, None] * e)
            cand.append((np.max(np.linalg.norm(pts, axis=1)), abs(a_end - a0), pts))
        cand.sort(key=lambda t: (t[0] > 1 + 1e-6, t[1]))
        return cand[0][2]
    if kind == 'eaton':
        # Kepler ellipse a=1, focus 0, major axis along d, P at end of minor axis; parametrise by
        # eccentric anomaly: x = a(cos E - e) u + b sin E w  (u = periapsis dir, w ⟂)
        pd = P @ d; b = np.sqrt(max(1 - pd * pd, 0)); e = np.sqrt(max(1 - b * b, 0))
        # minor-axis end: cos E = e -> point (0? ) x = (e - e)u ... = b sin E w ; so P = ±b w + 0*u? no:
        # with focus at origin, centre at -a e u; minor-axis ends are centre ± b w = -e u ± b w
        # P = -e u + b w  and travel direction at P is +-u ; inward motion d -> pick u = d.
        u = d.copy(); w = nrm(P + e * u) if b > 1e-9 else nrm(np.cross(d, [0, 0, 1.0]))
        # P corresponds to E with cosE - e = -e -> cosE = 0, sinE = 1 (E = pi/2); velocity there ∝ -sinE u ... sign
        # dx/dE = -sinE u + b cosE w -> at E=pi/2: -u. We need +u => run E decreasing: pi/2 -> -pi/2
        E = np.linspace(np.pi / 2, -np.pi / 2, n)
        return (np.cos(E) - e)[:, None] * u + (b * np.sin(E))[:, None] * w
    raise ValueError

def trace(balls, o, d, maxhits=8, far=40):
    segs = []; seq = []
    o = np.array(o, float); d = nrm(np.array(d, float))
    for _ in range(maxhits):
        best, who = np.inf, -1
        for i, B in enumerate(balls):
            oc = o - B['c']; b = oc @ d; cc = oc @ oc - B['r'] ** 2; disc = b * b - cc
            if disc > 0:
                t = -b - np.sqrt(disc)
                if 1e-6 < t < best: best, who = t, i
        if who < 0:
            segs.append(('line', np.array([o, o + far * d]))); break
        X = o + best * d
        segs.append(('line', np.array([o, X])))
        B = balls[who]; P = nrm((X - B['c']) / B['r'])
        Xe, De, L = lens_map(B['kind'], P[None], d[None])
        arc = B['c'] + B['r'] * inside_arc(B['kind'], P, d)
        segs.append(('arc', arc, who)); seq.append(who)
        o = B['c'] + B['r'] * Xe[0] + De[0] * 1e-6; d = De[0]
    return segs, seq

if __name__ == '__main__':
    from grin import lens_map
    balls = [dict(c=np.array([-2.4, 0.6, 1.0]), r=1.0, kind='lune'), dict(c=np.array([0.1, -1.5, 1.0]), r=1.0, kind='fish'),
             dict(c=np.array([2.2, 0.9, 1.0]), r=1.0, kind='eaton')]
    # check arcs end at the exit points
    rng = np.random.default_rng(0)
    for k in ['lune', 'fish', 'eaton']:
        P = nrm(rng.standard_normal(3)); d = nrm(rng.standard_normal(3)); d = -d if d @ P > 0 else d
        a = inside_arc(k, P, d); X, D, L = lens_map(k, P[None], d[None])
        print(k, 'end err', np.linalg.norm(a[-1] - X[0]), 'max r', np.linalg.norm(a, axis=1).max(), 'len', np.linalg.norm(np.diff(a, axis=0), axis=1).sum(), L[0])
    res = []
    for y0 in np.linspace(-8, 8, 321):
        for ang in np.linspace(-1.2, 1.2, 241):
            o = np.array([-9.0, y0, 1.0]); d = np.array([np.cos(ang), np.sin(ang), 0])
            segs, seq = trace(balls, o, d)
            if len(set(seq)) == 3:
                res.append((len(seq), y0, ang, seq))
    print(len(res))
    from collections import Counter
    print(Counter(tuple(r[3]) for r in res).most_common(15))
