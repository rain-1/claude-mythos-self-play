"""ring.py — P(p) = Prob(random triangle, one vertex uniform on each of three circles, contains p).
Exact in the third vertex (arc intersection), quadrature in the first two."""
import numpy as np, numba as nb, math

@nb.njit(inline='always')
def arc(K, ux, uy, sgn):
    # condition sgn*(K + |u| sin(phi - a)) >= 0  -> arc (start, length)
    r = math.hypot(ux, uy); a = math.atan2(uy, ux)
    if r < 1e-15:
        return 0.0, (2*math.pi if sgn*K >= 0 else 0.0)
    c = -K / r
    if sgn < 0:   # -K - r sin >= 0  <=> sin(phi-a) <= -K/r <=> sin(phi-a-pi) >= K/r
        a = a + math.pi; c = K / r
    if c <= -1: return 0.0, 2*math.pi
    if c >= 1: return 0.0, 0.0
    s = math.asin(c)
    return a + s, math.pi - 2*s

@nb.njit(inline='always')
def overlap(s1, L1, s2, L2):
    tp = 2*math.pi
    if L1 <= 0 or L2 <= 0: return 0.0
    if L1 >= tp: return L2
    if L2 >= tp: return L1
    s1 = s1 % tp; s2 = s2 % tp
    tot = 0.0
    for k in (-1, 0, 1):
        lo = max(s1, s2 + tp*k); hi = min(s1 + L1, s2 + L2 + tp*k)
        if hi > lo: tot += hi - lo
    return tot

@nb.njit
def prob_point(px, py, C, R, M):
    # C: (3,2) centres, R: (3,) radii; quadrature over vertex A on circle 0 and B on circle 1
    tot = 0.0
    for i in range(M):
        t1 = 2*math.pi*(i + 0.5)/M
        ax = C[0,0] + R[0]*math.cos(t1); ay = C[0,1] + R[0]*math.sin(t1)
        ux = px - ax; uy = py - ay
        for j in range(M):
            t2 = 2*math.pi*(j + 0.5)/M
            bx = C[1,0] + R[1]*math.cos(t2); by = C[1,1] + R[1]*math.sin(t2)
            vx = px - bx; vy = py - by
            cr = ux*vy - uy*vx
            if cr < 0:  # orient so that cross(u,v) > 0
                tx, ty = ux, uy; ux2, uy2 = vx, vy; vx2, vy2 = tx, ty
            else:
                ux2, uy2, vx2, vy2 = ux, uy, vx, vy
            # w = C3 - p + R3 (cos, sin) ; cross(u2, w) >= 0 and cross(w, v2) >= 0
            wx0 = C[2,0] - px; wy0 = C[2,1] - py
            # cross(u,w) = ux*wy - uy*wx = K1 + R3 (ux sin - uy cos) = K1 + R3|u| sin(phi - atan2(uy,ux))
            K1 = ux2*wy0 - uy2*wx0
            s1, L1 = arc(K1, R[2]*ux2, R[2]*uy2, 1.0)
            # cross(w, v) = wx*vy - wy*vx = K2 + R3 (vy cos - vx sin) = K2 - R3|v| sin(phi - atan2(vy,vx))
            K2 = wx0*vy2 - wy0*vx2
            s2, L2 = arc(-K2, R[2]*vx2, R[2]*vy2, -1.0)
            tot += overlap(s1, L1, s2, L2)
    return tot / (2*math.pi*M*M)

@nb.njit(parallel=True)
def field(xs, ys, C, R, M):
    out = np.zeros((ys.size, xs.size))
    for a in nb.prange(ys.size):
        for b in range(xs.size):
            out[a, b] = prob_point(xs[b], ys[a], C, R, M)
    return out

def config(r):
    """three mutually tangent circles with radii r[0..2]; returns centres, incentre of centre-triangle"""
    r1, r2, r3 = r
    d12, d13, d23 = r1+r2, r1+r3, r2+r3
    c1 = np.array([0.0, 0.0]); c2 = np.array([d12, 0.0])
    x = (d13**2 - d23**2 + d12**2)/(2*d12); y = math.sqrt(max(d13**2 - x*x, 0))
    c3 = np.array([x, y]); C = np.array([c1, c2, c3])
    a, b, c = d23, d13, d12   # side lengths opposite c1,c2,c3
    I = (a*c1 + b*c2 + c*c3)/(a+b+c)
    C = C - I
    return C, np.array(r, float)

if __name__ == '__main__':
    import sys, time
    C, R = config((1, 1, 1))
    t = time.time()
    for M in (64, 256, 1024):
        print(M, prob_point(0.0, 0.0, C, R, M), time.time()-t)
    for r in [(1,2,3), (1,1,5), (0.3,1,4), (1,10,100), (2,3,7)]:
        C, R = config(r)
        print(r, [prob_point(0.0, 0.0, C, R, M) for M in (256, 1024)])
