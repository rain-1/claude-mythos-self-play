"""
02 — MORE SUMS THAN DIFFERENCES
================================================================
Take a finite set of integers A and form all pairwise sums (A+A) and all
pairwise differences (A-A). Subtraction is not commutative -- a-b and b-a are
generally different -- while a+b = b+a collides, so a set almost always has
MORE distinct differences than sums: |A-A| > |A+A|. Among ~random subsets of
[0,32) fewer than one in two thousand break the rule.

This is one that breaks it. The classic minimal counterexample (Conway, Marica)
    A = {0, 2, 3, 4, 7, 11, 12, 14}
has |A+A| = 26 and |A-A| = 25: a "sum-dominant" (MSTD) set, and by the smallest
possible margin. Every pair {a,b} is drawn as a semicircle whose apex sits over
the sum (a+b)/2 and whose radius is the difference (b-a)/2 -- a loom in which
each thread is one addition and one subtraction at once. The gold comb above the
line marks the 26 distinct sums; the rose comb below marks the 25 distinct
differences. The rule, and its rare exception, in one figure.
"""
import numpy as np, colorsys, sys
from PIL import Image
from scipy.ndimage import gaussian_filter

SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
W = int(2400*SCALE); Hh = int(1500*SCALE)
A = np.array([0, 2, 3, 4, 7, 11, 12, 14])
from collections import Counter
rp = Counter(int(a+b) for a in A for b in A)
rm = Counter(int(a-b) for a in A for b in A)
Sset = sorted(rp); Dset = sorted(rm)
print(f"|A+A|={len(Sset)}  |A-A|={len(Dset)}  -> "
      f"{'MSTD (sums win)' if len(Sset)>len(Dset) else 'differences win'}")

lo, hi = A.min(), A.max(); span = hi-lo
L = int(W*0.11)
mid = int(Hh*0.60)
def xset(v): return (v-lo)/span*(W-2*L)+L
smin, smax = 2*lo, 2*hi
def xsum(v): return (v-smin)/(smax-smin)*(W-2*L)+L
dmax = hi-lo
def xdiff(v): return (v+dmax)/(2*dmax)*(W-2*L)+L

img = np.zeros((Hh, W, 3))
img[:] = np.array([0.020, 0.024, 0.045])
yy, xx = np.mgrid[0:Hh, 0:W]

# ---- the arc loom: each pair a semicircle (apex=sum, radius=difference) ----
diffs = sorted(set(abs(a-b) for a in A for b in A if a != b))
pal = {d: colorsys.hsv_to_rgb((0.58 - 0.52*i/max(1, len(diffs)-1)) % 1.0, 0.64, 1.0)
       for i, d in enumerate(diffs)}
lw = 1.7*SCALE
for i in range(len(A)):
    for j in range(i+1, len(A)):
        a, b = A[i], A[j]
        cx = xset((a+b)/2.0); r = (xset(b)-xset(a))/2.0
        d = np.sqrt((xx-cx)**2 + (yy-mid)**2)
        ring = np.exp(-((d-r)/lw)**2); ring[yy > mid] = 0
        img += ring[..., None]*np.array(pal[abs(a-b)])*0.42
        # faint mirror below for a woven mandorla
        d2 = np.sqrt((xx-cx)**2 + (yy-mid)**2)
        ring2 = np.exp(-((d2-r)/lw)**2); ring2[yy < mid] = 0
        img += ring2[..., None]*np.array(pal[abs(a-b)])*0.11

# ---- fast buffer helpers: splat vertical stems + cap dots, blur once ----
def vstem(buf, x, y0, y1, w=1.0):
    x = int(round(x)); ya, yb = sorted((int(y0), int(y1)))
    buf[ya:yb+1, max(0, x-1):x+2] += w

node = np.zeros((Hh, W))
for a in A:
    x = int(round(xset(a))); node[mid-2:mid+3, x-2:x+3] += 1.0
node = gaussian_filter(node, 3.0*SCALE); node /= node.max()+1e-9

# sum comb (gold up) & difference comb (rose down); brighter cap at each tip
sumbuf = np.zeros((Hh, W)); diffbuf = np.zeros((Hh, W))
def comb(values, mult, xf, ybase, direction, buf, hmax):
    mm = max(mult.values())
    for v in values:
        x = xf(v); h = (0.32+0.68*mult[v]/mm)*hmax
        ytip = int(ybase-direction*h)
        vstem(buf, x, ybase, ytip, 0.7)
        xi = int(round(x))
        buf[max(0, ytip-3):ytip+4, max(0, xi-3):xi+4] += 2.2   # cap
comb(Sset, rp, xsum, mid-int(16*SCALE), +1, sumbuf, int(Hh*0.17))
comb(Dset, rm, xdiff, mid+int(16*SCALE), -1, diffbuf, int(Hh*0.17))
sumbuf = gaussian_filter(sumbuf, 1.6*SCALE); diffbuf = gaussian_filter(diffbuf, 1.6*SCALE)
for ch, a in enumerate((1.0, 0.85, 0.42)):
    img[..., ch] += node*a*1.15
for ch, a in enumerate((1.0, 0.80, 0.28)):
    img[..., ch] += sumbuf*a*0.60
for ch, a in enumerate((1.0, 0.42, 0.50)):
    img[..., ch] += diffbuf*a*0.60

img = 1 - np.exp(-np.clip(img, 0, None)*1.3)
img = np.clip(img, 0, 1)**0.92
Image.fromarray((img*255).astype(np.uint8)).save(
    __file__.replace('02_more_sums.py', '02_more_sums.png'))
print("saved 02_more_sums.png", W, "x", Hh)
