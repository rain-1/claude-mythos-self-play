"""Row C — one cannot hear the shape of a drum.

The Gordon–Webb–Wolpert pair: two different polygons with IDENTICAL Laplace
spectra. C1 and C3 are the two drums, struck the same way (same modal
coefficients); C2 is the sound itself — both drums' computed ringdown combs,
mirrored, meeting in the middle: two instruments, one chord. Column III here
is not a reconstruction at all: reconstruction from this shadow is provably
non-unique. The zombie thought experiment, resolved in copper and verdigris.

Verification: both spectra computed independently by sparse FD eigsh and
compared; also checked against Driscoll (1997), lambda_1 = 2.53794 for the
unit-leg scaling (ours has legs 2 => lambda scales by 1/4).
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.ndimage import gaussian_filter
import tone

D1 = [(-3, -3), (-3, -1), (1, 3), (1, 1), (3, 1), (1, -1), (-1, -1), (-1, -3)]
D2 = [(-3, 1), (1, 1), (1, 3), (3, 1), (1, -1), (-1, -1), (-1, -3), (-3, -1)]
RNG = np.random.default_rng(1966)  # Kac year


def polygon_mask(poly, q):
    """STRICT-interior lattice points of poly on the integer-aligned lattice
    with spacing h=1/q over [-3,3]^2 (G = 6q+1 points per axis).

    Alignment matters: the GWW transplantation is an isometry of this lattice,
    so the two discrete Dirichlet Laplacians are EXACTLY isospectral at any q.
    Edges are axis-aligned or slope +-1 through integer vertices, so on-edge
    tests are exact in integers; non-boundary lattice points are >= h/sqrt(2)
    from every edge, so an offset ray-cast classifies them safely.
    """
    G = 6 * q + 1
    ix = np.arange(G) - 3 * q                    # integer lattice coords (x q)
    X, Y = np.meshgrid(ix, ix)                   # row 0 = bottom
    pv = [(x * q, y * q) for x, y in poly]
    n = len(pv)
    on_edge = np.zeros((G, G), dtype=bool)
    for i in range(n):
        x1, y1 = pv[i]
        x2, y2 = pv[(i + 1) % n]
        inbox = (X >= min(x1, x2)) & (X <= max(x1, x2)) & \
                (Y >= min(y1, y2)) & (Y <= max(y1, y2))
        collin = (x2 - x1) * (Y - y1) == (y2 - y1) * (X - x1)
        on_edge |= inbox & collin
    # even-odd ray cast with a small y-offset (never hits vertices/edges)
    Yf = Y + 0.31
    inside = np.zeros((G, G), dtype=bool)
    for i in range(n):
        x1, y1 = pv[i]
        x2, y2 = pv[(i + 1) % n]
        if y1 == y2:
            continue
        cond = (Yf < y1) != (Yf < y2)
        xcross = x1 + (Yf - y1) * (x2 - x1) / (y2 - y1)
        inside ^= cond & (X < xcross)
    inside &= ~on_edge
    xs = ix.astype(np.float64) / q
    return inside, xs


def dirichlet_spectrum(mask, h, k=64):
    """Smallest-k Dirichlet eigenpairs of the 5-point FD Laplacian on mask."""
    G = mask.shape[0]
    idx = -np.ones(mask.shape, dtype=np.int64)
    ii, jj = np.nonzero(mask)
    idx[ii, jj] = np.arange(ii.size)
    N = ii.size
    rows, cols, vals = [np.arange(N)], [np.arange(N)], [np.full(N, 4.0)]
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = ii + di, jj + dj
        ok = mask[ni, nj]
        rows.append(idx[ii[ok], jj[ok]])
        cols.append(idx[ni[ok], nj[ok]])
        vals.append(np.full(ok.sum(), -1.0))
    L = sparse.csr_matrix(
        (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
        shape=(N, N)) / h ** 2
    evals, evecs = eigsh(L, k=k, sigma=0, which="LM")
    order = np.argsort(evals)
    return evals[order], evecs[:, order], idx


def modes_to_grid(evecs, idx, G, k):
    out = np.zeros((k, G, G), dtype=np.float32)
    m = idx >= 0
    for q in range(k):
        v = evecs[:, q]
        # sign-fix: make the largest-magnitude entry positive (comparable strikes)
        v = v * np.sign(v[np.argmax(np.abs(v))])
        out[q][m] = v[idx[m]]
        out[q] /= np.abs(out[q]).max()
    return out


def struck_membrane(modes, evals, coeffs, t0=0.55):
    """Snapshot + energy body of a struck drum. Same coeffs => same strike."""
    w = coeffs / (1 + evals / evals[0]) ** 0.45         # slow rolloff: filigree
    snap = np.tensordot(w * np.cos(np.sqrt(evals) * t0), modes, axes=1)
    energy = np.tensordot(w ** 2, modes ** 2, axes=1)
    return snap, energy


def render_drum(snap, energy, mask, out_size, fname):
    """Chladni treatment: glowing sand on the nodal web (the drum's silence),
    over a deep verdigris membrane body shaded by modal energy."""
    G = mask.shape[0]
    sd = snap / np.std(snap[mask])
    e = energy / energy.max()
    nodal = np.exp(-(sd / 0.20) ** 2)                   # ridge at zero crossings
    # dark verdigris membrane body...
    body_v = tone.filmic(0.9 * e ** 0.55 + 0.06, k=1.8) * mask
    rgb = tone.lerp_palette(0.52 * body_v, tone.PAL_VERDIGRIS)
    # sign shimmer on the body: positive lobes warm, negative cool
    sgn = np.tanh(2.5 * sd) * mask
    rgb[..., 0] *= (1 + 0.22 * sgn * (1 - nodal))
    rgb[..., 2] *= (1 - 0.16 * sgn * (1 - nodal))
    # ...and the sand: nodal web + Dirichlet rim in their own gold ramp
    web = 1.35 * nodal * (0.35 + 0.65 * e ** 0.4) * mask
    edge = mask.astype(np.float32) - gaussian_filter(mask.astype(np.float32), 2.2)
    web += 6.0 * np.clip(edge, 0, None)
    web_v = tone.filmic(web, k=2.6, gamma=0.9)
    rgb += web_v[..., None] * np.array([1.00, 0.90, 0.52], np.float32)
    rgb = tone.bloom(rgb, threshold=0.72, gain=0.55)
    pad = int(0.05 * G)
    rgb = np.pad(np.clip(rgb, 0, 1), ((pad, pad), (pad, pad), (0, 0)))
    img = tone.to_image(rgb[::-1], out_size)  # row0=bottom -> flip
    img.save(fname)


def render_spectrum(ev1, ev2, coeffs, out_size, fname, W=2048, H=2048):
    """Two ringdown combs, mirrored about the horizontal midline: one chord.
    x = time (each mode decays as exp(-lambda t / lambda_1 * c)), y = frequency."""
    freqs1, freqs2 = np.sqrt(ev1), np.sqrt(ev2)
    fmax = max(freqs1.max(), freqs2.max()) * 1.06
    tt = np.linspace(0, 1, W, dtype=np.float32)
    field_top = np.zeros((H // 2, W), np.float32)
    field_bot = np.zeros((H // 2, W), np.float32)
    f0 = min(freqs1.min(), freqs2.min())
    yy = np.linspace(0.55 * f0, fmax, H // 2, dtype=np.float32)
    sig_y = fmax / 260
    w = coeffs / (1 + ev1 / ev1[0]) ** 0.45
    for field, freqs, ev in [(field_top, freqs1, ev1), (field_bot, freqs2, ev2)]:
        for fq, lam, a in zip(freqs, ev, w):
            # ringdown: damping grows with frequency; slow beat shimmer
            decay = np.exp(-(1.6 + 3.8 * (fq / fmax)) * tt) \
                * (1 + 0.30 * np.cos(2 * np.pi * (0.8 + 2.2 * fq / fmax) * tt))
            prof = np.exp(-0.5 * ((yy - fq) / sig_y) ** 2)
            field += (a ** 1.4) * prof[:, None] * decay[None, :]
        # the strike itself: broadband flash at t=0
        field += 0.35 * field[:, :1] * np.exp(-tt / 0.012)[None, :]
    # mirror: drum 1 sings upward, drum 2 downward; they meet at the midline
    field = np.concatenate([field_top[::-1], field_bot], axis=0)
    v = tone.norm_percentile(field, 0, 99.9)
    v = tone.filmic(v, k=3.6, gamma=0.85)
    rgb = tone.lerp_palette(v, tone.PAL_VERDIGRIS)
    rgb = tone.bloom(rgb, threshold=0.70, gain=0.7)
    tone.to_image(np.clip(rgb, 0, 1), out_size).save(fname)


def main(q=64, k=48, out_size=512, outdir="."):
    import os, time
    t0 = time.time()
    m1, xs = polygon_mask(D1, q)
    m2, _ = polygon_mask(D2, q)
    G = m1.shape[0]
    h = xs[1] - xs[0]
    assert m1.sum() == m2.sum(), "interior lattice-point counts must match exactly"
    print(f"q={q}, interior points per drum: {m1.sum()}", flush=True)
    ev1, vec1, idx1 = dirichlet_spectrum(m1, h, k)
    print(f"drum1 spectrum  {time.time()-t0:.1f}s", flush=True)
    ev2, vec2, idx2 = dirichlet_spectrum(m2, h, k)
    print(f"drum2 spectrum  {time.time()-t0:.1f}s", flush=True)

    rel = np.abs(ev1 - ev2) / ev1
    print(f"lambda_1 = {ev1[0]:.6f}  (Driscoll 1997 continuum value: 2.537943; "
          f"FD error O(h^2))", flush=True)
    print(f"isospectrality: max rel diff over {k} modes = {rel.max():.2e}", flush=True)

    modes1 = modes_to_grid(vec1, idx1, G, k)
    modes2 = modes_to_grid(vec2, idx2, G, k)
    coeffs = np.abs(RNG.normal(0.6, 0.35, k)).astype(np.float32) + 0.15

    s1, e1 = struck_membrane(modes1, ev1, coeffs)
    s2, e2 = struck_membrane(modes2, ev2, coeffs)
    render_drum(s1, e1, m1, out_size, os.path.join(outdir, "C1_the_world.png"))
    render_drum(s2, e2, m2, out_size, os.path.join(outdir, "C3_the_return.png"))
    render_spectrum(ev1, ev2, coeffs, out_size, os.path.join(outdir, "C2_the_shadow.png"))
    print(f"done  {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    import sys
    kw = dict(arg.split("=") for arg in sys.argv[1:])
    main(**{kk: (int(v) if v.isdigit() else v) for kk, v in kw.items()})
