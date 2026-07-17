"""COMPANION 'The Shattering' — the Thue-Morse diffraction (spectral) measure.
A single smooth cosine (k=1) shatters, at every doubling, into a self-similar
spray of spikes: the absolutely-continuous -> singular-continuous collapse.
The Thue-Morse crystal has NO Bragg peaks -- an order you cannot resolve into
pure tones. Quantity (levels) becomes quality (a new kind of measure).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
import tm_common as C

def wk(theta, k):
    """diffraction density w_k = (1/2^k)|S_{2^k}|^2 = prod_{j<k} 2 sin^2(pi 2^j theta); integral 1."""
    d = np.ones_like(theta)
    for j in range(k):
        d = d * 2 * np.sin(np.pi * (2.0 ** j) * theta) ** 2
    return d

def render(W=2560, H=2560, kmax=13, out="companion_the_shattering.png"):
    SS = 2
    Ws, Hs = W * SS, H * SS
    acc = np.zeros((Hs, Ws, 3), np.float32)
    th = np.linspace(0, 1, Ws)  # full spectrum [0,1)
    top_m = 0.12; bot_m = 0.06
    y_base = np.linspace(Hs * (1 - bot_m), Hs * top_m, kmax)  # k=1 low, kmax high
    amp = 0.115 * Hs
    # ramp cyan(smooth)->gold(shattered)
    def rowcol(frac):  # frac 0 (k=1) -> 1 (kmax)
        return C.ramp(0.95 - 0.9 * frac)  # 0.95~cyan end .. 0.05~gold
    yfront = np.full(Ws, Hs, np.float32)  # hidden-line running front (draw back->front = low k first)
    for ki in range(kmax):
        k = ki + 1
        d = wk(th, k); d = d / (d.max() + 1e-12)
        frac = ki / (kmax - 1)
        col = rowcol(frac)
        yline = (y_base[ki] - d * amp)
        # fill under ridge down to a little below baseline, with vertical fade; occlude where behind front
        xr = np.arange(Ws)
        ytop = np.clip(yline.astype(int), 0, Hs - 1)
        for x in xr:
            y0 = ytop[x]
            y1 = int(min(Hs, y_base[ki] + 6 * SS))
            if y1 <= y0:
                continue
            ys = np.arange(y0, y1)
            fade = np.clip(1 - (ys - y0) / (amp * 0.9), 0.0, 1.0) ** 1.6  # bright at ridge
            vis = ys < yfront[x]  # only where not hidden by nearer (already-drawn lower-k) ridge... front updated after
            body = 0.18 + 0.82 * fade
            acc[ys, x, 0] += col[0] * body * 0.9
            acc[ys, x, 1] += col[1] * body * 0.9
            acc[ys, x, 2] += col[2] * body * 0.9
            # bright ridge edge
            acc[max(0, y0 - 1 * SS):y0 + 1 * SS, x] += col * 1.4
        # update hidden-line front to the min (nearest to top) so higher rows occlude
        yfront = np.minimum(yfront, yline)
    # glow
    for c in range(3):
        acc[:, :, c] = gaussian_filter(acc[:, :, c], 0.6 * SS)
    bloom = np.stack([C.wide_bloom(acc[:, :, c], 4 * SS, 6) for c in range(3)], 2)
    acc = acc + 0.22 * bloom
    b = C.filmic(acc, expo=2.6, gamma=0.9, pct=99.7)
    img = (b * 255).astype(np.uint8)
    im = Image.fromarray(img).resize((W, H), Image.LANCZOS)
    annotate(im)
    im.save(out)
    print("saved", out)

def annotate(im):
    d = ImageDraw.Draw(im)
    def font(sz):
        for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
            try: return ImageFont.truetype(p, sz)
            except Exception: pass
        return ImageFont.load_default()
    W = im.size[0]
    d.text((int(W*0.045), int(W*0.045)), "THE SHATTERING", font=font(46), fill=(240, 226, 200))
    d.text((int(W*0.045), int(W*0.045)+58), "Thue–Morse diffraction  ·  purely singular-continuous spectrum",
           font=font(26), fill=(150, 170, 210))
    d.text((int(W*0.045), int(W*0.045)+94), "0→01, 1→10 : each doubling splits every peak — no Bragg lines survive",
           font=font(22), fill=(120, 135, 165))
    # bottom axis label
    d.text((int(W*0.045), int(W*0.955)-14), "spectral variable  θ ∈ [0,1)   —   levels k = 1 (smooth)  →  13 (shattered)",
           font=font(22), fill=(120, 135, 165))

if __name__ == "__main__":
    render()
