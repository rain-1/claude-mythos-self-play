"""01 hero: 'The Moment That Escaped' — occupation measure of a 1.6e9-step
Levy flight (Pareto alpha=1.45 steps, uniform angles). The second moment of
the step law diverges: the walk is an archipelago of dwellings joined by
leaps. Luminance = occupation density; hue = when (in the frame's own
history) a place was inhabited; epochs-mixed places whiten (the home that
belongs to every age). Faint cool threads = the leaps themselves.
Phase 3: full splat + compose."""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from levy_core import splat_bilinear, hist_eq
from hero_walk import walk_stream, ALPHA, N

SEED = 11
SS = 6144          # supersampled render
OUT = 4096
HUE_RES = 3072     # moment buffers at half res

# ---- window (from contact sheet: seed 11, center 0, q=0.25) ----
dec = np.load(f"walk_dec_s{SEED}.npy")
xlo, xhi = np.percentile(dec[:, 0], [2, 98])
ylo, yhi = np.percentile(dec[:, 1], [2, 98])
G = 700
H, xe, ye = np.histogram2d(dec[:, 0], dec[:, 1], bins=G,
                           range=[[xlo, xhi], [ylo, yhi]])
i, j = np.unravel_index(np.argmax(H), H.shape)
cx, cy = (xe[i]+xe[i+1])/2, (ye[j]+ye[j+1])/2
r = np.maximum(np.abs(dec[:, 0]-cx), np.abs(dec[:, 1]-cy))
half = np.quantile(r, 0.25) * 1.03
in_frac = (r < half).mean()
T_est = N * in_frac
print(f"window: c=({cx:.4g},{cy:.4g}) half={half:.4g} in-frame~{in_frac:.3f}")
del dec, H, r

acc = np.zeros((SS, SS), np.float32)
mt = np.zeros((HUE_RES, HUE_RES), np.float64)   # sum t
mt2 = np.zeros((HUE_RES, HUE_RES), np.float64)  # sum t^2
mw = np.zeros((HUE_RES, HUE_RES), np.float64)   # sum w  (for moments)
chord = np.zeros((SS, SS), np.float32)

scale = (SS - 1) / (2 * half)
hscale = (HUE_RES - 1) / (2 * half)
rank_base = 0
prev_tail = None  # last position of previous chunk (for chords across seams)
CH_TH = 3.0 * (SS / 4096)   # chord length threshold in SS px

chords_drawn = 0
for start, p in walk_stream(N, ALPHA, SEED):
    X = (p[:, 0] - (cx - half)) * scale
    Y = (p[:, 1] - (cy - half)) * scale
    m = (X >= 0) & (X < SS - 1) & (Y >= 0) & (Y < SS - 1)
    # exact in-frame rank as time
    ranks = rank_base + np.cumsum(m)
    rank_base = ranks[-1]
    t = (ranks[m] / max(T_est, 1.0)).astype(np.float64)
    Xi, Yi = X[m], Y[m]
    splat_bilinear(acc, Xi, Yi, SS)
    Xh = Xi * (hscale / scale); Yh = Yi * (hscale / scale)
    splat_bilinear(mw, Xh, Yh, HUE_RES)
    splat_bilinear(mt, Xh, Yh, HUE_RES, w=t)
    splat_bilinear(mt2, Xh, Yh, HUE_RES, w=t * t)
    # chords within chunk (+ seam to previous chunk)
    if prev_tail is not None:
        Px = np.concatenate([[(prev_tail[0]-(cx-half))*scale], X])
        Py = np.concatenate([[(prev_tail[1]-(cy-half))*scale], Y])
    else:
        Px, Py = X, Y
    dX = np.diff(Px); dY = np.diff(Py)
    L = np.hypot(dX, dY)
    idx = np.where(L > CH_TH)[0]
    inb = ((Px[idx] > -SS*0.2) & (Px[idx] < SS*1.2) & (Py[idx] > -SS*0.2) & (Py[idx] < SS*1.2)) | \
          ((Px[idx+1] > -SS*0.2) & (Px[idx+1] < SS*1.2) & (Py[idx+1] > -SS*0.2) & (Py[idx+1] < SS*1.2))
    idx = idx[inb]
    for k in idx:
        n = int(min(L[k] / 1.4, 6000)) + 2
        s = np.linspace(0, 1, n)
        splat_bilinear(chord, Px[k]+dX[k]*s, Py[k]+dY[k]*s, SS,
                       w=np.full(n, 1.0/n, np.float32))
    chords_drawn += len(idx)
    prev_tail = p[-1]
    if (start // 20_000_000) % 8 == 0:
        print(f"  {start/1e9:.2f}G done, chords {chords_drawn}", flush=True)

print("total in-frame:", rank_base, "est was", T_est)
np.save("hero_acc.npy", acc)
np.save("hero_chord.npy", chord)
np.savez("hero_moments.npz", mw=mw.astype(np.float32),
         mt=mt.astype(np.float32), mt2=mt2.astype(np.float32),
         T=rank_base, half=half, cx=cx, cy=cy)
print("saved buffers")
