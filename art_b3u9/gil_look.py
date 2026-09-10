"""gil_look.py — quick look at the Gilbreath triangle (top rows) and the signed difference field."""
import numpy as np
from PIL import Image

LIM = 3_000_000
sieve = np.ones(LIM // 2, dtype=bool); sieve[0] = False
for i in range(1, int(LIM ** 0.5) // 2 + 1):
    if sieve[i]:
        p = 2 * i + 1; sieve[p * p // 2::p] = False
primes = np.concatenate([[2], 2 * np.nonzero(sieve)[0] + 1]).astype(np.int64)
COLS, ROWS = 1200, 300
G = primes[:COLS + ROWS + 2].copy()
img = np.zeros((ROWS, COLS, 3), np.uint8) + 245
for n in range(ROWS):
    G = np.abs(G[1:] - G[:-1])
    row = G[:COLS]
    v = row.astype(float)
    img[n, row == 0] = (245, 245, 245)
    img[n, row == 2] = (200, 215, 235)
    big = row > 2
    s = np.clip(np.log2(v[big]) / 6.5, 0, 1)
    img[n, big, 0] = 255; img[n, big, 1] = (200 * (1 - s)).astype(np.uint8); img[n, big, 2] = (80 * (1 - s)).astype(np.uint8)
    img[n, row == 1] = (0, 0, 0)
Image.fromarray(img).resize((COLS * 2, ROWS * 4), Image.NEAREST).save('/tmp/claude-0/-home-user-claude-mythos-self-play/38c33a52-2f72-54f9-891a-930f8e1e4306/scratchpad/gil.png')
# signed field D_n(j) / std_n, n = 1..60, j < COLS
D = primes[:COLS + 80].copy()
img2 = np.zeros((60, COLS, 3), np.uint8) + 245
for n in range(1, 61):
    D = D[1:] - D[:-1]
    row = D[:COLS].astype(float); sd = row.std() + 1e-9
    x = np.clip(row / (2 * sd), -1, 1)
    warm = x > 0
    img2[n - 1, :, 0] = np.where(warm, 245, 245 - 200 * (-x)).astype(np.uint8)
    img2[n - 1, :, 1] = (245 - 150 * np.abs(x)).astype(np.uint8)
    img2[n - 1, :, 2] = np.where(warm, 245 - 200 * x, 245).astype(np.uint8)
    img2[n - 1, D[:COLS] == 0] = (0, 160, 0)
Image.fromarray(img2).resize((COLS * 2, 60 * 10), Image.NEAREST).save('/tmp/claude-0/-home-user-claude-mythos-self-play/38c33a52-2f72-54f9-891a-930f8e1e4306/scratchpad/signed.png')
print('ok')
