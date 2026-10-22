"""Exact mathematical marbling (Lu, Jaffer et al.): every operation is an area-preserving
homeomorphism of the bath; a pixel is coloured by pulling it back through the operations
until it lands inside the drop that put ink there."""
import numpy as np, numba as nb

# op rows: kind, a,b,c,d,e,f,g
# 0 drop: cx,cy,r,ink
# 1 tine line: px,py (point on line), mx,my (unit dir), z (shift), u (decay len), (ignored)
# 2 vortex/circular tine: cx,cy, z (angular shift at r0), r0, u (decay length) -- rotation by z*exp(-|r-r0|/u)/r
# 3 wavy tine: like 1 but shift modulated: z*sin(2pi*(s)/lam) along the line? (comb of parallel tines spaced)
@nb.njit(parallel=True, fastmath=True)
def pull(xs, ys, ops, base_ink, jitter):
    H, W = xs.shape
    out = np.full((H, W), base_ink, np.int32)
    tout = np.zeros((H, W), np.float32)
    n = ops.shape[0]
    for i in nb.prange(H):
        for j in range(W):
            x = xs[i, j]; y = ys[i, j]
            for k in range(n - 1, -1, -1):
                o = ops[k]
                kind = int(o[0])
                if kind == 0:
                    dx = x - o[1]; dy = y - o[2]
                    d2 = dx * dx + dy * dy
                    r2 = o[3] * o[3]
                    if d2 < r2:
                        out[i, j] = int(o[4])
                        tout[i, j] = np.sqrt(d2) / o[3]
                        break
                    f = np.sqrt(1 - r2 / d2)
                    x = o[1] + dx * f; y = o[2] + dy * f
                elif kind == 1:
                    # distance from line through (px,py) dir (mx,my)
                    dx = x - o[1]; dy = y - o[2]
                    d = abs(dx * (-o[4]) + dy * o[3])
                    sft = o[5] * o[6] / (d + o[6])
                    x -= sft * o[3]; y -= sft * o[4]
                elif kind == 2:
                    dx = x - o[1]; dy = y - o[2]
                    r = np.sqrt(dx * dx + dy * dy) + 1e-9
                    a = o[3] * np.exp(-abs(r - o[4]) / o[5]) / r * o[4]
                    c = np.cos(-a); s = np.sin(-a)
                    x = o[1] + dx * c - dy * s; y = o[2] + dx * s + dy * c
                elif kind == 3:
                    # comb: parallel tines every lam along normal, shift along dir m with
                    # z*u/(dn+u), dn = distance to nearest tine
                    dx = x - o[1]; dy = y - o[2]
                    nn = dx * (-o[4]) + dy * o[3]
                    lam = o[7]
                    q = nn / lam
                    dn = abs(q - np.floor(q + 0.5)) * lam
                    sft = o[5] * o[6] / (dn + o[6])
                    x -= sft * o[3]; y -= sft * o[4]
                elif kind == 4:
                    # sine shear: shift along m by z*sin(2pi*nn/lam + ph), nn = normal coordinate
                    dx = x - o[1]; dy = y - o[2]
                    nn = dx * (-o[4]) + dy * o[3]
                    sft = o[5] * np.sin(6.283185307179586 * nn / o[6] + o[7])
                    x -= sft * o[3]; y -= sft * o[4]
    return out, tout

class Bath:
    def __init__(self):
        self.ops = []
    def drop(self, x, y, r, ink): self.ops.append([0, x, y, r, ink, 0, 0, 0])
    def line(self, p, m, z, u):
        m = np.asarray(m, float); m /= np.linalg.norm(m)
        self.ops.append([1, p[0], p[1], m[0], m[1], z, u, 0])
    def vortex(self, c, z, r0, u): self.ops.append([2, c[0], c[1], z, r0, u, 0, 0])
    def comb(self, p, m, z, u, lam):
        m = np.asarray(m, float); m /= np.linalg.norm(m)
        self.ops.append([3, p[0], p[1], m[0], m[1], z, u, lam])
    def wave(self, p, m, z, lam, ph=0.0):
        m = np.asarray(m, float); m /= np.linalg.norm(m)
        self.ops.append([4, p[0], p[1], m[0], m[1], z, lam, ph])
    def render(self, xs, ys, base=0):
        return pull(xs.astype(np.float64), ys.astype(np.float64), np.array(self.ops, np.float64), base, 0.0)
