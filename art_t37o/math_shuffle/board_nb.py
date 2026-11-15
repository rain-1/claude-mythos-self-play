"""exact count of perfect n x n Memory boards (numba DFS; first empty cell x unused vector x sign)"""
import numpy as np, numba as nb, sys, board, time

@nb.njit(cache=True)
def count(n, V):
    m = len(V); N = n * n
    occ = np.zeros(N, np.bool_); used = np.zeros(m, np.bool_)
    pos = np.zeros(m + 1, np.int64); ch = np.zeros(m + 1, np.int64); part = np.zeros(m + 1, np.int64)
    depth = 0; total = 0; pos[0] = 0; ch[0] = -1
    while depth >= 0:
        if depth == m:
            total += 1; depth -= 1
            occ[part[depth]] = False; used[ch[depth] // 2] = False
            continue
        p = pos[depth]; y = p // n; x = p % n
        c = ch[depth] + 1; found = False
        while c < 2 * m:
            i = c // 2
            if not used[i]:
                s = 1 if c % 2 == 0 else -1
                X = x + s * V[i, 0]; Y = y + s * V[i, 1]
                if X >= 0 and X < n and Y >= 0 and Y < n and not occ[Y * n + X]:
                    found = True; break
            c += 1
        if found:
            ch[depth] = c; occ[p] = True; q = Y * n + X; occ[q] = True; part[depth] = q; used[c // 2] = True
            depth += 1
            if depth < m:
                r = p + 1
                while occ[r]: r += 1
                pos[depth] = r; ch[depth] = -1
        else:
            occ[p] = False
            depth -= 1
            if depth >= 0:
                occ[part[depth]] = False; used[ch[depth] // 2] = False
    return total

if __name__ == "__main__":
    n = int(sys.argv[1]); V = np.array(board.vecs(n), np.int64); t = time.time()
    print("n", n, "perfect boards:", count(n, V), "time", round(time.time() - t, 1), flush=True)
