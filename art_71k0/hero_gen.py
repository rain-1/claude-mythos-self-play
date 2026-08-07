"""Hero data: doubly-lex-sorted sparse random matrix at n=4096 with settlement
instrumentation.  For each final row/column: the last sort step at which it
MOVED (position changed).  Saves npz + a 1024 preview PNG per density."""
import numpy as np, sys, time
from PIL import Image

rng = np.random.default_rng(710)

def pack(A):
    return np.packbits(A, axis=1)

def bytes_rows(A):
    kb = pack(A); m = kb.shape[1]; b = kb.tobytes()
    return [b[i*m:(i+1)*m] for i in range(A.shape[0])]

def run(n, c, tag):
    p = c / n
    A = (rng.random((n, n)) < p)
    A0 = A.copy()
    rowlast = np.zeros(n, np.int32)      # by current position
    collast = np.zeros(n, np.int32)
    t = 0
    while True:
        t += 1
        if t % 2 == 1:
            rows = bytes_rows(A)
            order = sorted(range(n), key=rows.__getitem__)
            order = np.array(order)
            moved = order != np.arange(n)
            rowlast = np.where(moved, t, rowlast[order])
            A = A[order]
            cols = bytes_rows(np.ascontiguousarray(A.T))
            done = all(cols[j] <= cols[j+1] for j in range(n-1))
        else:
            cols = bytes_rows(np.ascontiguousarray(A.T))
            order = sorted(range(n), key=cols.__getitem__)
            order = np.array(order)
            moved = order != np.arange(n)
            collast = np.where(moved, t, collast[order])
            A = A[:, order]
            rows = bytes_rows(A)
            done = all(rows[i] <= rows[i+1] for i in range(n-1))
        if done:
            break
    T = t
    print(f"c={c}: T={T} ones={A.sum()} rowlast_hist={np.bincount(rowlast)} "
          f"collast_hist={np.bincount(collast)}", flush=True)
    np.savez_compressed(f"hero_{tag}.npz", Af=np.packbits(A), n=n, c=c, T=T,
                        rowlast=rowlast, collast=collast,
                        A0=np.packbits(A0))
    # preview: 1024 downsample, brightness = local ones density + dots
    ds = n // 1024
    dens = A.reshape(1024, ds, 1024, ds).sum(axis=(1, 3)).astype(np.float32)
    img = np.clip(dens / max(1e-9, np.percentile(dens[dens > 0], 98)) * 255, 0, 255) if (dens>0).any() else dens
    Image.fromarray(img.astype(np.uint8)).save(f"hero_{tag}_prev.png")
    return T

if __name__ == "__main__":
    n = 4096
    for c in [16, 32, 64, 128, 256]:
        t0 = time.time()
        run(n, float(c), f"c{c}")
        print(f"  ({time.time()-t0:.0f}s)", flush=True)
