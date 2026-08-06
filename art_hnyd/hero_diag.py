"""Diagnostics: what does the settled 4096 matrix + strata actually look like?"""
import numpy as np
from PIL import Image

z = np.load("hero_trace.npz")
A0, Af, lc, cc = z['A0'], z['A_final'], z['last_change'], z['change_count']
T = int(z['T'])
print("T =", T)
for t in range(0, T + 1):
    print(f"last_change=={t}: {(lc == t).sum()} cells")
print("change_count histogram:", np.bincount(cc.ravel()))

# masks per pass: how are changes distributed?
masks = z['masks']
for t in range(T):
    m = masks[t]
    rows_touched = int((m.any(axis=1)).sum())
    cols_touched = int((m.any(axis=0)).sum())
    print(f"pass {t+1}: cells={m.sum()} rows_touched={rows_touched} cols_touched={cols_touched}")

def save(img, name):
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(name)

# downsample 8x by mean
def ds(x, f=8):
    n = x.shape[0]
    return x.reshape(n // f, f, n // f, f).mean(axis=(1, 3))

save(ds(Af.astype(np.float32)), "diag_final.png")
save(ds(A0.astype(np.float32)), "diag_init.png")
save(ds(lc.astype(np.float32)) / T, "diag_lastchange.png")
# categorical last-change at full res crop (top-left 1024)
pal = np.array([[0,0,0],[40,40,60],[60,50,90],[90,60,120],[150,80,120],[220,120,80],[255,220,120]], float)/255
crop = lc[:1024, :1024]
img = pal[np.clip(crop, 0, 6)]
Image.fromarray((img*255).astype(np.uint8)).save("diag_lc_crop.png")
# full categorical, downsampled by max (late passes pop)
f = 4
lcm = lc.reshape(1024, f, 1024, f).max(axis=(1, 3))
img = pal[np.clip(lcm, 0, 6)]
Image.fromarray((img*255).astype(np.uint8)).save("diag_lc_max.png")
print("saved diagnostics")
