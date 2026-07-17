"""Four-bar linkage engine + Roberts-Chebyshev cognates, with certificates.

Convention: ground pivots OA, OB in the complex plane. Crank OA->A length a,
coupler A->B length b, follower OB->B length c. Coupler point P = A + mu*(B-A),
mu complex. Angles: alpha = arg(A-OA), beta = arg(B-A), gamma = arg(B-OB).

Roberts: with OC = OA + mu*(OB-OA),
  P = OA + a e^{ia} + mu b e^{ib}            (machine 1: crank tracks alpha)
    = OB + c e^{ig} + (mu-1) b e^{ib}        (machine 3 chain)
    = OC + mu c e^{ig} + (1-mu) a e^{ia}     (machine 2 chain)

Machine 2 (OA, OC): crank OA len |mu|b tracks beta+arg(mu); coupler len |mu|a
  tracks alpha; follower OC len |mu|c tracks gamma+arg(mu); coupler-point ratio 1/mu.
Machine 3 (OB, OC): crank OB len |mu-1|b tracks beta+arg(mu-1); coupler len
  |1-mu|c tracks gamma; follower OC len |1-mu|a tracks alpha+arg(1-mu);
  coupler-point ratio 1/(1-mu).
"""
import numpy as np

def solve_follower(A, OB, b, c, branch=+1):
    """Given moving pivot A, find B with |B-A|=b, |B-OB|=c. Returns complex B
    (nan where no solution). branch = +1/-1 picks intersection side."""
    d = OB - A
    L = np.abs(d)
    with np.errstate(invalid='ignore', divide='ignore'):
        x = (L**2 + b**2 - c**2) / (2 * L)   # along A->OB
        h2 = b**2 - x**2
        h = np.sqrt(np.where(h2 >= 0, h2, np.nan))
    u = d / np.where(L == 0, np.nan, L)
    return A + u * (x + 1j * branch * h)

def trace(OA, OB, a, b, c, mu, n=20000, branch=+1):
    """Drive crank angle alpha uniformly over [0,2pi); keep only feasible poses.
    Returns dict with alpha, A, B, P, beta, gamma, feasible mask."""
    alpha = np.linspace(0, 2 * np.pi, n, endpoint=False)
    A = OA + a * np.exp(1j * alpha)
    B = solve_follower(A, OB, b, c, branch)
    ok = ~np.isnan(B)
    P = A + mu * (B - A)
    beta = np.angle(B - A)
    gamma = np.angle(B - OB)
    return dict(alpha=alpha, A=A, B=B, P=P, beta=beta, gamma=gamma, ok=ok)

def grashof(g, a, b, c):
    """Returns (class_string, s+l-(p+q)). Links: ground g, crank a, coupler b, follower c."""
    L = np.sort([g, a, b, c])
    s, l = L[0], L[3]
    excess = s + l - (L[1] + L[2])
    if excess < 0:
        lens = dict(ground=g, crank=a, coupler=b, follower=c)
        shortest = min(lens, key=lens.get)
        cls = {'crank': 'crank-rocker', 'ground': 'double-crank',
               'coupler': 'double-rocker(Grashof)', 'follower': 'rocker-crank'}[shortest]
    elif excess > 0:
        cls = 'non-Grashof triple-rocker'
    else:
        cls = 'change-point'
    return cls, excess

def cognates(OA, OB, a, b, c, mu):
    """Return the two Roberts cognates as (OA', OB', a', b', c', mu') tuples,
    ordered so that trace(...) with these params draws the same coupler curve."""
    OC = OA + mu * (OB - OA)
    m2 = (OA, OC, abs(mu) * b, abs(mu) * a, abs(mu) * c, 1 / mu)
    m3 = (OB, OC, abs(mu - 1) * b, abs(1 - mu) * c, abs(1 - mu) * a, 1 / (1 - mu))
    return m2, m3, OC

def curve_setdist(Pa, Pb, sub=None):
    """Symmetric Hausdorff distance between two complex point clouds (KDTree)."""
    from scipy.spatial import cKDTree
    Pa = Pa[~np.isnan(Pa)]; Pb = Pb[~np.isnan(Pb)]
    Xa = np.c_[Pa.real, Pa.imag]; Xb = np.c_[Pb.real, Pb.imag]
    d1 = cKDTree(Xb).query(Xa)[0].max()
    d2 = cKDTree(Xa).query(Xb)[0].max()
    return max(d1, d2)

def full_pointset(OA, OB, a, b, c, mu, n=6000):
    """Both branches concatenated -> the complete coupler curve point set."""
    t1 = trace(OA, OB, a, b, c, mu, n, +1)
    t2 = trace(OA, OB, a, b, c, mu, n, -1)
    return np.concatenate([t1['P'][t1['ok']], t2['P'][t2['ok']]])

def sextic_certificate(P, rng=np.random.RandomState(7)):
    """Fit an implicit algebraic curve through the coupler-curve points.
    Returns (deg5_smallest_sv, deg6_smallest_sv, tricircularity_ratio):
    deg-6 sv ~ 0 (curve IS a sextic), deg-5 sv >> 0 (it is not a quintic),
    and the degree-6 homogeneous part is proportional to (x^2+y^2)^3.
    """
    P = P[~np.isnan(P)]
    P = P[rng.choice(len(P), min(4000, len(P)), replace=False)]
    x, y = P.real, P.imag
    # center+scale for conditioning (affine change keeps degree & circularity)
    s = np.hypot(x - x.mean(), y - y.mean()).std()   # ISOTROPIC scale only
    x = (x - x.mean()) / s; y = (y - y.mean()) / s
    def vander(deg):
        cols = [(x**i) * (y**j) for i in range(deg + 1) for j in range(deg + 1 - i)]
        return np.array(cols).T, [(i, j) for i in range(deg + 1) for j in range(deg + 1 - i)]
    out = {}
    for deg in (5, 6):
        M, idx = vander(deg)
        M = M / np.linalg.norm(M, axis=0)          # column scaling
        sv = np.linalg.svd(M, compute_uv=False)
        out[deg] = sv[-1] / sv[0]
    # tricircularity: leading form of the deg-6 fit
    M, idx = vander(6)
    colnorm = np.linalg.norm(M, axis=0)
    _, _, Vt = np.linalg.svd(M / colnorm)
    coef = Vt[-1] / colnorm                        # raw-monomial coefficients
    lead = {(i, j): c for (i, j), c in zip(idx, coef) if i + j == 6}
    # (x^2+y^2)^3 = x^6 + 3x^4y^2 + 3x^2y^4 + y^6
    target = {(6, 0): 1, (4, 2): 3, (2, 4): 3, (0, 6): 1, (5, 1): 0, (3, 3): 0,
              (1, 5): 0}
    v = np.array([lead[k] for k in sorted(target)])
    t = np.array([target[k] for k in sorted(target)], float)
    # best scalar s minimizing |v - s t|; report relative residual
    s = (v @ t) / (t @ t)
    tric = np.linalg.norm(v - s * t) / np.linalg.norm(v)
    return out[5], out[6], tric

if __name__ == '__main__':
    rng = np.random.RandomState(3)
    # a Grashof crank-rocker: crank shortest
    OA, OB = 0 + 0j, 4.0 + 0j
    a, b, c = 1.0, 3.4, 2.6
    mu = 0.55 + 0.78j
    cls, ex = grashof(abs(OB - OA), a, b, c)
    print('class:', cls, 'excess:', ex)

    P1 = full_pointset(OA, OB, a, b, c, mu)
    (m2, m3, OC) = cognates(OA, OB, a, b, c, mu)
    P2 = full_pointset(*m2)
    P3 = full_pointset(*m3)
    print('cognate2 curve dist:', curve_setdist(P1, P2))
    print('cognate3 curve dist:', curve_setdist(P1, P3))

    # Roberts fixed-pivot triangle similar to coupler triangle: OC-OA = mu (OB-OA)
    print('pivot-triangle ratio check:', abs((OC - OA) / (OB - OA) - mu))

    s5, s6, tric = sextic_certificate(P1)
    print('deg5 smallest sv (should be >>0):', s5)
    print('deg6 smallest sv (should be ~0):', s6)
    print('tricircularity rel residual (should be ~0):', tric)
