"""BONUS — The Run That Ends in a Square  (Rabinowitsch's theorem as six candles)

x^2 + x + m is prime for EVERY x = 0..m-2  if and only if  h(-(4m-1)) = 1.
The six Heegner values m = 2, 3, 5, 11, 17, 41 (d = 7, 11, 19, 43, 67, 163) are
the only ones (m>1).  Each column: an unbroken rope of prime-light climbing from
x=0, snuffed at x = m-1 where the value is exactly m^2 - a perfect square,
drawn as a cyan square.  Above the square the light continues only as broken
sparks (primes among composites), dissolving: the melody ends, the weather
begins.  Verified in-script: every streak value prime, every break = m^2,
and streak maximality.
"""
import numpy as np, math, sys, time
from scipy.ndimage import gaussian_filter
import kit

PROTO = "--proto" in sys.argv
S = 1024 if PROTO else 2560
SS = 1 if PROTO else 2
W = H = S * SS
rs = W / 1024.0
t0 = time.time()

def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True

MS = [(2, 7), (3, 11), (5, 19), (11, 43), (17, 67), (41, 163)]
EXTRA = 14
for m, d in MS:
    assert d == 4 * m - 1
    assert all(is_prime(x * x + x + m) for x in range(m - 1))
    assert (m - 1) ** 2 + (m - 1) + m == m * m and not is_prime(m * m)
print("streaks + square breaks verified")

buf = np.zeros((H, W, 3), np.float32)
GOLD = np.array([1.0, 0.82, 0.38], np.float32)
EMBER = np.array([0.95, 0.45, 0.15], np.float32)
ICE = np.array([0.45, 0.85, 1.0], np.float32)

nmax = 41 + EXTRA
y0 = 0.88 * H                       # floor (x = 0)
y1 = 0.075 * H                      # top (x = nmax)
def ypos(x):
    return y0 + (y1 - y0) * x / nmax

cols = np.linspace(0.13, 0.87, len(MS)) * W
rope = np.zeros((H, W), np.float32)
spark = np.zeros((H, W), np.float32)
sq = np.zeros((H, W), np.float32)
for (m, d), cx in zip(MS, cols):
    # unbroken rope of prime light: x = 0 .. m-2
    ya, yb = ypos(0), ypos(m - 2)
    kit.line_splat(rope, cx, ya, cx, yb, 5.0 * (ya - yb) if m > 2 else 30.0,
                   n=int(max(30, ya - yb)))
    # beads at each streak prime
    for x in range(m - 1):
        kit.splat_points(spark, [cx], [ypos(x)], 0.85, 2.6 * rs, (H, W))
    # the square break at x = m-1 (value m^2): cyan square outline
    yq = ypos(m - 1)
    hs = 7.5 * rs
    for a, b, cc, dd in [(cx - hs, yq - hs, cx + hs, yq - hs),
                         (cx + hs, yq - hs, cx + hs, yq + hs),
                         (cx + hs, yq + hs, cx - hs, yq + hs),
                         (cx - hs, yq + hs, cx - hs, yq - hs)]:
        kit.line_splat(sq, a, b, cc, dd, 26.0 * rs, n=int(20 * rs))
    # after the square: honest weather - sparks only where prime, fading
    for x in range(m, m + EXTRA):
        v = x * x + x + m
        if is_prime(v):
            fade = 0.55 * (0.90 ** (x - m))
            kit.splat_points(spark, [cx], [ypos(x)], fade, 2.2 * rs, (H, W))
        else:
            kit.splat_points(spark, [cx], [ypos(x)], 0.06, 1.6 * rs, (H, W))

restore = 0.35 + 0.65 * rs
rope_c = gaussian_filter(rope, 1.6 * rs) * restore
rope_g = gaussian_filter(rope, 9 * rs) * restore * 5.0
buf += np.clip(rope_c, 0, 1.1)[..., None] * GOLD[None, None, :]
buf += np.clip(rope_g, 0, 0.45)[..., None] * EMBER[None, None, :] * 0.9
buf += np.clip(spark, 0, 1.3)[..., None] * np.array([1.0, 0.93, 0.7], np.float32)[None, None, :] * 1.1
sq_c = gaussian_filter(sq, 1.2 * rs) * restore
sq_g = gaussian_filter(sq, 7 * rs) * restore * 4.0
buf += np.clip(sq_c, 0, 1.2)[..., None] * ICE[None, None, :] * 1.25
buf += np.clip(sq_g, 0, 0.4)[..., None] * ICE[None, None, :] * 0.55

# the law: a whisper-thread through the six squares (break height = m-1)
law = np.zeros((H, W), np.float32)
pts = [(cx, ypos(m - 1)) for (m, d), cx in zip(MS, cols)]
for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
    kit.line_splat(law, xa, ya, xb, yb, 40.0, n=800)
buf += np.clip(gaussian_filter(law, 1.4 * rs) * restore, 0, 0.14)[..., None] * \
    ICE[None, None, :] * 0.7

# faint floor line
fl = np.zeros((H, W), np.float32)
kit.line_splat(fl, 0.06 * W, y0 + 14 * rs, 0.94 * W, y0 + 14 * rs, 140.0, n=3000)
buf += np.clip(gaussian_filter(fl, 1.5 * rs) * restore, 0, 0.25)[..., None] * \
    np.array([0.5, 0.45, 0.4], np.float32)[None, None, :]

buf = kit.bloom(buf, mask_thresh=0.55, sigma=16 * rs, gain=0.3, tint=(1.0, 0.9, 0.7))
img = kit.filmic(buf, k=1.35, gamma=0.92)
if SS > 1:
    from PIL import Image
    img = np.array(Image.fromarray(img).resize((S, S), Image.LANCZOS))

fs = max(13, int(14 * S / 1024))
texts = []
for (m, d), cx in zip(MS, cols):
    texts.append((cx / SS, y0 / SS + 30 * S / 1024, f"m={m}", "mm", (210, 190, 150)))
    texts.append((cx / SS, y0 / SS + 30 * S / 1024 + 1.5 * fs, f"d={d}", "mm", (140, 135, 125)))
    yq = ypos(m - 1) / SS
    texts.append((cx / SS + 16 * S / 1024, yq, f"{m * m} = {m}^2", "lm", (150, 195, 215)))
texts.append((S * 0.035, S * 0.045, "THE RUN THAT ENDS IN A SQUARE", "lm", (190, 170, 130)))
texts.append((S * 0.035, S * 0.045 + 1.8 * fs,
              "x^2 + x + m is prime for ALL x = 0..m-2  <=>  h(-(4m-1)) = 1   (Rabinowitsch 1913)",
              "lm", (140, 132, 118)))
texts.append((S * 0.035, S * 0.045 + 3.3 * fs,
              "six columns of unbroken prime-light; each dies exactly on a perfect square,",
              "lm", (140, 132, 118)))
texts.append((S * 0.035, S * 0.045 + 4.8 * fs,
              "then the weather: primes only sometimes.  m=41 is Euler's polynomial; d=163.",
              "lm", (140, 132, 118)))
img = kit.stamp_text(img, texts, fontsize=fs)
from PIL import Image
out = "streaks_proto.png" if PROTO else "run_that_ends_in_a_square.png"
Image.fromarray(img).save(out)
print("saved", out, f"{time.time()-t0:.0f}s")
