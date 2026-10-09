"""Pieces of a rolling-shutter needle.  Row y (relative to the hub) sees the needle at angle
phi(y) = M + c*y; the needle point on that row is at r = y/sin(phi), valid iff 0 <= r <= R.
So the image is the cotangent graph x = y*cot(M + c*y), and its pieces are the maximal runs of
rows with 0 <= y/sin(phi) <= R.  Mean number of pieces over M, as a function of e = cR."""
import numpy as np
def pieces(e, M, R=1.0, n=400001):
    c = e/R
    y = np.linspace(-R, R, n)
    s = np.sin(M + c*y)
    with np.errstate(divide='ignore', invalid='ignore'):
        r = y/s
    ok = (r >= 0) & (r <= R)
    ok[n//2] = True                                  # the hub row: the needle's root is always there
    starts = np.sum(ok[1:] & ~ok[:-1]) + ok[0]
    return starts
rng = np.random.default_rng(0)
print(' e    mean pieces   (2e/pi + 1)   ratio')
for e in [0.5, 1.0, 1.5, 2, 3, 5, 8, 12, 20, 40, 80]:
    m = np.mean([pieces(e, rng.uniform(0, 2*np.pi)) for _ in range(400)])
    print(f'{e:5.1f}   {m:8.3f}    {2*e/np.pi + 1:8.3f}   {m/(2*e/np.pi+1):.3f}')
