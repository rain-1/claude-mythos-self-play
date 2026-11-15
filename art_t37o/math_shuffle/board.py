"""Perfect Memory boards.  An n x n board (n even) holds n^2/2 pairs of cards.  Call the board
PERFECT if the n^2/2 displacement vectors between twins (up to sign) are exactly the n^2/2
shortest vectors of Z^2 -- possible only when a circle cuts the vector list at n^2/2:
n = 2, 6, 10, 12, ...   (2-D analogue of a Skolem sequence).
usage: python3 board.py count 6 | find n seconds seed"""
import sys, math, json, time, random
sys.setrecursionlimit(10000)

def vecs(n):
    v = []
    for x in range(-n, n + 1):
        for y in range(0, n + 1):
            if (y > 0 or x > 0): v.append((x * x + y * y, math.atan2(y, x), x, y))
    v.sort(); need = n * n // 2
    if v[need - 1][0] == v[need][0]: return None
    return [(a[2], a[3]) for a in v[:need]]

def count(n, limit=None):
    V = vecs(n); occ = [[False] * n for _ in range(n)]; used = [False] * len(V)
    sols = []; cur = []
    def rec(pos):
        while pos < n * n and occ[pos // n][pos % n]: pos += 1
        if pos == n * n:
            sols.append(list(cur)); return
        y, x = divmod(pos, n); occ[y][x] = True
        for i, (dx, dy) in enumerate(V):
            if used[i]: continue
            for s in (1, -1):
                X, Y = x + s * dx, y + s * dy
                if 0 <= X < n and 0 <= Y < n and not occ[Y][X]:
                    occ[Y][X] = True; used[i] = True; cur.append((x, y, X, Y))
                    rec(pos + 1)
                    cur.pop(); occ[Y][X] = False; used[i] = False
                    if limit and len(sols) >= limit: occ[y][x] = False; return
        occ[y][x] = False
    rec(0); return sols

def canon(sol, n):
    best = None
    for f in range(8):
        def tr(x, y):
            if f & 1: x = n - 1 - x
            if f & 2: y = n - 1 - y
            if f & 4: x, y = y, x
            return x, y
        s = tuple(sorted(tuple(sorted((tr(a, b), tr(c, d)))) for a, b, c, d in sol))
        if best is None or s < best: best = s
    return best

def find(n, secs, seed):
    """randomised DFS with restarts: most-constrained cell first"""
    V = vecs(n); rnd = random.Random(seed); t0 = time.time(); N = n * n
    while time.time() - t0 < secs:
        occ = [[False] * n for _ in range(n)]; used = [False] * len(V); cur = []; nodes = [0]
        order = list(range(len(V)))
        def options(x, y):
            o = []
            for i in order:
                if used[i]: continue
                dx, dy = V[i]
                for s in (1, -1):
                    X, Y = x + s * dx, y + s * dy
                    if 0 <= X < n and 0 <= Y < n and not occ[Y][X]: o.append((i, X, Y))
            return o
        def rec(left):
            if left == 0: return True
            nodes[0] += 1
            if nodes[0] > 200000: return False
            # the longest unused vector is the hardest to place: branch on it
            i = max(k for k in range(len(V)) if not used[k]); dx, dy = V[i]
            cand = []
            for y in range(n):
                for x in range(n):
                    X, Y = x + dx, y + dy
                    if not occ[y][x] and 0 <= X < n and 0 <= Y < n and not occ[Y][X]: cand.append((x, y, X, Y))
            rnd.shuffle(cand)
            # prefer placements near the rim (long vectors must hug it)
            cand.sort(key=lambda c: -(abs(c[0] - (n - 1) / 2) + abs(c[1] - (n - 1) / 2) + abs(c[2] - (n - 1) / 2) + abs(c[3] - (n - 1) / 2)) + rnd.random() * 2)
            for x, y, X, Y in cand[:6]:
                occ[y][x] = occ[Y][X] = True; used[i] = True; cur.append((x, y, X, Y))
                if rec(left - 1): return True
                cur.pop(); occ[y][x] = occ[Y][X] = False; used[i] = False
            return False
        if rec(len(V)): return cur
    return None

if __name__ == "__main__":
    if sys.argv[1] == "count":
        n = int(sys.argv[2]); S = count(n)
        orb = sorted(set(canon(s, n) for s in S))
        print("n", n, "perfect boards", len(S), "up to the 8 symmetries", len(orb))
        json.dump(dict(n=n, total=len(S), orbits=[[[a, b, c, d] for (a, b), (c, d) in o] for o in orb]), open(f"boards_{n}.json", "w"))
    else:
        n = int(sys.argv[2]); s = find(n, float(sys.argv[3]), int(sys.argv[4]))
        print("n", n, "found" if s else "none"); 
        if s: json.dump(dict(n=n, pairs=s), open(f"board_{n}.json", "w")); print(s)
