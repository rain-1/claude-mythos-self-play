import numpy as np
from PIL import Image

rng = np.random.default_rng(31337)

def bytes_rows(A):
    kb = np.packbits(A, axis=1); m = kb.shape[1]; b = kb.tobytes()
    return [b[i*m:(i+1)*m] for i in range(A.shape[0])]

def sort_fix(A, start='R'):
    """Alternate sorts until doubly sorted; returns final matrix and T."""
    n = A.shape[0]; t = 0; kind = start
    while True:
        t += 1
        if kind == 'R':
            rows = bytes_rows(A)
            order = sorted(range(n), key=rows.__getitem__)
            A = A[np.array(order)]
            cols = bytes_rows(np.ascontiguousarray(A.T))
            if all(cols[j] <= cols[j+1] for j in range(n-1)): return A, t
            kind = 'C'
        else:
            cols = bytes_rows(np.ascontiguousarray(A.T))
            order = sorted(range(n), key=cols.__getitem__)
            A = A[:, np.array(order)]
            rows = bytes_rows(A)
            if all(rows[i] <= rows[i+1] for i in range(n-1)): return A, t
            kind = 'R'

n = 4096
# --- experiment 1+2: c=32, both orders, late-settler locations
for c in [32.0, 256.0]:
    A0 = (rng.random((n, n)) < c/n)
    R1, t1 = sort_fix(A0.copy(), 'R')
    C1, t2 = sort_fix(A0.copy(), 'C')
    diff = (R1 != C1)
    print(f"c={c}: T_R={t1} T_C={t2} same_fixed_point={not diff.any()} "
          f"ndiff={diff.sum()}")
    if diff.any():
        ds = n // 1024
        d2 = diff.reshape(1024, ds, 1024, ds).sum(axis=(1, 3)).astype(np.float32)
        img = np.clip(d2 / max(1, d2.max()) * 4 * 255, 0, 255)
        Image.fromarray(img.astype(np.uint8)).save(f"exp_diff_c{int(c)}.png")

# --- experiment 3: extreme sparse full view c=4
A0 = (rng.random((n, n)) < 4.0/n)
F, t = sort_fix(A0.copy(), 'R')
print("c=4: T=", t, "ones=", F.sum())
ds = n // 1024
d2 = F.reshape(1024, ds, 1024, ds).sum(axis=(1, 3)).astype(np.float32)
Image.fromarray(np.clip(d2*255, 0, 255).astype(np.uint8)).save("exp_sparse_c4.png")

# --- experiment 4: zoom into coastline at c=32 (top-left 1024x1024 raw)
A0 = (rng.random((n, n)) < 32.0/n)
F, t = sort_fix(A0.copy(), 'R')
Image.fromarray((F[:1024, :1024]*255).astype(np.uint8)).save("exp_zoom_c32.png")
Image.fromarray((F[:256, :256]*255).astype(np.uint8)).resize((1024,1024), Image.NEAREST).save("exp_zoom2_c32.png")
