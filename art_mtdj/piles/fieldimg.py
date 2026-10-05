import numpy as np
from scipy.ndimage import map_coordinates
def field_grid(N):
    v = np.load(f'field_{N}.npy'); idx = np.load(f'fieldidx_{N}.npy')
    G = np.full((N + 1, N + 1), np.nan); G[idx[:, 0], idx[:, 1]] = v
    return G
def sample(G, N, S, scale=0.45, cy=0.55, order=1):
    """pixel -> barycentric (a,b,c) with vertices at angles 90,210,330 degrees"""
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    X = (xx / S - 0.5) / scale; Y = (cy - yy / S) / scale
    e = np.array([[np.cos(t), np.sin(t)] for t in np.pi / 2 + 2 * np.pi * np.arange(3) / 3])
    # solve a e0 + b e1 + c e2 = (X,Y)*N with a+b+c=N
    M = np.array([[e[0, 0], e[1, 0], e[2, 0]], [e[0, 1], e[1, 1], e[2, 1]], [1, 1, 1]])
    Mi = np.linalg.inv(M)
    rhs = np.stack([X * N, Y * N, np.full_like(X, N)], 0).reshape(3, -1)
    abc = (Mi @ rhs).reshape(3, S, S)
    inside = (abc >= -1e-9).all(0)
    Gf = np.where(np.isnan(G), 0, G)
    import itertools
    val = np.zeros(abc.shape[1:])
    for p in itertools.permutations(range(3)):
        val += map_coordinates(Gf, [abc[p[0]], abc[p[1]]], order=order, mode='nearest')
    val /= 6
    return val, inside, abc
