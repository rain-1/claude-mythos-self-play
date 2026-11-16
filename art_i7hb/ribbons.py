"""A haberdasher's card of fourteen ribbons, three pins wide and n = 3..16 pins long, each with the
fewest buttons that leave the thread one way round:  M(3,n) = floor(n/3) + [n = 1 mod 3]."""
import sys, numpy as np
import cyano, lace
size = int(sys.argv[1]); out = sys.argv[2]
def config(n):
    k, r = divmod(n, 3)
    side = lambda j: 0 if j % 2 == 0 else 2          # alternate top / bottom: any choice works
    D = [(side(j), 3 * j + 2) for j in range(k)]
    if r == 1: D.append((D[-1][0], n - 1))
    return D
sh = cyano.Sheet(size, seed=23, ss=2, coat_box=(0.07, 0.055, 0.93, 0.865))
cell = 0.0285
xL, xR = 0.150, 0.445
y0 = 0.105; pitch = 0.107
im, d, ss = sh.canvas()
allb = []; nums = np.zeros((size, size), np.float32)
for n in range(3, 17):
    D = config(n)
    assert lace.count(3, n, D) == 1 and len(D) == n // 3 + (n % 3 == 1)
    col = 0 if n <= 9 else 1; row = n - 3 if col == 0 else n - 10
    x = xL if col == 0 else xR; y = y0 + row * pitch
    box = (x, y, x + cell * n, y + cell * 3)
    gr = lace.Grid(sh, 3, n, box, seed=100 + n, jitter=0.03, rot=np.random.default_rng(n).normal(0, 0.012))
    lace.draw_loop(sh, d, ss, gr, lace.unique_cycle(3, n, D), width=0.19, corner=0.24, phase=n)
    allb.append((gr, D, n))
    nums = np.maximum(nums, sh.text(f'{n}', (x - 0.020, y + cell * 1.5), 21, anchor='rm', layer='mask', italic=False))
m = sh.to_mask(im)
sh.lay(m, opacity=0.975, halo=0.28, height=0.3, lift=lace.lift_field(sh, 9, 0.3, 110))
sh.lay(nums, opacity=0.9, height=0.4)   # paper numerals laid beside each ribbon
for gr, D, n in allb:
    lace.lay_buttons(sh, gr, D, seed=n, r=0.40)
sh.expose()
sh.text('A Button Every Third Pin', (0.5, 0.908), 36)
sh.text('ribbons three pins wide and 3 to 16 long, each with the fewest buttons that leave the thread one way round;', (0.5, 0.942), 15.5)
sh.text('any three clear columns let it go two ways, so a ribbon n long needs a third of n (rounded down), and one more when 3 divides n − 1', (0.5, 0.965), 15.5)
sh.develop(); sh.save(out)
