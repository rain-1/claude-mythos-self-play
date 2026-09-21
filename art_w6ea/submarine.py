"""submarine.py — the submarine bombing game (MO 515379 / folklore).

A submarine sits at an unknown integer position a at time 0 and moves with an
unknown integer velocity b.  At each integer time t = 1, 2, 3, ... the hunter
bombs ONE integer.  The hunter always wins: fix a bijection n -> (a_n, b_n) of
N onto Z^2 and at time n bomb a_n + b_n * n.  Submarine (a,b) dies at time
T(a,b) = the index n with (a_n, b_n) = (a, b).

This module builds the enumeration, the capture-time field T, and certificates.
Everything here is exact integer arithmetic.
"""
import numpy as np


# ---------------------------------------------------------------- enumerations
def shell_order(M):
    """max-norm shells: all (a,b) with max(|a|,|b|) = m, m = 0..M, ring by ring.
    Returns an (N,2) int array in enumeration order."""
    pts = [(0, 0)]
    for m in range(1, M + 1):
        ring = []
        for a in range(-m, m + 1):          # top edge  b = +m
            ring.append((a, m))
        for b in range(m - 1, -m, -1):      # right edge a = +m
            ring.append((m, b))
        for a in range(m, -m - 1, -1):      # bottom edge b = -m
            ring.append((a, -m))
        for b in range(-m + 1, m):          # left edge  a = -m
            ring.append((-m, b))
        pts.extend(ring)
    return np.array(pts, np.int64)


def diagonal_order(M):
    """L1 shells (Cantor-style diagonals): |a| + |b| = m, m = 0, 1, 2, ..."""
    pts = []
    m = 0
    while True:
        ring = []
        for a in range(-m, m + 1):
            r = m - abs(a)
            if r == 0:
                ring.append((a, 0))
            else:
                ring.append((a, r)); ring.append((a, -r))
        ring = [(a, b) for (a, b) in ring if abs(a) <= M and abs(b) <= M]
        pts.extend(sorted(ring, key=lambda p: (np.arctan2(p[1], p[0]))))
        if m > 2 * M:
            break
        m += 1
    return np.array(pts, np.int64)


def spiral_order(M):
    """Archimedean spiral order: sort the box by (radius, angle) in fine radial bins."""
    a, b = np.meshgrid(np.arange(-M, M + 1), np.arange(-M, M + 1), indexing='ij')
    a, b = a.ravel(), b.ravel()
    r = np.hypot(a, b)
    th = np.mod(np.arctan2(b, a), 2 * np.pi)
    key = np.floor(r) * 1e6 + th * 1e3
    idx = np.argsort(key, kind='stable')
    return np.stack([a[idx], b[idx]], 1).astype(np.int64)


ORDERS = dict(shell=shell_order, diagonal=diagonal_order, spiral=spiral_order)


# ------------------------------------------------------------------- the game
class Hunt:
    def __init__(self, M, order='shell'):
        self.M = M
        self.order = order
        self.seq = ORDERS[order](M)                      # (N,2): (a_n, b_n), n = 1..N
        self.N = len(self.seq)
        # capture-time field on the box
        self.T = np.zeros((2 * M + 1, 2 * M + 1), np.int64)   # T[a+M, b+M]
        for n, (a, b) in enumerate(self.seq, start=1):
            self.T[a + M, b + M] = n
        # the bomb at time n lands on integer x_n = a_n + b_n * n
        n = np.arange(1, self.N + 1, dtype=np.int64)
        self.bomb_x = self.seq[:, 0] + self.seq[:, 1] * n
        self.bomb_t = n

    def capture_time(self, a, b):
        return int(self.T[a + self.M, b + self.M])

    # ---- certificates -----------------------------------------------------
    def certify(self):
        M, N = self.M, self.N
        c = {}
        c['order'] = self.order
        c['M'] = M
        c['N_submarines'] = int(N)
        c['is_bijection'] = bool(len(np.unique(self.seq, axis=0)) == N and N == (2 * M + 1) ** 2)
        # every submarine is hit exactly at its capture time
        a, b = self.seq[:, 0], self.seq[:, 1]
        t = self.bomb_t
        c['all_hit'] = bool(np.all(a + b * t == self.bomb_x))
        c['T_min'], c['T_max'] = int(self.T.min()), int(self.T.max())
        # the naive hunter: bomb the integers in the order 0, 1, -1, 2, -2, ...
        # which submarines does it EVER hit inside the box, within N steps?
        naive = np.zeros(N + 1, np.int64)
        k = np.arange(1, N + 1)
        naive[1:] = np.where(k % 2 == 1, (k - 1) // 2, -(k // 2))       # 0,-1,1,-2,2,...
        hit = np.zeros((2 * M + 1, 2 * M + 1), bool)
        for n in range(1, N + 1):
            x = naive[n]
            # submarines with a + b n = x : b ranges, a = x - b n
            bs = np.arange(-M, M + 1)
            aa = x - bs * n
            ok = (np.abs(aa) <= M)
            hit[aa[ok] + M, bs[ok] + M] = True
        c['naive_hunter_hit_fraction'] = float(hit.mean())
        c['naive_steps'] = int(N)
        # live-set geometry: at time t the live (a,b) are those with T > t
        ts = [10, 100, 1000, 10000]
        live = {}
        for tt in ts:
            if tt <= N:
                live[tt] = float((self.T > tt).mean())
        c['live_fraction'] = live
        return c


def live_radius(t):
    """shell order: (a,b) is still alive at time t iff max(|a|,|b|) >= (sqrt(t)-1)/2."""
    return (np.sqrt(np.maximum(t, 0.0)) - 1.0) / 2.0


if __name__ == '__main__':
    import json
    for od in ('shell', 'diagonal', 'spiral'):
        h = Hunt(40, od)
        print(od, json.dumps(h.certify(), indent=None)[:400])
