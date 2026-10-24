"""Build the panel textures (face id + lead distance + ripple height) and the globe planes."""
import numpy as np
from graph import tutte, degrees, check_planar
from geo import geodesic
from scipy import ndimage

V, F = geodesic(1)
F = [tuple(int(x) for x in f) for f in F]
n = len(V)
deg = degrees(F)
FC = np.array([V[list(f)].mean(0) for f in F])
FC /= np.linalg.norm(FC, axis=1)[:, None]


def outer_faces():
    o1 = [f for f in F if any(deg[v] == 5 for v in f)][0]
    o2 = [f for f in F if all(deg[v] == 6 for v in f)][0]
    return o1, o2


def stereo(outer):
    c = V[list(outer)].mean(0); c /= np.linalg.norm(c)
    z = c; x = np.cross(z, [0.3, 0.5, 0.7]); x /= np.linalg.norm(x); y = np.cross(z, x)
    Q = V @ np.stack([x, y, z], 1)
    return Q[:, :2] / (1 - Q[:, 2:3] + 1e-9)


def drawings():
    o1, o2 = outer_faces()
    out = []
    out.append(('tutte', o1, tutte(F, n, o1)))
    out.append(('tutte', o2, tutte(F, n, o2)))
    S1 = stereo(o1)
    out.append(('soft', o1, tutte(F, n, o1, lambda u, v: np.linalg.norm(S1[u] - S1[v]) ** 0.6)))
    S2 = stereo(o2)
    out.append(('even', o2, tutte(F, n, o2, lambda u, v: np.linalg.norm(S2[u] - S2[v]) ** 1.8)))
    S3 = stereo(o1)
    out.append(('even', o1, tutte(F, n, o1, lambda u, v: np.linalg.norm(S3[u] - S3[v]) ** 1.8)))
    return out


def normalise(P, outer, apex_up=True):
    """Map so the outer triangle is equilateral with unit side, centroid at origin, apex up/down."""
    a, b, c = [P[v] for v in outer]
    src = np.array([a, b, c])
    ang = np.pi / 2 + np.array([0, 2, 4]) * np.pi / 3
    if not apex_up:
        ang = ang + np.pi
    dst = np.stack([np.cos(ang), np.sin(ang)], 1) / np.sqrt(3)
    # affine map src -> dst
    A = np.c_[src, np.ones(3)]
    M = np.linalg.solve(A, dst)
    Q = np.c_[P, np.ones(len(P))] @ M
    # orientation: inner faces must stay ccw for consistent texture (mirror allowed)
    return Q


def panel_texture(P, outer, res=1400, lead=0.0075, frame=0.016, seed=0):
    """Returns face-id (int16, -1 = outside), distance-to-lead (in local units), ripple height."""
    half = 0.62
    xs = np.linspace(-half, half, res)
    X, Y = np.meshgrid(xs, -xs)
    fid = -np.ones((res, res), np.int16)
    dist = np.full((res, res), 9.0, np.float32)
    for k, f in enumerate(F):
        if set(f) == set(outer):
            continue
        a, b, c = P[list(f)]
        # barycentric inside test with edge distances
        ds = []
        sgn = np.sign(np.cross(b - a, c - a))
        for p, q in ((a, b), (b, c), (c, a)):
            e = q - p
            L = np.hypot(*e)
            d = sgn * ((X - p[0]) * e[1] * -1 + (Y - p[1]) * e[0]) / L
            ds.append(d)
        dm = np.minimum(np.minimum(ds[0], ds[1]), ds[2])
        inside = dm >= 0
        fid[inside] = k
        dist[inside] = dm[inside]
    # distance to outer boundary for the frame came
    A, B, C = P[list(outer)]
    sgn = np.sign(np.cross(B - A, C - A))
    dsb = []
    for p, q in ((A, B), (B, C), (C, A)):
        e = q - p; L = np.hypot(*e)
        dsb.append(sgn * ((X - p[0]) * -e[1] + (Y - p[1]) * e[0]) / L)
    dout = np.minimum(np.minimum(dsb[0], dsb[1]), dsb[2])  # >0 inside outer triangle... sign below
    if (dout[res // 2, res // 2]) < 0:
        dout = -dout
    # lead profile value: s = signed distance to nearest came centre-line, came half-width
    leadd = np.where(dout < frame, np.abs(dout - frame * 0.5) - frame * 0.5, dist - lead)
    leadd = np.where(dout < 0, 9.0, leadd)
    # came half width map for shading (the frame is wider)
    hw = np.where(dout < frame * 1.5, frame * 0.5, lead).astype(np.float32)
    rng = np.random.default_rng(seed)
    # ripple: smooth noise, different per face orientation (cathedral glass)
    noise = rng.standard_normal((res, res)).astype(np.float32)
    h = ndimage.gaussian_filter(noise, res / 90) * 1.0
    h2 = ndimage.gaussian_filter(rng.standard_normal((res, res)).astype(np.float32), res / 30)
    h = h / (h.std() + 1e-9) + 0.6 * h2 / (h2.std() + 1e-9)
    return fid, leadd.astype(np.float32), hw, h.astype(np.float32), half


def face_colours(seed=3):
    """Hue = azimuth around the axis through the first outer face; paleness by latitude."""
    o1, _ = outer_faces()
    z = V[list(o1)].mean(0); z /= np.linalg.norm(z)
    x = np.cross(z, [0.3, 0.5, 0.7]); x /= np.linalg.norm(x); y = np.cross(z, x)
    Q = FC @ np.stack([x, y, z], 1)
    az = (np.arctan2(Q[:, 1], Q[:, 0]) / (2 * np.pi)) % 1
    lat = np.arccos(np.clip(Q[:, 2], -1, 1)) / np.pi  # 0 near outer face, 1 opposite
    return az, lat
