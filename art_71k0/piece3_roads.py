"""Piece 3: THE ROADS HOME (2560^2).
Every non-real root of x^n - x + d = 0, for EVERY real d, lives on one fixed
curve  R^(n-1) sin(n psi) = sin(psi)  (x = R e^{i psi})  -- plus the real axis.
Bohl 1908; Cermak-Fedorkova-Jansky, Pacific J. Math 332 (2024); MO 513995.

Layers per panel:
  - roads: base silver polyline of the full locus (arcs + real axis)
  - traffic: occupation measure of the 5 roots as d sweeps R with Cauchy
    weight w(d) = 1/(1+(d/s)^2): ink per arc sample = w(d(psi))|d'(psi)| dpsi
    (dim where the root rushes -- collisions -- bright where it lingers)
  - milestones: cyan bead-sets = the n roots at chosen d values (np.roots,
    each certified to sit on the sampled road within tol)
  - collision stars: gold at x = +-n^{-1/(n-1)} (double roots, d = +-d*_n)
  - asymptote rays psi = k pi / n: faint violet
Main panel n=5; bottom strip n=3,4,6,7,8,9."""
import numpy as np, sys
from artlib import canvas, polyline, star, bloom, tonemap, save, bake_text, _splat_points

PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"
FINAL = 1280 if PREVIEW else 2560
SS = 1 if PREVIEW else 2
S = FINAL * SS
rs = S / 1280.0

GOLD  = np.array([1.00, 0.70, 0.24])
CYAN  = np.array([0.45, 0.92, 1.00])
SILV  = np.array([0.62, 0.70, 0.86])
VIOL  = np.array([0.52, 0.38, 0.85])
WHITE = np.array([1.0, 0.97, 0.9])

def arcs_of(n, nsamp=24000):
    """upper-half-plane arcs of R^(n-1) = sin(psi)/sin(n psi): list of
    (psi, R, d, dprime) arrays per positive interval."""
    zeros = np.array([k*np.pi/n for k in range(0, n+1)])
    out = []
    for k in range(len(zeros)-1):
        a, b = zeros[k], zeros[k+1]
        ps = np.linspace(a, b, nsamp+2)[1:-1]
        rat = np.sin(ps)/np.sin(n*ps)
        good = rat > 0
        if not good.any(): continue
        ps, rat = ps[good], rat[good]
        R = rat**(1.0/(n-1))
        d = R*np.sin((n-1)*ps)/np.sin(n*ps)
        dp = np.gradient(d, ps)
        out.append((ps, R, d, dp))
    return out

def draw_panel(buf, n, cx, cy, scale, lw_amp, main=True):
    lim = 2.35
    sc_norm = scale / (0.170*S)          # traffic ink is per-unit-length: scale it
    def to_px(z):
        return cx + np.real(z)*scale, cy - np.imag(z)*scale
    # asymptote rays
    for k in range(1, n):
        th = k*np.pi/n
        for sgn in (1, -1):
            t = np.linspace(0.9, lim*1.35, 200)
            z = t*np.exp(1j*th*sgn)
            xs, ys = to_px(z)
            _splat_points(buf, xs, ys, 0.028*lw_amp*rs, VIOL, 1)
    # real axis road + traffic
    xr = np.linspace(-lim*1.3, lim*1.3, 30000)
    d = xr - xr**n
    w = 1.0/(1.0 + (d/1.2)**2)
    dp = np.abs(1 - n*xr**(n-1))
    dx = xr[1]-xr[0]
    xs, ys = to_px(xr + 0j)
    _splat_points(buf, xs, ys, 0.042*lw_amp*rs, SILV, 1)
    _splat_points(buf, xs, ys, 160.0*lw_amp*rs*sc_norm*w*dp*dx, GOLD, 1)
    # complex arcs (upper + mirrored)
    for (ps, R, d, dp) in arcs_of(n):
        z = R*np.exp(1j*ps)
        keep = np.abs(z) < lim*1.35
        z, dloc, dploc, psloc = z[keep], d[keep], dp[keep], ps[keep]
        if len(z) < 4: continue
        dpsi = np.abs(np.gradient(psloc))
        w = 1.0/(1.0 + (dloc/1.2)**2)
        ink = 160.0*lw_amp*rs*sc_norm*w*np.abs(dploc)*dpsi
        for conj in (1, -1):
            zz = np.real(z) + 1j*conj*np.imag(z)
            xs, ys = to_px(zz)
            _splat_points(buf, xs, ys, 0.012*lw_amp*rs, SILV, 1)
            _splat_points(buf, xs, ys, ink, GOLD, 1)
    # collision stars: x = +- n^{-1/(n-1)}
    xc = n**(-1.0/(n-1))
    for sgn in (1, -1):
        xs, ys = to_px(sgn*xc + 0j)
        star(buf, xs, ys, WHITE, amp=(1.3 if main else 0.55)*lw_amp,
             rad=(5.2 if main else 3.2)*rs)
    # milestones
    dvals = ([0.0, 0.25, 0.535, 1.0, 2.0, -0.25, -0.535, -1.0, -2.0]
             if main else [0.0, 1.0, -1.0])
    cert = []
    road_pts = []
    for (ps, R, dd, dp) in arcs_of(n, 4000):
        z = R*np.exp(1j*ps)
        road_pts.append(z); road_pts.append(np.conj(z))
    road = np.concatenate(road_pts) if road_pts else np.array([])
    for dv in dvals:
        coeffs = [1.0] + [0.0]*(n-2) + [-1.0, dv]
        rts = np.roots(coeffs)
        for r in rts:
            if abs(r.imag) > 1e-9 and len(road):
                cert.append(np.min(np.abs(road - r)))
            xs, ys = to_px(r)
            star(buf, xs, ys, CYAN, amp=(0.95 if main else 0.45)*lw_amp,
                 rad=(3.0 if main else 1.8)*rs)
    if cert:
        print(f"n={n}: milestone max road-distance {max(cert):.2e} "
              f"(certify < 2e-3 of unit)")
        assert max(cert) < 2e-3
    return

buf = canvas(S)
# main panel n=5
draw_panel(buf, 5, 0.50*S, 0.415*S, 0.170*S, 1.0, main=True)
# bottom strip
ns = [3, 4, 6, 7, 8, 9]
for i, n in enumerate(ns):
    cx = (0.09 + 0.164*i)*S
    draw_panel(buf, n, cx, 0.875*S, 0.030*S, 0.5, main=False)

buf *= (1.0 if PREVIEW else 1.8)   # FINAL_BOOST: thin-line loss at LANCZOS downscale
buf = bloom(buf, sigmas=(2*rs, 8*rs, 26*rs), weights=(1.0, 0.32, 0.15),
            thresh=0.6)
img = tonemap(buf, k=1.05, gamma=0.90)

fs = int(15*rs)
texts = [
 (0.035*S, 0.035*S, "THE ROADS HOME", int(34*rs), (1,0.92,0.75), True, "la"),
 (0.035*S, 0.035*S+int(44*rs), "every non-real root of  x⁵ − x + d,  for every real d,"
  " travels one fixed curve", fs, (0.8,0.82,0.9), False, "la"),
 (0.035*S, 0.035*S+int(66*rs), "R⁴·sin 5ψ = sin ψ      traffic = occupation as d sweeps ℝ (Cauchy-weighted)",
  fs, (0.8,0.82,0.9), False, "la"),
 (0.035*S, 0.035*S+int(88*rs), "gold = the roads lit by dwell · cyan beads = the five roots at d = 0, ±¼, ±d*, ±1, ±2",
  fs, (0.65,0.68,0.78), False, "la"),
 (0.035*S, 0.035*S+int(110*rs), "white stars = collisions (double roots) at x = ±5^{-1/4}, d* = (4/5)·5^{-1/4} ≈ 0.53499",
  fs, (0.65,0.68,0.78), False, "la"),
 (0.965*S, 0.035*S, "Bohl 1908 · Čermák–Fedorková–Jánský PJM 332 (2024) · MO 513995",
  fs, (0.6,0.62,0.72), False, "ra"),
 (0.965*S, 0.035*S+int(22*rs), "identities verified symbolically + 60 digits, n = 3–12",
  fs, (0.6,0.62,0.72), False, "ra"),
 (0.09*S, 0.955*S, "the family xⁿ − x + d:   n = 3, 4, 6, 7, 8, 9",
  fs, (0.6,0.62,0.72), False, "la"),
]
img = bake_text(img, texts, S)
save(img, "roads_preview.png" if PREVIEW else "roads_2560.png", final=FINAL)
print("saved", "preview" if PREVIEW else "final")
