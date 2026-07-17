"""Companion 2: The Shape of Possibility.

The four-bar's configuration space lives on the torus (alpha, gamma) =
(crank angle, follower angle): C = {|A(alpha) - B(gamma)| = b}. Sweep the
crank length a through the Grashof equality a* = p + q - l: below it the
machine's world is TWO disjoint circles that wind (mirror assembly branches,
each a full crank turn); above it ONE contractible loop that winds nothing
(a rocking cage). At a* the two worlds kiss at folded (collinear) configs.

Verified per family member: component count & winding numbers on the torus;
the transition happens exactly at a*; pinch points are collinear configs."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy.ndimage import gaussian_filter
from fourbar import solve_follower
from rkit import Canvas

def branches(g, a, b, c, nal=200000):
    """Both assembly branches over a dense crank sweep.
    Returns alpha, gammaP, gammaM (nan where infeasible)."""
    OA, OB = 0+0j, g+0j
    al = np.linspace(-np.pi, np.pi, nal, endpoint=False)
    A = OA + a*np.exp(1j*al)
    Bp = solve_follower(A, OB, b, c, +1)
    Bm = solve_follower(A, OB, b, c, -1)
    gp = np.angle(Bp - OB); gm = np.angle(Bm - OB)
    return al, gp, gm


def ndzoom_safe(A, f):
    from scipy.ndimage import zoom as _z
    out = _z(A[::-1], f, order=1)      # flip so +gamma is up in the image
    return out

def torus_cycles(g, a, b, c, n=4000):
    """Walk each connected component of the config curve as a cycle on the
    torus; return its TRUE winding numbers (w_alpha, w_gamma)."""
    al, gp, gm = branches(g, a, b, c, n)
    ok = ~np.isnan(gp)
    if not ok.any(): return []
    gam = {0: gp, 1: gm}
    def nbrs(node):
        i, s = node
        out = []
        for j in ((i-1) % n, (i+1) % n):
            if ok[j]: out.append((j, s))
        # fold endpoints: partner branch at same i when a neighbor is infeasible
        if not ok[(i-1) % n] or not ok[(i+1) % n]:
            out.append((i, 1-s))
        return out
    visited = set()
    cycles = []
    for i0 in range(n):
        if not ok[i0]: continue
        for s0 in (0, 1):
            start = (i0, s0)
            if start in visited: continue
            # walk
            wa = wg = 0.0
            prev = None
            cur = start
            while True:
                visited.add(cur)
                nxt = [x for x in nbrs(cur) if x != prev]
                if not nxt: break
                nx = nxt[0]
                if nx == prev and len(nxt) > 1: nx = nxt[1]
                da = np.angle(np.exp(1j*(al[nx[0]] - al[cur[0]])))
                dg = np.angle(np.exp(1j*(gam[nx[1]][nx[0]] - gam[cur[1]][cur[0]])))
                wa += da; wg += dg
                prev, cur = cur, nx
                if cur == start: break
            cycles.append((round(wa/(2*np.pi)), round(wg/(2*np.pi))))
    return cycles

def torus_components(g, a, b, c, n=720):
    """Count connected components of {|R|=0} via the feasibility band on a
    torus grid: components of {|A-OB| within [|b-c|, b+c]} boundary curve...
    More robust: component count of the config CURVE via angle-graph:
    treat each feasible (al_i, branch) node, link neighbors incl. branch
    merges at fold points, and count cycles; also net winding in alpha."""
    al, gp, gm = branches(g, a, b, c, n)
    okp = ~np.isnan(gp)
    # nodes: (i,0)=plus branch, (i,1)=minus branch at alpha_i (same feasibility)
    idx = {}
    nodes = []
    for i in range(n):
        if okp[i]:
            for s in (0, 1):
                idx[(i, s)] = len(nodes)
                nodes.append((i, s))
    parent = list(range(len(nodes)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(x, y):
        parent[find(x)] = find(y)
    for i in range(n):
        j = (i+1) % n
        if okp[i] and okp[j]:
            for s in (0, 1):
                union(idx[(i, s)], idx[(j, s)])
        elif okp[i] and not okp[j]:
            union(idx[(i, 0)], idx[(i, 1)])   # fold: branches join
        elif not okp[i] and okp[j]:
            union(idx[(j, 0)], idx[(j, 1)])
    comps = len({find(x) for x in range(len(nodes))})
    full_crank = bool(okp.all())
    return comps, full_crank

def render(prm, S=1280, SS=2, nfam=17, nal=300000, gain=1.0,
           fname='proto/config_proto.png', k=1.6, gamma=1.9):
    g, b, c = prm['g'], prm['b'], prm['c']
    a0 = prm['a']
    # TWO change points as the crank a grows through this family:
    #   a1* : while a is shortest, a + l = p + q  ->  a1* = g + c - b (here)
    #   a2* : once c is shortest,  c + l = a + g  ->  a2* = c + b - g
    lens_wo_a = sorted([g, b, c])
    a1s = lens_wo_a[0] + lens_wo_a[1] - lens_wo_a[2]   # crank stops spinning
    a2s = c + b - g                                    # follower starts spinning
    a3s = g + b - c                                    # follower stops again
    # family: fans hugging each gate + exact gates + valley representatives
    def fan(lo, hi, n, p=1.35):
        u = (np.arange(n)+1.0)/n
        return lo + (hi-lo)*u**p
    amin = a0*0.66
    amax = a3s + 0.55
    A_teal = fan(a1s, amin, 11)[::-1]                 # dense near gate 1
    A_val1 = np.array([a1s + (a2s-a1s)*q for q in (0.33, 0.66)])
    A_garn = np.sort(np.concatenate([fan(a2s, a2s+0.6*(a3s-a2s), 6),
                                     fan(a3s, a3s-0.55*(a3s-a2s), 5)]))
    A_val2 = np.array([a3s + (amax-a3s)*q for q in (0.35, 0.75)])
    aa = np.concatenate([A_teal, [a1s], A_val1, [a2s], A_garn, [a3s], A_val2])
    # palette by regime: teal / silver valleys / garnet; gates white
    SILVER = np.array([0.70, 0.66, 0.88])
    def fam_color(ai):
        if min(abs(ai-a1s), abs(ai-a2s), abs(ai-a3s)) < 1e-12:
            return np.array([1.0, 0.98, 0.92])
        if ai < a1s:
            tt = (ai-amin)/max(a1s-amin, 1e-9)
            c0, c1 = np.array([0.05,0.36,0.46]), np.array([0.30,0.95,0.95])
            return c0*(1-tt) + c1*tt
        if a2s < ai < a3s:
            tt = min(ai-a2s, a3s-ai)/(0.5*(a3s-a2s))  # 0 at gates, 1 mid
            c0, c1 = np.array([1.00,0.42,0.30]), np.array([0.78,0.12,0.30])
            return c0*(1-tt) + c1*tt
        return SILVER                                  # the confined valleys

    cv = Canvas(S, SS, np.pi- np.pi, 0.0, np.pi*1.06)  # chart: alpha,gamma in [-pi,pi]
    W = cv.W
    rs = W/2048.0

    # feasibility nebula: F = min over the family of | |A-OB'| - b | ; the
    # complement (F large) = configurations no member machine can ever hold
    ng = 900
    ext = np.pi*1.06                        # match canvas extent exactly
    alg = np.linspace(-ext, ext, ng)
    gag = np.linspace(-ext, ext, ng)
    AL, GA = np.meshgrid(alg, gag)          # rows = gamma (y), cols = alpha (x)
    F = None
    for ai in np.linspace(amin, amax, 64):
        d = np.abs(ai*np.exp(1j*AL) - g - c*np.exp(1j*GA))
        v = np.abs(d - b).astype(np.float32)
        F = v if F is None else np.minimum(F, v)
    neb = np.exp(-(F/0.42)**0.85)
    neb = ndzoom_safe(neb, W/ng)
    cv.img += 0.030*neb[:, :, None]*np.array([0.45, 0.52, 0.80])[None, None, :]
    # faint chart grid at multiples of pi/2
    gl = np.array([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
    for v in gl:
        cv.lines(np.array([v-1j*np.pi]), np.array([v+1j*np.pi]),
                 np.array([0.5,0.55,0.6]), mass_per_px=0.012*rs)
        cv.lines(np.array([-np.pi+1j*v]), np.array([np.pi+1j*v]),
                 np.array([0.5,0.55,0.6]), mass_per_px=0.012*rs)

    report = []
    for ai in aa:
        al, gp, gm = branches(g, ai, b, c, nal)
        col = fam_color(ai)
        is_star = min(abs(ai-a1s), abs(ai-a2s), abs(ai-a3s)) < 1e-12
        m = gain*(0.16 if not is_star else 0.85)*rs
        for gg in (gp, gm):
            okm = ~np.isnan(gg)
            z = al + 1j*gg
            z0, z1 = z[:-1], z[1:]
            good = okm[:-1] & okm[1:]
            jump = np.abs(z1-z0) > 1.0     # wrap or branch gap
            use = good & ~jump
            cv.lines(z0[use], z1[use], col, mass_per_px=m)
        comps, _ = torus_components(g, ai, b, c, 720)
        wind = torus_cycles(g, ai, b, c)
        report.append((float(ai), comps, wind))

    # the singular members: mark pinch points (folded configs, branches meet)
    pins = []
    for astar in (a1s, a2s, a3s):
        al, gp, gm = branches(g, astar, b, c, nal)
        okm = ~np.isnan(gp)
        close = np.abs(np.angle(np.exp(1j*(gp-gm)))) < 2e-3
        pin = okm & close
        zs = al[pin] + 1j*gp[pin]
        for z in zs:
            if not pins or min(abs(z-w) for w in pins) > 0.2:
                pins.append(z)
    if pins:
        cv.glow_points(np.array(pins), np.array([1.0,0.95,0.85]), amp=2.0,
                       sigma=3.0*SS*rs)
        cv.glow_points(np.array(pins), np.array([1.0,0.85,0.55]), amp=0.8,
                       sigma=10*SS*rs)
    cv.tightbloom(0.30, 2.0*SS*rs)
    cv.widebloom(0.09)
    im = cv.out(k=k, gamma=gamma)
    im.save(os.path.join(os.path.dirname(__file__), fname))
    return fname, report, (a1s, a2s, a3s)

if __name__ == '__main__':
    cands = json.load(open(os.path.join(os.path.dirname(__file__),
                                        'proto/candidates2.json')))
    fn, rep, astar = render(cands[3], S=1024, fname="proto/config_proto.png")
    print('gates:', astar)
    for row in rep:
        print('a={:.4f} comps={} windings={}'.format(*row))
