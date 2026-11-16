"""lace.py -- Hamiltonian cycles of grid graphs as threads on a sun print."""
import subprocess, os, sys, numpy as np
from collections import defaultdict
import cyano
HERE = os.path.dirname(os.path.abspath(__file__))
HC = os.path.join(HERE, 'math_loop', 'hc')

def hc(*args):
    return subprocess.run([HC] + [str(a) for a in args], capture_output=True, text=True).stdout

def cells(dels): return [f'{r},{c}' for r, c in dels]

def count(m, n, dels=()): return int(hc('count', m, n, *cells(dels)))

def unique_cycle(m, n, dels):
    out = hc('cycle', m, n, *cells(dels))
    assert not out.startswith('count'), out
    return [tuple(map(int, l.split())) for l in out.strip().splitlines()]

def samples(m, n, K, seed, dels=()):
    out = hc('sample', m, n, K, seed, *cells(dels))
    res = []
    for l in out.strip().splitlines():
        v = list(map(int, l.split())); res.append([tuple(v[i:i + 4]) for i in range(0, len(v), 4)])
    return res

def order(edges):
    adj = defaultdict(list)
    for r, c, r2, c2 in edges: adj[(r, c)].append((r2, c2)); adj[(r2, c2)].append((r, c))
    start = min(adj); loop = [start]; prev = None; x = start
    while True:
        a, b = adj[x]; y = a if a != prev else b
        if y == start: break
        loop.append(y); prev, x = x, y
    assert len(loop) == len(adj)
    return loop

def loop_points(loop, pos, corner=0.30):
    """polyline through the vertices with corners of radius ~corner cells"""
    P = np.array([pos[v] for v in loop], float)
    Q = np.roll(P, -1, axis=0)
    pts = np.empty((3 * len(P), 2))
    pts[0::3] = P; pts[1::3] = P + corner * (Q - P) * 1.0; pts[2::3] = Q - corner * (Q - P)
    # drop the vertices themselves so Chaikin rounds each corner between the two guide points
    ctrl = np.empty((2 * len(P), 2)); ctrl[0::2] = P + corner * (Q - P); ctrl[1::2] = Q - corner * (Q - P)
    C = cyano.chaikin(ctrl, closed=True, it=3)
    return np.vstack([C, C[:1]])

class Grid:
    """an m x n array of pin positions inside a box (fractions of the sheet), with a hand's jitter"""
    def __init__(self, sheet, m, n, box, seed=0, jitter=0.035, rot=0.0):
        x0, y0, x1, y1 = [v * sheet.n for v in box]
        self.cell = min((x1 - x0) / n, (y1 - y0) / m)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rng = np.random.default_rng(seed)
        self.pos = {}
        ca, sa = np.cos(rot), np.sin(rot)
        # slow warp: the cloth is not perfectly square on the paper
        wx = rng.normal(0, 1, (2, 2)); wy = rng.normal(0, 1, (2, 2))
        for r in range(m):
            for c in range(n):
                u = (c - (n - 1) / 2); v = (r - (m - 1) / 2)
                du = 0.05 * (wx[0, 0] * np.sin(0.9 * v / m * 3 + wx[0, 1]) ) + rng.normal(0, jitter)
                dv = 0.05 * (wy[0, 0] * np.sin(0.9 * u / n * 3 + wy[0, 1]) ) + rng.normal(0, jitter)
                x = (u + du) * self.cell; y = (v + dv) * self.cell
                self.pos[(r, c)] = (cx + ca * x - sa * y, cy + sa * x + ca * y)
        self.m, self.n = m, n

def draw_loop(sheet, draw, ss, grid, edges, width=0.18, phase=0.0, corner=0.22):
    P = loop_points(order(edges), grid.pos, corner)
    cyano.draw_cord(draw, P, width * grid.cell, ss, phase=phase)

def draw_pins(draw, ss, grid, skip=(), r=0.055):
    for v, (x, y) in grid.pos.items():
        if v in skip: continue
        R = r * grid.cell * ss
        draw.ellipse([x * ss - R, y * ss - R, x * ss + R, y * ss + R], fill=255)

def lay_buttons(sheet, grid, dels, seed=0, r=0.40):
    rng = np.random.default_rng(seed)
    for i, v in enumerate(sorted(dels)):
        x, y = grid.pos[v]
        rr = r * grid.cell * rng.uniform(0.88, 1.08)
        T = cyano.button(sheet, x + rng.normal(0, 0.03) * grid.cell, y + rng.normal(0, 0.03) * grid.cell, rr,
                         holes=4 if rng.random() < 0.6 else 2, rng=rng, kind=int(rng.random() < 0.45))
        from scipy import ndimage as ndi
        # a button stands 2-3 mm off the paper: soft edge
        ys, xs = np.where(T < 0.999)
        if len(ys):
            sl = (slice(max(0, ys.min() - 8), ys.max() + 9), slice(max(0, xs.min() - 8), xs.max() + 9))
            T[sl] = ndi.gaussian_filter(T[sl], 0.9 * sheet.S)
        sheet.lay_transmission(T)

def lift_field(sheet, seed, amount=0.5, cell=120):
    rng = np.random.default_rng(seed)
    f = cyano.fbm((sheet.n, sheet.n), cell * sheet.S, rng, octaves=2)
    return np.clip((f - 0.35) * 2.0, 0, 1).astype(np.float32) * amount
