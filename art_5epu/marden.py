"""COMPANION A — 'The Foci of the Made'  (Marden / Siebeck, the geometric lens).

Marden's theorem: for a cubic p with roots at the vertices A,B,C of a triangle,
the roots of p' are the two FOCI of the Steiner inellipse (inscribed, tangent to
each side at its midpoint). So the critical points ARE the foci of the ellipse
the triangle inscribes. A constellation of cubics shows the theorem across the
whole range of triangle shapes: near-equilateral (the inellipse is nearly a
circle, its foci nearly coincident -- the critical points merge) through scalene
and elongated (the foci -- the critical points -- pull far apart). One grand
central cubic anchors the plate. Foci = blazing cyan; midpoint tangencies = cyan
beads; vertices + edges + inellipse = gold.

Run:  python3 marden.py [FINAL]
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import tonemap, fast_bloom, splat, line_splat, downscale, fatten

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 640
SS = 2
S = FINAL * SS
R = 1.62
rs = FINAL / 640.0
PXU = S/(2*R)

def w2p(z):
    z = np.atleast_1d(z)
    return np.stack([(z.real + R)/(2*R)*S, (R - z.imag)/(2*R)*S], -1)

def steiner(A, B, C):
    f = np.roots(np.polyder(np.poly([A, B, C])))
    g = (A + B + C)/3
    M = (A + B)/2
    a = (abs(M - f[0]) + abs(M - f[1]))/2
    c = abs(f[0] - f[1])/2; b = np.sqrt(max(a*a - c*c, 0))
    u = (f[1] - f[0])/(abs(f[1] - f[0]) + 1e-18)
    return g, f, a, b, u

def ellipse_pts(g, a, b, u):
    m = max(64, int(2*np.pi*max(a, b, 1e-3)*PXU))
    t = np.linspace(0, 2*np.pi, m)
    return g + a*np.cos(t)*u + b*np.sin(t)*(1j*u)

GOLD  = np.array([0.98, 0.78, 0.38], np.float32)
GOLDE = np.array([1.0,  0.85, 0.52], np.float32)
CYAN  = np.array([0.55, 0.92, 1.0],  np.float32)
buf = np.zeros((S, S, 3), np.float32)

def add_field(roots, bright=0.5):
    """Faint equipotential net of a cubic's roots -> rings pinch into figure-
    eights at the two foci (= critical points = the Steiner foci). Ties the
    geometric lens back to the hero's electrostatic register."""
    xs = np.linspace(-R, R, S, dtype=np.float32); ys = np.linspace(R, -R, S, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)
    U = np.zeros((S, S), np.float32)
    for z0 in roots:
        U += np.log(np.hypot(X - z0.real, Y - z0.imag) + 1e-9).astype(np.float32)
    gy, gx = np.gradient(U); gmag = np.hypot(gx, gy) + 1e-9
    dU = 0.5
    frac = np.abs((U/dU + 0.5) % 1.0 - 0.5)
    contour = np.exp(-((frac*dU/gmag)/(0.9*SS*rs))**2)
    rad = np.hypot(X, Y)
    fade = np.clip(1.0 - (rad - 0.42)/0.52, 0.0, 1.0)
    buf[..., 0] += contour*fade*GOLD[0]*bright
    buf[..., 1] += contour*fade*GOLD[1]*bright
    buf[..., 2] += contour*fade*GOLD[2]*bright

ink = np.zeros((S, S, 3), np.float32)           # thin strokes -> fattened later
focus_layer = np.zeros((S, S, 3), np.float32)   # foci get their own bloom pass

def draw_cubic(A, B, C, w=1.0, echo=True):
    """Draw one cubic's Marden picture. w scales brightness (hero brighter)."""
    g, f, a, b, u = steiner(A, B, C)
    # soft warm nimbus: a breathing echo family nested around the inellipse
    if echo:
        for k in range(22):
            s = 1.0 + 0.19*np.cos(2*np.pi*k/22)
            ep = ellipse_pts(g, a*s, b*s, u)
            splat(ink, w2p(ep), GOLD*0.8, 0.035*w, S)
    # triangle edges
    for P, Q in [(A, B), (B, C), (C, A)]:
        line_splat(ink, w2p(P)[0], w2p(Q)[0], GOLD, 0.62*w, S)
    # Steiner inellipse
    splat(ink, w2p(ellipse_pts(g, a, b, u)), GOLDE, 0.95*w, S)
    # midpoint tangency beads
    mids = np.array([(A+B)/2, (B+C)/2, (C+A)/2])
    splat(focus_layer, w2p(mids), (0.30, 0.62, 0.80), 9.0*SS*rs*w, S)
    # vertices
    splat(focus_layer, w2p(np.array([A, B, C])), (0.70, 0.62, 0.40), 10.0*SS*rs*w, S)
    # FOCI = the critical points -> own layer so they blaze
    splat(focus_layer, w2p(f), (0.45, 0.96, 1.0), 42.0*SS*rs*w, S)
    return f, a, b

# --- constellation: a grand central cubic + satellites across the shape range
specs = []
# central hero (scalene, moderate)
specs.append((0.0+0.0j, 0.94, [1.95, 4.55, -0.35], 1.0))
# central cubic's field FIRST (behind everything)
_cA = 0.94*np.array([np.exp(1j*a) for a in [1.95, 4.55, -0.35]])
add_field(_cA, bright=0.30)
# satellites: (center, scale, vertex-angles, weight)
rng = np.random.default_rng(7)
sat = [
    (-1.05+0.78j, 0.34, [0.4, 2.5, 4.6], 0.62),      # near-equilateral (foci merge)
    ( 1.06+0.82j, 0.40, [0.9, 2.0, 4.9], 0.62),      # obtuse
    ( 1.14-0.86j, 0.36, [1.4, 2.2, 5.3], 0.62),      # elongated (foci far)
    (-1.12-0.80j, 0.38, [0.2, 1.9, 3.9], 0.62),      # scalene
    ( 0.02+1.24j, 0.30, [0.6, 2.7, 4.2], 0.55),      # small top
    ( 0.00-1.26j, 0.30, [1.1, 3.0, 5.1], 0.55),      # small bottom
]
specs += sat

sep_report = []
for center, scale, angs, w in specs:
    V = center + scale*np.array([np.exp(1j*a) for a in angs])
    f, a, b = draw_cubic(V[0], V[1], V[2], w=w)
    sep_report.append((abs(f[0]-f[1]), b/max(a,1e-9)))

# fatten the thin stroke art so it survives the downscale (rs-scaled width)
buf += fatten(ink, 1.0*SS*rs)
# foci: hot core + tight + wide bloom so each critical point is a blazing star
fbloom = fast_bloom(focus_layer, 2*SS*rs)*1.3 + fast_bloom(focus_layer, 9*SS*rs)*0.6
buf += focus_layer*1.6 + fbloom
bloom = fast_bloom(buf, 5*SS*rs)*0.5 + fast_bloom(buf, 18*SS*rs)*0.32
out = downscale(tonemap(buf + bloom, k=1.7, gamma=0.85), SS)
name = "variants/marden_v1.png" if FINAL <= 800 else "marden.png"
out.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), name))
print("saved", name, out.size)
for i,(sep,ecc) in enumerate(sep_report):
    print(f"  cubic {i}: foci-sep={sep:.3f}  b/a={ecc:.3f}")
