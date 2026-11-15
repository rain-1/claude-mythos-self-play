"""MO 453577 'A perfect shuffle on N' -- three computations.
 (1) the greedy shuffle on N is the Wythoff pairing (checked to 10^6 pairs)
 (2) G(n) = number of 'good' shuffles of n pairs (all n pair-distances distinct), exact
 (3) the greedy shuffle of the PLANE Z^2 (cells in square-spiral order, difference
     vectors up to sign in order of length then angle): is every vector used?
"""
import numpy as np, numba as nb, json, sys, math, time

def greedy_line(K):
    N = 3*K+10
    used = np.zeros(N, bool); pairs = []
    c = 1
    for n in range(1, K+1):
        while used[c]: c += 1
        used[c] = used[c+n] = True; pairs.append((c, c+n))
    return pairs

@nb.njit(cache=True)
def count_good(n):
    L = 2*n
    occ = np.zeros(L, np.bool_); du = np.zeros(L+1, np.bool_)
    pos = np.zeros(n+1, np.int64); dch = np.zeros(n+1, np.int64)
    depth = 0; total = 0; perfect = 0
    p = 0
    pos[0] = 0; dch[0] = 0
    while depth >= 0:
        if depth == n:
            total += 1
            ok = True
            for d in range(1, n+1):
                if not du[d]:
                    ok = False; break
            if ok: perfect += 1
            depth -= 1
            p = pos[depth]; d = dch[depth]
            occ[p] = False; occ[p+d] = False; du[d] = False
            continue
        p = pos[depth]
        d = dch[depth] + 1
        found = False
        while p + d < L:
            if (not du[d]) and (not occ[p+d]):
                found = True; break
            d += 1
        if found:
            dch[depth] = d
            occ[p] = True; occ[p+d] = True; du[d] = True
            depth += 1
            if depth < n:
                q = p+1
                while occ[q]: q += 1
                pos[depth] = q; dch[depth] = 0
        else:
            depth -= 1
            if depth >= 0:
                p = pos[depth]; d = dch[depth]
                occ[p] = False; occ[p+d] = False; du[d] = False
    return total, perfect

def spiral(M):
    """cells of Z^2 in square-spiral order, first M"""
    out = np.zeros((M,2), np.int32); x=y=0; dx,dy=1,0; seg=1; i=0
    while i < M:
        for _ in range(2):
            for _ in range(seg):
                if i>=M: break
                out[i]=(x,y); i+=1; x+=dx; y+=dy
            dx,dy = -dy,dx
        seg+=1
    return out

def vectors(R):
    """difference vectors up to sign, |v|<=R, ordered by length then angle in [0,pi)"""
    v=[]
    for x in range(-R,R+1):
        for y in range(0,R+1):
            if (y>0 or x>0) and x*x+y*y<=R*R: v.append((x*x+y*y, math.atan2(y,x), x, y))
    v.sort()
    return np.array([(a[2],a[3]) for a in v], np.int32)

@nb.njit(cache=True)
def greedy_plane(cells, vecs, H):
    W = 2*H+1
    occ = np.zeros((W,W), np.bool_)
    nv = len(vecs); vused = np.zeros(nv, np.bool_)
    M = len(cells)
    px = np.zeros((M,4), np.int32)   # ax,ay,bx,by
    vr = np.zeros(M, np.int64)       # rank of the vector used
    lo = np.zeros(M, np.int64)       # smallest unused rank at that time
    first = 0; np_ = 0
    for i in range(M):
        x = cells[i,0]; y = cells[i,1]
        if occ[x+H,y+H]: continue
        while vused[first]: first += 1
        j = first
        bx = 0; by = 0
        while True:
            if not vused[j]:
                vx = vecs[j,0]; vy = vecs[j,1]
                if not occ[x+vx+H, y+vy+H]:
                    bx = x+vx; by = y+vy; break
                if not occ[x-vx+H, y-vy+H]:
                    bx = x-vx; by = y-vy; break
            j += 1
        vused[j] = True; occ[x+H,y+H] = True; occ[bx+H,by+H] = True
        px[np_,0]=x; px[np_,1]=y; px[np_,2]=bx; px[np_,3]=by
        vr[np_] = j; lo[np_] = first; np_ += 1
    return px[:np_], vr[:np_], lo[:np_]

if __name__ == "__main__":
    what = sys.argv[1]
    if what == "line":
        K = 10**6; P = greedy_line(K)
        from math import isqrt
        ok = all(a == (k + isqrt(5*k*k))//2 and b == a+k for k,(a,b) in enumerate(P,1))
        print("greedy = Wythoff for k <=", K, ":", ok)
    if what == "count":
        res = {}
        for n in range(1, int(sys.argv[2])+1):
            t=time.time(); g,p = count_good(n)
            dd = 1
            for k in range(1,2*n,2): dd *= k
            res[n] = dict(good=int(g), perfect=int(p), all=dd, frac=g/dd)
            print(n, g, p, dd, g/dd, (g/dd)**(1/n), round(time.time()-t,1), flush=True)
            json.dump(res, open("counts.json","w"), indent=1)
    if what == "plane":
        Rc = int(sys.argv[2])
        M = (2*Rc+1)**2
        cells = spiral(M); Rv = int(1.6*Rc)+20
        vecs = vectors(Rv); H = Rc+Rv+2
        t=time.time(); px, vr, lo = greedy_plane(cells, vecs, H)
        n = len(px); lag = vr - lo
        print("cells", M, "pairs", n, "vectors avail", len(vecs), "time", round(time.time()-t,1))
        print("pairs using the smallest unused vector:", int((lag==0).sum()), "frac", (lag==0).mean())
        print("max lag", int(lag.max()), "mean lag", lag.mean())
        for q in [10**k for k in range(1,8)]:
            if q<=n: print(" first", q, "pairs: frac lag>0", (lag[:q]>0).mean(), "max lag", int(lag[:q].max()),
                           "max |rank-index|", int(np.abs(vr[:q]-np.arange(q)).max()))
        print("smallest unused rank at end", int(lo[-1]), "of", n)
        np.savez_compressed(f"plane_{Rc}.npz", px=px, vr=vr, lo=lo, vecs=vecs[:int(vr.max())+1])
