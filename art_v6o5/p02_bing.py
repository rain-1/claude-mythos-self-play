"""02 - A House That Forgets Every Loop.

Bing's house with two rooms is a 2-dimensional complex you can build inside a
box. The upper room is reachable only by a chimney that rises from the bottom
face, straight up THROUGH the lower room, and opens above. The lower room is
reachable only by a chimney that drops from the top face, down THROUGH the
upper room, and opens below. Two connecting walls finish it.

The house is CONTRACTIBLE: it has no holes a loop could catch on; topology says
you can shrink the whole thing to a point, so every loop is forgettable. Yet it
is NOT COLLAPSIBLE -- there is no free face to start folding from, no first
step. A thing that is trivial, and yet that you cannot trivialise by any honest
local move. We sphere-trace it as a cut-away dollhouse so the two impossible
chimneys can be seen passing through the wrong rooms.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

import os
TH = 0.05          # wall half-thickness
CW = 0.28          # chimney half-width (inner)
CXL, CXR = -0.46, 0.46   # left / right chimney horizontal centres (x)
CZL = float(os.environ.get("CZL", "0.22"))   # left chimney toward front
CZR = float(os.environ.get("CZR", "-0.22"))  # right chimney toward back


def box(p, c, h):
    q = np.abs(p - c) - h
    qm = np.maximum(q, 0.0)
    return np.minimum(np.maximum(q[..., 0], np.maximum(q[..., 1], q[..., 2])), 0.0) \
        + np.sqrt((qm ** 2).sum(-1) + 1e-12)


def slab(p, c, h):
    return box(p, np.array(c), np.array(h))


def holed(p, c, h, hc, hh):
    """A wall (c,h) with a rectangular hole (hc,hh) punched through it."""
    d = slab(p, c, h)
    hole = slab(p, hc, hh)
    return np.maximum(d, -hole)


def chimney(p, cx, y0, y1, cz=0.0):
    """Four thin walls forming an open square tube spanning y in [y0,y1]."""
    yc, yh = 0.5 * (y0 + y1), 0.5 * (y1 - y0)
    d = slab(p, [cx - CW, yc, cz], [TH, yh, CW])
    d = np.minimum(d, slab(p, [cx + CW, yc, cz], [TH, yh, CW]))
    d = np.minimum(d, slab(p, [cx, yc, cz - CW], [CW, yh, TH]))
    d = np.minimum(d, slab(p, [cx, yc, cz + CW], [CW, yh, TH]))
    return d


# material ids
M_SHELL, M_FLOOR, M_UP, M_LO, M_FIN = 0, 1, 2, 3, 4
BIG = 1e9


def scene(p, zclip=0.62):
    """Return (distance, material_id) for points p (..., 3)."""
    prims = []
    # ---- outer shell (front wall omitted; it is the cut-away face) ----
    shell = slab(p, [-1, 0, 0], [TH, 1, 1])            # left
    shell = np.minimum(shell, slab(p, [1, 0, 0], [TH, 1, 1]))   # right
    shell = np.minimum(shell, slab(p, [0, 0, -1], [1, 1, TH]))  # back
    # top wall with hole for the right chimney (top entrance)
    top = holed(p, [0, 1, 0], [1, TH, 1], [CXR, 1, CZR], [CW - TH, 0.5, CW - TH])
    # bottom wall with hole for the left chimney (bottom entrance)
    bot = holed(p, [0, -1, 0], [1, TH, 1], [CXL, -1, CZL], [CW - TH, 0.5, CW - TH])
    shell = np.minimum(shell, np.minimum(top, bot))
    prims.append((shell, M_SHELL))

    # ---- middle floor with two holes (each chimney pierces it) ----
    floor = slab(p, [0, 0, 0], [1, TH, 1])
    floor = np.maximum(floor, -slab(p, [CXL, 0, CZL], [CW - TH, 0.5, CW - TH]))
    floor = np.maximum(floor, -slab(p, [CXR, 0, CZR], [CW - TH, 0.5, CW - TH]))
    prims.append((floor, M_FLOOR))

    # ---- left chimney: bottom face -> up through lower room -> into upper ----
    up = chimney(p, CXL, -1.0, 0.5, CZL)
    prims.append((up, M_UP))
    # ---- right chimney: top face -> down through upper room -> into lower ----
    lo = chimney(p, CXR, -0.5, 1.0, CZR)
    prims.append((lo, M_LO))

    # ---- two connecting walls (make it non-collapsible) ----
    # in UPPER room: right chimney -> right side wall
    finU = slab(p, [0.5 * (CXR + CW + 1), 0.5, CZR],
                [0.5 * (1 - CXR - CW), 0.5, TH])
    # in LOWER room: left chimney -> left side wall
    finL = slab(p, [0.5 * (-1 + CXL - CW), -0.5, CZL],
                [0.5 * (CXL - CW + 1), 0.5, TH])
    prims.append((np.minimum(finU, finL), M_FIN))

    dstack = np.stack([d for d, _ in prims], axis=-1)
    mids = np.array([m for _, m in prims])
    dmin = dstack.min(-1)
    mat = mids[dstack.argmin(-1)]
    # cut-away: intersect with z <= zclip  (reveal the interior)
    cut = p[..., 2] - zclip
    d = np.maximum(dmin, cut)
    return d, mat


def sdf_d(p, zclip=0.62):
    return scene(p, zclip)[0]


MATCOL = np.array([
    [0.40, 0.44, 0.52],   # shell  - dim cool slate (recede)
    [0.56, 0.52, 0.46],   # floor  - warm slate
    [1.00, 0.52, 0.18],   # upper-access chimney - amber
    [0.16, 0.74, 0.88],   # lower-access chimney - teal
    [0.98, 0.80, 0.26],   # fins   - gold
])


def render(S, supersample=2, fname="02_a_house_that_forgets_every_loop.png", zclip=0.62):
    W = S * supersample
    # ---- camera ----
    cam = np.array([float(os.environ.get("CAMX", "2.55")),
                    float(os.environ.get("CAMY", "1.35")),
                    float(os.environ.get("CAMZ", "2.05"))])
    look = np.array([0.0, -0.05, 0.0])
    up = np.array([0.0, 1.0, 0.0])
    fwd = look - cam; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, up); right /= np.linalg.norm(right)
    upv = np.cross(right, fwd)
    fov = 1.05
    js = (np.arange(W) + 0.5) / W * 2 - 1
    px, py = np.meshgrid(js, -js)
    px = px.ravel() * np.tan(fov / 2)
    py = py.ravel() * np.tan(fov / 2)
    dirs = (fwd[None, :] + px[:, None] * right[None, :] + py[:, None] * upv[None, :])
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    N = dirs.shape[0]
    origin = np.broadcast_to(cam, (N, 3)).astype(np.float64)

    # ---- vectorised sphere tracing on a shrinking active set ----
    t = np.zeros(N)
    hit = np.zeros(N, bool)
    idx = np.arange(N)
    o = origin.copy(); dr = dirs.copy()
    tmax = 7.0
    for step in range(160):
        p = o + dr * t[idx, None]
        d, _ = scene(p, zclip)
        t[idx] += d * 0.92
        done = d < 6e-4
        esc = t[idx] > tmax
        hit[idx[done]] = True
        keep = ~(done | esc)
        idx = idx[keep]
        o = o[keep]; dr = dr[keep]
        if len(idx) == 0:
            break

    # ---- shade hits ----
    img = np.zeros((N, 3))
    H = np.where(hit)[0]
    ph = origin[H] + dirs[H] * t[H, None]
    # normals via tetrahedron finite differences
    e = 7e-4
    k1 = np.array([1, -1, -1.]); k2 = np.array([-1, -1, 1.])
    k3 = np.array([-1, 1, -1.]); k4 = np.array([1, 1, 1.])
    nrm = (k1 * sdf_d(ph + e * k1, zclip)[:, None]
           + k2 * sdf_d(ph + e * k2, zclip)[:, None]
           + k3 * sdf_d(ph + e * k3, zclip)[:, None]
           + k4 * sdf_d(ph + e * k4, zclip)[:, None])
    nrm /= (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9)
    _, mat = scene(ph, zclip)
    base = MATCOL[mat]

    # lights: a key (warm, upper-right-front) + fill (cool) + rim
    L1 = np.array([0.5, 0.7, 0.55]); L1 /= np.linalg.norm(L1)
    L2 = np.array([-0.6, 0.2, 0.3]); L2 /= np.linalg.norm(L2)
    diff1 = np.clip(nrm @ L1, 0, 1)
    diff2 = np.clip(nrm @ L2, 0, 1)
    view = -dirs[H]
    rim = np.clip(1 - np.clip((nrm * view).sum(1), 0, 1), 0, 1) ** 2.2
    # specular (key light)
    halfv = L1 + view; halfv /= (np.linalg.norm(halfv, axis=1, keepdims=True) + 1e-9)
    spec = np.clip((nrm * halfv).sum(1), 0, 1) ** 32

    shade = (0.11                                  # ambient
             + 0.72 * diff1[:, None] * np.array([1.0, 0.93, 0.82])
             + 0.26 * diff2[:, None] * np.array([0.6, 0.78, 1.0]))
    colH = base * shade
    colH += rim[:, None] * np.array([0.5, 0.7, 1.0]) * 0.35
    colH += spec[:, None] * np.array([1.0, 0.97, 0.9]) * 0.5
    # simple ambient occlusion: darker deep inside (by world y below mid + enclosure)
    img[H] = colH

    img = img.reshape(W, W, 3)

    # ---- atmosphere: faint warm interior glow from the open front ----
    lum = img.mean(2)
    for sig, amp in [(2.0 * supersample, 0.18), (8.0 * supersample, 0.12)]:
        b = gaussian_filter(lum, sig)
        img += b[..., None] * amp * np.array([1.0, 0.9, 0.75])

    # vignette + tone
    yy, xx = np.mgrid[0:W, 0:W]
    rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - W / 2) / (W / 2)) ** 2)
    img *= np.clip(1.15 - 0.35 * rr, 0, 1)[..., None]
    img = 1.0 - np.exp(-1.25 * np.clip(img, 0, None))
    img = np.clip(img, 0, 1) ** (1 / 1.95)

    out = (img * 255).astype(np.uint8)
    im = Image.fromarray(out, "RGB")
    if supersample != 1:
        im = im.resize((S, S), Image.LANCZOS)
    im.save(fname)
    print("  saved", fname, im.size)
    return im


if __name__ == "__main__":
    import sys
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 384
    ss = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    zc = float(sys.argv[3]) if len(sys.argv) > 3 else 0.62
    render(S, ss, zclip=zc)
