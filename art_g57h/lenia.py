"""lenia.py — minimal Lenia engine (Bert Chan, 2019) + animals.json decoder.

A(x) in [0,1] on a torus; kernel K(r) = exp(4 - 1/(r(1-r))) shell (beta=[1]) of radius R,
growth G(u) = 2 exp(-(u-mu)^2/(2 sigma^2)) - 1, A <- clip(A + dt G(K*A), 0, 1), dt = 1/T.
Convolution by FFT (scipy.fft, real, cached kernel spectrum).
"""
import json, re
import numpy as np
from scipy import fft as sfft

DIM_DELIM = {1: '$', 2: '%', 3: '#', 4: '@'}


def ch2val(c):
    if c in '.b':
        return 0
    if c == 'o':
        return 255
    if len(c) == 1:
        return ord(c) - ord('A') + 1
    return (ord(c[0]) - ord('p')) * 24 + (ord(c[1]) - ord('A') + 25)


def rle2arr(st):
    """decode Lenia's RLE cell string into a 2-D float array in [0,1]"""
    stacks = [[]]
    last, count = '', ''
    for ch in st.rstrip('!'):
        if ch.isdigit():
            count += ch
        elif ch in 'pqrstuvwxy':
            last = ch
        else:
            if ch == '$':
                stacks[0].append(None)  # row break
                continue
            if last:
                ch = last + ch
                last = ''
            n = int(count) if count else 1
            count = ''
            stacks[0].extend([ch2val(ch)] * n)
    rows, cur = [], []
    for v in stacks[0]:
        if v is None:
            rows.append(cur)
            cur = []
        else:
            cur.append(v)
    if cur:
        rows.append(cur)
    w = max(len(r) for r in rows)
    A = np.zeros((len(rows), w), np.float32)
    for i, r in enumerate(rows):
        A[i, :len(r)] = r
    return A / 255.0


def load_animal(path, code):
    for a in json.load(open(path)):
        if a.get('code') == code:
            return a
    raise KeyError(code)


def kernel_shell(R, beta=(1.0,), size=None):
    """radial shell kernel on a size x size torus, centred at (0,0)"""
    N = size
    y = np.arange(N); y = np.minimum(y, N - y)
    Y, X = np.meshgrid(y, y, indexing='ij')
    r = np.sqrt(X.astype(np.float64) ** 2 + Y ** 2) / R
    nb = len(beta)
    Br = nb * r
    idx = np.minimum(np.floor(Br).astype(int), nb - 1)
    frac = Br - idx
    core = np.exp(4 - 1.0 / np.clip(frac * (1 - frac), 1e-12, None))
    K = np.where(r < 1, np.asarray(beta)[idx] * core, 0.0)
    K /= K.sum()
    return K.astype(np.float32)


class Lenia:
    def __init__(self, size, R=13, T=10, mu=0.15, sigma=0.015, beta=(1.0,), workers=4):
        self.N = size
        self.R, self.dt, self.mu, self.sigma = R, 1.0 / T, mu, sigma
        K = kernel_shell(R, beta, size)
        self.fK = sfft.rfft2(K, workers=workers)
        self.workers = workers
        self.A = np.zeros((size, size), np.float32)
        self.t = 0

    def place(self, cells, cy, cx, angle_deg=0.0, flip=False):
        """paste a pattern (rotated by angle, optionally flipped) centred at (cy, cx)"""
        from scipy.ndimage import rotate
        P = np.asarray(cells, np.float32)
        if flip:
            P = P[:, ::-1]
        if angle_deg % 360:
            P = rotate(P, angle_deg, reshape=True, order=1, mode='constant', cval=0.0)
            P = np.clip(P, 0, 1)
        h, w = P.shape
        y0, x0 = int(round(cy - h / 2)), int(round(cx - w / 2))
        for i in range(h):
            yi = (y0 + i) % self.N
            for j in range(w):
                xj = (x0 + j) % self.N
                self.A[yi, xj] = max(self.A[yi, xj], P[i, j])

    def growth(self, U):
        return 2.0 * np.exp(-((U - self.mu) ** 2) / (2 * self.sigma ** 2)) - 1.0

    def step(self, n=1):
        for _ in range(n):
            U = sfft.irfft2(sfft.rfft2(self.A, workers=self.workers) * self.fK,
                            s=(self.N, self.N), workers=self.workers)
            self.A = np.clip(self.A + self.dt * self.growth(U), 0.0, 1.0).astype(np.float32)
            self.t += 1

    def mass(self):
        return float(self.A.sum())

    def centroid(self):
        """torus-aware centroid (circular mean per axis)"""
        m = self.A.sum() + 1e-12
        ang = 2 * np.pi * np.arange(self.N) / self.N
        cy = np.angle((self.A.sum(1) * np.exp(1j * ang)).sum() / m) / (2 * np.pi) * self.N % self.N
        cx = np.angle((self.A.sum(0) * np.exp(1j * ang)).sum() / m) / (2 * np.pi) * self.N % self.N
        return cy, cx


if __name__ == '__main__':
    import sys, time
    path = sys.argv[1]
    a = load_animal(path, 'O2u')
    P = rle2arr(a['cells'])
    print('Orbium', P.shape, 'max', P.max(), 'sum', P.sum(), 'params', a['params'])
    L = Lenia(256, R=13, T=10, mu=a['params']['m'], sigma=a['params']['s'])
    L.place(P, 128, 128)
    cs = []
    t0 = time.time()
    for k in range(40):
        L.step(25)
        cs.append((L.t, L.mass(), *L.centroid()))
    print('time per step %.4f s' % ((time.time() - t0) / 1000))
    for c in cs[::5]:
        print('t=%4d mass=%.2f cy=%.1f cx=%.1f' % c)
