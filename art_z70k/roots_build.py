"""Production: accumulate roots of all degree-d Littlewood polynomials ({-1,+1})
into a high-res field with BILINEAR (anti-aliased) splatting and honest
conjugate symmetry. Saves the raw float field for fast tone-map iteration.
"""
import numpy as np, time, sys

d = int(sys.argv[1]) if len(sys.argv) > 1 else 22
S = int(sys.argv[2]) if len(sys.argv) > 2 else 2048
R = float(sys.argv[3]) if len(sys.argv) > 3 else 1.55
out = sys.argv[4] if len(sys.argv) > 4 else f"acc_d{d}_S{S}.npy"

t0 = time.time()
K = 1 << d
print(f"d={d} K={K} S={S} R={R} -> {out}", flush=True)
acc = np.zeros((S, S), dtype=np.float64)

def bilin(xs, ys, w=1.0):
    inb = (xs >= 0) & (xs < S-1) & (ys >= 0) & (ys < S-1)
    xs = xs[inb]; ys = ys[inb]
    x0 = np.floor(xs).astype(np.int64); y0 = np.floor(ys).astype(np.int64)
    fx = xs - x0; fy = ys - y0
    np.add.at(acc, (y0,   x0),   w*(1-fx)*(1-fy))
    np.add.at(acc, (y0,   x0+1), w*fx*(1-fy))
    np.add.at(acc, (y0+1, x0),   w*(1-fx)*fy)
    np.add.at(acc, (y0+1, x0+1), w*fx*fy)

CH = 1 << 16
idx_all = np.arange(K, dtype=np.uint64)
arange_d = np.arange(d, dtype=np.uint64)
for start in range(0, K, CH):
    chunk = idx_all[start:start+CH]
    m = chunk.shape[0]
    bits = ((chunk[:, None] >> arange_d[None, :]) & 1).astype(np.float64)
    coeffs = bits * 2.0 - 1.0
    C = np.zeros((m, d, d), dtype=np.float64)
    if d > 1:
        C[:, 1:, :-1] = np.eye(d-1)[None]
    C[:, :, -1] = -coeffs
    z = np.linalg.eigvals(C).ravel()
    zr = z.real; zi = z.imag
    xs = (zr + R) / (2*R) * (S-1)
    ys = (R - zi) / (2*R) * (S-1)        # z
    bilin(xs, ys)
    off = np.abs(zi) > 1e-7              # splat conjugate only for non-real roots (kills axis seam)
    ys2 = (R + zi[off]) / (2*R) * (S-1)
    bilin(xs[off], ys2)
    if (start // CH) % 8 == 0:
        print(f"  {start+m}/{K}  t={time.time()-t0:.1f}s", flush=True)

np.save(out, acc.astype(np.float32))
print(f"DONE t={time.time()-t0:.1f}s max={acc.max():.0f} nz={np.count_nonzero(acc)}", flush=True)
