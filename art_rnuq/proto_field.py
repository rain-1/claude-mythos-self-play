"""proto_field.py — quick look at the local discrepancy function D(x,y) = A([0,x)x[0,y)) - N x y
for several point sets (Fibonacci lattice, Halton, random, Kronecker), raw grey, 512 each."""
import numpy as np
from PIL import Image
S = 512

def disc_field(px, py, S):
    N = len(px)
    H, _, _ = np.histogram2d(py, px, bins=S, range=[[0, 1], [0, 1]])
    A = np.cumsum(np.cumsum(H, 0), 1)                 # points with y<y_edge, x<x_edge
    yy, xx = (np.arange(1, S + 1) / S)[:, None], (np.arange(1, S + 1) / S)[None, :]
    return A - N * xx * yy

def fib(m):
    F = [1, 1]
    while len(F) <= m: F.append(F[-1] + F[-2])
    N, a = F[m], F[m - 1]
    i = np.arange(N)
    return (i + 0.5) / N, ((i * a) % N + 0.5) / N

def halton(N, b):
    out = np.zeros(N); f = 1.0 / b; i = np.arange(1, N + 1).astype(float)
    while i.max() > 0:
        out += f * (i % b); i = np.floor(i / b); f /= b
    return out

def kron(N, a1, a2):
    i = np.arange(N)
    return (i * a1) % 1.0, (i * a2) % 1.0

sets = {}
sets['fib4181'] = fib(19)
sets['halton'] = (halton(4181, 2), halton(4181, 3))
rng = np.random.default_rng(3); sets['random'] = (rng.random(4181), rng.random(4181))
sets['kron'] = kron(4181, np.sqrt(2) % 1, np.sqrt(3) % 1)
sets['fib10946'] = fib(21)
sets['kron_golden'] = kron(4181, (np.sqrt(5) - 1) / 2, np.sqrt(2) - 1)
tiles = []
for k, (px, py) in sets.items():
    D = disc_field(px, py, S)
    print(k, 'D range %.2f %.2f  std %.2f' % (D.min(), D.max(), D.std()))
    g = np.clip(0.5 + D / (2 * np.abs(D).max()), 0, 1)
    tiles.append((g * 255).astype(np.uint8))
row1 = np.concatenate(tiles[:3], 1); row2 = np.concatenate(tiles[3:], 1)
Image.fromarray(np.concatenate([row1, row2], 0)).save('cache/proto_field_grey.png')
print('saved')
