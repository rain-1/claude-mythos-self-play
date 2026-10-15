# cayley.py — all 125 labelled trees on five glass beads, as a five-fold rose window.
# sector k (one per bead colour) holds: the star centred on k, the 12 paths whose middle bead is k,
# and the 12 forks (spiders 2,1,1) whose branch bead is k.  5 + 60 + 60 = 125 = 5^3 (Cayley).
import numpy as np, itertools, sys
from beadscene import Scene, GLASS
GLASS0 = dict(GLASS)
COLS = ['strawberry', 'butter', 'mint', 'sky', 'lilac']
def prufer_trees(n=5):
    T = set()
    for code in itertools.product(range(n), repeat=n - 2):
        deg = [1] * n
        for c in code: deg[c] += 1
        E = []; code = list(code)
        for c in code:
            leaf = min(i for i in range(n) if deg[i] == 1); E.append(tuple(sorted((leaf, c)))); deg[leaf] -= 1; deg[c] -= 1
        u, v = [i for i in range(n) if deg[i] == 1]; E.append((u, v)); T.add(tuple(sorted(E)))
    return T
def build(fn='cayley.bin', s=2.75, Rs=11.0, Rp=24.5, Rf=42.5, rot=np.pi / 2, thread_col=(0.95, 0.92, 0.95), rt=0.11, legend=True, ab=0.7, sc=1.45):
    import beadscene
    for kk in list(beadscene.GLASS): beadscene.GLASS[kk] = tuple(ab * v for v in GLASS0[kk])
    trees = prufer_trees(); assert len(trees) == 125
    S = Scene(); r = 1.0
    def bead(p, k): S.bead(p[0], p[1], r, 'glass', COLS[k])
    def edge(p, q): S.thread([p, q], r, rt, col=thread_col, closed=False)
    stars, paths, forks = {}, {k: [] for k in range(5)}, {k: [] for k in range(5)}
    for E in trees:
        deg = np.zeros(5, int)
        for a, b in E: deg[a] += 1; deg[b] += 1
        adj = {i: [] for i in range(5)}
        for a, b in E: adj[a].append(b); adj[b].append(a)
        if deg.max() == 4: stars[int(deg.argmax())] = E
        elif deg.max() == 2:   # path: walk from the smaller end
            ends = [i for i in range(5) if deg[i] == 1]; seq = [min(ends)]
            while len(seq) < 5: seq.append([j for j in adj[seq[-1]] if j not in seq][0])
            paths[seq[2]].append(seq)
        else:
            c = int(deg.argmax()); x = [j for j in adj[c] if deg[j] == 2][0]; y = [j for j in adj[x] if j != c][0]
            u, v = sorted(j for j in adj[c] if j != x); forks[c].append((c, x, y, u, v))
    count = len(stars) + sum(map(len, paths.values())) + sum(map(len, forks.values())); assert count == 125
    def P(R, a): return (R * np.cos(a), R * np.sin(a))
    for k in range(5):
        a0 = rot - 2 * np.pi * k / 5          # sector centre (clockwise from the top)
        # star
        c = np.array(P(Rs, a0)); S.bead(c[0], c[1], sc, 'glass', COLS[k])
        others = [j for j in range(5) if j != k]
        for i, j in enumerate(others):
            ang = a0 + np.pi / 4 + i * np.pi / 2; q = c + sc * s * np.array([np.cos(ang), np.sin(ang)]); S.bead(q[0], q[1], sc, 'glass', COLS[j])
            S.thread([c, q], sc, rt * sc, col=thread_col, closed=False)
        # paths: 12 radial spokes, ordered so neighbours share colours
        L = sorted(paths[k], key=lambda q: (min(q[1], q[3]), max(q[1], q[3]), q[0] if q[1] < q[3] else q[4]))
        L = [q if q[1] < q[3] else q[::-1] for q in L]
        for i, q in enumerate(L):
            a = a0 + (i - 5.5) * 2 * np.pi / 60
            pts = [np.array(P(Rp + s * j, a)) for j in range(5)]
            for j in range(5): bead(pts[j], q[j])
            for j in range(4): edge(pts[j], pts[j + 1])
        F = sorted(forks[k], key=lambda q: (q[1], q[2]))
        for i, (c_, x, y, u, v) in enumerate(F):
            a = a0 + (i - 5.5) * 2 * np.pi / 60
            ry, rx, rc = Rf, Rf + s, Rf + 2 * s
            py, px, pc = np.array(P(ry, a)), np.array(P(rx, a)), np.array(P(rc, a))
            dr = np.array([np.cos(a), np.sin(a)]); dt = np.array([-np.sin(a), np.cos(a)])
            pu = pc + s * (np.cos(0.62) * dr + np.sin(0.62) * dt); pv = pc + s * (np.cos(0.62) * dr - np.sin(0.62) * dt)
            for p, kk in [(py, y), (px, x), (pc, c_), (pu, u), (pv, v)]: bead(p, kk)
            edge(py, px); edge(px, pc); edge(pc, pu); edge(pc, pv)
    if legend:   # the five loose beads at the centre: the vertices, before any tree is chosen
        for k in range(5): p = P(3.6, rot - 2 * np.pi * k / 5); S.bead(p[0], p[1], 1.2, 'glass', COLS[k])
    S.save(fn)
if __name__ == '__main__':
    build()
