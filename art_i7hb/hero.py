"""Hero: a 12 x 12 lace of one thread.  140 pins, 6 buttons, exactly one way round."""
import sys, numpy as np
import cyano, lace
size = int(sys.argv[1]); out = sys.argv[2]
which = int(sys.argv[3]) if len(sys.argv) > 3 else 0
SOL = [[(0,11),(1,1),(4,0),(4,9),(8,0),(8,11)],
       [(0,9),(1,2),(1,6),(9,11),(11,3),(11,7)],
       [(0,11),(1,2),(1,6),(10,2),(11,5),(11,9)],
       [(0,0),(2,11),(5,10),(6,0),(10,2),(10,9)],
       [(0,3),(0,7),(1,10),(10,2),(10,6),(11,11)],
       [(0,11),(1,6),(2,1),(10,2),(11,5),(11,9)],
       [(1,10),(2,0),(6,2),(6,11),(8,0),(9,10)]]
M = N = 12; D = SOL[which]
assert lace.count(M, N, D) == 1
total = lace.count(M, N)
U = lace.unique_cycle(M, N, D)
sh = cyano.Sheet(size, seed=7 + which, ss=2, coat_box=(0.075, 0.06, 0.925, 0.855))
gr = lace.Grid(sh, M, N, (0.165, 0.118, 0.835, 0.797), seed=4, jitter=0.03, rot=-0.01)
im, d, ss = sh.canvas()
lace.draw_loop(sh, d, ss, gr, U, width=0.185, corner=0.24)
m = sh.to_mask(im)
sh.lay(m, opacity=0.975, halo=0.28, height=0.35, lift=lace.lift_field(sh, 5, 0.55, 150))
lace.lay_buttons(sh, gr, D, seed=2, r=0.41)
sh.expose()
sh.text('The Only Way Round', (0.5, 0.905), 38)
sh.text('one hundred and thirty-eight pins and six buttons: the thread that visits every pin once and comes home', (0.5, 0.940), 16.5)
sh.text(f'can be laid in exactly one way.   Lift the buttons and there are {total:,}.', (0.5, 0.964), 16.5)
# the one red: a collector's stamp, a 3 x 5 loop with its single button
n = sh.n; S = sh.S
from PIL import Image, ImageDraw
st = Image.new('L', (n, n), 0); dd = ImageDraw.Draw(st)
cx, cy, c = 0.895 * n, 0.935 * n, 8.5 * S
E = lace.unique_cycle(3, 5, [(0, 2)])
dd.rounded_rectangle([cx - 3.1 * c, cy - 2.1 * c, cx + 3.1 * c, cy + 2.1 * c], radius=int(0.8 * c), outline=255, width=max(1, int(1.6 * S)))
for r, cc, r2, c2 in E:
    dd.line([cx + (cc - 2) * c, cy + (r - 1) * c, cx + (c2 - 2) * c, cy + (r2 - 1) * c], fill=255, width=max(1, int(2.2 * S)))
dd.ellipse([cx - 0.3 * c, cy - 1.3 * c, cx + 0.3 * c, cy - 0.7 * c], fill=255)
sh.stamp(np.asarray(st, np.float32) / 255)
sh.develop()
sh.save(out)
