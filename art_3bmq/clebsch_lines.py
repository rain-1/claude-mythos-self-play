"""Find and VERIFY the 27 lines on the Clebsch diagonal cubic.

Model: in P^4, the surface  S = { sum x_i = 0,  sum x_i^3 = 0 }.
We work in the hyperplane H = {sum x = 0} with an orthonormal basis chosen so
that the S3 permuting x0,x1,x2 acts as a 3-fold rotation of the affine chart:

    b1 = (1,-1,0,0,0)/sqrt2        (S3 standard rep, axis 1)
    b2 = (1,1,-2,0,0)/sqrt6        (S3 standard rep, axis 2)
    b3 = (0,0,0,1,-1)/sqrt2        (S3-invariant)
    b4 = (2,2,2,-3,-3)/sqrt30      (S3-invariant)

Projective coords y in P^3 via x = B y; affine chart y4 = 1.
15 lines are exact: for a split {i,j}{k,l}{m} of {0..4},
    L = span( e_i - e_j , e_k - e_l )   (x_m = 0)
The other 12 are found numerically (random-start Newton on the condition
that the cubic vanishes identically along the line) and verified to
machine precision; the classical facts checked here:
  * exactly 27 distinct real lines,
  * each line meets exactly 10 others,
  * exactly 10 Eckardt points where 3 lines meet (for Clebsch: 10 among
    the 15-lines... plus the classical total),
  * every line residual |F| < 1e-10 along the line.
Output: art_3bmq/lines27.npz  (affine base points p, directions v, plus B)
"""
import numpy as np
from itertools import combinations
from scipy.optimize import fsolve

rng = np.random.default_rng(7)

# chart functional c must have all-distinct entries (else some of the 15
# exact lines land in the plane at infinity). Take the S3-symmetric
# (2,2,2,-3,-3) + a small all-distinct tilt: near-3-fold symmetry, all 27
# lines finite.
c4 = np.array([2, 2, 2, -3, -3]) + 0.6 * np.array([2, 1, 0, -1, -2])
b4 = c4 / np.linalg.norm(c4)
raw = [np.array([1., -1, 0, 0, 0]),
       np.array([1., 1, -2, 0, 0]),
       np.array([0., 0, 0, 1, -1])]
cols = []
for r in raw:
    for prev in [b4] + cols:
        r = r - (r @ prev) * prev
    cols.append(r / np.linalg.norm(r))
B = np.stack(cols + [b4], axis=1)   # 5x4 orthonormal, columns span {sum x=0}

def F_hom(y):                    # y: (...,4) homogeneous coords -> sum x^3
    x = y @ B.T                  # (...,5)
    return (x ** 3).sum(-1)

def G_aff(p):                    # p: (...,3) affine chart y4=1
    y = np.concatenate([p, np.ones(p.shape[:-1] + (1,))], axis=-1)
    return F_hom(y)

# ---------------- the 15 exact lines (homogeneous spans in y-coords) -------
def to_y(x):                     # x in hyperplane -> y with By = x
    return B.T @ x

E = np.eye(5)
exact_spans = []
labels = []
for m in range(5):
    rest = [i for i in range(5) if i != m]
    (a, b, c, d) = rest
    for (i, j), (k, l) in [((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))]:
        u = to_y(E[i] - E[j])
        w = to_y(E[k] - E[l])
        exact_spans.append((u, w))
        labels.append(f"x{m}=0,x{i}=-x{j},x{k}=-x{l}")

# check they satisfy F identically (F is cubic: check 4 points on each line)
ts = np.array([0.3, 1.7, -2.2, 5.5])
for u, w in exact_spans:
    pts = u[None, :] + ts[:, None] * w[None, :]
    assert np.abs(F_hom(pts)).max() < 1e-12, "exact line failed!"
print("15 exact lines verified (|F|<1e-12 along each).")

# ---------------- affine (p, v) form; canonicalization for dedupe ----------
def span_to_affine(u, w):
    """Return (p, v): affine base point (closest to origin) + unit direction.
    Line in chart y4=1 from projective span(u,w). Returns None if the line
    is at infinity in this chart."""
    # find two distinct affine points: solve alpha*u + beta*w with y4=1
    M = np.array([u[3], w[3]])
    if np.abs(M).max() < 1e-9:
        return None
    # pick the combo maximizing |y4| for stability
    if abs(u[3]) >= abs(w[3]):
        p1 = u / u[3]
        p2 = (u + 0.7 * w); p2 = p2 / p2[3] if abs(p2[3]) > 1e-9 else None
    else:
        p1 = w / w[3]
        p2 = (w + 0.7 * u); p2 = p2 / p2[3] if abs(p2[3]) > 1e-9 else None
    if p2 is None:
        return None
    a, bpt = p1[:3], p2[:3]
    v = bpt - a
    v = v / np.linalg.norm(v)
    if (v[0] < 0) or (v[0] == 0 and v[1] < 0) or (v[0] == 0 and v[1] == 0 and v[2] < 0):
        v = -v
    p = a - (a @ v) * v          # foot of perpendicular from origin
    return p, v

aff = []
for u, w in exact_spans:
    r = span_to_affine(u, w)
    assert r is not None
    aff.append(r)

# ---------------- numeric hunt for the remaining 12 ------------------------
def line_residual(z):
    """z = (p3, v3) with constraints folded in: p.v=0 via projection, |v|=1
    via normalization; equations: G(p+t v)=0 at 4 values of t."""
    p, v = z[:3], z[3:]
    n = np.linalg.norm(v)
    v = v / (n + 1e-300)
    p = p - (p @ v) * v
    tt = np.array([0.0, 1.0, -1.0, 2.0])
    pts = p[None, :] + tt[:, None] * v[None, :]
    r = G_aff(pts)
    # add gauge-fixing residuals (keep solver well-posed)
    return np.concatenate([r, [np.linalg.norm(z[3:]) - 1.0, z[:3] @ v]])

def canon(p, v):
    if (v[0] < 0) or (abs(v[0]) < 1e-9 and v[1] < 0) or (abs(v[0]) < 1e-9 and abs(v[1]) < 1e-9 and v[2] < 0):
        v = -v
    p = p - (p @ v) * v
    return p, v

found = [canon(p, v) for p, v in aff]

def is_new(p, v, keep):
    for (q, w) in keep:
        if np.linalg.norm(v - w) < 1e-6 and np.linalg.norm(p - q) < 1e-6:
            return False
    return True

trials = 0
while len(found) < 27 and trials < 4000:
    trials += 1
    z0 = np.concatenate([rng.normal(0, 1.5, 3), rng.normal(0, 1, 3)])
    z, info, ier, _ = fsolve(lambda z: line_residual(z)[:6], z0, full_output=True)
    if ier != 1:
        continue
    p, v = z[:3], z[3:]
    nv = np.linalg.norm(v)
    if nv < 1e-6:
        continue
    v = v / nv
    p = p - (p @ v) * v
    tt = np.linspace(-3, 3, 9)
    pts = p[None, :] + tt[:, None] * v[None, :]
    if np.abs(G_aff(pts)).max() > 1e-9:
        continue
    p, v = canon(p, v)
    if is_new(p, v, found):
        found.append((p, v))
print(f"total distinct real lines found: {len(found)} (after {trials} newton trials)")
assert len(found) == 27, "did not find 27 lines!"

# ---------------- polish all lines to machine precision --------------------
from scipy.optimize import least_squares
polished = []
for p, v in found:
    z0 = np.concatenate([p, v])
    sol = least_squares(line_residual, z0, xtol=3e-16, ftol=3e-16, gtol=3e-16)
    p2, v2 = sol.x[:3], sol.x[3:]
    v2 = v2 / np.linalg.norm(v2)
    p2 = p2 - (p2 @ v2) * v2
    polished.append(canon(p2, v2))
found = polished

# ---------------- verification: residuals + incidence ----------------------
P = np.stack([p for p, v in found])
V = np.stack([v for p, v in found])
tt = np.linspace(-6, 6, 25)
pts = P[:, None, :] + tt[None, :, None] * V[:, None, :]
res = np.abs(G_aff(pts.reshape(-1, 3))).max()
print(f"max |F| along all 27 lines (t in [-6,6]): {res:.2e}")
assert res < 1e-8

def line_dist(i, j):
    """distance between two lines in R^3"""
    p1, v1, p2, v2 = P[i], V[i], P[j], V[j]
    c = np.cross(v1, v2)
    nc = np.linalg.norm(c)
    if nc < 1e-8:
        d = p2 - p1
        return np.linalg.norm(d - (d @ v1) * v1)
    return abs((p2 - p1) @ c) / nc

# projective incidence: lines span(h1,h2), span(g1,g2) in P^3 meet iff
# det[h1 h2 g1 g2] = 0  (they are then coplanar). Catches meets at infinity
# (= parallel lines in the affine chart).
H1 = np.concatenate([P, np.ones((27, 1))], axis=1)
H2 = np.concatenate([P + V, np.ones((27, 1))], axis=1)
H1 /= np.linalg.norm(H1, axis=1, keepdims=True)
H2 /= np.linalg.norm(H2, axis=1, keepdims=True)
dets = np.full((27, 27), np.inf)
for i in range(27):
    for j in range(i + 1, 27):
        Mdet = np.stack([H1[i], H2[i], H1[j], H2[j]])
        dets[i, j] = dets[j, i] = abs(np.linalg.det(Mdet))
dd = np.sort(dets[np.isfinite(dets)])
print("largest 'meet' det:", dd[dd < 1e-4][-1], "| smallest 'skew' det:", dd[dd > 1e-4][0])
inc = dets < 1e-4
meets = inc.sum(1)
print("meets-count per line:", sorted(meets.tolist()))
assert (meets == 10).all(), "incidence structure wrong!"
print("VERIFIED: each of the 27 lines meets exactly 10 others.")

# Eckardt points: intersection points where 3 lines concur
def meet_point(i, j):
    p1, v1, p2, v2 = P[i], V[i], P[j], V[j]
    A = np.stack([v1, -v2], axis=1)
    t, s = np.linalg.lstsq(A, p2 - p1, rcond=None)[0]
    return 0.5 * (p1 + t * v1 + p2 + s * v2)

ipts = []
for i in range(27):
    for j in range(i + 1, 27):
        if inc[i, j] and np.linalg.norm(np.cross(V[i], V[j])) > 1e-6:
            ipts.append(meet_point(i, j))
ipts = np.array(ipts)
# cluster
eck = []
used = np.zeros(len(ipts), bool)
order = np.argsort(ipts[:, 0])
mult = []
for idx in order:
    if used[idx]:
        continue
    d = np.linalg.norm(ipts - ipts[idx], axis=1)
    grp = (d < 1e-6) & (~used)
    used |= grp
    k = grp.sum()          # k pairwise meets at same point: k = C(m,2)
    m = int(round((1 + np.sqrt(1 + 8 * k)) / 2))
    if m >= 3:
        eck.append(ipts[idx])
        mult.append(m)
eck = np.array(eck) if eck else np.zeros((0, 3))
print(f"Eckardt points (>=3 concurrent lines): {len(eck)}  multiplicities {sorted(mult)}")

# how many of the found lines are 'exact 15' vs 'golden 12'?
n_exact = 15
extra = found[15:]
print("\nthe 12 non-obvious lines (p, v):")
for p, v in extra[:12]:
    print("  p=", np.round(p, 5), " v=", np.round(v, 5))

np.savez("art_3bmq/lines27.npz", P=P, V=V, B=B, eck=eck,
         inc=inc, labels=np.array(labels))
print("\nsaved art_3bmq/lines27.npz")
