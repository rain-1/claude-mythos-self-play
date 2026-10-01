"""compose.py — caption block in plum ink on a finished render (sorbet house style).
usage: compose.py in.png out.png size "title" "italic line" "small line" ["small line 2"] [y0=0.885]
"""
import sys, numpy as np
from PIL import Image
from sorbet import text_mask, absorb, text_w

def to_lin(a):
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)

def to_srgb(l):
    l = np.clip(l, 0, 1)
    return np.where(l <= 0.0031308, 12.92 * l, 1.055 * l ** (1 / 2.4) - 0.055)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('y0=')]
    y0 = float(next((a[3:] for a in sys.argv if a.startswith('y0=')), 0.885))
    src, out, size = args[0], args[1], int(args[2])
    lines = args[3:]
    im = Image.open(src).convert('RGB')
    if im.size[0] != size:
        im = im.resize((size, size), Image.LANCZOS)
    S = size
    lin = to_lin(np.asarray(im, np.float32))
    items = []
    y = S * y0
    fonts = [('serif_bold', 0.025), ('italic', 0.0165), ('italic', 0.0128), ('italic', 0.0128)]
    gaps = [0.034, 0.024, 0.019, 0.019]
    for i, txt in enumerate(lines):
        fk, fs = fonts[min(i, 3)]
        sz = S * fs
        while text_w(txt, sz, fk) > S * 0.90:
            sz *= 0.97
        items.append((txt, S / 2, y, sz, fk, 'ms'))
        y += S * gaps[min(i, 3)]
    m = text_mask(S, S, items)
    # soften the paper under the caption so the ink reads (lift toward paper)
    ink = absorb((0.40, 0.31, 0.44))
    lin = lin * np.exp(-2.4 * m[..., None] * ink[None, None, :])
    srgb = to_srgb(lin) * 255 + np.random.default_rng(3).uniform(-0.5, 0.5, lin.shape)
    Image.fromarray(np.clip(srgb + 0.5, 0, 255).astype(np.uint8)).save(out, optimize=True)

if __name__ == '__main__':
    main()
