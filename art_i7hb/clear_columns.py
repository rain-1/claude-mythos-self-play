"""The lemma as a double exposure.  3 x 11 pins.
row 1: buttons at columns 3, 6, 9 (counting from 1): one way round.
row 2: the middle button slid along: four clear columns, and the thread can go two ways --
       laid one way for the morning and the other for the afternoon.
rows 3, 4: the two ways apart."""
import sys, numpy as np
from PIL import Image
import cyano, lace
size = int(sys.argv[1]); out = sys.argv[2]
n = 11
A = [(0, 2), (2, 5), (0, 8)]; B = [(0, 2), (0, 3), (0, 8)]
assert lace.count(3, n, A) == 1 and lace.count(3, n, B) == 2
two = sorted(set(tuple(sorted(s)) for s in lace.samples(3, n, 40, 1, B)))
assert len(two) == 2
sh = cyano.Sheet(size, seed=31, ss=2, coat_box=(0.07, 0.05, 0.93, 0.865))
cell = 0.060; x = 0.5 - cell * n / 2 + 0.012; y0 = 0.095; pitch = 0.192
grids = [lace.Grid(sh, 3, n, (x, y0 + i * pitch, x + cell * n, y0 + i * pitch + 3 * cell), seed=40 + (1 if i else 0), jitter=0.028,
                   rot=[0.006, -0.008, -0.008, -0.008][i]) for i in range(4)]
# rows 2-4 share one hand's jitter so the two ways register exactly
halves = np.zeros((size, size), np.float32)
for k in range(2):
    im, d, ss = sh.canvas()
    lace.draw_loop(sh, d, ss, grids[1], list(two[k]), width=0.17, corner=0.24, phase=k)
    halves += 0.5 * sh.to_mask(im)
im, d, ss = sh.canvas()
lace.draw_loop(sh, d, ss, grids[0], lace.unique_cycle(3, n, A), width=0.17, corner=0.24)
lace.draw_loop(sh, d, ss, grids[2], list(two[0]), width=0.17, corner=0.24)
lace.draw_loop(sh, d, ss, grids[3], list(two[1]), width=0.17, corner=0.24, phase=1)
for g, D in zip(grids, [A, B, B, B]): lace.draw_pins(d, ss, g, skip=set(D), r=0.04)
m = sh.to_mask(im)
labels = np.zeros((size, size), np.float32)
for i, t in enumerate(['one way', 'both', 'morning', 'afternoon']):
    labels = np.maximum(labels, sh.text(t, (x - 0.018, y0 + i * pitch + 1.5 * cell), 23, anchor='rm', layer='mask'))
sh.lay(np.clip(halves, 0, 1) ** 0.45, opacity=0.975, height=0.4)
sh.lay(m, opacity=0.975, halo=0.28, height=0.3)
sh.lay(labels, opacity=0.9, height=0.4)
for i, (g, D) in enumerate(zip(grids, [A, B, B, B])): lace.lay_buttons(sh, g, D, seed=7 if i else 3, r=0.40)
sh.expose()
sh.text('Three Clear Columns', (0.5, 0.908), 36)
sh.text('slide one button along and the ribbon has a stretch of clear columns; there the thread can be laid two ways.', (0.5, 0.942), 15.5)
sh.text('The second sheet had half the day under each: white where the two agree, half blue where they part.', (0.5, 0.965), 15.5)
sh.develop(); sh.save(out)
