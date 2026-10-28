# 2-D city-building array (MO 516465): a[i,j] = least h with V_ij(h) = h,
# V = buildings visible along the row (to the left) + along the column (below).
import numpy as np, numba, sys

@numba.njit(cache=True)
def vis_count(line, n, h):
    # line[0..n-1] are earlier buildings; the new roof sits at position n, height h.
    c = 0
    best = -1e300
    for k in range(n-1, -1, -1):
        s = (line[k] - h) / (n - k)
        if s >= best - 1e-12:
            c += 1
        if s > best:
            best = s
    return c

@numba.njit(cache=True)
def build(N):
    a = np.zeros((N, N), np.int64)
    row = np.zeros(N); col = np.zeros(N)
    for i in range(N):
        for j in range(N):
            if i == 0 and j == 0:
                continue
            for k in range(i): col[k] = a[k, j]
            for k in range(j): row[k] = a[i, k]
            h = 0
            while True:
                v = vis_count(col, i, h) + vis_count(row, j, h)
                if v == h:
                    break
                h += 1
            a[i, j] = h
    return a

if __name__ == '__main__':
    N = int(sys.argv[1])
    a = build(N)
    np.save(f'city_{N}.npy', a)
    print(a[:12, :12])
    d = np.diag(a); print('diag', d[:60].tolist()); print('max diag', d.max(), 'argmax', d.argmax(), 'max', a.max())
