"""COMPANION 'The Tiling' — the dragon is a number system.
Base b = -1+i, digits {0,1}: every Gaussian integer has a unique finite
expansion (a canonical number system), and the fractional tile T = {sum d_k b^-k}
is the twindragon. Its ZZ[i]-translates pave the plane with no gaps and no overlaps.
The dragon curve of the hero is exactly the boundary between these tiles:
the same fold, seen as territory instead of path.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
import tm_common as C

B = -1 + 1j

def verify():
    ok = True
    for a in range(-8, 9):
        for c in range(-8, 9):
            n = complex(a, c); z = n; ds = []
            for _ in range(64):
                if z == 0: break
                d = int((z.real + z.imag) % 2)     # d = (a+b) mod 2  (residue mod b)
                ds.append(d); z = (z - d) / B
                z = complex(round(z.real), round(z.imag))
            rec = sum(d * B ** k for k, d in enumerate(ds))
            if abs(rec - n) > 1e-6 or z != 0:
                ok = False
    return ok

def tile_points(N=7_000_000, warm=40, seed=7):
    rng = np.random.default_rng(seed)
    d = rng.integers(0, 2, N + warm)
    z = 0 + 0j
    for i in range(warm):
        z = (z + d[i]) / B
    xs = np.empty(N); ys = np.empty(N)
    for i in range(N):
        z = (z + d[warm + i]) / B
        xs[i] = z.real; ys[i] = z.imag
    return xs, ys

# cohesive deep palette (dusk family), 6 hues; deepened so it reads as jewel/stained-glass
TILEHUES = 0.72 * np.array([
    [1.00, 0.70, 0.20],   # gold
    [0.90, 0.30, 0.22],   # ember
    [0.80, 0.16, 0.46],   # magenta
    [0.40, 0.18, 0.60],   # indigo
    [0.14, 0.42, 0.80],   # cyan
    [0.55, 0.30, 0.72],   # violet
])

def render(W=2560, out="companion_the_tiling.png"):
    assert verify(), "base -1+i is not a canonical number system?!"
    SS = 2; Ws = W * SS
    tx, ty = tile_points()
    # frame window — zoomed so each interlocking twindragon tile reads clearly
    cx, cy = -0.10, -0.50; half = 1.60
    def topix(x, y):
        px = (x - (cx - half)) / (2 * half) * Ws
        py = (y - (cy - half)) / (2 * half) * Ws
        return px, py
    acc = np.zeros((Ws, Ws, 3), np.float32)
    ntiles = 0
    for a in range(-9, 10):
        for c in range(-9, 10):
            X = tx + a; Y = ty + c
            px, py = topix(X, Y)
            m = (px >= 0) & (px < Ws) & (py >= 0) & (py < Ws)
            if not m.any():
                continue
            hue = TILEHUES[(3 * a + 2 * c) % len(TILEHUES)]
            # subtle per-tile brightness variation for depth (deterministic, no RNG-flicker)
            bri = 0.82 + 0.18 * (((a * 7 + c * 13) % 5) / 4.0)
            ix = px[m].astype(int); iy = py[m].astype(int)
            for ch in range(3):
                np.add.at(acc[:, :, ch], (iy, ix), hue[ch] * bri)
            ntiles += 1
    print("tiles drawn", ntiles)
    # light blur to knit chaos-game speckle into solid tiles, then bloom on the boundaries
    for ch in range(3):
        acc[:, :, ch] = gaussian_filter(acc[:, :, ch], 1.0 * SS)
    bloom = np.stack([C.wide_bloom(acc[:, :, ch], 4 * SS, 6) for ch in range(3)], 2)
    acc = acc + 0.14 * bloom
    b = C.filmic(acc, expo=2.2, gamma=1.02, pct=99.4)
    # deepen: vignette so it reads as a jewel mosaic, not a flat poster
    yy, xx = np.mgrid[0:Ws, 0:Ws]
    r = np.hypot(xx - Ws / 2, yy - Ws / 2) / (Ws / 2)
    vig = np.clip(1.04 - 0.60 * r ** 2.0, 0.22, 1.0)
    b = b * vig[..., None]
    # saturation lift for jewel tones
    lum = b.mean(2, keepdims=True); b = np.clip(lum + (b - lum) * 1.22, 0, 1)
    img = (b * 255).astype(np.uint8)
    im = Image.fromarray(img).resize((W, W), Image.LANCZOS)
    annotate(im)
    im.save(out)
    print("saved", out)

def annotate(im):
    d = ImageDraw.Draw(im); W = im.size[0]
    def font(sz, bold=False):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
        try: return ImageFont.truetype(p, sz)
        except Exception: return ImageFont.load_default()
    d.text((int(W*0.045), int(W*0.045)), "THE TILING", font=font(46, True), fill=(244, 232, 208))
    d.text((int(W*0.045), int(W*0.045)+58), "the dragon is a number system  ·  base b = −1+i, digits {0,1}",
           font=font(26), fill=(230, 205, 175))
    d.text((int(W*0.045), int(W*0.045)+94), "every Gaussian integer expands uniquely — the twindragon tile paves ℂ",
           font=font(22), fill=(225, 200, 175))
    d.text((int(W*0.045), int(W*0.955)-14),
           "each tile T = { Σ dₖ b⁻ᵏ } is one address of ℤ[i];  its boundary is the fold itself",
           font=font(22), fill=(230, 210, 185))

if __name__ == "__main__":
    render()
