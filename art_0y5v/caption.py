# Caption block: serif-bold title, an italic line, a small legend; optional inset drawn by a callback.
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

FB = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FI = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
FR = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
INK = (92, 77, 102)

def wrap(draw, text, font, width):
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def caption(img, title, line, legend, x0, y0, width, scale=1.0, fade=None, ink=INK):
    """Draw onto img (PIL RGB) starting at (x0, y0). fade=(y_start, y_end, colour) washes the band first."""
    W, H = img.size
    if fade is not None:
        ys, ye, col = fade
        a = np.zeros((H, W), np.float32)
        yy = np.arange(H)[:, None]
        a[:] = np.clip((yy - ys) / max(1, ye - ys), 0, 1)
        a = a * a * (3 - 2 * a) * 0.82
        base = np.asarray(img).astype(np.float32)
        out = base * (1 - a[..., None]) + np.array(col, np.float32) * a[..., None]
        img = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    ft = ImageFont.truetype(FB, int(64 * scale))
    fi = ImageFont.truetype(FI, int(44 * scale))
    fl = ImageFont.truetype(FI, int(32 * scale))
    y = y0
    d.text((x0, y), title, font=ft, fill=ink); y += int(84 * scale)
    for l in wrap(d, line, fi, width):
        d.text((x0, y), l, font=fi, fill=ink); y += int(54 * scale)
    y += int(10 * scale)
    for l in wrap(d, legend, fl, width):
        d.text((x0, y), l, font=fl, fill=ink + (0,) if False else ink); y += int(40 * scale)
    return img, y
