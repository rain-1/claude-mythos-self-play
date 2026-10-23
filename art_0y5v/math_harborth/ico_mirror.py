"""Search for mirror-symmetric integral drawings of the icosahedron with integer coordinates.
Mirror = y-axis. Fixed vertices on the axis: A0=(0,a), h1=(0,p), h4=(0,s), B1=(0,b).
Pairs (rep x != 0, mirror image (-x,y)): A1=A, A2=A'; h2=H, h0=H'; h3=K, h5=K'; B0=B, B2=B'.
Usage: python3 ico_mirror.py L XMAX
"""
import sys, math, json
import numpy as np
from numba import njit

L = int(sys.argv[1]) if len(sys.argv) > 1 else 60
XMAX = int(sys.argv[2]) if len(sys.argv) > 2 else L

EDGES = [(0,1),(0,2),(1,2),(9,10),(10,11),(9,11),
         (3,4),(4,5),(5,6),(6,7),(7,8),(8,3),
         (0,3),(0,4),(0,5),(1,5),(1,6),(1,7),(2,7),(2,8),(2,3),
         (9,4),(9,5),(9,6),(10,6),(10,7),(10,8),(11,8),(11,3),(11,4)]
E = np.array(EDGES, dtype=np.int64)
# faces (for min angle)
FACES = [(0,1,2),(9,10,11),
 (0,3,4),(0,4,5),(0,1,5),(1,5,6),(1,6,7),(1,2,7),(2,7,8),(2,8,3),(2,0,3),
 (9,4,5),(9,5,6),(9,10,6),(10,6,7),(10,7,8),(10,11,8),(11,8,3),(11,3,4),(11,9,4)]
F = np.array(FACES, dtype=np.int64)

@njit(cache=True)
def isq(n):
    if n < 0: return -1
    r = int(math.isqrt(n)) if False else int(math.sqrt(n))
    while r*r > n: r -= 1
    while (r+1)*(r+1) <= n: r += 1
    return r if r*r == n else -1

@njit(cache=True)
def orient(ax,ay,bx,by,cx,cy):
    v = (bx-ax)*(cy-ay) - (by-ay)*(cx-ax)
    return 1 if v > 0 else (-1 if v < 0 else 0)

@njit(cache=True)
def onseg(ax,ay,bx,by,cx,cy):
    # c on closed segment ab (assumes collinear)
    return min(ax,bx) <= cx <= max(ax,bx) and min(ay,by) <= cy <= max(ay,by)

@njit(cache=True)
def planar(X, Y, E):
    n = X.shape[0]
    for i in range(n):
        for j in range(i+1, n):
            if X[i]==X[j] and Y[i]==Y[j]: return False
    m = E.shape[0]
    # vertex on edge
    for k in range(m):
        a = E[k,0]; b = E[k,1]
        for v in range(n):
            if v == a or v == b: continue
            if orient(X[a],Y[a],X[b],Y[b],X[v],Y[v]) == 0 and onseg(X[a],Y[a],X[b],Y[b],X[v],Y[v]):
                return False
    for k in range(m):
        a = E[k,0]; b = E[k,1]
        for l in range(k+1, m):
            c = E[l,0]; d = E[l,1]
            if a==c or a==d or b==c or b==d: continue
            o1 = orient(X[a],Y[a],X[b],Y[b],X[c],Y[c]); o2 = orient(X[a],Y[a],X[b],Y[b],X[d],Y[d])
            o3 = orient(X[c],Y[c],X[d],Y[d],X[a],Y[a]); o4 = orient(X[c],Y[c],X[d],Y[d],X[b],Y[b])
            if o1*o2 < 0 and o3*o4 < 0: return False
            if o1 == 0 and onseg(X[a],Y[a],X[b],Y[b],X[c],Y[c]): return False
            if o2 == 0 and onseg(X[a],Y[a],X[b],Y[b],X[d],Y[d]): return False
            if o3 == 0 and onseg(X[c],Y[c],X[d],Y[d],X[a],Y[a]): return False
            if o4 == 0 and onseg(X[c],Y[c],X[d],Y[d],X[b],Y[b]): return False
    return True

@njit(cache=True)
def minangle(X, Y, F):
    best = 10.0
    for f in range(F.shape[0]):
        for t in range(3):
            o = F[f,t]; p = F[f,(t+1)%3]; q = F[f,(t+2)%3]
            ux = X[p]-X[o]; uy = Y[p]-Y[o]; vx = X[q]-X[o]; vy = Y[q]-Y[o]
            c = (ux*vx+uy*vy)/math.sqrt((ux*ux+uy*uy)*(vx*vx+vy*vy))
            if c > 1: c = 1.0
            if c < -1: c = -1.0
            ang = math.acos(c)
            if ang < best: best = ang
    return best

@njit(cache=True)
def search(L, XMAX, legs, nlegs, PVx, PVy, E, F, out, maxout):
    # legs[x, :nlegs[x]] = d>=0 with x^2+d^2 square and sqrt <= L
    nout = 0
    npv = PVx.shape[0]
    candx = np.empty(npv, np.int64); candy = np.empty(npv, np.int64)
    X = np.zeros(12, np.int64); Y = np.zeros(12, np.int64)
    TA = np.empty(4000, np.int64); TS = np.empty(4000, np.int64)
    TP = np.empty(4000, np.int64); TB = np.empty(4000, np.int64)
    for e in range(1, XMAX+1):
        hx = e; hy = 0
        for kk in range(npv):
            kx = hx + PVx[kk]; ky = hy + PVy[kk]
            if kx == 0 or abs(kx) > XMAX: continue
            # candidates
            nc = 0
            for ww in range(npv):
                px = hx + PVx[ww]; py = hy + PVy[ww]
                if px == 0 or abs(px) > XMAX: continue
                if px == kx and py == ky: continue
                dx = px - kx; dy = py - ky
                d2 = dx*dx+dy*dy
                if d2 > L*L: continue
                if isq(d2) < 0: continue
                candx[nc] = px; candy[nc] = py; nc += 1
            if nc < 2: continue
            for ia in range(nc):
                ax = candx[ia]; ay = candy[ia]
                # T(A) ∩ T(H)  -> axis values
                na = 0
                aax = abs(ax)
                for t1 in range(nlegs[aax]):
                    for sg1 in range(2):
                        if t1 == 0 and sg1 == 1 and legs[aax,0] == 0: continue
                        v = ay + (legs[aax,t1] if sg1 == 0 else -legs[aax,t1])
                        dy = v - hy
                        if isq(hx*hx + dy*dy) >= 0 and hx*hx+dy*dy <= L*L:
                            TA[na] = v; na += 1
                if na == 0: continue
                ns = 0
                for t1 in range(nlegs[aax]):
                    for sg1 in range(2):
                        if t1 == 0 and sg1 == 1 and legs[aax,0] == 0: continue
                        v = ay + (legs[aax,t1] if sg1 == 0 else -legs[aax,t1])
                        dy = v - ky
                        if isq(kx*kx + dy*dy) >= 0 and kx*kx+dy*dy <= L*L:
                            TS[ns] = v; ns += 1
                if ns == 0: continue
                for ib in range(nc):
                    if ib == ia: continue
                    bx = candx[ib]; by = candy[ib]
                    bbx = abs(bx)
                    npp = 0
                    for t1 in range(nlegs[bbx]):
                        for sg1 in range(2):
                            if t1 == 0 and sg1 == 1 and legs[bbx,0] == 0: continue
                            v = by + (legs[bbx,t1] if sg1 == 0 else -legs[bbx,t1])
                            dy = v - hy
                            if isq(hx*hx + dy*dy) >= 0 and hx*hx+dy*dy <= L*L:
                                TP[npp] = v; npp += 1
                    if npp == 0: continue
                    nb = 0
                    for t1 in range(nlegs[bbx]):
                        for sg1 in range(2):
                            if t1 == 0 and sg1 == 1 and legs[bbx,0] == 0: continue
                            v = by + (legs[bbx,t1] if sg1 == 0 else -legs[bbx,t1])
                            dy = v - ky
                            if isq(kx*kx + dy*dy) >= 0 and kx*kx+dy*dy <= L*L:
                                TB[nb] = v; nb += 1
                    if nb == 0: continue
                    # assemble
                    X[1] = ax; Y[1] = ay; X[2] = -ax; Y[2] = ay
                    X[5] = hx; Y[5] = hy; X[3] = -hx; Y[3] = hy
                    X[6] = kx; Y[6] = ky; X[8] = -kx; Y[8] = ky
                    X[9] = bx; Y[9] = by; X[11] = -bx; Y[11] = by
                    X[0] = 0; X[4] = 0; X[7] = 0; X[10] = 0
                    for q1 in range(na):
                        Y[0] = TA[q1]
                        for q2 in range(ns):
                            Y[7] = TS[q2]
                            for q3 in range(npp):
                                Y[4] = TP[q3]
                                for q4 in range(nb):
                                    Y[10] = TB[q4]
                                    if planar(X, Y, E):
                                        if nout < maxout:
                                            for z in range(12):
                                                out[nout, 2*z] = X[z]; out[nout, 2*z+1] = Y[z]
                                        nout += 1
    return nout

def main():
    legs = np.zeros((XMAX+1, 2*L+5), np.int64); nlegs = np.zeros(XMAX+1, np.int64)
    for x in range(XMAX+1):
        ds = [d for d in range(0, L+1) if x*x+d*d <= L*L and math.isqrt(x*x+d*d)**2 == x*x+d*d]
        if x == 0: ds = list(range(0, L+1))
        legs[x,:len(ds)] = ds; nlegs[x] = len(ds)
    pv = [(dx,dy) for dx in range(-L,L+1) for dy in range(-L,L+1)
          if 0 < dx*dx+dy*dy <= L*L and math.isqrt(dx*dx+dy*dy)**2 == dx*dx+dy*dy]
    PVx = np.array([p[0] for p in pv], np.int64); PVy = np.array([p[1] for p in pv], np.int64)
    print("PV", len(pv), flush=True)
    maxout = 200000
    out = np.zeros((maxout, 24), np.int64)
    n = search(L, XMAX, legs, nlegs, PVx, PVy, E, F, out, maxout)
    print("found", n)
    res = []
    for r in range(min(n, maxout)):
        X = out[r, 0::2].copy(); Y = out[r, 1::2].copy()
        lens = [math.isqrt(int((X[a]-X[b])**2 + (Y[a]-Y[b])**2)) for a,b in EDGES]
        res.append((max(lens), minangle(X.astype(np.float64), Y.astype(np.float64), F)*180/math.pi, X.tolist(), Y.tolist(), lens))
    json.dump(res, open(f"ico_mirror_L{L}.json", "w"))
    res.sort(key=lambda r: (-r[1]))
    for r in res[:10]: print(r)

main()
