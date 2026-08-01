"""Exact determinant of the Fibonacci-sum 0/1 matrix M_n (MO 513340).

(M_n)_{ij} = 1 iff i+j is a Fibonacci number, 1<=i,j<=n.

Sparse integer Gaussian elimination with min-degree pivoting.
Sign is tracked exactly via Fenwick trees over surviving row/col indices.
A total-unimodularity tripwire asserts every intermediate entry stays in
{-1,0,1} (each Schur entry equals a minor divided by +-1 pivots).
"""
import heapq


def fibs_upto(m):
    """Distinct Fibonacci numbers 1,2,3,5,8,... up to m."""
    fs = [1, 2]
    while fs[-1] <= m:
        fs.append(fs[-1] + fs[-2])
    return [f for f in fs if f <= m]


class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        while i <= self.n:
            self.t[i] += v
            i += i & (-i)

    def pref(self, i):
        s = 0
        while i > 0:
            s += self.t[i]
            i -= i & (-i)
        return s


def det_fib(n, tripwire=True):
    """Return det M_n (exact int, expected in {-1,0,1})."""
    if n == 0:
        return 1
    F = fibs_upto(2 * n)
    # rows[i] = {j: val}, cols[j] = set of rows with nonzero in col j
    rows = [None] + [dict() for _ in range(n)]
    cols = [None] + [set() for _ in range(n)]
    for i in range(1, n + 1):
        for q in F:
            j = q - i
            if 1 <= j <= n:
                rows[i][j] = 1
                cols[j].add(i)
    alive_r = [False] * (n + 1)
    alive_c = [False] * (n + 1)
    fr = Fenwick(n)
    fc = Fenwick(n)
    for i in range(1, n + 1):
        alive_r[i] = alive_c[i] = True
        fr.add(i, 1)
        fc.add(i, 1)

    sign = 1
    heap = [(len(rows[i]), i) for i in range(1, n + 1)]
    heapq.heapify(heap)
    remaining = n
    while remaining > 0:
        # pick alive row of min current degree
        r = None
        while heap:
            d, i = heapq.heappop(heap)
            if alive_r[i] and len(rows[i]) == d:
                r = i
                break
        if r is None:
            # some alive row must exist; rebuild heap lazily
            cand = [i for i in range(1, n + 1) if alive_r[i]]
            heap = [(len(rows[i]), i) for i in cand]
            heapq.heapify(heap)
            continue
        if len(rows[r]) == 0:
            return 0
        # among entries of row r pick col of min degree
        c = min(rows[r], key=lambda j: len(cols[j]))
        v = rows[r][c]
        if tripwire:
            assert v in (-1, 1), (n, r, c, v)
        # sign: positions among remaining rows/cols (1-indexed ranks)
        rho = fr.pref(r)      # rank of r among alive rows
        gam = fc.pref(c)
        if (rho + gam) % 2 == 1:
            sign = -sign
        if v < 0:
            sign = -sign
        # eliminate
        rowr = rows[r]
        alive_r[r] = False
        alive_c[c] = False
        fr.add(r, -1)
        fc.add(c, -1)
        # remove col c entries index
        for i2 in list(cols[c]):
            if i2 == r:
                continue
            w = rows[i2].pop(c)
            # row_i2 -= (w/v) * row_r ; v=+-1 so w/v = w*v
            m = w * v
            ri2 = rows[i2]
            for j2, u in rowr.items():
                if j2 == c:
                    continue
                nv = ri2.get(j2, 0) - m * u
                if nv == 0:
                    ri2.pop(j2, None)
                    cols[j2].discard(i2)
                else:
                    if tripwire:
                        assert -1 <= nv <= 1, ("TU violated", n, i2, j2, nv)
                    ri2[j2] = nv
                    cols[j2].add(i2)
            heapq.heappush(heap, (len(ri2), i2))
        cols[c] = None
        # remove row r from col indices
        for j2 in rowr:
            if j2 != c and cols[j2] is not None:
                cols[j2].discard(r)
        rows[r] = None
        remaining -= 1
    return sign


def zeck(n):
    """Zeckendorf digit string, msd first, over F=1,2,3,5,8,..."""
    if n == 0:
        return "0"
    F = fibs_upto(n)
    out = []
    for f in reversed(F):
        if f <= n:
            out.append("1")
            n -= f
        else:
            if out:
                out.append("0")
    # standard greedy: after taking f, next must skip adjacent — greedy handles
    return "".join(out)


def zeck_digits(n):
    """List of 0/1 Zeckendorf digits msd-first over 1,2,3,5,8,..."""
    if n == 0:
        return [0]
    F = fibs_upto(n)
    out = []
    started = False
    for f in reversed(F):
        if f <= n:
            out.append(1)
            n -= f
            started = True
        elif started:
            out.append(0)
    return out


if __name__ == "__main__":
    import sys
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 130
    nz = [n for n in range(1, N + 1) if det_fib(n) != 0]
    print("nonzero n <=", N, ":", nz)
