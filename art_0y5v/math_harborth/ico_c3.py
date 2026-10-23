"""C3-symmetric icosahedron search in the Eisenstein lattice.
Point (x,y) with x = y mod 2 represents (x, y*sqrt3) (i.e. twice an Eisenstein integer);
squared distance dx^2 + 3 dy^2; rotation by 120 deg: (x,y) -> ((-x-3y)/2, (x-y)/2).
Vertex orbits: A_i = r^i O, h_{2i} = r^i E, h_{2i+1} = r^i D, B_i = r^i I.
Usage: python3 ico_c3.py L B
"""
import sys, math, json
import numpy as np
from numba import njit
sys.path.insert(0, '.')
from gsearch import isq, place_ok
from graphs import icosahedron
from common import faces_from_drawing

L = int(sys.argv[1]); BOX = int(sys.argv[2])
n, EDGES, ref = icosahedron()
FACES = faces_from_drawing(ref, EDGES)

@njit(cache=True)
def rot(x, y):
    return (-x - 3*y)//2, (x - y)//2

@njit(cache=True)
def okd(x1, y1, x2, y2, L):
    d2 = (x1-x2)**2 + 3*(y1-y2)**2
    return d2 > 0 and d2 <= L*L and isq(d2) >= 0

@njit(cache=True)
def planar_full(X, Y, E, adjm, FF, k, L, sign):
    n = X.shape[0]
    order_pos = np.zeros(n, np.int64)
    for t in range(n):
        order_pos[t] = t
    for t in range(1, n):
        if not place_ok(t, X, Y, order_pos, E, adjm, n, k, L, FF):
            return False
    return True

@njit(cache=True)
def search(L, BOX, PVx, PVy, E, adjm, FF1, FF2, out, maxout):
    nsol = 0; ncomb = 0
    X = np.zeros(12, np.int64); Y = np.zeros(12, np.int64)
    npv = PVx.shape[0]
    Ex = np.empty(npv, np.int64); Ey = np.empty(npv, np.int64)
    Ox = np.empty(npv, np.int64); Oy = np.empty(npv, np.int64)
    Ix = np.empty(npv, np.int64); Iy = np.empty(npv, np.int64)
    for dx in range(-BOX, BOX+1):
        for dy in range(-BOX, BOX+1):
            if (dx - dy) % 2 != 0: continue
            if dx == 0 and dy == 0: continue
            # canonical: use the 6 rotations (r and -1 ... -1 is not a symmetry of orientation? it is a rotation by 180)
            # D canonical under rotation by 60deg multiples: require angle in [0,60)
            if not (dy >= 0 and dx > dy*1 and True): pass
            r1x, r1y = rot(dx, dy); r2x, r2y = rot(r1x, r1y)
            # E: |E-D| ok and |E - r^2 D| ok
            ne = 0
            for w in range(npv):
                ex = dx + PVx[w]; ey = dy + PVy[w]
                if okd(ex, ey, r2x, r2y, L):
                    Ex[ne] = ex; Ey[ne] = ey; ne += 1
            for ie in range(ne):
                ex = Ex[ie]; ey = Ey[ie]
                rex, rey = rot(ex, ey)
                # O: |O-E|,|O-D|,|O-rE|, 3N(O) square
                no = 0
                for w in range(npv):
                    ox = ex + PVx[w]; oy = ey + PVy[w]
                    if okd(ox, oy, dx, dy, L) and okd(ox, oy, rex, rey, L):
                        nn = 3*(ox*ox + 3*oy*oy)
                        if isq(nn) >= 0 and nn <= L*L:
                            Ox[no] = ox; Oy[no] = oy; no += 1
                if no == 0: continue
                ni = 0
                for w in range(npv):
                    ix = dx + PVx[w]; iy = dy + PVy[w]
                    if okd(ix, iy, rex, rey, L) and okd(ix, iy, r1x, r1y, L):
                        nn = 3*(ix*ix + 3*iy*iy)
                        if isq(nn) >= 0 and nn <= L*L:
                            Ix[ni] = ix; Iy[ni] = iy; ni += 1
                if ni == 0: continue
                for io in range(no):
                    for ii in range(ni):
                        ncomb += 1
                        # assemble
                        px = Ox[io]; py = Oy[io]
                        for i in range(3):
                            X[i] = px; Y[i] = py; px, py = rot(px, py)
                        px = ex; py = ey
                        for i in range(3):
                            X[3+2*i] = px; Y[3+2*i] = py; px, py = rot(px, py)
                        px = dx; py = dy
                        for i in range(3):
                            X[4+2*i] = px; Y[4+2*i] = py; px, py = rot(px, py)
                        px = Ix[ii]; py = Iy[ii]
                        for i in range(3):
                            X[9+i] = px; Y[9+i] = py; px, py = rot(px, py)
                        if planar_full(X, Y, E, adjm, FF1, 3, L, 1) or planar_full(X, Y, E, adjm, FF2, 3, L, -1):
                            if nsol < maxout:
                                for z in range(12):
                                    out[nsol, 2*z] = X[z]; out[nsol, 2*z+1] = Y[z]
                            nsol += 1
    return nsol, ncomb

def main():
    pv = []
    for dy in range(-L, L+1):
        for dx in range(-L, L+1):
            if (dx - dy) % 2: continue
            d2 = dx*dx + 3*dy*dy
            if 0 < d2 <= L*L and math.isqrt(d2)**2 == d2:
                pv.append((dx, dy))
    PVx = np.array([p[0] for p in pv], np.int64); PVy = np.array([p[1] for p in pv], np.int64)
    print("PV", len(pv), flush=True)
    E = np.array(EDGES, np.int64)
    adjm = np.zeros((12, 12), np.bool_)
    for a, b in EDGES: adjm[a, b] = adjm[b, a] = True
    FF1 = np.array(FACES, np.int64); FF2 = FF1[:, [0, 2, 1]].copy()
    maxout = 100000
    out = np.zeros((maxout, 24), np.int64)
    nsol, ncomb = search(L, BOX, PVx, PVy, E, adjm, FF1, FF2, out, maxout)
    print("solutions", nsol, "combinatorial", ncomb)
    sols = out[:min(nsol, maxout)].tolist()
    json.dump(sols, open(f"ico_c3_L{L}_B{BOX}.json", "w"))

main()
