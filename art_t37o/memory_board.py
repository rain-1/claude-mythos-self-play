"""A perfect Memory board: 6 x 6 cards, 18 pairs, the 18 displacement vectors between twins are
exactly the 18 shortest vectors of the square lattice (|v|^2 <= 10), each used once.
Shape = length of the step, colourway = which of the directions of that length.
usage: python3 memory_board.py SIZE out.png [seed]"""
import sys, json, numpy as np
sys.path.insert(0, "math_shuffle")
import board as B
from mosaic import *

SHAPES = {1: "disc", 2: "diamond", 4: "ring", 5: "cross", 8: "frame", 9: "saltire", 10: "quatrefoil"}
WAYS = [("lap1", "mar0", 0), ("ter0", "apr0", 0), ("grn0", "tur5", 0), ("gol1", "lap0", 1)]

def shape(name, p, q):
    r = np.hypot(p, q); a = np.abs(p); b = np.abs(q)
    if name == "disc": return r < 0.52
    if name == "diamond": return a + b < 0.66
    if name == "ring": return (r < 0.62) & (r > 0.36)
    if name == "cross": return ((a < 0.17) | (b < 0.17)) & (np.maximum(a, b) < 0.62)
    if name == "frame": return (np.maximum(a, b) < 0.60) & (np.maximum(a, b) > 0.36)
    if name == "saltire": return (np.abs(a - b) < 0.24) & (np.maximum(a, b) < 0.56)
    if name == "quatrefoil": return (np.hypot(a - 0.30, b - 0.30) < 0.235)

def build(size, pairs, seed=6, counts=None):
    M = Mosaic(size, seed); S = M.S; X, Y = M.X, M.Y
    n = 6; side = 3290 * S; cell = side / n; h = cell / 32
    x0 = (size - side) / 2; x1 = x0 + side; y0 = 210 * S; y1 = y0 + side
    inbox = (X > x0) & (X < x1) & (Y > y0) & (Y < y1)
    V = B.vecs(n)
    # which motif does each cell carry
    motif = {}
    for (ax, ay, bx, by) in pairs:
        dx, dy = bx - ax, by - ay
        if (dx, dy) not in V: dx, dy = -dx, -dy
        L = dx * dx + dy * dy
        way = [v for v in V if v[0] ** 2 + v[1] ** 2 == L].index((dx, dy))
        motif[(ax, ay)] = motif[(bx, by)] = (L, way)
    assert len(set(motif.values())) == 18 and len(motif) == 36
    T = tess(X - x0, Y - y0, h, 1200, w=h, jit=0.36)
    ci = np.clip(np.floor((X - x0) / cell), 0, n - 1).astype(np.int32); cj = np.clip(np.floor((Y - y0) / cell), 0, n - 1).astype(np.int32)
    p = ((X - x0) / cell - ci - 0.5) * 2; q = ((Y - y0) / cell - cj - 0.5) * 2
    edge = np.maximum(np.abs(p), np.abs(q))
    col = np.zeros((size, size, 3), np.float32); mat = np.zeros((size, size), np.uint8)
    figs = np.zeros((size, size), bool)
    for (i, j), (L, way) in motif.items():
        m = (ci == i) & (cj == j)
        fgn, bgn, gold = WAYS[way]
        if L == 1 and way == 0: fgn = "red0"
        f = shape(SHAPES[L], p, q) & m
        col[m] = C(bgn); col[f] = C(fgn); mat[f] = gold
        figs |= f
    # each card: a marble margin and a dark fillet
    marg = edge > 1 - 3.0 / 16; fil = (edge > 1 - 3.0 / 16) & (edge < 1 - 2.0 / 16)
    col[marg] = C("mar1"); col[fil] = C("umb1"); mat[marg] = 0
    M.lay(inbox, T, col, mat=mat)
    M.tid ^= (figs.astype(np.uint32) * np.uint32(0x5bd1e995))
    M.cut(figs, width=2.2 * S + 0.6); M.cut(marg & ~fil, width=1.4 * S + .5); M.cut(fil, width=1.4 * S + .5)
    cells = ((ci + cj) % 2 == 0)
    M.cut(cells | ~inbox, width=2.0 * S + .5)
    # border and slab
    bw = 3 * h
    bo = (X > x0 - bw) & (X < x1 + bw) & (Y > y0 - bw) & (Y < y1 + bw) & ~inbox
    dd = np.maximum(np.maximum(x0 - X, X - x1), np.maximum(y0 - Y, Y - y1))
    horiz = np.maximum(y0 - Y, Y - y1) >= np.maximum(x0 - X, X - x1)
    T = tess(np.where(horiz, X, Y), dd + 50 * h, h, 505 + horiz.astype(np.int32), w=1.1 * h)
    colb = np.where(((T.row - 50) == 1)[..., None], C("umb1"), C("mar0"))
    M.lay(bo, T, colb); M.cut(horiz & bo); M.cut(inbox)
    out_m = ~inbox & ~bo
    slab = marble(size, seed + 9)
    l2 = "Shape is the length of the step and colour its direction."
    if counts: l2 += " There are %s such boards, %s up to the symmetries of the square." % counts
    txt = text_mask(size, [
        ("EIGHTEEN PAIRS, EIGHTEEN STEPS", size / 2, 3742 * S, 104 * S, "Regular", 15 * S),
        ("Thirty-six cards. No two pairs lie the same step apart, and the steps used are exactly the eighteen shortest there are.",
         size / 2, 3850 * S, 49 * S, "Italic", 0.6 * S),
        (l2, size / 2, 3922 * S, 49 * S, "Italic", 0.6 * S),
    ])
    slab = incise(slab, txt, S)
    dout = ndi.distance_transform_edt(out_m).astype(np.float32)
    slab *= (1 - 0.18 * np.exp(-dout / (10 * S)))[..., None]
    M.mat[out_m] = 9; M.rgb[out_m] = slab[out_m]
    return M

if __name__ == "__main__":
    size = int(sys.argv[1]); out = sys.argv[2]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    counts = tuple(sys.argv[4:6]) if len(sys.argv) > 5 else None
    pairs = B.find(6, 20, seed)
    json.dump(dict(n=6, pairs=pairs), open("math_shuffle/board_6_drawn.json", "w"))
    save(build(size, pairs, counts=counts).finish(), out)
