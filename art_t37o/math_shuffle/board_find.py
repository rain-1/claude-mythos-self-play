"""find one perfect n x n Memory board: DFS that always branches on the most constrained thing
(the free cell with fewest ways to be covered, or the unused step with fewest placements),
random order, node cap, restarts.   usage: python3 board_find.py n seconds seed"""
import numpy as np, numba as nb, sys, json, time, board

@nb.njit(cache=True)
def attempt(n, V, seed, cap):
    np.random.seed(seed)
    m = len(V); N = n * n
    occ = np.zeros(N, np.bool_); used = np.zeros(m, np.bool_)
    sol = np.zeros((m, 3), np.int64)                 # cell a, cell b, vector
    # explicit stack of option lists
    optA = np.zeros((m, 4 * m + 2 * N), np.int64); optB = np.zeros((m, 4 * m + 2 * N), np.int64); optV = np.zeros((m, 4 * m + 2 * N), np.int64)
    cnt = np.zeros(m, np.int64); ptr = np.zeros(m, np.int64)
    depth = 0; nodes = 0; fresh = True
    cellc = np.zeros(N, np.int64); vecc = np.zeros(m, np.int64)
    while True:
        if depth == m: return 1, sol, nodes
        if fresh:
            nodes += 1
            if nodes > cap: return 0, sol, nodes
            cellc[:] = 0; vecc[:] = 0
            for i in range(m):
                if used[i]: continue
                dx = V[i, 0]; dy = V[i, 1]
                for y in range(n):
                    Y = y + dy
                    if Y < 0 or Y >= n: continue
                    for x in range(n):
                        X = x + dx
                        if X < 0 or X >= n: continue
                        a = y * n + x; b = Y * n + X
                        if occ[a] or occ[b]: continue
                        vecc[i] += 1; cellc[a] += 1; cellc[b] += 1
            best = 1 << 60; kind = 0; which = -1
            for i in range(m):
                if not used[i] and vecc[i] < best: best = vecc[i]; kind = 0; which = i
            for c in range(N):
                if not occ[c] and cellc[c] < best: best = cellc[c]; kind = 1; which = c
            k = 0
            if best > 0:
                for i in range(m):
                    if used[i] or (kind == 0 and i != which): continue
                    dx = V[i, 0]; dy = V[i, 1]
                    for y in range(n):
                        Y = y + dy
                        if Y < 0 or Y >= n: continue
                        for x in range(n):
                            X = x + dx
                            if X < 0 or X >= n: continue
                            a = y * n + x; b = Y * n + X
                            if occ[a] or occ[b]: continue
                            if kind == 1 and a != which and b != which: continue
                            optA[depth, k] = a; optB[depth, k] = b; optV[depth, k] = i; k += 1
                for j in range(k - 1, 0, -1):          # shuffle
                    r = np.random.randint(0, j + 1)
                    t = optA[depth, j]; optA[depth, j] = optA[depth, r]; optA[depth, r] = t
                    t = optB[depth, j]; optB[depth, j] = optB[depth, r]; optB[depth, r] = t
                    t = optV[depth, j]; optV[depth, j] = optV[depth, r]; optV[depth, r] = t
            cnt[depth] = k; ptr[depth] = 0
        if ptr[depth] < cnt[depth]:
            j = ptr[depth]; ptr[depth] += 1
            a = optA[depth, j]; b = optB[depth, j]; i = optV[depth, j]
            occ[a] = True; occ[b] = True; used[i] = True
            sol[depth, 0] = a; sol[depth, 1] = b; sol[depth, 2] = i
            depth += 1; fresh = True
        else:
            depth -= 1; fresh = False
            if depth < 0: return -1, sol, nodes
            occ[sol[depth, 0]] = False; occ[sol[depth, 1]] = False; used[sol[depth, 2]] = False

if __name__ == "__main__":
    n = int(sys.argv[1]); secs = float(sys.argv[2]); seed = int(sys.argv[3])
    V = np.array(board.vecs(n), np.int64); t = time.time(); tries = 0
    while time.time() - t < secs:
        ok, sol, nodes = attempt(n, V, seed * 100003 + tries, 300000); tries += 1
        if ok == 1:
            pairs = [[int(a % n), int(a // n), int(b % n), int(b // n)] for a, b, _ in sol]
            vs = set(); cells = set(); VV = set(map(tuple, V.tolist()))
            for a, b, c, d in pairs:
                v = (c - a, d - b); v = v if v in VV else (-v[0], -v[1]); assert v in VV; vs.add(v); cells |= {(a, b), (c, d)}
            assert vs == VV and len(cells) == n * n
            json.dump(dict(n=n, pairs=pairs), open(f"board_{n}.json", "w"))
            print("n", n, "FOUND and verified after", tries, "tries,", round(time.time() - t, 1), "s", flush=True); break
        if ok == -1: print("n", n, "search space exhausted: NONE"); break
    else: print("n", n, "none in", tries, "tries")
