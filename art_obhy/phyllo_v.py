"""01 - phyllotaxis as Voronoi florets coloured by the THREE-GAP THEOREM.

angles a_n = frac(n*alpha) for the golden rotation alpha = 1 - 1/phi.
Steinhaus' three-gap (three-distance) theorem: the points {a_1..a_N} on the
circle cut it into arcs of at most THREE distinct lengths. We colour each
seed's Voronoi floret by which gap-class it bounds. The classes weave into
spiral bands; the gap pattern reorganises at Fibonacci N (continued-fraction
convergents = the good rational approximations of the irrational rotation).
"""
import numpy as np
from scipy.spatial import cKDTree
import artkit as ak

PHI = (1 + 5 ** 0.5) / 2
ALPHA = 1 - 1 / PHI            # fractional golden rotation ~0.381966
GA = 2 * np.pi * ALPHA         # golden angle


def three_gap_classes(N, alpha=ALPHA):
    a = (np.arange(1, N + 1) * alpha) % 1.0
    order = np.argsort(a)
    sa = a[order]
    gaps = np.empty(N)
    gaps[:-1] = np.diff(sa)
    gaps[-1] = (sa[0] + 1.0) - sa[-1]
    # cluster gap lengths into <=3 classes by rounding
    uniq = np.unique(np.round(gaps, 9))
    # map each gap to nearest unique value index, sorted small->large
    uniq_sorted = np.sort(uniq)
    cls_of_sorted = np.searchsorted(uniq_sorted, np.round(gaps, 9))
    cls = np.empty(N, int)
    cls[order] = cls_of_sorted
    return cls, len(uniq_sorted)


CYCLIC = np.array([
    ak_hex("2b1b54") if False else [0.17,0.11,0.33],   # placeholder, set below
])

def cyclic_palette():
    stops = ["1b2a6b", "2f6fd0", "23c8c0", "5fe07a", "f0d24a",
             "f5853c", "ef4d6b", "b148d8", "5a3fb0", "1b2a6b"]
    cols = np.array([[int(s[i:i+2],16)/255 for i in (0,2,4)] for s in stops])
    t = np.linspace(0, 1, len(stops))
    tt = np.linspace(0, 1, 1024)
    out = np.empty((1024, 3))
    for c in range(3):
        out[:, c] = np.interp(tt, t, cols[:, c])
    return out

def render(N=9000, S=1000, fname="proto_pv.png", color_mode="phase",
           palette=None, mortar=0.30, expo_k=1.5, sat=1.3, bloom_amp=1.0,
           radial_warm=True, gamma=1/1.9, phase_turns=1.0, dome=0.55, dome_scale=0.95,
           spec_amp=0.0, spec_off=0.55, spec_w=0.30):
    n = np.arange(1, N + 1)
    r = np.sqrt(n)
    th = n * GA
    x = r * np.cos(th); y = r * np.sin(th)
    Rmax = r.max()
    cls, ngap = three_gap_classes(N)
    print("N", N, "distinct gap lengths:", ngap)

    if palette is None:
        palette = [ak_hex("ff5d73"), ak_hex("ffc24b"), ak_hex("3fd0c8"),
                   ak_hex("8a6cff"), ak_hex("6effa0")]
    palette = np.array(palette, np.float32)
    cyc = cyclic_palette()
    a_n = (n * ALPHA) % 1.0
    seed_phase_col = cyc[np.clip((a_n * phase_turns % 1.0 * 1024).astype(int), 0, 1023)]

    # per-seed local dominant parastichy = |index diff| to nearest neighbour
    FIBS = [1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597]
    # consecutive bands alternate around the wheel so adjacent rings contrast
    FIBCOL = {
        1:[0.20,0.16,0.40],2:[0.26,0.22,0.60],3:[0.20,0.42,0.85],5:[0.10,0.70,0.82],
        8:[0.15,0.86,0.55],13:[0.62,0.90,0.26],21:[0.98,0.80,0.22],34:[0.98,0.46,0.18],
        55:[0.97,0.22,0.36],89:[0.80,0.20,0.78],144:[0.46,0.28,0.92],233:[0.18,0.46,0.98],
        377:[0.10,0.82,0.80],610:[0.55,0.92,0.34],987:[0.98,0.72,0.24],1597:[0.98,0.40,0.30]}
    fibset = set(FIBS)
    stree = cKDTree(np.column_stack([x, y]))
    _, sidx = stree.query(np.column_stack([x, y]), k=4, workers=-1)
    fib_of_seed = np.zeros(N, int)
    for i in range(N):
        for j in sidx[i, 1:]:
            d = abs(int(n[i]) - int(n[j]))
            if d in fibset:
                fib_of_seed[i] = d
                break
    seed_fib_col = np.array([FIBCOL.get(f, [0.5,0.5,0.5]) for f in fib_of_seed], np.float32)

    # pixel grid in seed-coords
    margin = 0.05
    lim = Rmax * (1 + margin)
    xs = np.linspace(-lim, lim, S)
    ys = np.linspace(-lim, lim, S)
    gx, gy = np.meshgrid(xs, ys)
    P = np.column_stack([gx.ravel(), gy.ravel()])

    tree = cKDTree(np.column_stack([x, y]))
    dist, idx = tree.query(P, k=2, workers=-1)
    nn = idx[:, 0]
    d1 = dist[:, 0]; d2 = dist[:, 1]

    # colour by chosen mode of nearest seed
    if color_mode == "phase":
        col = seed_phase_col[nn]                        # (S*S,3)
    elif color_mode == "fib":
        col = seed_fib_col[nn]
    else:
        col = palette[cls[nn] % len(palette)]
    # radial luminance: warm/bright core -> dim cool rim (depth)
    rr = np.hypot(P[:, 0], P[:, 1]) / Rmax
    lum = (1.15 - 0.55 * rr)
    col = col * lum[:, None]
    # domed-pearl shading: each floret bright at its seed, fading to its rim
    # (per-pixel radial gradient from d1 -- the craft-note-approved dome)
    if dome > 0:
        domed = np.clip(1.0 - d1 / dome_scale, 0.0, 1.0)
        col = col * ((1 - dome) + dome * domed)[:, None]
    # off-centre specular -> glossy pearl (craft note: per-pixel gradient, not ellipses)
    if spec_amp > 0:
        sx = x[nn]; sy = y[nn]
        ox_ = P[:, 0] - sx; oy_ = P[:, 1] - sy        # offset from seed centre
        ldx, ldy = -0.55, 0.55                          # light from upper-left
        hx = ox_ - ldx * spec_off; hy = oy_ - ldy * spec_off
        spec = np.exp(-(hx * hx + hy * hy) / (2 * spec_w * spec_w))
        col = col + spec_amp * spec[:, None] * np.array([1.0, 0.98, 0.92], np.float32)
    # mortar: darken cell boundaries (where 1st & 2nd nearest seeds tie)
    edge = (d2 - d1)
    # normalise edge by local seed spacing (~constant); mortar where edge small
    msk = np.exp(-(edge / (mortar)) ** 2)
    col = col * (1 - 0.85 * msk)[:, None]
    # outside the seed disk -> black
    outside = rr > 1.0
    col[outside] = 0.0

    field = col.reshape(S, S, 3).astype(np.float32)
    field = ak.bloom(field, sigmas=(2, 6, 16), amps=(0.12*bloom_amp, 0.07*bloom_amp, 0.04*bloom_amp))
    rgb = ak.filmic(field, k=expo_k)
    luma = (0.2126*rgb[..., 0]+0.7152*rgb[..., 1]+0.0722*rgb[..., 2])[..., None]
    rgb = np.clip(luma + (rgb - luma) * sat, 0, 1)
    rgb = ak.gamma(rgb, gamma)
    ak.save(rgb, fname)
    print("wrote", fname)


def ak_hex(h):
    return [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]


if __name__ == "__main__":
    render()
