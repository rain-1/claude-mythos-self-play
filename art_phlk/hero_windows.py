"""Hero phase 2: contact sheet of candidate windows from decimated walks.
Score-assisted, chosen by eye."""
import numpy as np
from PIL import Image
from levy_core import splat_bilinear, hist_eq

TH = 340  # thumb size

def thumbs(seed):
    pos = np.load(f"walk_dec_s{seed}.npy")
    # coarse density over 2-98% box to find cluster centers
    xlo, xhi = np.percentile(pos[:, 0], [2, 98])
    ylo, yhi = np.percentile(pos[:, 1], [2, 98])
    G = 700
    H, xe, ye = np.histogram2d(pos[:, 0], pos[:, 1], bins=G,
                               range=[[xlo, xhi], [ylo, yhi]])
    Hs = H.copy()
    order = np.argsort(Hs.ravel())[::-1]
    centers = []
    taken = np.zeros((G, G), bool)
    for f in order[:4000]:
        i, j = np.unravel_index(f, (G, G))
        if taken[max(0,i-30):i+30, max(0,j-30):j+30].any():
            continue
        taken[i, j] = True
        centers.append(((xe[i]+xe[i+1])/2, (ye[j]+ye[j+1])/2))
        if len(centers) >= 4:
            break
    rows = []
    meta = []
    for ci, (cx, cy) in enumerate(centers):
        r = np.maximum(np.abs(pos[:, 0]-cx), np.abs(pos[:, 1]-cy))
        row = []
        for q in (0.25, 0.45, 0.65):
            half = np.quantile(r, q) * 1.03
            acc = np.zeros((TH, TH), np.float32)
            s = (TH-1)/(2*half)
            splat_bilinear(acc, (pos[:, 0]-(cx-half))*s, (pos[:, 1]-(cy-half))*s, TH)
            v = hist_eq(acc, gamma=2.2)
            # coverage score: fraction of cells lit above faint
            cov = (v > 0.25).mean()
            row.append(v)
            meta.append((seed, ci, q, half, cov))
        rows.append(np.concatenate(row, axis=1))
    sheet = np.concatenate(rows, axis=0)
    img = (np.clip(sheet, 0, 1) ** 0.9 * 255).astype(np.uint8)
    Image.fromarray(img).save(f"windows_s{seed}.png")
    for m in meta:
        print("seed %d center %d q=%.2f half=%.3g coverage=%.3f" % m)

for seed in (11, 23):
    thumbs(seed)
