"""HERO 'The Fold' — the paperfolding dragon as a glowing gradient thread.
Folding = complement + reverse: the negation of the reversed negation.
One unit-step curve, colored by arc-time through the shared dusk ramp, coils
and spirals and fills the plane; the self-similar boundary is its own fringe.
k=19 (524288 segments), rotated 30 deg so the lattice weave reads organic.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import tm_common as C

def render(k=19, rot_deg=70, W=4096, SS=2, expo=3.0, gamma=0.92, pct=99.9,
           sat=1.16, out="hero_the_fold.png"):
    x, y = C.dragon_xy(k)
    th = np.deg2rad(rot_deg); ca, sa = np.cos(th), np.sin(th)
    x, y = ca * x - sa * y, sa * x + ca * y
    Ws = W * SS
    x0, x1 = x.min(), x.max(); y0, y1 = y.min(), y.max()
    pad = 0.045
    sc = (1 - 2 * pad) / max(x1 - x0, y1 - y0)
    px = (x - (x0 + x1) / 2) * sc * Ws + Ws / 2
    py = (y - (y0 + y1) / 2) * sc * Ws + Ws / 2
    T = np.linspace(0, 1, len(px)); col = C.ramp(T)
    acc = np.zeros((Ws, Ws, 3), np.float32)
    seglen = sc * Ws
    nsub = max(2, int(seglen / 1.0))
    ts = np.linspace(0, 1, nsub, endpoint=False)
    print(f"k={k}: {len(px)} vertices, nsub={nsub}, splatting {len(px)*nsub/1e6:.1f}M samples ...")
    ax = px[:-1][:, None] + (px[1:] - px[:-1])[:, None] * ts[None, :]
    ay = py[:-1][:, None] + (py[1:] - py[:-1])[:, None] * ts[None, :]
    cc = (col[:-1][:, None, :] * (1 - ts)[None, :, None] +
          col[1:][:, None, :] * ts[None, :, None])
    C.bilinear_splat(acc, ax.ravel(), ay.ravel(), cc.reshape(-1, 3), w=1.0 / nsub)
    print("blur + bloom ...")
    for c in range(3):
        acc[:, :, c] = gaussian_filter(acc[:, :, c], 0.45 * SS)
    bloom = np.stack([C.wide_bloom(acc[:, :, c], 5 * SS, 6) for c in range(3)], 2)
    acc = acc + 0.16 * bloom
    b = C.filmic(acc, expo=expo, gamma=gamma, pct=pct)
    lum = b.mean(2, keepdims=True); b = np.clip(lum + (b - lum) * sat, 0, 1)
    img = (b * 255).astype(np.uint8)
    im = Image.fromarray(img).resize((W, W), Image.LANCZOS)
    im.save(out)
    print("saved", out, im.size)

if __name__ == "__main__":
    render()
