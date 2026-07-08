import numpy as np

print("=== 1. Gauss map transfer operator: mixing rate vs GKW lambda=0.30366 ===")
M = 20000
x = (np.arange(M) + 0.5) / M
g = 1.0/(np.log(2)*(1+x))           # Gauss measure density
def L(f):
    # (Lf)(x) = sum_k f(1/(k+x)) / (k+x)^2 ; tail beyond K: f ~ f(0+) region, use asymptotic
    out = np.zeros_like(x)
    K = 4000
    for k in range(1, K+1):
        u = 1.0/(k+x)
        out += np.interp(u, x, f) / (k+x)**2
    # tail: sum_{k>K} f(1/(k+x))/(k+x)^2 ~ f(0)*sum 1/(k+x)^2 ~ f0*(1/(K+x))
    f0 = f[0]
    out += f0/(K+x)   # approx integral tail
    return out
# initial: narrow bump at 1/phi
phi = (1+np.sqrt(5))/2
x0 = 1/phi
f = np.exp(-0.5*((x-x0)/0.01)**2); f /= np.mean(f)   # density integrates to 1
prev = None
for n in range(1, 13):
    f = L(f)
    dev = np.max(np.abs(f-g))
    r = dev/prev if prev else float('nan')
    prev = dev
    print(f"  n={n:2d}  sup|f-g|={dev:.3e}  ratio={r:.4f}")
print("  (expect ratio -> 0.3036 = GKW lambda)")
print("  mass check:", np.mean(f))

print()
print("=== 2. Arnold cat map period mod N ===")
def order(N):
    A = np.array([[1,1],[1,2]], dtype=object)
    M_ = np.array([[1,0],[0,1]], dtype=object)
    t = 0
    while True:
        M_ = (M_ @ A) % N
        t += 1
        if (M_ == np.eye(2, dtype=object)).all(): return t
        if t > 100000: return -1
for N in [256, 512, 1024]:
    print(f"  N={N}: period={order(N)}")
# ghost times for N=512: scan smallness of A^t mod N (centered)
N = 512
A = np.array([[1,1],[1,2]], dtype=object)
M_ = np.eye(2, dtype=object)
best = []
per = order(N)
for t in range(1, per):
    M_ = (M_ @ A) % N
    C = np.array([[int(v) if v <= N//2 else int(v)-N for v in row] for row in M_])
    norm = np.abs(C).max()
    if norm <= 8:
        best.append((t, norm, C.tolist()))
M2 = np.eye(2, dtype=object)
print("  near-identity times (|entries|<=8):", [(t,n) for t,n,_ in best])
for t,n,C in best[:8]: print(f"    t={t}: {C}")

print()
print("=== 3. Pell x^2-2y^2=n: fundamental orbits ===")
# brute scan box, reduce by unit action u:(x,y)->(x+2y,x+y), inverse (x,y)->(x-2y? ) inv of (1+sqrt2) is (-1+sqrt2): (x,y)->(-x+2y, x-y)
def norm2(x,y): return x*x-2*y*y
found = {}
B = 300
for xx in range(-B, B+1):
    for yy in range(-B, B+1):
        n = norm2(xx,yy)
        if n != 0 and abs(n) <= 12:
            found.setdefault(n, []).append((xx,yy))
def reduce_pt(x,y):
    # move into fundamental domain by applying unit^{\pm1} to minimize x^2+y^2
    while True:
        cands = [(x+2*y, x+y), (-x+2*y, x-y), (x,y)]
        best_ = min(cands, key=lambda p: p[0]**2+p[1]**2)
        if best_ == (x,y): return (x,y)
        x,y = best_
for n in sorted(found, key=lambda v:(abs(v), v))[:10]:
    reps = set()
    for (xx,yy) in found[n]:
        r = reduce_pt(xx,yy)
        # also fold sign symmetry (x,y)->(-x,-y)
        r = max(r, (-r[0],-r[1]))
        reps.add(r)
    print(f"  n={n:3d}: #lattice pts in box={len(found[n]):5d}, orbit reps (mod units,±)={sorted(reps)}")
