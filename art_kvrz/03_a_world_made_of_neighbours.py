"""
03 · A WORLD MADE OF NEIGHBOURS
===============================
Emergent geometry from pure relation.

A cloud of points is sampled on a sphere.  We then DISCARD every coordinate
and keep only the bare adjacency: who is among whose eight nearest neighbours.
From that relation alone -- a symmetric 0/1 matrix, no positions, no metric --
we recover a space, by diagonalising the graph Laplacian L = D - A and using
its three lowest non-trivial eigenvectors as coordinates (Laplacian
eigenmaps / spectral embedding).  For a sphere those eigenvectors ARE the
three linear harmonics, so the orb reappears, woven of its own edges.

Leibniz held that space is not a thing but "the order of coexistences" -- an
order read off the relations between monads that have, in themselves, no
position at all.  Here that is literal: forget where everything is, keep only
who lies near whom, and the world comes back.  Vertices are coloured by one
harmonic of the recovered space; the far side of the globe is dimmed so it
reads as solid.

Front-page seed: the philosophy.SE monadology / emergent-spacetime cluster
("Mutually grounded emergent monadology and applications to emergent
spacetime"; "Nothing and a Thing").  Technique new to this thread: spectral
(Laplacian-eigenmap) graph embedding -- geometry from adjacency.
"""
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh
from scipy.ndimage import gaussian_filter
from PIL import Image

def fib_sphere(N, seed=0, jit=0.4):
    rng = np.random.default_rng(seed)
    i = np.arange(N) + 0.5
    phi = np.arccos(1 - 2 * i / N); th = np.pi * (1 + 5 ** 0.5) * i
    p = np.column_stack([np.sin(phi) * np.cos(th), np.sin(phi) * np.sin(th), np.cos(phi)])
    p = p + rng.standard_normal((N, 3)) * (jit / np.sqrt(N))
    return p / np.linalg.norm(p, axis=1, keepdims=True)

def knn_graph(P, k=8):
    d, idx = cKDTree(P).query(P, k=k + 1)
    N = len(P); rows = np.repeat(np.arange(N), k); cols = idx[:, 1:].ravel()
    A = csr_matrix((np.ones_like(rows, float), (rows, cols)), shape=(N, N))
    return A.maximum(A.T)

def embed(A, ncomp=6):
    deg = np.asarray(A.sum(1)).ravel()
    dinv = diags(1 / np.sqrt(deg))
    Ln = (dinv @ (diags(deg) - A) @ dinv).tocsc()
    vals, vecs = eigsh(Ln, k=ncomp, which='SM')
    o = np.argsort(vals)
    return vals[o], vecs[:, o], deg

DIVERGE = np.array([
    [0.16, 0.40, 0.86], [0.33, 0.78, 0.93], [0.93, 0.93, 0.88],
    [0.98, 0.74, 0.32], [0.92, 0.30, 0.34],
])
def cmap(t):
    x = np.clip(t, 0, 1) * (len(DIVERGE) - 1)
    i = np.clip(x.astype(int), 0, len(DIVERGE) - 2); f = (x - i)[..., None]
    return DIVERGE[i] * (1 - f) + DIVERGE[i + 1] * f

def rot(a, b, c):
    Rx = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    Ry = np.array([[np.cos(b), 0, np.sin(b)], [0, 1, 0], [-np.sin(b), 0, np.cos(b)]])
    Rz = np.array([[np.cos(c), -np.sin(c), 0], [np.sin(c), np.cos(c), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def bilin_add(acc, px, py, vals):
    W = acc.shape[0]
    x0 = np.floor(px).astype(int); y0 = np.floor(py).astype(int)
    fx = px - x0; fy = py - y0
    for dx, wx in ((0, 1 - fx), (1, fx)):
        for dy, wy in ((0, 1 - fy), (1, fy)):
            xi = x0 + dx; yi = y0 + dy
            ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < W)
            np.add.at(acc, (yi[ok], xi[ok]), vals[ok] * (wx * wy)[ok][:, None])

def render(P3, A, colvec, S=2048, supers=2, ang=(0.5, 0.7, 0.15), persp=0.35,
           node_amp=0.30, edge_amp=0.52, glow=0.42, k=1.7, gamma=0.85):
    W = S * supers; sc = W / 2000.0
    X = P3 @ rot(*ang).T
    z = X[:, 2]; zc = (z - z.min()) / (np.ptp(z) + 1e-9)
    scale = 1.0 / (1.0 - persp * (X[:, 2] / np.abs(X).max()))
    sx = X[:, 0] * scale; sy = X[:, 1] * scale
    m = max(np.abs(sx).max(), np.abs(sy).max()) * 1.1
    px = (sx / m * 0.5 + 0.5) * (W - 1); py = (sy / m * 0.5 + 0.5) * (W - 1)
    cols = cmap((colvec - colvec.min()) / (np.ptp(colvec) + 1e-9))
    acc = np.zeros((W, W, 3), np.float32)
    C = A.tocoo(); e = C.row < C.col; ei, ej = C.row[e], C.col[e]
    seg = np.hypot(px[ei] - px[ej], py[ei] - py[ej])
    nmax = max(2, int(np.percentile(seg, 98)) + 1)
    backdim = 0.12
    for t in np.linspace(0, 1, nmax):
        ex = px[ei] * (1 - t) + px[ej] * t; ey = py[ei] * (1 - t) + py[ej] * t
        ec = cols[ei] * (1 - t) + cols[ej] * t
        ezt = zc[ei] * (1 - t) + zc[ej] * t
        bright = (backdim + (1 - backdim) * ezt ** 1.6)[:, None] * ec * (edge_amp / nmax * 6)
        bilin_add(acc, ex, ey, bright)
    bilin_add(acc, px, py, (0.25 + 0.75 * zc ** 1.6)[:, None] * cols * node_amp)
    base = gaussian_filter(acc, (1.0 * sc, 1.0 * sc, 0))
    g = gaussian_filter(acc, (6.0 * sc, 6.0 * sc, 0)) * glow
    img = base + g
    img = img / (img.max() + 1e-9)
    img = 1.0 - np.exp(-k * img * 4)
    img = np.power(np.clip(img, 0, 1), gamma)
    return Image.fromarray((img * 255).astype(np.uint8), "RGB").resize((S, S), Image.LANCZOS)

if __name__ == "__main__":
    import sys
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 2048
    N, k, seed = 2000, 6, 2
    print(f"sampling {N} points, building kNN graph, discarding coordinates ...")
    v = fib_sphere(N, seed)
    A = knn_graph(v, k)
    vals, vecs, deg = embed(A, 6)
    P3 = vecs[:, 1:4]; P3 = P3 / P3.std(0)
    r = np.linalg.norm(P3, axis=1)
    print("recovered radius CV =", round(r.std() / r.mean(), 4),
          "(low = clean sphere) | eigs", np.round(vals, 4))
    im = render(P3, A, vecs[:, 1], S=S, ang=(0.5, 0.7, 0.15))
    im.save("03_a_world_made_of_neighbours.png")
    print("saved 03_a_world_made_of_neighbours.png", im.size)
