"""world.py packing.npy out.bin [key=val] — a field of Apollonian pearl-balls on the cloth.
Ball list: (x, y, S); each ball keeps only pearls with world radius > rw (detail scales with size)."""
import sys, numpy as np
ARG = dict(a.split('=', 1) for a in sys.argv[3:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))
A = np.load(sys.argv[1])
WHEEL = np.array([(1.00, 0.52, 0.62), (1.00, 0.70, 0.52), (1.00, 0.86, 0.46), (0.76, 0.93, 0.50), (0.52, 0.90, 0.76),
                  (0.52, 0.80, 1.00), (0.64, 0.66, 1.00), (0.80, 0.60, 1.00), (1.00, 0.60, 0.90)])
lr = np.log(A[:, 3] / A[:, 3].max())
def tint_for(h0):
    h = (h0 + P('hk', 0.30) * (-lr)) % 1.0
    x = h * len(WHEEL); i = x.astype(int) % len(WHEEL); f = (x - np.floor(x))[:, None]
    return WHEEL[i] ** (1 - f) * WHEEL[(i + 1) % len(WHEEL)] ** f
glow = np.clip(-lr / 4, 0, 1) if P('glowmode', 'size') == 'size' else np.ones(len(lr))
balls = [tuple(map(float, b.split(':'))) for b in P('balls', '0:0:3').split(',')]
rw = P('rw', 0.012)
rows = []
for bi, (x, y, S) in enumerate(balls):
    keep = (A[:, 3] * S > rw) & (A[:, 4] > P('dropdepth', -1))
    if P('zcut', 9.0) < 9:
        zz = A[:, 2] * (-1 if P('flip', 0) else 1)
        keep &= zz < P('zcut', 9.0)
    AA = A[keep, :3] * np.array([1, 1, -1 if P('flip', 0) else 1])
    c = AA * S + np.array([x, y, S]); r = A[keep, 3] * S
    if P('huemode', 'size') == 'az':
        az = (np.arctan2(AA[:, 1], AA[:, 0]) / (2 * np.pi)) % 1.0
        h = (P('h0', 0.0) + az * P('turns', 1.0) + P('hk', 0.0) * (-lr[keep])) % 1.0
        xw = h * len(WHEEL); iw = xw.astype(int) % len(WHEEL); fw = (xw - np.floor(xw))[:, None]
        t = WHEEL[iw] ** (1 - fw) * WHEEL[(iw + 1) % len(WHEEL)] ** fw
    else:
        t = tint_for(P('h0', 0.55) + bi * P('dh', 0.11))[keep]
    t = 1 - P('sat', 1.0) * (1 - t)
    rows.append(np.column_stack([c, r, t, glow[keep]]))
    print('ball', bi, (x, y, S), 'pearls', keep.sum())
out = np.vstack(rows).astype(np.float64); out.tofile(sys.argv[2]); print('total', len(out))
