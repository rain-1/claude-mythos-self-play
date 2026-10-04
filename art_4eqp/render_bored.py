# render_bored.py — the easily bored sequence (MO 377105) as a two-sided arc diagram.
# Above the line: for every digit n, the square it could not avoid (period L chosen) = an arc from n-L to n.
# Below the line: the repetition it refused (the other digit's (a, L)), a ghost arc in the cool family.
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from sorbet import Sheet, PIG, absorb, wheel_tint, text_mask, text_w
W = int(sys.argv[1]); out = sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 4232
H = W
b = np.fromfile('bored.bin', np.uint8)[:n]; R = np.fromfile('bored_R.bin', np.int32).reshape(-1, 4)[:n]
SS = 2
x0, x1 = 0.06 * W, 0.94 * W
ybase = 0.56 * H
sx = (x1 - x0) / n
def X(i): return x0 + (i + 0.5) * sx
HSC = 0.86 * (ybase - 0.05 * H) / (0.5 * 2116 * sx) # tallest chosen arc (period 2116 for the full square) fits
def arcs(sel_list, sign, wscale):
    im = Image.new('F', (W * SS, H * SS), 0.0); dr = ImageDraw.Draw(im)
    for (i0, i1, wt, lw) in sel_list:
        cx = (X(i0) + X(i1)) / 2 * SS; r = (X(i1) - X(i0)) / 2 * SS
        h = r * HSC
        box = [cx - r, ybase * SS - h, cx + r, ybase * SS + h]
        if sign > 0: dr.arc(box, 180, 360, fill=float(wt), width=max(1, int(round(lw * SS))))
        else: dr.arc(box, 0, 180, fill=float(wt), width=max(1, int(round(lw * SS))))
    a = np.asarray(im, np.float32)
    return a.reshape(H, SS, W, SS).mean(axis=(1, 3))
sh = Sheet(W, H, seed=21)
lmax = np.log(2116.0)
NB = 9
def hue_of(L): return np.clip(np.log(L) / lmax, 0, 1)
# chosen arcs: period L ending at digit n (the square occupies n-2L+1 .. n): arc spans its two halves' centres
groups = {}
for t in range(1, n):
    a, L, a2, L2 = R[t]
    if a >= 2:
        hb = min(int(hue_of(L) * NB), NB - 1)
        groups.setdefault(('up', hb), []).append((t - L, t, 1.0, max(0.7, 0.9 * (W / 1600) * (1 + 0.25 * np.log(L)))))
    if a2 >= 2:
        hb = min(int(hue_of(L2) * NB), NB - 1)
        groups.setdefault(('dn', hb), []).append((t - L2, t, 1.0, max(0.7, 0.9 * (W / 1600) * (1 + 0.25 * np.log(L2)))))
warm = ['strawberry', 'coral', 'peach', 'honey', 'butter', 'lime', 'mint', 'sky', 'periwinkle', 'lilac']
for (side, hb), lst in groups.items():
    t = (hb + 0.5) / NB
    if side == 'up':
        tint = wheel_tint(0.02 + 0.80 * t)
        sh.wash(arcs(lst, +1, 1), tint, 0.55)
    else:
        tint = wheel_tint(0.02 + 0.80 * t)
        sh.wash(arcs(lst, -1, 1), tint, 0.22)
# the digits themselves as a ribbon on the baseline: 0 = paper, 1 = plum tick
rib = np.zeros((H, W), np.float32)
for i in np.nonzero(b)[0]:
    xa = int(X(i) - sx / 2); xb = max(xa + 1, int(X(i) + sx / 2))
    rib[int(ybase - 0.004 * H):int(ybase + 0.004 * H), xa:xb] = 1
sh.wash(rib, 'plum', 0.8)
img = sh.develop(dmax=1.9)
img.save(out)
