"""Covering depth of all C(n,3) triangles on n points of the unit circle: D(y) = C(n,3) - sum_i C(k_i(y), 2)."""
import numpy as np
from numba import njit, prange


@njit(parallel=True, cache=True)
def depth(W, x0, x1, px_, py_):
    n = px_.shape[0]
    out = np.zeros((W, W), np.int32)
    st = (x1 - x0) / W
    tot = n * (n - 1) * (n - 2) // 6
    for j in prange(W):
        al = np.empty(n)
        for i in range(W):
            x = x0 + (i + 0.5) * st
            y = x0 + (j + 0.5) * st
            if x * x + y * y >= 1.0:
                out[j, i] = -1
                continue
            for k in range(n):
                al[k] = np.arctan2(py_[k] - y, px_[k] - x)
            s = 0
            for a in range(n):
                c = 0
                for b in range(n):
                    if b != a:
                        d = (al[b] - al[a]) % (2 * np.pi)
                        if d < np.pi:
                            c += 1
                s += c * (c - 1) // 2
            out[j, i] = tot - s
    return out
