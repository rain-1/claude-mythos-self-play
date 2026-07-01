"""
03 — THE REAL THE LIST FORGOT
================================================================
Cantor's diagonal argument (1891). Suppose you had a list -- a countable
enumeration -- of all the real numbers in [0,1], each written in binary as a
row. Read the digits down the main diagonal (row n, column n) and FLIP every
one. The resulting number differs from row 1 in its 1st digit, from row 2 in
its 2nd digit, from row n in its nth digit -- so it equals no row of the list.
Whatever list you propose, it forgets a real. The reals are uncountable.

The list drawn here is the infinite Walsh-Hadamard array: row n, column k is the
parity of the bits shared by n and k. It is exact, self-similar at every scale,
and orthogonal -- a clean stand-in for "an enumeration of patterns." Its main
diagonal happens to be the Thue-Morse sequence 0110100110010110... ; Cantor's
flip of it, 1001011001101001..., blazes in gold across the field and is repeated
as the strip below. That gold real is provably no row of the array above it.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

M = 512                       # rows/cols of the list
UP = 4                        # pixels per cell
Wf = M*UP
# ---- Walsh-Hadamard field: parity of popcount(n & k) ----
n = np.arange(M)[:, None]; k = np.arange(M)[None, :]
x = (n & k).astype(np.int64)
par = np.zeros_like(x)
while x.any():
    par ^= (x & 1); x >>= 1
T = par.astype(np.float64)                     # 0/1 field
diag = np.array([int(T[i, i]) for i in range(M)])
tm = np.array([bin(i).count('1') & 1 for i in range(M)])
assert np.array_equal(diag, tm), "diagonal must be Thue-Morse"
escaped = 1-diag
print("diagonal (Thue-Morse):", ''.join(map(str, diag[:32])))
print("escaped real (flip)  :", ''.join(map(str, escaped[:32])))
print("the escaped real equals no row?",
      all(not np.array_equal(escaped, T[r].astype(int)) for r in range(M)))

# ---- render the field, cool self-similar, with a soft radial depth ----
fieldpix = np.kron(T, np.ones((UP, UP)))       # M*UP square
Hh = Wf + int(Wf*0.19)                          # room for the escaped strip + label
img = np.zeros((Hh, Wf, 3))
img[:] = np.array([0.015, 0.020, 0.040])
yy, xx = np.mgrid[0:Wf, 0:Wf]
rad = np.sqrt(((xx-Wf/2)/(Wf*0.62))**2 + ((yy-Wf/2)/(Wf*0.62))**2)
vig = np.clip(1.15-0.5*rad, 0.35, 1.0)
blue = np.array([0.26, 0.40, 0.72])
for c in range(3):
    img[:Wf, :, c] += fieldpix*blue[c]*vig

# ---- the escaped real: gold main diagonal, blazing ----
gold = np.zeros((Wf, Wf))
for i in range(M):
    y0, x0 = i*UP, i*UP
    gold[y0:y0+UP, x0:x0+UP] = 1.0
goldb = gaussian_filter(gold, UP*0.9)
goldb /= goldb.max()+1e-9
glow = gaussian_filter(gold, UP*3.0); glow /= glow.max()+1e-9
gcol = np.array([1.0, 0.82, 0.34])
for c in range(3):
    img[:Wf, :, c] += goldb*gcol[c]*1.15 + glow*gcol[c]*0.55

# ---- the escaped real as a bit-strip below the field ----
strip_y0 = Wf + int(Wf*0.045)
sh = int(Wf*0.055)
bar = np.zeros((sh, Wf))
for kk in range(M):
    if escaped[kk]:
        bar[:, kk*UP:kk*UP+UP] = 1.0
barg = gaussian_filter(bar, 1.4)
for c in range(3):
    img[strip_y0:strip_y0+sh, :, c] += barg*gcol[c]*1.0
# thin connector: the diagonal's last cell down to the strip
img[Wf:strip_y0, Wf-UP:Wf, :] += gcol*0.25

img = 1-np.exp(-np.clip(img, 0, None)*1.35)
img = np.clip(img, 0, 1)**0.92
Image.fromarray((img*255).astype(np.uint8)).save(
    __file__.replace('03_the_list_forgot.py', '03_the_list_forgot.png'))
print("saved 03_the_list_forgot.png", Wf, "x", Hh)
