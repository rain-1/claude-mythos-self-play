"""Four sun prints on one page: 8 x 8 pins, the loop laid K times on each.
   no buttons: 4,638,576 ways round | two buttons: fewer | four buttons: one | four, misplaced: none"""
import sys, numpy as np
from scipy import ndimage as ndi
import cyano, lace
size = int(sys.argv[1]); out = sys.argv[2]; K = int(sys.argv[3]) if len(sys.argv) > 3 else 96
M = N = 8
D4 = [(0, 0), (2, 7), (6, 2), (6, 5)]
D2 = [(0, 0), (2, 7)]
D0bad = [(0, 0), (3, 6), (6, 2), (6, 5)]
c0 = lace.count(M, N); c2 = lace.count(M, N, D2); c4 = lace.count(M, N, D4); cb = lace.count(M, N, D0bad)
print(c0, c2, c4, cb)
assert c4 == 1 and cb == 0
g = 0.075; a0, a1, b0, b1 = 0.085, 0.5 - g / 2, 0.5 + g / 2, 0.915
ya0, ya1, yb0, yb1 = 0.048, 0.048 + (a1 - a0), 0.492, 0.492 + (a1 - a0)
boxes = [(a0, ya0, a1, ya1), (b0, ya0, b1, ya1), (a0, yb0, a1, yb1), (b0, yb0, b1, yb1)]
sh = cyano.Sheet(size, seed=11, ss=2, coat_box=boxes)
pad = 0.047
grids = [lace.Grid(sh, M, N, (b[0] + pad, b[1] + pad, b[2] - pad, b[3] - pad), seed=20 + i, jitter=0.03,
                   rot=[-0.012, 0.016, 0.008, -0.02][i]) for i, b in enumerate(boxes)]
S0 = lace.samples(M, N, K, 5); S2 = lace.samples(M, N, K, 6, D2); U = lace.unique_cycle(M, N, D4)
acc = np.zeros((size * 2, size * 2), np.float32)
for k in range(K):
    im, d, ss = sh.canvas()
    lace.draw_loop(sh, d, ss, grids[0], S0[k], phase=k)
    lace.draw_loop(sh, d, ss, grids[1], S2[k], phase=k)
    acc += np.asarray(im, np.float32)
acc /= 255.0 * K
from PIL import Image
mean = np.asarray(Image.fromarray((acc * 65535).astype(np.uint16).astype(np.int32), 'I').resize((size, size), Image.BOX), np.float32) / 65535.0
# a thread exposed for a k-th of the time leaves a k-th of a shadow; sharpen the response a
# little so single passes are visible (the eye, and iron salts, are not linear)
mean = np.clip(mean, 0, 1) ** 0.72
sh.lay(mean, opacity=0.97, height=0.5)
im, d, ss = sh.canvas()
lace.draw_loop(sh, d, ss, grids[2], U)
for i, (gr, dl) in enumerate(zip(grids, [(), D2, D4, D0bad])):
    lace.draw_pins(d, ss, gr, skip=set(dl))
m = sh.to_mask(im)
sh.lay(m, opacity=0.97, halo=0.25)
for i, (gr, dl) in enumerate(zip(grids, [(), D2, D4, D0bad])):
    lace.lay_buttons(sh, gr, dl, seed=3 + i)
sh.expose()
labs = [f'no buttons:  {c0:,} ways round', f'two buttons:  {c2:,} ways', 'four buttons:  one way', 'the same four, one moved:  none']
for b, t in zip(boxes, labs):
    sh.text(t, ((b[0] + b[2]) / 2, b[3] + 0.034), 17.5)
sh.text('Four Buttons', (0.5, 0.943), 30)
sh.text(f'sixty-four pins; on the upper sheets one thread was laid {K} ways, each for a {K}th of the afternoon', (0.5, 0.974), 14.5)
sh.develop()
sh.save(out)
